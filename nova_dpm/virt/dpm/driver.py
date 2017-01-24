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
from nova.i18n import _
from nova.objects import flavor as flavor_object
from nova.virt import driver
from nova_dpm.virt.dpm import client_proxy
from nova_dpm.virt.dpm import constants
from nova_dpm.virt.dpm import exceptions
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
        inst = vm.PartitionInstance(instance, self._cpc)
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

        partition_list = vm.cpcsubset_partition_list(self._cpc)
        part_list = []
        for partition in partition_list:
            part_list.append(partition.get_property('name'))

        return part_list

    def get_info(self, instance):

        info = vm.PartitionInstanceInfo(instance, self._cpc)

        return info

    def _get_nic_string(self, nic, vif):
        """Generate the NIC string that must be available from inside the OS

        Passing the string into the operating system is achieved via appending
        it to the partitions boot-os-specific-parameters property.
        The value of this property will then be appended to the kernels cmdline
        and be accessible from within the instance under /proc/cmdline.
        It is ignored by the Linux Boot process but can be parsed by
        other userspace tools and scripts.

        This allows the following operations to be done from within the
        Instance/Partitions Operating System:

        * Replace the z Systems Firmware generated MAC address
          of the NIC with the one generated from Neutron. The MAC can be
          removed from this parameter once it is possible to set the correct
          MAC right on DPM NIC creation.

        * Configure the physical network adapter port to be used.
          The port number can be removed once Linux is able to get this
          information via a different channel.
        """
        # Format: <dev-no>,<port-no>,<mac>;
        # <devno>: The DPM device number
        # <port-no>: The network adapters port that should be usd
        # <mac>: MAC address without deliminator. This saves 5 additional
        #        characters in the limited boot-os-specific-parameters property
        # Example: 0001,1,aabbccddeeff;
        # TODO(andreas_s): Update <port-no> once provided by Neutron. Till
        # then default to 0
        nic_boot_parms = "{devno},0,{mac};".format(**{
            "devno": nic.get_property("device-number"),
            "mac": vif["address"].replace(":", "")
        })
        return nic_boot_parms

    def spawn(self, context, instance, image_meta, injected_files,
              admin_password, network_info=None, block_device_info=None,
              flavor=None):

        if not flavor:
            context = context_object.get_admin_context(read_deleted='yes')
            flavor = (
                flavor_object.Flavor.get_by_id(context,
                                               instance.instance_type_id))
        LOG.debug("Flavor = %(flavor)s" % {'flavor': flavor})

        inst = vm.PartitionInstance(instance, self._cpc, flavor)
        props = inst.properties()
        inst.create(props)

        # The creation of NICs is limited in DPM by the partitions
        # boot-os-specific-parameters property. It is used to pass additional
        # network configuration data into the partitions Operating System
        if len(network_info) > constants.MAX_NICS_PER_PARTITION:
            # TODO(andreas_s): How to handle cleanup?
            # TODO(andreas_s): Not sure about the naming. Should we use
            # "NIC" or "Port"?
            raise exceptions.MaxAmountOfInstancePortsExceededError(_(
                "Exceeded the maximum number of Ports per partition. A single "
                "partition can only be attached to {max_ports} Ports, but "
                "{current_ports} Ports have been requested.").format(
                max_ports=constants.MAX_NICS_PER_PARTITION,
                current_ports=len(network_info)
            ))
        nic_boot_string = ""
        for vif in network_info:
            nic = inst.attach_nic(self._conf, vif)
            nic_boot_string += self._get_nic_string(nic, vif)
        inst.append_to_boot_os_specific_parameters(nic_boot_string)

        block_device_mapping = driver.block_device_info_get_mapping(
            block_device_info)
        inst.attachHba(self._conf)
        inst._build_resources(context, instance, block_device_mapping)

        inst.launch()

    def destroy(self, context, instance, network_info, block_device_info=None,
                destroy_disks=True, migrate_data=None):
        inst = vm.PartitionInstance(instance, self._cpc)
        inst.destroy()

    def power_off(self, instance, timeout=0, retry_interval=0):
        inst = vm.PartitionInstance(instance, self._cpc)
        inst.power_off_vm()

    def power_on(self, context, instance, network_info,
                 block_device_info=None):
        inst = vm.PartitionInstance(instance, self._cpc)
        inst.power_on_vm()

    def reboot(self, context, instance, network_info, reboot_type,
               block_device_info=None, bad_volumes_callback=None):
        inst = vm.PartitionInstance(instance, self._cpc)
        inst.reboot_vm()
