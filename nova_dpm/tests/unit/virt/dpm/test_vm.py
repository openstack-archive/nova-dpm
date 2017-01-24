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
from nova_dpm.virt.dpm.exceptions import BootOsSpecificParametersExceededError
from nova_dpm.virt.dpm import vm


"""
vm unit testcase
"""


def getMockInstance():
    session = fakezhmcclient.Session("hostip", "dummyhost", "dummyhost")
    client = fakezhmcclient.Client(session)
    cpc = fakezhmcclient.getFakeCPC()
    inst = vm.PartitionInstance(fakeutils.getFakeInstance(), cpc, client)
    inst.partition = fakezhmcclient.getFakePartition()
    return inst


class VmFunctionTestCase(TestCase):
    def setUp(self):
        super(VmFunctionTestCase, self).setUp()
        self.valid_name = (
            'OpenStack-foo-6511ee0f-0d64-4392-b9e0-cdbea10a17c3')
        self.invalid_name = 'OpenStack-Instance-6511ee0f'
        self.cpc = fakezhmcclient.getFakeCPC()

    @mock.patch.object(vm.CONF, 'host', 'foo')
    def test_is_valid_partition_name(self):
        self.assertTrue(vm.is_valid_partition_name(self.valid_name))
        self.assertFalse(vm.is_valid_partition_name(self.invalid_name))

    @mock.patch.object(vm.CONF, 'host', 'foo')
    def test_partition_list(self):
        partition_list = vm.cpcsubset_partition_list(self.cpc)
        list = self.cpc.partitions.list()
        length = len(list)
        for i in range(length):
            self.assertEqual(list[i].get_property('name'),
                             partition_list[i].get_property('name'))

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    def test_get_boot_properties(self, m_get_part):
        inst = vm.PartitionInstance(None, None, None)
        inst._boot_os_specific_parameters = "foo"
        props = inst.get_boot_properties()
        self.assertEqual("test-operating-system", props["boot-device"])
        self.assertEqual("foo", props["boot-os-specific-parameters"])
        self.assertTrue(2, len(props))


class InstancePropertiesTestCase(TestCase):
    def setUp(self):
        super(InstancePropertiesTestCase, self).setUp()
        self.mock_nova_inst = mock.Mock()
        self.mock_nova_inst.uuid = 'foo-id'
        vm.CONF.set_override("host", "foo")

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    def test_partition_name(self, mock_get_part):
        inst = vm.PartitionInstance(
            self.mock_nova_inst, mock.Mock(), mock.Mock())
        self.assertEqual("OpenStack-foo-foo-id", inst.partition_name)

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    def test_partition_description(self, mock_get_part):
        inst = vm.PartitionInstance(
            self.mock_nova_inst, mock.Mock(), mock.Mock())
        self.assertEqual("OpenStack CPCSubset=foo",
                         inst.partition_description)

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    def test_properties(self, mock_get_part):
        mock_flavor = mock.Mock()
        mock_flavor.vcpus = 5
        mock_flavor.memory_mb = 2000

        inst = vm.PartitionInstance(
            self.mock_nova_inst, mock.Mock(),
            mock.Mock(), flavor=mock_flavor)
        props = inst.properties()
        self.assertEqual('OpenStack-foo-foo-id', props['name'])
        self.assertEqual('OpenStack CPCSubset=foo', props['description'])
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
        self.vif1 = {
            'id': 1234, 'type': 'dpm_vswitch', 'address': '12:34:56:78:9A:BC',
            'details': {'object_id': '00000000-aaaa-bbbb-cccc-abcdabcdabcd'}}

    @mock.patch.object(vm.LOG, 'debug')
    def test_attach_nic(self, mock_debug):

        ret_val = mock.MagicMock()
        ret_val.get_property.return_value = "0001"
        # Required to satisfy dict[..] operations on mocks
        ret_val .__getitem__.side_effect = dict.__getitem__
        with mock.patch.object(fakezhmcclient.NicManager, 'create',
                               return_value=ret_val) as mock_create:
            nic_interface = self.inst.attach_nic(self.conf, self.vif1)
        self.assertEqual(ret_val, nic_interface)
        self.assertTrue(mock_create.called)
        call_arg_dict = mock_create.mock_calls[0][1][0]
        # Name
        self.assertTrue(call_arg_dict['name'].startswith('OpenStack'))
        self.assertIn(str(1234), call_arg_dict['name'])
        # Description
        self.assertTrue(call_arg_dict['description'].startswith('OpenStack'))
        self.assertIn('mac=12:34:56:78:9A:BC', call_arg_dict['description'])
        self.assertIn('CPCSubset=' + self.conf['cpcsubset_name'],
                      call_arg_dict['description'])
        # virtual-switch-uri
        self.assertEqual(
            '/api/virtual-switches/00000000-aaaa-bbbb-cccc-abcdabcdabcd',
            call_arg_dict['virtual-switch-uri'])

    def test_attach_nic_boot_os_specific_parm_exceeded(self):
        ret_val = mock.MagicMock()
        ret_val.get_property.return_value = "0001"
        # Required to satisfy dict[..] operations on mocks
        ret_val .__getitem__.side_effect = dict.__getitem__
        # Only 256 chars are allowed. Setting 256 to make sure we exceed it
        self.inst._boot_os_specific_parameters = "n" * 256
        with mock.patch.object(fakezhmcclient.NicManager, 'create',
                               return_value=ret_val):
            self.assertRaises(BootOsSpecificParametersExceededError,
                              self.inst.attach_nic, self.conf, self.vif1)

    def test__append_nic_to_boot_os_specific_parameters(self):
        mock_part = mock.Mock()
        mock_part.get_property.return_value = "foo"
        with mock.patch.object(vm.PartitionInstance, 'get_partition',
                               return_value=mock_part):
            inst = vm.PartitionInstance(None, None, None)
        mock_nic = mock.Mock()
        mock_nic.get_property.return_value = "0001"
        inst._append_nic_to_boot_os_specific_parameters(mock_nic, self.vif1)
        self.assertEqual("foo0001,0,123456789ABC;",
                         inst._boot_os_specific_parameters)

    def test__append_nic_to_boot_os_specific_parameters_too_long(self):
        mock_part = mock.Mock()
        # Defining a large initial boot property. Now adding nic to it
        # should fail
        mock_part.get_property.return_value = "x" * 250

        with mock.patch.object(vm.PartitionInstance, 'get_partition',
                               return_value=mock_part):
            inst = vm.PartitionInstance(None, None, None)
        mock_nic = mock.Mock()
        mock_nic.get_property.return_value = "0001"

        self.assertRaises(
            BootOsSpecificParametersExceededError,
            inst._append_nic_to_boot_os_specific_parameters,
            mock_nic, self.vif1)


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


class InstancePartitionLifecycleTestCase(TestCase):

    @mock.patch.object(vm.PartitionInstance, "_loop_status_update")
    def test_launch(self, mock_loop_stat_upd):
        mock_part = mock.Mock()
        mock_inst = mock.Mock()
        with mock.patch.object(vm.PartitionInstance, "get_partition",
                               return_value=mock_part):
            part_inst = vm.PartitionInstance(mock_inst, None, None)
        part_inst._boot_os_specific_parameters = "foo"
        part_inst.launch()

        self.assertEqual("building", mock_inst.vm_state)
        self.assertEqual("spawning", mock_inst.task_state)
        mock_inst.save.assert_called_once()
        mock_part.update_properties.assert_called_once_with(
            properties={'boot-os-specific-parameters': 'foo',
                        'boot-device': 'test-operating-system'})
        mock_part.start.assert_called_once_with(True)
        mock_loop_stat_upd.assert_called_once()
