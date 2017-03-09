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
import requests.packages.urllib3
import zhmcclient

from nova.test import TestCase
from nova_dpm.tests.unit.virt.dpm import test_utils as utils
from nova_dpm.virt.dpm import host


class HostTestCase(TestCase):

    def setUp(self):
        super(HostTestCase, self).setUp()
        requests.packages.urllib3.disable_warnings()
        self.session = utils.create_session_1()
        self.client = zhmcclient.Client(self.session)
        self.cpc = self.client.cpcs.find(**{"name": "cpc_2"})
        self.flags(host=utils.HOST)
        self.flags(group="dpm", max_processors=3)
        self.flags(group="dpm", max_memory=2048)
        self.host = host.Host(self.cpc, self.client)

    def test_host_properties(self):

        host_properties = self.host.properties
        self.assertEqual(host_properties['hypervisor_hostname'],
                         utils.HOST)
        self.assertEqual(host_properties['cpc_name'], 'cpc_2')
        cpu_info = host_properties['cpu_info']
        cpu_info_dict = json.loads(cpu_info)
        self.assertEqual(cpu_info_dict['arch'], 's390x')
        self.assertEqual(cpu_info_dict['vendor'], 'IBM')

    def test_get_proc_used(self):
        proc_used = self.host._get_proc_used()
        self.assertEqual(proc_used, utils.MAC_PROC)

    def test_mem_used(self):
        memory_used = self.host._get_mem_used()
        self.assertEqual(memory_used, utils.TOTAL_MEM)
