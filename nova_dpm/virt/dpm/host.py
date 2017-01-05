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

from nova import context as context_object
from nova.objects import fields as obj_fields
from nova.objects import instance as instance_object
from oslo_log import log as logging
from oslo_serialization import jsonutils
from oslo_utils import importutils


LOG = logging.getLogger(__name__)
PRSM_HYPERVISOR = 'PRSM'
S390_ARCH = 's390x'
IBM = 'IBM'
HOST = 'host'
CPC_SOCKETS = 0  # TODO(preethipy): Update with relevant value
CPC_THREADS = 1  # TODO(preethipy): Update with relevant value
HYPERVISOR_VERSION = 1000  # TODO(preethipy): Update with
# relevant value

zhmcclient = None


class Host(object):

    def __init__(self, conf, cpc, client):

        LOG.debug('Host initializing for cpcsubset %(cpcsubset_name)s'
                  % {'cpcsubset_name': conf['cpcsubset_name']})

        self._get_zhmclient()
        self._conf = conf
        self._client = client
        self._cpc = cpc
        self._instances = []  # TODO(preethipy): Instance details
        # to be populated
        self._properties = None

        LOG.debug('Host initializing done')

    @property
    def properties(self):
        LOG.debug('properties')
        self._properties = self._get_host_poperties()
        return self._properties

    def _get_host_poperties(self):
        LOG.debug('_get_host_properties')
        dict_mo = {
            "memory_mb": self._conf["max_memory_mb"],
            "vcpus": self._conf["max_processors"],
            'vcpus_used': self._get_proc_used(),
            "local_gb": 1024,  # TODO(preethipy): Update with relevant value
            "memory_mb_used": self._get_mem_used(),
            "local_gb_used": 0,  # TODO(preethipy): Update with relevant value
            "cpu_info": self._get_cpu_info(self._conf["max_processors"]),
            "hypervisor_type": PRSM_HYPERVISOR,
            "hypervisor_version": HYPERVISOR_VERSION,
            "numa_topology": None,
            "hypervisor_hostname": self._conf['cpcsubset_name'],
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
        instance_list = self._get_instances_list()
        partition_list = self._partition_list()
        processor_used = 0
        for instance in instance_list:
            for partition in partition_list:
                if (instance.hostname ==
                        partition.properties['name']):
                    if (processor_used <
                            partition.get_property('cp-processors')):
                        processor_used = partition.get_property(
                            'cp-processors')
        return processor_used

    def _get_mem_used(self):
        instance_list = self._get_instances_list()
        partition_list = self._partition_list()
        memory_used = 0
        for instance in instance_list:
            for partition in partition_list:
                if (instance.hostname ==
                        partition.properties['name']):
                    memory_used += partition.get_property(
                        'initial-memory')
                    break

        return memory_used

    def _get_instances_list(self):
        context = context_object.get_admin_context(read_deleted='no')
        instance_list = instance_object.InstanceList.get_all(context)
        return instance_list

    def _partition_list(self):
        partition_manager = zhmcclient.PartitionManager(self._cpc)
        partition_lists = partition_manager.list(full_properties=False)
        return partition_lists

    def _get_zhmclient(self):
        LOG.debug("_get_zhmclient")
        global zhmcclient
        if zhmcclient is None:
            zhmcclient = importutils.import_module('zhmcclient')
