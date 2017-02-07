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
        self._conf = {'cpcsubset_name': CONF.host,
                      'cpc_object_id': CONF.dpm.cpc_object_id,
                      'max_processors': CONF.dpm.max_processors,
                      'max_memory_mb': CONF.dpm.max_memory,
                      'max_partitions': CONF.dpm.max_instances,
                      'physical_storage_adapter_mappings':
                          CONF.dpm.physical_storage_adapter_mappings}

        self._cpc = self._client.cpcs.find(**{
            "object-id": self._conf['cpc_object_id']})
        LOG.debug("Matching hypervisor found %(cpcsubset_name)s for object-id "
                  "%(cpcid)s and CPC %(cpcname)s" %
                  {'cpcsubset_name': self._conf['cpcsubset_name'],
                   'cpcid': self._conf['cpc_object_id'],
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
        inst = vm.PartitionInstance(instance, self._cpc)
        props = {}
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
        self.prep_for_spawn(context=None, instance=instance)

    def prep_for_spawn(self, context, instance,
                       flavor=None):

        if not flavor:
            context = context_object.get_admin_context(read_deleted='yes')
            flavor = (
                flavor_object.Flavor.get_by_id(context,
                                               instance.instance_type_id))
        LOG.debug("Flavor = %(flavor)s" % {'flavor': flavor})

        inst = vm.PartitionInstance(instance, self._cpc, flavor)
        inst.create(inst.properties())

        inst.attach_hbas(self._conf)

    def spawn(self, context, instance, image_meta, injected_files,
              admin_password, network_info=None, block_device_info=None,
              flavor=None):

        inst = vm.PartitionInstance(instance, self._cpc)

        for vif in network_info:
            inst.attach_nic(self._conf, vif)

        boot_volume_mapping = self._get_boot_volume_bdm(block_device_info)

        self.do_boot(boot_volume_mapping, inst)


    def _get_boot_volume_bdm(self, block_device_info):
        # block_device_mappings is a list of block_device_mappings
        # (one list item per Volume).
        block_device_mappings = driver.block_device_info_get_mapping(
            block_device_info)
        # We pick the first volume as boot volume.
        boot_block_device_mapping = block_device_mappings[0]
        LOG.debug("Using Volume with block device mapping %(bdm)s "
                  "for boot."
                  % {'bdm': str(boot_block_device_mapping)})
        return boot_block_device_mapping

    def do_boot(self, boot_volume_mapping, inst):

        hbas = inst.partition.hbas.list()
        lun = str(boot_volume_mapping['connection_info']
                  ['data']['target_lun'])

        for hba in hbas:
            boot_hba = hba
            boot_hba_uri = boot_hba.get_property("element-uri")
            boot_host_wwpn = boot_hba.get_property("wwpn")
            LOG.debug("Trying HBA %(uri)s with WWPN %(wwpn)s as boot hba." %
                      {"uri": boot_hba_uri, "wwpn": boot_host_wwpn})

            # target_wwpns is a list of (target) WWPNs belonging to the storage
            # subsystem where paths to our hosts boot WWPN exist.
            target_wwpns = boot_volume_mapping['connection_info']['data']
            ['initiator_target_map'].get(boot_host_wwpn, [])

            if not target_wwpns:
                LOG.debug('No target WWPNs found for host WWPN %(wwpn)s '
                          'in block device mapping provided by Cinder.'
                          'Continue with next hba.' %
                          {'wwpn': boot_host_wwpn})
                continue

            # We can use any of the target WWPNs in the list. As multipathing is
            # not supported by the zLinux boot process, we are using
            # the first target WWPN in the list
            for target_wwpn in target_wwpns:
                LOG.debug("Trying target WWPN %(wwpn)s for boot." %
                          {"wwpn": target_wwpn})
                inst.set_boot_properties(target_wwpn, lun, boot_hba_uri)
                inst.launch()
                # TODO(andreas_s): test if boot successful, if so return
                # else continue
            LOG.debug("No target wwpn was working. Trying next hba.")



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
