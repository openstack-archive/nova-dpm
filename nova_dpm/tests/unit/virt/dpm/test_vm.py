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

import mock

from nova.test import TestCase
from nova_dpm.tests.unit.virt.dpm import fakezhmcclient
from nova_dpm.virt.dpm import vm
from nova_dpm.virt.dpm.vm import Instance

"""
vm unit testcase
"""


class VmNicTestCase(TestCase):

    def setUp(self):
        super(VmNicTestCase, self).setUp()
        self.cpc = fakezhmcclient.getFakeCPC()
        self.conf = fakezhmcclient.getFakeCPCconf()
        self.inst = Instance("DummyInstance", self.cpc)
        self.inst.partition = fakezhmcclient.getFakePartition()
        self.inst.partition.nics = fakezhmcclient.getFakeNicManager()

    @mock.patch.object(vm.LOG, 'debug')
    def test_attach_nic(self, mock_debug):

        vif1 = {'id': 1234, 'type': 'dpm_vswitch',
                'address': "12-34-56-78-9A-BC",
                'details':
                    {'object-id': '00000000-aaaa-bbbb-cccc-abcdabcdabcd'}}
        network_info = [vif1]
        nic_interface = self.inst.attach_nic(self.conf, network_info)
        self.assertEqual(nic_interface.properties['name'],
                         "OpenStack_Port_1234")
        self.assertEqual(nic_interface.properties['object-uri'],
                         "/api/partitions/00000000-aaaa-bbbb-"
                         "cccc-abcdabcdabcd/nics/00000000-nics-"
                         "bbbb-cccc-abcdabcdabcd")
