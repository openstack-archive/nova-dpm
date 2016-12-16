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

from nova.compute import power_state
from nova_dpm.virt.dpm import utils
import zhmcclient


DPM_TO_NOVA_STATE = {
    utils.PartitionState.RUNNING: power_state.RUNNING,
    utils.PartitionState.STOPPED: power_state.SHUTDOWN,
    utils.PartitionState.UNKNOWN: power_state.NOSTATE,
    utils.PartitionState.PAUSED: power_state.PAUSED,
    utils.PartitionState.STARTING: power_state.NOSTATE
}


def _translate_vm_state(dpm_state):

    if dpm_state is None:
        return power_state.NOSTATE

    try:
        nova_state = DPM_TO_NOVA_STATE[dpm_state.lower()]
    except KeyError:
        nova_state = power_state.NOSTATE

    return nova_state


class Instance(object):
    def __init__(self, instance, flavor, cpc):
        self.instance = instance
        self.flavor = flavor
        self.cpc = cpc
        self.partition = None

    def properties(self):
        properties = {}
        properties['name'] = self.instance.hostname
        properties['cp-processors'] = self.flavor.vcpus
        properties['initial-memory'] = self.flavor.memory_mb
        properties['maximum-memory'] = self.flavor.memory_mb

        return properties

    def create(self):
        partition_manager = zhmcclient.PartitionManager(self.cpc)
        self.partition = partition_manager.create(self.properties())

    def launch(self):
        self.create()


class InstanceInfo(object):
    """Instance Information

    This object loads VM information like state, memory used etc

    """

    def __init__(self, instance, cpc):
        self.instance = instance
        self.cpc = cpc
        self.partition = None
        partition_manager = zhmcclient.PartitionManager(self.cpc)
        partition_lists = partition_manager.list(full_properties=False)
        for partition in partition_lists:
            if partition.properties['name'] == self.instance.hostname:
                self.partition = partition

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
            num_cpu = self.partition.get_property('cp-processors')

        return num_cpu

    @property
    def cpu_time(self):

        # TODO(pranjank): will implement
        # As of now returning dummy value
        return 100
