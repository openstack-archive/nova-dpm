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
Partition will map nova parameter to PRSM parameter
"""
import re
import sys

from nova.compute import manager as compute_manager
from nova.compute import power_state
from nova.compute import task_states
from nova.compute import vm_states
from nova import exception
from nova.i18n import _
from nova_dpm import conf
from nova_dpm.virt.dpm import constants
from nova_dpm.virt.dpm import exceptions
from nova_dpm.virt.dpm import utils
from oslo_log import log as logging
from zhmcclient._exceptions import NotFound
from zhmcclient import HTTPError

CONF = conf.CONF
OPENSTACK_PREFIX = 'OpenStack'
CPCSUBSET_PREFIX = 'CPCSubset='
STATUS_TIMEOUT = 60

STARTED_STATUSES = (
    utils.PartitionState.RUNNING,
    utils.PartitionState.DEGRADED,
    utils.PartitionState.RESERVATION_ERROR)
STOPPED_STATUSES = (
    utils.PartitionState.STOPPED,
    utils.PartitionState.TERMINATED,
    utils.PartitionState.PAUSED)


DPM_TO_NOVA_STATE = {
    utils.PartitionState.RUNNING: power_state.RUNNING,
    utils.PartitionState.STOPPED: power_state.SHUTDOWN,
    utils.PartitionState.UNKNOWN: power_state.NOSTATE,
    # operation to get out of the "paused" status is "stop"
    utils.PartitionState.PAUSED: power_state.SHUTDOWN,
    utils.PartitionState.STARTING: power_state.PAUSED
}

CPCSUBSET_NAME = 'cpcsubset_name'
LOG = logging.getLogger(__name__)


def _translate_vm_state(dpm_state):

    if dpm_state is None:
        return power_state.NOSTATE

    try:
        nova_state = DPM_TO_NOVA_STATE[dpm_state.lower()]
    except KeyError:
        nova_state = power_state.NOSTATE

    return nova_state


def is_valid_partition_name(name):
    """Validate the partition name

    This function will validate the name of partition
    which is managed by openstack

    The valid format is
    'OpenStack-hostname-6511ee0f-0d64-4392-b9e0-cdbea10a17c3'
    where hostname is CONF.host

    :param name: name of partition
    :return: bool
    """
    partition_name_regx = (
        re.compile(r"^" + OPENSTACK_PREFIX +
                   "-" +
                   CONF.host +
                   "-[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$"))
    if partition_name_regx.match(name):
        return True
    return False


def cpcsubset_partition_list(cpc):
    """cpc subset partition list

    Return the list of partitions which is
     managed by one compute service (cpc subset)

    :param cpc: cpc
    :return: list of partitions managed by compute service
    """
    cpc_partition_list = cpc.partitions.list()
    openstack_partition_list = []

    for partition in cpc_partition_list:
        if is_valid_partition_name(
                partition.get_property('name')):
            openstack_partition_list.append(partition)

    return openstack_partition_list


class PartitionInstance(object):
    def __init__(self, instance, cpc):
        self.instance = instance
        self.cpc = cpc
        self.partition = self.get_partition()

    @staticmethod
    def create_object(instance, cpc, flavor=None):
        """Generator method. Simplifies things in unittests"""
        return PartitionInstance(instance, cpc)

    @property
    def partition_name(self):
        """This function will create partition name using the instance uuid

        :return: name of partition
        """
        return OPENSTACK_PREFIX + "-" + CONF.host + "-" + self.instance.uuid

    @property
    def partition_description(self):
        """This function will create partition description

        :return: description to be used for partition creation
        """
        return OPENSTACK_PREFIX + " " + CPCSUBSET_PREFIX + CONF.host

    def properties(self):
        properties = {}
        properties['name'] = self.partition_name
        properties['description'] = self.partition_description
        if self.instance.flavor is not None:
            properties['ifl-processors'] = self.instance.flavor.vcpus
            properties['initial-memory'] = self.instance.flavor.memory_mb
            properties['maximum-memory'] = self.instance.flavor.memory_mb
        return properties

    def create(self, properties):
        partition_manager = self.cpc.partitions
        self.partition = partition_manager.create(properties)

    def set_boot_os_specific_parameters(self, data):
        """Set the boot-os-specific-parameters property

        The value of this property will be appended to the kernels cmdline
        argument.
        """
        if len(data) > constants.BOOT_OS_SPECIFIC_PARAMETERS_MAX_LEN:
            raise exceptions.BootOsSpecificParametersPropertyExceededError()
        self.partition.update_properties({
            'boot-os-specific-parameters': data
        })

    def attach_nic(self, vif):
        # TODO(preethipy): Implement the listener flow to register for
        # nic creation events
        LOG.debug("Creating nic interface for the instance")

        port_id = vif['id']
        vif_type = vif['type']
        mac = vif['address']
        vif_details = vif['details']
        dpm_object_id = vif_details['object_id']

        # Only dpm_vswitch attachments are supported for now
        if vif_type != "dpm_vswitch":
            raise Exception

        dpm_nic_dict = {
            "name": "OpenStack_Port_" + str(port_id),
            "description": "OpenStack mac=" + mac +
                           ", CPCSubset=" +
                           CONF.host,
            "virtual-switch-uri": "/api/virtual-switches/"
                                  + dpm_object_id
        }
        LOG.debug("Creating NIC %s", dpm_nic_dict)
        nic_interface = self.partition.nics.create(dpm_nic_dict)
        LOG.debug("NIC created successfully %s with URI %s",
                  nic_interface.properties['name'],
                  nic_interface.properties['virtual-switch-uri'])
        return nic_interface

    def attach_hbas(self):
        LOG.debug('Creating vhbas for instance',
                  instance=self.instance)
        mapping = self.get_adapter_port_mappings()
        for adapterPort in mapping.get_adapter_port_mapping():
            adapter_object_id = adapterPort['adapter_id']
            adapter_port = adapterPort['port']
            dpm_hba_dict = {
                "name": "OpenStack_Port_" + adapter_object_id +
                        "_" + str(adapter_port),
                "description": "OpenStack CPCSubset= " +
                               CONF.host,
                "adapter-port-uri": "/api/adapters/"
                                    + adapter_object_id +
                                    "/storage-ports/" +
                                    str(adapter_port)
            }
            hba = self.partition.hbas.create(dpm_hba_dict)
            LOG.debug("HBA created successfully %s "
                      "with URI %s and adapter port URI %s",
                      hba.properties['name'], hba.properties['element-uri'],
                      hba.properties['adapter-port-uri'])

    def get_adapter_port_mappings(self):
        LOG.debug('Creating Adapter uris')
        mapping = PhysicalAdapterModel(self.cpc)
        for entry in CONF.dpm.physical_storage_adapter_mappings:
            adapter_uuid, port = entry
            adapter = mapping._get_adapter(adapter_uuid)
            mapping._validate_adapter_type(adapter)
            mapping._add_adapter_port(adapter_uuid, port)
        return mapping

    def _build_resources(self, context, instance, block_device_mapping):
        LOG.debug('Start building block device mappings for instance %s',
                  self.instance)
        resources = {}
        instance.vm_state = vm_states.BUILDING
        instance.task_state = task_states.BLOCK_DEVICE_MAPPING
        instance.save()

        block_device_info = compute_manager.ComputeManager().\
            _prep_block_device(context, instance,
                               block_device_mapping)
        resources['block_device_info'] = block_device_info
        return resources

    def get_hba_uris(self):
        LOG.debug('Get Hba properties')
        return self.partition.get_property('hba-uris')

    def get_boot_hba_uri(self):
        hbas = self.get_hba_uris()
        # Using the first adapter in the config option for boot
        adapter_uuid, port = CONF.dpm.physical_storage_adapter_mappings[0]
        hba_uri = None

        for hba in hbas:
            if hba.find(adapter_uuid):
                hba_uri = str(hba)
                break

        if not hba_uri:
            raise Exception('No HBA found')
        return hba_uri

    def get_partition_wwpns(self):
        LOG.debug('Get Partition wwpns')
        partition_wwpns = []
        if self.partition is not None:
            hba_manager = self.partition.hbas
            hbas = hba_manager.list(full_properties=False)
            for hba in hbas:
                wwpn = hba.get_property('wwpn')
                partition_wwpns.append(wwpn.replace('0x', ''))
        return partition_wwpns

    def set_boot_properties(self, wwpn, lun, booturi):
        LOG.debug('set_boot_properties')
        bootProperties = {'boot-device': 'storage-adapter',
                          'boot-storage-device': booturi,
                          'boot-world-wide-port-name': wwpn,
                          'boot-logical-unit-number': lun}
        self.partition.update_properties(properties=bootProperties)

    def launch(self, partition=None):
        LOG.debug('Partition launch triggered')
        self.instance.vm_state = vm_states.BUILDING
        self.instance.task_state = task_states.SPAWNING
        self.instance.save()

        self.partition.start(True)
        # TODO(preethipy): The below method to be removed once the bug
        # on DPM is fixed to return correct status on API return
        self.partition.wait_for_status(
            status=utils.PartitionState.RUNNING,
            status_timeout=STATUS_TIMEOUT)

    def destroy(self):
        LOG.debug('Partition Destroy triggered')
        if self.partition:
            try:
                self.partition.stop(True)
            except HTTPError as http_error:
                # (http_status == 409 and reason == 1) means
                # Partition status is not valid to perform the operation.
                # e.g - If partition is already stop then stop operation
                # is not a valid operation on partition.
                if http_error.http_status == 409 and http_error.reason == 1:
                    pass
                else:
                    raise http_error
            try:
                self.partition.wait_for_status(
                    status=utils.PartitionState.STOPPED,
                    status_timeout=STATUS_TIMEOUT)
                self.instance.vm_state = vm_states.STOPPED
                self.instance.save()
                self.partition.delete()
            except exception.InstanceInvalidState as invalid_state:
                errormsg = (_("Partition - %(partition)s status "
                              "%(status)s is invalid") %
                            {'partition': self.partition.properties['name'],
                             'status': self.partition.properties['status']})
                raise invalid_state(errormsg)
        else:
            errormsg = (_("Partition corresponding to the instance "
                          "%(instance)s and instance uuid %(uuid)s "
                          "does not exist") %
                        {'instance': self.instance.hostname,
                         'uuid': self.instance.uuid})
            raise exception.InstanceNotFound(errormsg)

    def power_on_vm(self):
        LOG.debug('Partition power on triggered')

        self._ensure_status_transitioned()

        if self.partition.get_property(
                'status') == utils.PartitionState.PAUSED:
            self.partition.stop(True)
            self.partition.wait_for_status(
                status=utils.PartitionState.STOPPED, status_timeout=60)

        if self.partition.get_property('status') not in STARTED_STATUSES:
            self.partition.start(True)
            self.partition.wait_for_status(
                status=STARTED_STATUSES, status_timeout=60)

    def _ensure_status_transitioned(self):
        partition_state = self.partition.get_property('status')

        if partition_state == utils.PartitionState.STARTING:
            self.partition.wait_for_status(
                status=STARTED_STATUSES, status_timeout=60)
        elif partition_state == utils.PartitionState.SHUTTING_DOWN:
            self.partition.wait_for_status(
                status=STOPPED_STATUSES, status_timeout=60)

    def power_off_vm(self):
        LOG.debug('Partition power off triggered')
        self.partition.stop(True)
        # TODO(preethipy): The below method to be removed once the bug
        # on DPM(701894) is fixed to return correct status on API return
        self.partition.wait_for_status(
            status=utils.PartitionState.STOPPED,
            status_timeout=STATUS_TIMEOUT)

    def reboot_vm(self):
        LOG.debug('Partition reboot triggered')
        self.partition.stop(True)
        # TODO(preethipy): The below method to be removed once the bug
        # on DPM(701894) is fixed to return correct status on API return
        self.partition.wait_for_status(
            status=utils.PartitionState.STOPPED,
            status_timeout=STATUS_TIMEOUT)

        self.partition.start(True)
        # TODO(preethipy): The below method to be removed once the bug
        # on DPM(701894) is fixed to return correct status on API return
        self.partition.wait_for_status(
            status=utils.PartitionState.RUNNING,
            status_timeout=STATUS_TIMEOUT)

    def get_partition(self):
        """Get the zhmcclient partition object for this PartitionInstance

        returns: zhmcclient partition object or None if not found
        """
        try:
            return self.cpc.partitions.find(name=self.partition_name)
        except NotFound:
            return None


class PartitionInstanceInfo(object):
    """Instance Information

    This object loads VM information like state, memory used etc

    """

    def __init__(self, instance, cpc):
        self.instance = instance
        self.cpc = cpc
        self.partition = None
        partition_manager = self.cpc.partitions
        partition_lists = partition_manager.list(full_properties=False)
        inst = PartitionInstance(self.instance, self.cpc)
        for partition in partition_lists:
            if partition.properties['name'] == inst.partition_name:
                self.partition = partition
                self.partition.pull_full_properties()

    @property
    def state(self):

        status = None
        if self.partition is not None:
            status = self.partition.get_property('status')

        return _translate_vm_state(status)

    @property
    def mem(self):

        mem = None
        if self.partition is not None:
            mem = self.partition.get_property('initial-memory')

        return mem

    @property
    def max_mem(self):

        max_mem = None
        if self.partition is not None:
            max_mem = self.partition.get_property('maximum-memory')

        return max_mem

    @property
    def num_cpu(self):

        num_cpu = None
        if self.partition is not None:
            num_cpu = self.partition.get_property('ifl-processors')

        return num_cpu

    @property
    def cpu_time(self):

        # TODO(pranjank): will implement
        # As of now returning dummy value
        return 100


class PhysicalAdapterModel(object):
    """Model for physical storage adapter

    Validates and retrieval capabilities for
    adapter id and port
    """
    def __init__(self, cpc):
        self._cpc = cpc
        self._adapter_ports = []

    def _get_adapter(self, adapter_id):
        try:
            # TODO(andreas_s): Optimize in zhmcclient - For 'find' the
            # whole list of items is retrieved
            return self._cpc.adapters.find(**{'object-id': adapter_id})
        except NotFound:
            LOG.error("Configured adapter %s could not be "
                      "found. Please update the agent "
                      "configuration. Agent terminated!",
                      adapter_id)
            sys.exit(1)

    @staticmethod
    def _validate_adapter_type(adapter):
        adapt_type = adapter.get_property('type')
        if adapt_type not in ['fcp']:
            LOG.error("Configured adapter %s is not an fcp ",
                      adapter)
            sys.exit(1)

    def _add_adapter_port(self, adapter_id, port):
        self._adapter_ports.append({"adapter_id": adapter_id,
                                    "port": port})

    def get_adapter_port_mapping(self):
        """Get a list of adapter port uri

        :return: list of adapter_port dict
        """
        return self._adapter_ports
