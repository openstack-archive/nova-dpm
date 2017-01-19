# Copyright 2016 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A connection to a z Systems through Dynamic Partition Manager( DPM) APIs.

Supports DPM APIs for virtualization in z Systems
"""

import nova_dpm.conf

from nova import context as context_object
from nova import exception
from nova.objects import flavor as flavor_object
from nova.virt import driver
from nova_dpm.virt.dpm import client_proxy
from nova_dpm.virt.dpm import host as Host
from nova_dpm.virt.dpm import utils
from nova_dpm.virt.dpm import vm
from oslo_log import log as logging
from oslo_utils import importutils

LOG = logging.getLogger(__name__)
CONF = nova_dpm.conf.CONF

dpm_volume_drivers = [
    'fibre_channel=nova_dpm.virt.dpm.volume.'
    'fibrechannel.DpmFibreChannelVolumeDriver',
]


class DPMDriver(driver.ComputeDriver):

    def __init__(self, virtapi):
        super(DPMDriver, self).__init__(virtapi)
        LOG.debug("__init__")
        self.virtapi = virtapi
        self._compute_event_callback = None

        self._host = None
        self._client = None
        self._cpc = None

        # Retrieve zhmc ipaddress, username, password from the nova.conf
        zhmc = CONF.dpm.hmc
        userid = CONF.dpm.hmc_username
        password = CONF.dpm.hmc_password

        self._client = client_proxy.get_client_for_sesion(zhmc, userid,
                                                          password)
        LOG.debug("HMC details %(zhmc)s %(userid)s"
                  % {'zhmc': zhmc, 'userid': userid})

        self._initiator = None
        self._fc_wwnns = None
        self._fc_wwpns = None

        self.volume_drivers = self._get_volume_drivers()

    def init_host(self, host):
        """Driver initialization of the hypervisor node"""
        LOG.debug("init_host")

        # retrieve from ncpu service configurationfile
        self._conf = {'cpcsubset_name': CONF.dpm.host,
                      'cpc_uuid': CONF.dpm.cpc_uuid,
                      'max_processors': CONF.dpm.max_processors,
                      'max_memory_mb': CONF.dpm.max_memory,
                      'max_partitions': CONF.dpm.max_instances,
                      'physical_storage_adapter_mappings':
                          CONF.dpm.physical_storage_adapter_mappings}

        self._cpc = self._client.cpcs.find(**{
            "object-id": self._conf['cpc_uuid']})
        LOG.debug("Matching hypervisor found %(cpcsubset_name)s for UUID "
                  "%(uuid)s and CPC %(cpcname)s" %
                  {'cpcsubset_name': self._conf['cpcsubset_name'],
                   'uuid': self._conf['cpc_uuid'],
                   'cpcname': self._cpc.properties['name']})

        utils.valide_host_conf(self._conf, self._cpc)
        self._host = Host.Host(self._conf, self._cpc, self._client)

    def get_available_resource(self, nodename):
        """Retrieve resource information.

        This method is called when nova-compute launches, and
        as part of a periodic task that records the results in the DB.

        :param nodename:
            node which the caller want to get resources from
            a driver that manages only one node can safely ignore this
        :returns: Dictionary describing resources
        """
        LOG.debug("get_available_resource")

        dictval = self._host.properties

        return dictval

    def get_available_nodes(self, refresh=False):
        """Returns nodenames of all nodes managed by the compute service.

        This method is for multi compute-nodes support. If a driver supports
        multi compute-nodes, this method returns a list of nodenames managed
        by the service. Otherwise, this method should return
        [hypervisor_hostname].
        """
        # TODO(preethipy): Refresh parameter should be handled to fetch
        # updated nodenames
        LOG.debug("get_available_nodes return node %(cpcsubset_name)s" %
                  {'cpcsubset_name': self._host.properties[
                      "hypervisor_hostname"]})
        nodenames = [self._host.properties["hypervisor_hostname"]]

        return nodenames

    def node_is_available(self, nodename):
        """Return whether this compute service manages a particular node."""
        LOG.debug("node_is_available")

        if nodename in self.get_available_nodes():
            return True
        # Refresh and check again.
        return nodename in self.get_available_nodes(refresh=True)

    def attach_volume(self, context, connection_info, instance, mountpoint,
                      disk_bus=None, device_type=None, encryption=None):

        # There currently is no need for disk_info. I just left it in
        # in case we need it in the future
        disk_info = {}
        self._connect_volume(connection_info, disk_info)

    def detach_volume(self, connection_info, instance, mountpoint,
                      encryption=None):

        # There currently is no need for disk_dev. I just left it in
        # in case we need it in the future
        disk_dev = {}
        self._disconnect_volume(connection_info, disk_dev)

    def _get_volume_drivers(self):
        driver_registry = dict()
        for driver_str in dpm_volume_drivers:
            driver_type, _sep, driver = driver_str.partition('=')
            driver_class = importutils.import_class(driver)
            driver_registry[driver_type] = driver_class(self._host)
        return driver_registry

    def _get_volume_driver(self, connection_info):
        driver_type = connection_info.get('driver_volume_type')
        if driver_type not in self.volume_drivers:
            raise exception.VolumeDriverNotFound(driver_type=driver_type)
        return self.volume_drivers[driver_type]

    def get_volume_connector(self, instance):
        """The Fibre Channel connector properties."""
        inst = vm.Instance(instance, self._cpc)
        inst.get_hba_properties()
        props = {}
        wwpns = {}

        # TODO(stefan) replace the next lines of code by a call
        # to DPM to retrieve WWPNs for the instance
        hbas = ["0x50014380242b9751", "0x50014380242b9711"]

        if hbas:
            for hba in hbas:
                wwpn = hba.replace('0x', '')
                wwpns.append(wwpn)

        if wwpns:
            props['wwpns'] = wwpns

        return props

    def _connect_volume(self, connection_info, disk_info):
        vol_driver = self._get_volume_driver(connection_info)
        vol_driver.connect_volume(connection_info, disk_info)

    def _disconnect_volume(self, connection_info, disk_dev):
        vol_driver = self._get_volume_driver(connection_info)
        vol_driver.disconnect_volume(connection_info, disk_dev)

    def list_instances(self):

        partition_manager = self._cpc.partitions
        partition_lists = partition_manager.list(full_properties=False)

        part_list = []
        for partition in partition_lists:
            part_list.append(partition.get_property('name'))

        return part_list

    def get_info(self, instance):

        info = vm.InstanceInfo(instance, self._cpc)

        return info

    def spawn(self, context, instance, image_meta, injected_files,
              admin_password, network_info=None, block_device_info=None,
              flavor=None):

        if not flavor:
            context = context_object.get_admin_context(read_deleted='yes')
            flavor = (
                flavor_object.Flavor.get_by_id(context,
                                               instance.instance_type_id))
        LOG.debug("Flavor = %(flavor)s" % {'flavor': flavor})

        inst = vm.Instance(instance, self._cpc, self._client, flavor)
        inst.create(inst.properties())
        for vif in network_info:
            inst.attach_nic(self._conf, vif)

        block_device_mapping = driver.block_device_info_get_mapping(
            block_device_info)
        inst.attachHba(self._conf)
        inst._build_resources(context, instance, block_device_mapping)
        # TODO (andreas_s): Replace with target WWPN and LUN once cinder
        # integration is available
        inst.add_boot_property('boot-device', 'test-operating-system')

        inst.launch()

    def destroy(self, context, instance, network_info, block_device_info=None,
                destroy_disks=True, migrate_data=None):
        inst = vm.Instance(instance, self._cpc, self._client)
        inst.destroy()

    def power_off(self, instance, timeout=0, retry_interval=0):
        inst = vm.Instance(instance, self._cpc, self._client)
        inst.power_off_vm()

    def power_on(self, context, instance, network_info,
                 block_device_info=None):
        inst = vm.Instance(instance, self._cpc, self._client)
        inst.power_on_vm()

    def reboot(self, context, instance, network_info, reboot_type,
               block_device_info=None, bad_volumes_callback=None):
        inst = vm.Instance(instance, self._cpc, self._client)
        inst.reboot_vm()
