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
Host will have the handle to the CPCSubsetMgr which will retrieve cpcsubsets
"""

import nova_dpm.conf

from nova.objects import fields as obj_fields
from nova_dpm.virt.dpm import vm
from oslo_log import log as logging
from oslo_serialization import jsonutils


LOG = logging.getLogger(__name__)
CONF = nova_dpm.conf.CONF
PRSM_HYPERVISOR = 'PRSM'
S390_ARCH = 's390x'
IBM = 'IBM'
HOST = 'host'
CPC_SOCKETS = 0  # TODO(preethipy): Update with relevant value
CPC_THREADS = 1  # TODO(preethipy): Update with relevant value
# relevant value


class Host(object):

    def __init__(self, cpc):

        LOG.debug('Host initializing for cpcsubset %s', CONF.host)

        self._cpc = cpc
        self._instances = []  # TODO(preethipy): Instance details

        LOG.debug('Host initializing done')

    @property
    def properties(self):
        dict_mo = {
            "memory_mb": CONF.dpm.max_memory,
            "vcpus": CONF.dpm.max_processors,
            'vcpus_used': self._get_proc_used(),
            "local_gb": 1024,  # TODO(preethipy): Update with relevant value
            "memory_mb_used": self._get_mem_used(),
            "local_gb_used": 0,  # TODO(preethipy): Update with relevant value
            "cpu_info": self._get_cpu_info(CONF.dpm.max_processors),
            "hypervisor_type": PRSM_HYPERVISOR,
            "hypervisor_version": self._get_version_in_int(),  # required int
            "numa_topology": None,
            "hypervisor_hostname": CONF.host,
            "cpc_name": self._cpc.properties['name'],
            "disk_available_least": 1024,  # TODO(preethipy): Update with
            # relevant value
            'supported_instances':
            [(S390_ARCH, obj_fields.HVType.BAREMETAL, obj_fields.VMMode.HVM)]}
        # TODO(preethipy): BareMETAL will be updated with PRSM after HVType
        # updated in upstream code

        LOG.debug(dict_mo)

        return dict_mo

    def _get_cpu_info(self, cores):
        """Get cpuinfo information.

        Obtains cpu feature from virConnect.getCapabilities,
        and returns as a json string.

        :return: see above description

        """
        cpu_info = dict()
        cpu_info['arch'] = S390_ARCH
        cpu_info['model'] = HOST
        cpu_info['vendor'] = IBM
        topology = dict()
        topology['sockets'] = CPC_SOCKETS
        topology['cores'] = cores
        topology['threads'] = CPC_THREADS
        cpu_info['topology'] = topology

        features = list()  # TODO(preethipy): Update with featureset required
        cpu_info['features'] = features
        return jsonutils.dumps(cpu_info)

    def _get_proc_used(self):
        part_list = vm.cpcsubset_partition_list(self._cpc)
        processor_used = 0
        for partition in part_list:
            processor_used = max(
                processor_used,
                partition.get_property('ifl-processors'))

        return processor_used

    def _get_mem_used(self):
        part_list = vm.cpcsubset_partition_list(self._cpc)
        memory_used = 0
        for partition in part_list:
            memory_used += partition.get_property('initial-memory')

        return memory_used

    def _get_version_in_int(self):
        version = self._cpc.get_property('se-version')
        # version is in this format e.g - '2.13.1'
        # But hypervisor_version should be in integer format
        # So we will convert 2.13.1 into 2013001.
        # <major-version>.<3-digits-minor-version>.<3-digits fix-version>
        val = version.split('.')
        major_version = int(val[0])
        minor_version = int(val[1])
        fixed_version = int(val[2])
        full_version = (major_version * 1000 * 1000
                        + minor_version * 1000
                        + fixed_version)
        return full_version
