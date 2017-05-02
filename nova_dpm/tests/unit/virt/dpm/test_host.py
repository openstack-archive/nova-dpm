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
import zhmcclient

from nova.test import TestCase
from nova_dpm.tests.unit.virt.dpm import test_data as utils
from nova_dpm.virt.dpm import host


class HostTestCase(TestCase):

    def setUp(self):
        super(HostTestCase, self).setUp()
        self.session = utils.create_session_1()
        client = zhmcclient.Client(self.session)
        self.cpc = client.cpcs.find(**{"name": "cpc_2"})
        self.flags(host=utils.HOST)
        self.flags(group="dpm", max_processors=3)
        self.flags(group="dpm", max_memory=2048)
        self.host = host.Host(self.cpc)

    def test_host_properties(self):

        host_properties = self.host.properties
        self.assertEqual(utils.HOST,
                         host_properties['hypervisor_hostname'])
        self.assertEqual('cpc_2', host_properties['cpc_name'])
        self.assertEqual(3, host_properties['vcpus'])
        self.assertEqual(2048, host_properties['memory_mb'])
        self.assertEqual(utils.MAX_PROC_USED, host_properties['vcpus_used'])
        self.assertEqual(utils.TOTAL_MEM_USED,
                         host_properties['memory_mb_used'])
        self.assertEqual(2013001, host_properties['hypervisor_version'])
        self.assertEqual('PRSM', host_properties['hypervisor_type'])
        cpu_info = host_properties['cpu_info']
        cpu_info_dict = json.loads(cpu_info)
        self.assertEqual('s390x', cpu_info_dict['arch'])
        self.assertEqual('IBM', cpu_info_dict['vendor'])

    def test_get_proc_used(self):
        proc_used = self.host._get_proc_used()
        self.assertEqual(utils.MAX_PROC_USED, proc_used)

    def test_mem_used(self):
        memory_used = self.host._get_mem_used()
        self.assertEqual(utils.TOTAL_MEM_USED, memory_used)

    def test_get_version_in_int(self):
        version = self.host._get_version_in_int()
        self.assertEqual(2013001, version)
