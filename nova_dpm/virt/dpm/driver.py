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

from nova import exception
from nova.i18n import _
from nova.virt import driver
from nova_dpm.virt.dpm import client_proxy
from nova_dpm.virt.dpm import constants
from nova_dpm.virt.dpm import exceptions
from nova_dpm.virt.dpm import host as Host
from nova_dpm.virt.dpm import utils
from nova_dpm.virt.dpm import vm
from oslo_log import log as logging
from oslo_utils import importutils
import sys
import zhmcclient


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

        self._client = client_proxy.get_client_for_session(zhmc, userid,
                                                           password)
        LOG.debug("HMC details %s %s", zhmc, userid)

        self.deleted_instance_wwpns_mapping = {}

        self.volume_drivers = self._get_volume_drivers()

    def _get_partition_instance(self, instance, context=None,
                                block_device_mapping=None):
        if instance.image_ref != '':
            raise exceptions.BootFromImageNotSupported()
        else:
            return vm.PartitionInstance(instance, self._cpc, context,
                                        block_device_mapping)

    def init_host(self, host):
        """Driver initialization of the hypervisor node"""
        LOG.debug("init_host")
        try:
            self._cpc = self._client.cpcs.find(**{
                "object-id": CONF.dpm.cpc_object_id})
        except zhmcclient.NotFound:
            LOG.error("Matching hypervisor %s not found for object-id %s "
                      "and username %s on HMC %s",
                      CONF.host, CONF.dpm.cpc_object_id,
                      CONF.dpm.hmc_username, CONF.dpm.hmc)
            sys.exit(1)
        LOG.debug("Matching hypervisor found %s for object-id %s and CPC %s",
                  CONF.host, CONF.dpm.cpc_object_id,
                  self._cpc.properties['name'])

        utils.validate_host_conf(self._cpc)
        self._host = Host.Host(self._cpc)

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

        But we do not support multiple nodes per agent. So it will return
        [hypervisor_hostname]

        And it will also not make sense to use refresh=True/False because
        we have one node per agent.
        """

        LOG.debug("get_available_nodes returns node %s",
                  self._host.properties["hypervisor_hostname"])
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
        """Get connector information for the instance for attaching to volumes.

        Connector information is a dictionary representing the initiator WWPNs
        and a unique identifier of the partition.
            {
                'wwpns': list of wwpns,
                'host': UUID of instance
            }

        Cinder creates a corresponding "host" on the Storage Subsystem,
        representing the Instance and discovers the instances LUNs
        to see which storage paths are active.
        """
        props = {}
        # 'get_volume_connector' will be invoked during creation
        # of the partition and during deletion of the partition.
        # But 'wwpns' we can access only when partition is available.
        # During spawn flow 'get_volume_connector' function will be called
        # before 'spawn' function so to get 'wwpns' we first creating
        # the partition using 'prep_for_spawn' function so that
        # we can access 'wwpns'.(i.e - else part)
        # But during deletion 'get_volume_connector' will be called
        # after 'destroy' function which will delete the partition so
        # after that we can not get the 'wwpns'
        # In order to get 'wwpns' after 'destroy' function we are
        # saving 'wwpns' before deleting partition in 'destroy' function
        # in 'deleted_instance_wwpns_mapping' variable and using these 'wwpns'
        # in 'get_volume_connector'(i.e - if part)
        # after using these 'wwpns' we are removing these 'wwpns' from
        # 'deleted_instance_wwpns_mapping' variable because
        # we are not going to use these 'wwpns' any more after this.
        if instance.uuid in self.deleted_instance_wwpns_mapping:
            props['wwpns'] = self.deleted_instance_wwpns_mapping.pop(
                instance.uuid)
        else:
            inst = self._get_partition_instance(instance)
            props['wwpns'] = inst.get_partition_wwpns()

        props['host'] = instance.uuid

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

    def default_device_names_for_instance(self,
                                          instance,
                                          root_device_name,
                                          *block_device_lists):
        """Prepare for spawn

        This method is implemented as hack to get the "boot from volume"
        use case going. The original intend of this method is
        irrelevant for the nova-dpm driver.

        Nova was initially developed for software hypervisors like
        libvirt/kvm. Therefore it has a different way of dealing
        with LUNs (volumes) and WWPNs. In the libvirt/kvm case,
        a LUN requested by an instance gets attached to the hypervisor
        (compute node). The hypervisor then takes care of virtualizing
        and offering it to the instance itself. In this case,
        the the hypervisors WWPNs are used as initiator.
        Those need to be configured in the Storage Subsystems hostmapping.
        The instances itself do not deal with LUN IDs and WWPNs at all!
        With DPM this is different. There is no hypervisor to
        attach the LUNs to. In fact the instance (partition) has direct
        access to an HBA with it's own host WWPN. Therefore the Instances
        host WWPN (and not the compute node ones) must be used for the
        LUN masking in the Storage Subsystem.

        Typically, an instance is created in the Nova drivers 'spawn' method.
        But before that spawn method is even called, the Nova manager
        asks the driver for the initiator WWPNs to be used. But at this point
        in time it is not yet available, as the partition and the
        corresponding vHBA do not yet exist.

        To work around this, we abuse this method to create the partition and
        the vHBAs before Nova is asking for the initial WWPNs.

        The flow from nova manager.py perspective is like this:

        driver.default_device_names_for_instance (hack to create the
        partition and it's vHBAs)
        driver.get_volume_connector (returns the partitions WWPNs)
        driver.spawn (continues setting up the partition)
        """
        self._prep_for_spawn(instance)

    def _prep_for_spawn(self, instance):

        inst = self._get_partition_instance(instance)
        inst.create(inst.properties())

        inst.attach_hbas()

    @staticmethod
    def _get_block_device_mapping(block_device_info):
        bdm = driver.block_device_info_get_mapping(
            block_device_info)
        LOG.debug("Block device mapping %s", str(bdm))
        return bdm

    def spawn(self, context, instance, image_meta, injected_files,
              admin_password, allocations, network_info=None,
              block_device_info=None):

        bdm = self._get_block_device_mapping(block_device_info)
        inst = self._get_partition_instance(instance, context, bdm)

        # The creation of NICs is limited in DPM by the partitions
        # boot-os-specific-parameters property. It is used to pass additional
        # network configuration data into the partitions Operating System
        if len(network_info) > constants.MAX_NICS_PER_PARTITION:
            # TODO(andreas_s): How to handle cleanup?
            # TODO(andreas_s): Not sure about the naming. Should we use
            # "NIC" or "Port"?
            raise exceptions.MaxAmountOfInstancePortsExceededError(_(
                "Exceeded the maximum number of Ports per Instance. A single "
                "DPM Instance can only be attached to {max_ports} Ports, but "
                "{current_ports} Ports have been requested.").format(
                max_ports=constants.MAX_NICS_PER_PARTITION,
                current_ports=len(network_info)
            ))
        inst.attach_nics(network_info)
        inst.set_boot_properties()
        inst.launch()

    def destroy(self, context, instance, network_info, block_device_info=None,
                destroy_disks=True, migrate_data=None):
        inst = self._get_partition_instance(instance)
        # Need to save wwpns before deletion of the partition
        # Because after driver.destroy function driver.get_volume_connector
        # will be called which required hbas wwpns of partition.
        self.deleted_instance_wwpns_mapping[
            instance.uuid] = inst.get_partition_wwpns()
        inst.destroy()

    def power_off(self, instance, timeout=0, retry_interval=0):
        inst = self._get_partition_instance(instance)
        inst.power_off_vm()

    def power_on(self, context, instance, network_info,
                 block_device_info=None):
        inst = self._get_partition_instance(instance)
        inst.power_on_vm()

    def reboot(self, context, instance, network_info, reboot_type,
               block_device_info=None, bad_volumes_callback=None):
        inst = self._get_partition_instance(instance)
        inst.reboot_vm()
