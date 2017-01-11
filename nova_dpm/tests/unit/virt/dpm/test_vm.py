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

from nova.compute import manager as compute_manager
from nova.test import TestCase
from nova_dpm.tests.unit.virt.dpm import fakeutils
from nova_dpm.tests.unit.virt.dpm import fakezhmcclient
from nova_dpm.virt.dpm import vm
from nova_dpm.virt.dpm.vm import Instance


"""
vm unit testcase
"""


def getMockInstance():
    session = fakezhmcclient.Session("hostip", "dummyhost", "dummyhost")
    client = fakezhmcclient.Client(session)
    cpc = fakezhmcclient.getFakeCPC()
    inst = Instance(fakeutils.getFakeInstance(), cpc, client)
    inst.partition = fakezhmcclient.getFakePartition()
    return inst


class InstancePropertiesTestCase(TestCase):
    def setUp(self):
        super(InstancePropertiesTestCase, self).setUp()
        self.mock_nova_inst = mock.Mock()
        self.mock_nova_inst.uuid = 'foo-id'
        vm.CONF.set_override("host", "foo-host")

    @mock.patch.object(vm.Instance, 'get_partition')
    def test_partition_name(self, mock_get_part):
        inst = vm.Instance(self.mock_nova_inst, mock.Mock(), mock.Mock())
        self.assertEqual("OpenStack-Instance-foo-id", inst.partition_name)

    @mock.patch.object(vm.Instance, 'get_partition')
    def test_partition_description(self, mock_get_part):
        inst = vm.Instance(self.mock_nova_inst, mock.Mock(), mock.Mock())
        self.assertEqual("OpenStack CPCSubset=foo-host",
                         inst.partition_description)

    @mock.patch.object(vm.Instance, 'get_partition')
    def test_properties(self, mock_get_part):
        mock_flavor = mock.Mock()
        mock_flavor.vcpus = 5
        mock_flavor.memory_mb = 2000

        inst = vm.Instance(self.mock_nova_inst, mock.Mock(), mock.Mock(),
                           flavor=mock_flavor)
        props = inst.properties()
        self.assertEqual('OpenStack-Instance-foo-id', props['name'])
        self.assertEqual('OpenStack CPCSubset=foo-host', props['description'])
        self.assertEqual(5, props['ifl-processors'])
        self.assertEqual(2000, props['initial-memory'])
        self.assertEqual(2000, props['maximum-memory'])


class VmNicTestCase(TestCase):

    def setUp(self):
        super(VmNicTestCase, self).setUp()
        vm.zhmcclient = fakezhmcclient
        self.conf = fakeutils.getFakeCPCconf()

        self.inst = getMockInstance()
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


class VmHBATestCase(TestCase):

    def setUp(self):
        super(VmHBATestCase, self).setUp()
        vm.zhmcclient = fakezhmcclient
        self.conf = fakeutils.getFakeCPCconf()

        self.inst = getMockInstance()

        self.conf['physical_storage_adapter_mappings'] = \
            ["aaaaaaaa-bbbb-cccc-1123-567890abcdef:1"]
        self.inst.partition.hbas = fakezhmcclient.getFakeHbaManager()

    @mock.patch.object(vm.LOG, 'debug')
    @mock.patch.object(compute_manager.ComputeManager, '_prep_block_device',
                       return_value="blockdeviceinfo")
    def test_build_resources(self, mock_prep_block_dev, mock_debug):
        context = None
        novainstance = fakeutils.getFakeInstance()
        block_device_mapping = None
        resources = self.inst._build_resources(
            context, novainstance, block_device_mapping)
        self.assertEqual(resources['block_device_info'],
                         "blockdeviceinfo")

    @mock.patch.object(vm.LOG, 'debug')
    def test_attach_hba(self, mock_debug):
        self.inst.attachHba(self.conf)
