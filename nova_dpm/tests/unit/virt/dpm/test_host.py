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

import json
import mock

from nova.test import TestCase
from nova_dpm.tests.unit.virt.dpm import fakeutils
from nova_dpm.tests.unit.virt.dpm import fakezhmcclient
from nova_dpm.virt.dpm import host
from nova_dpm.virt.dpm import vm

"""
cpcsubset unit testcase
"""


def fakeHost():

    session = fakezhmcclient.Session("hostip", "dummyhost", "dummyhost")
    client = fakezhmcclient.Client(session)
    cpcmanager = fakezhmcclient.getCpcmgrForClient(client)
    cpc = fakezhmcclient.getFakeCPC(cpcmanager)
    conf = fakezhmcclient.getFakeCPCconf()

    host1 = host.Host(conf, cpc, client)
    return host1


def fakeProperties():
    props = {}
    props = {"memory_mb": 100,
             "vcpus": 10,
             'vcpus_used': 5,
             "local_gb": 1024,
             "memory_mb_used": 1024,
             "local_gb_used": 0,
             "cpu_info": None,
             "hypervisor_type": "PRSM",
             "hypervisor_version": "1",
             "numa_topology": "",
             "hypervisor_hostname": "FakepropsHostname",
             "cpc_name": "FakepropsCpcName",
             "disk_available_least": 1024,
             # relevant value
             'supported_instances':
             [("S390", "DPM", "hvm")]}
    return props


class HostTestCase(TestCase):

    def setUp(self):
        super(HostTestCase, self).setUp()
        self._session = fakezhmcclient.Session(
            "dummy", "dummy", "dummy")
        self._client = fakezhmcclient.Client(self._session)
        self._cpcmanager = fakezhmcclient.getCpcmgrForClient(self._client)
        self._cpc = fakezhmcclient.getFakeCPC(self._cpcmanager)
        self._conf = fakeutils.getFakeCPCconf()
        self.host_obj = host.Host(self._conf, self._cpc, self._client)

    @mock.patch.object(host.LOG, 'debug')
    def test_host(self, mock_warning):
        host.Host(self._conf, self._cpc, self._client)

        expected_arg = "Host initializing done"
        assertlogs = False
        for call in mock_warning.call_args_list:
            if (len(call) > 0):
                if (len(call[0]) > 0 and call[0][0] == expected_arg):
                    assertlogs = True

        self.assertTrue(assertlogs)

    @mock.patch.object(host.LOG, 'debug')
    def test_host_properties(self, mock_warning):

        client = fakezhmcclient.Client(self._session)

        cpcmanager = fakezhmcclient.getCpcmgrForClient(client)
        cpc = fakezhmcclient.getFakeCPC(cpcmanager)
        conf = fakeutils.getFakeCPCconf()

        host1 = host.Host(conf, cpc, client)
        host_properties = host1.properties
        self.assertEqual(host_properties['hypervisor_hostname'],
                         'S12subset')
        self.assertEqual(host_properties['cpc_name'], 'fakecpc')
        cpu_info = host_properties['cpu_info']
        cpu_info_dict = json.loads(cpu_info)
        self.assertEqual(cpu_info_dict['arch'], 's390x')
        self.assertEqual(cpu_info_dict['vendor'], 'IBM')

    @mock.patch.object(
        vm,
        'cpcsubset_partition_list',
        return_value=fakezhmcclient.get_fake_partition_list())
    def test_get_proc_used(self, mock_partitions_list):
        proc_used = self.host_obj._get_proc_used()
        self.assertEqual(proc_used, fakezhmcclient.MAX_CP_PROCESSOR)

    @mock.patch.object(
        vm,
        'cpcsubset_partition_list',
        return_value=fakezhmcclient.get_fake_partition_list())
    def test_mem_used(self, mock_partitions_list):
        memory_used = self.host_obj._get_mem_used()
        self.assertEqual(memory_used, fakezhmcclient.USED_MEMORY)
