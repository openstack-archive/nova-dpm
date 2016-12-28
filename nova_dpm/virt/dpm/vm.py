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
import sys

from nova.compute import manager as compute_manager
from nova.compute import power_state
from nova.compute import task_states
from nova.compute import vm_states
from nova.i18n import _LE
from nova_dpm.virt.dpm import utils
from oslo_log import log as logging

import zhmcclient


DPM_TO_NOVA_STATE = {
    utils.PartitionState.RUNNING: power_state.RUNNING,
    utils.PartitionState.STOPPED: power_state.SHUTDOWN,
    utils.PartitionState.UNKNOWN: power_state.NOSTATE,
    utils.PartitionState.PAUSED: power_state.PAUSED,
    utils.PartitionState.STARTING: power_state.NOSTATE
}

OBJECT_ID = 'object-id'
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


class Instance(object):
    def __init__(self, instance, cpc, flavor=None):
        self.instance = instance
        self.flavor = flavor
        self.cpc = cpc
        self.partition = None

    def properties(self):
        properties = {}
        properties['name'] = self.instance.hostname
        if not self.flavor:
            properties['cp-processors'] = self.flavor.vcpus
            properties['initial-memory'] = self.flavor.memory_mb
            properties['maximum-memory'] = self.flavor.memory_mb
        return properties

    def create(self, properties):
        partition_manager = zhmcclient.PartitionManager(self.cpc)
        self.partition = partition_manager.create(properties)

    def attach_nic(self, conf, network_info):
        # TODO(preethipy): This function can be moved to Partition.py
        # TODO(preethipy): Implement the listener flow to register for
        # nic creation events
        LOG.debug("Creating nic interface for the instance")

        for vif in network_info:

            port_id = vif['id']
            vif_type = vif['type']
            mac = vif['address']
            vif_details = vif['details']
            dpm_object_id = vif_details[OBJECT_ID]

            # Only dpm_vswitch attachments are supported for now
            if vif_type != "dpm_vswitch":
                raise Exception

            dpm_nic_dict = {
                "name": "OpenStack_Port_" + port_id,
                "description": "OpenStack mac= " + mac +
                               ", CPCSubset= " +
                               conf[CPCSUBSET_NAME],
                "virtual-switch-uri": "/api/virtual-switches/"
                                      + dpm_object_id
            }
            nic_interface = self.partition.nics.create(dpm_nic_dict)
            LOG.debug("NIC created successfully %(nic_name) "
                      "with URI %(nic_uri)"
                      % {'nic_name': nic_interface.properties['name'],
                         'nic_uri': nic_interface.properties[
                             'virtual-switch-uri']})

    def attachHba(self, conf):
        LOG.debug('Creating vhbas for instance',
                  instance=self.instance)
        mapping = self.createStorageAdapterUris(conf)
        for adapterPort in mapping.get_adapter_port_mapping():
            adapter_object_id = adapterPort['dpm_object_id']
            adapter_port = adapterPort['port']
            dpm_hba_dict = {
                "name": "OpenStack_Port_" + adapter_object_id +
                        "_" + adapter_port,
                "description": "OpenStack CPCSubset= " +
                               conf[CPCSUBSET_NAME],
                "adapter-port-uri": "/api/adapters/"
                                    + adapter_object_id +
                                    "/storage-ports/" +
                                    adapter_port
            }
            hba = self.partition.hbas.create(dpm_hba_dict)
            LOG.debug("HBA created successfully %(hba_name) "
                      "with URI %(hba_uri) and adapterporturi"
                      "%(adapter-port-uri)"
                      % {'hba_name': hba.properties['name'],
                         'hba_uri': hba.properties[
                             'element-uri'],
                         'adapter-port-uri': hba.properties[
                             'adapter-port-uri']})

    def createStorageAdapterUris(self, conf):
        LOG.debug('Creating Adapter uris')
        interface_mappings = conf['physical_storage_adapter_mappings']
        mapping = PhysicalAdapterModel(self.cpc)
        for entry in interface_mappings:
            adapter_uuid, port = \
                PhysicalAdapterModel._parse_config_line(entry)
            adapter = mapping._get_adapter(adapter_uuid)
            mapping._validate_adapter_type(adapter)
            mapping._add_adapter_port(adapter_uuid, port)
        return mapping

    def _build_resources(self, context, instance, block_device_mapping):
        LOG.debug('Start building block device mappings for instance.',
                  instance=self.instance)
        resources = {}
        instance.vm_state = vm_states.BUILDING
        instance.task_state = task_states.BLOCK_DEVICE_MAPPING
        instance.save()

        block_device_info = compute_manager.ComputeManager().\
            _prep_block_device(context, instance,
                               block_device_mapping)
        resources['block_device_info'] = block_device_info
        return resources

    def get_hba_properties():
        LOG.debug('Get Hba properties')

    def launch(self):
        self.create()


class InstanceInfo(object):
    """Instance Information

    This object loads VM information like state, memory used etc

    """

    @property
    def state(self):

        # TODO(pranjank): will implement
        # As of now returning dummy value
        return power_state.RUNNING

    @property
    def mem(self):

        # TODO(pranjank): will implement
        # As of now returning dummy value
        return 1024

    @property
    def max_mem(self):

        # TODO(pranjan): will implement
        # As of now returning dummy value
        return 2048

    @property
    def num_cpu(self):

        # TODO(pranjank): will implement
        # As of now returning dummy value
        return 3

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
        except zhmcclient.NotFound:
            LOG.error(_LE("Configured adapter %s could not be "
                          "found. Please update the agent "
                          "configuration. Agent terminated!"),
                      adapter_id)
            sys.exit(1)

    @staticmethod
    def _validate_adapter_type(adapter):
        adapt_type = adapter.get_property('type')
        if adapt_type not in ['fcp']:
            LOG.error(_LE("Configured adapter %s is not an fcp "),
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

    @staticmethod
    def _parse_config_line(line):
        result = line.split(":")
        adapter_id = result[0]
        # If no port-element-id was defined, default to 0
        # result[1] can also be '' - handled by 'and result[1]'
        port = int(result[1] if len(result) == 2 and result[1] else 0)
        return adapter_id, port
