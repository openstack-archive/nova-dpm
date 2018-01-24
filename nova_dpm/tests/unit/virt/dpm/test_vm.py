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

from oslo_config import cfg

from nova.compute import power_state
from nova.objects import flavor as flavor_obj
from nova.objects import instance as instance_obj
from nova.test import TestCase
from nova_dpm.virt.dpm import exceptions
from nova_dpm.virt.dpm import vm

import mock
import zhmcclient
import zhmcclient_mock


PARTITION_WWPN = 'CCCCCCCCCCCCCCCC'
LUN = 0
BLOCK_DEVICE = {
    'connection_info': {
        'driver_volume_type': 'fibre_channel',
        'connector': {
            'wwpns': [PARTITION_WWPN],
            'host': '3cfb165c-0df3-4d80-87b2-4c353e61318f'},
        'data': {
            'initiator_target_map': {
                PARTITION_WWPN: [
                    'AAAAAAAAAAAAAAAA',
                    'BBBBBBBBBBBBBBBB']},
            'target_discovered': False,
            'target_lun': LUN}}}


def fake_session():
    session = zhmcclient_mock.FakedSession(
        'fake-host', 'fake-hmc', '2.13.1', '1.8')

    cpc1 = session.hmc.cpcs.add({
        'name': 'cpc_1',
        'description': 'CPC #1',
        'dpm-enabled': True,
        'processor-count-ifl': 10,
        'storage-customer': 2048,
    })
    cpc1.partitions.add({
        'name': 'OpenStack-foo-6511ee0f-0d64-4392-b9e0-aaaaaaaaaaaa',
        'description': 'OpenStack CPCSubset=foo',
        'initial-memory': 1,
        'status': 'ACTIVE',
        'maximum-memory': 512,
        'ifl-processors': 3
    })
    cpc1.partitions.add({
        'name': 'OpenStack-foo-cccccccc-cccc-cccc-cccc-cccccccccccc',
        'description': 'OpenStack CPCSubset=foo',
        'initial-memory': 1,
        'status': 'paused',
        'maximum-memory': 512,
        'ifl-processors': 3
    })
    cpc1.partitions.add({
        'name': 'OpenStack-foo-6511ee0f-0d64-4392-aaaa-bbbbbbbbbbbb',
        'description': 'OpenStack CPCSubset=foo',
        'initial-memory': 512,
        'status': 'stopped',
        'maximum-memory': 512,
        'ifl-processors': 3
    })
    adapter1 = cpc1.adapters.add({
        'object-id': '6511ee0f-0d64-4392-b9e0-cdbea10a17c3',
        'name': 'fcp_1',
        'description': 'FCP #1',
        'type': 'fcp',
    })
    adapter1.ports.add({
        'name': 'fcp_1_1',
        'description': 'FCP #1 Port #1',
    })
    cpc1.virtual_switches.add({
        'name': 'virtual_switch',
        'object-id': '3ea09d2a-b18d-11e6-89a4-42f2e9ef1641'
    })
    return session


class ValidPartitionNameTestCase(TestCase):

    def setUp(self):
        super(ValidPartitionNameTestCase, self).setUp()

    def test_is_valid_partition_name(self):
        # All name should be in this format
        # OpenStack-hostname-[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}
        # where hostname is basically host of 'self.flags(host='foo').
        self.flags(host='foo')
        name1 = 'OpenStack-foo-6511ee0f-0d64-4392-b9e0-cdbea10a17c3'
        self.assertTrue(vm.is_valid_partition_name(name1))

        self.flags(host='foo-bar')
        name2 = 'OpenStack-foo-bar-6511ee0f-0d64-4392-b9e0-cdbea10a17c3'
        self.assertTrue(vm.is_valid_partition_name(name2))

        self.flags(host='foo-bar')
        name3 = 'invalid_name'
        self.assertFalse(vm.is_valid_partition_name(name3))

        self.flags(host='foo')
        name4 = 'fooOpenStack-foo-6511ee0f-0d64-4392-b9e0-cdbea10a17c3'
        self.assertFalse(vm.is_valid_partition_name(name4))

        self.flags(host='foo')
        # Name should be in this format
        # OpenStack-hostname-[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}
        #  but name5 is in
        # OpenStack-hostname-[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{13}
        # See at last instead of 12 character it is 13 character.
        name5 = 'OpenStack-foo-6511ee0f-0d64-4392-b9e0-cdbea10a17c31'
        self.assertFalse(vm.is_valid_partition_name(name5))


class VmPartitionInstanceTestCase(TestCase):
    def setUp(self):
        super(VmPartitionInstanceTestCase, self).setUp()

        self.session = fake_session()
        self.client = zhmcclient.Client(self.session)
        self.cpc = self.client.cpcs.find(**{"name": "cpc_1"})
        self.flags(host="foo")

        flavor = flavor_obj.Flavor()
        flavor.vcpus = 1
        flavor.memory_mb = 512
        self.instance = instance_obj.Instance()
        self.instance.uuid = '6511ee0f-0d64-4392-b9e0-aaaaaaaaaaaa'
        self.instance.flavor = flavor
        self.part_name = "OpenStack-foo-" + self.instance.uuid
        self.part_description = 'OpenStack CPCSubset=foo'

        self.create_partition_properties = {
            'name': self.part_name,
            'description': self.part_description,
            'initial-memory': 512,
            'maximum-memory': 512,
            # The zhmcclient mock support does not provide an empty default
            'boot-os-specific-parameters': ""
        }
        # Create partition in a cpc not from openstack
        # and used same uuid of instance to create
        # vm.PartitionInstance class instance except create_partition.
        partition = self.cpc.partitions.create(
            self.create_partition_properties)

        adapter = self.cpc.adapters.find(**{'name': 'fcp_1'})
        self.adapter_object_id = adapter.get_property('object-id')
        self.port_element_id = adapter.ports.list()[0].get_property(
            'element-id')
        storage = self.adapter_object_id + ":" + self.port_element_id
        cfg.CONF.set_override("physical_storage_adapter_mappings", [storage],
                              group="dpm")
        dpm_hba_dict = {
            "name": "OpenStack_Port_" + self.adapter_object_id +
                    "_" + str(self.port_element_id),
            "description": "OpenStack CPCSubset= foo",
            "adapter-port-uri": "/api/adapters/"
                                + self.adapter_object_id +
                                "/storage-ports/" +
                                str(self.port_element_id)
        }
        # create hba in cpc.partition not from openstack
        # and later used to test all function which is related
        # to hbas except hba_create
        partition.hbas.create(dpm_hba_dict)
        self.partition_inst = vm.PartitionInstance(
            self.instance, self.cpc)

    def test_properties(self):
        properties = self.partition_inst.properties()
        self.assertEqual(self.part_name, properties['name'])
        self.assertEqual(self.part_description, properties['description'])
        self.assertEqual(1, properties['ifl-processors'])
        self.assertEqual(512, properties['initial-memory'])
        self.assertEqual(512, properties['maximum-memory'])

    def test_partition_create(self):
        partition_name = ('OpenStack-foo-'
                          + '6511ee0f-0d64-4392-b9e0-bbbbbbbbbbbb')
        properties = {
            'name': partition_name,
            'description': self.part_description,
            'ifl-processors': self.instance.flavor.vcpus,
            'initial-memory': self.instance.flavor.memory_mb,
            'maximum-memory': self.instance.flavor.memory_mb}

        self.partition_inst.create(properties)
        partition = self.cpc.partitions.find(**{"name": partition_name})
        self.assertEqual(partition_name, partition.get_property('name'))

    def test_partition_name(self):
        self.assertEqual(
            self.part_name,
            self.partition_inst.partition_name)

    def test_partition_description(self):
        self.assertEqual(
            self.part_description,
            self.partition_inst.partition_description)

    def test_get_partition(self):
        self.assertEqual(
            self.part_name,
            self.partition_inst.get_partition().get_property('name'))

    def test__set_nic_string_in_os_specific_parameters(self):
        nic = mock.Mock()
        nic.get_property = lambda prop: {'device-number': 'devno'}[prop]

        vif_obj = mock.Mock()
        vif_obj.mac = 'mac'

        self.partition_inst._set_nic_string_in_os_specific_parameters(nic,
                                                                      vif_obj)

        boot_os_params = self.partition_inst.partition.get_property(
            'boot-os-specific-parameters')
        self.assertIn('devno,0,mac;', boot_os_params)

    def test__get_nic_properties_dict(self):
        cfg.CONF.set_override("host", "subset")
        vif = mock.Mock()
        vif.dpm_nic_object_id = "nic_oid"
        vif.mac = "mac"
        vif.port_id = "port_id"

        nic_props = self.partition_inst._get_nic_properties_dict(vif)

        self.assertEqual("OpenStack_Port_port_id", nic_props["name"])
        self.assertEqual("OpenStack mac=mac, CPCSubset=subset",
                         nic_props["description"])
        self.assertEqual("/api/virtual-switches/nic_oid",
                         nic_props["virtual-switch-uri"])

    def test_attach_nic(self):
        vif = mock.Mock()
        vif.mac = "fa:16:3e:e4:9a:98"
        vif.dpm_nic_object_id = "3ea09d2a-b18d-11e6-89a4-42f2e9ef1641"
        vif.type = "dpm_vswitch"
        vif.port_id = "703da361-9d4d-4441-b99b-e081c3e9cfbb"
        vif.vlan_id = None
        nic_interface = self.partition_inst.attach_nic(vif)
        self.assertEqual(
            'OpenStack_Port_703da361-9d4d-4441-b99b-e081c3e9cfbb',
            nic_interface.properties['name'])

    def test_attach_nic_with_non_dpm_vswitch(self):
        vif = mock.Mock()
        vif.type = "non_dpm_vswitch"

        self.assertRaises(
            exceptions.InvalidVIFTypeError,
            self.partition_inst.attach_nic, vif)

    def test_attach_nic_vlan(self):
        vif = mock.Mock()
        vif.type = "dpm_vswitch"
        vif.vlan_id = 1

        self.assertRaises(
            exceptions.InvalidNetworkTypeError,
            self.partition_inst.attach_nic, vif)

    @mock.patch.object(vm.PartitionInstance, 'attach_nic')
    def test_attach_nics(self, mocked_attach_nic):
        vif1 = {"address": "mac1"}
        vif2 = {"address": "mac2"}
        self.partition_inst.attach_nics([vif1, vif2])
        mock_calls = mocked_attach_nic.call_args_list
        # attach nic called 2 times
        self.assertEqual(2, len(mock_calls))

        # mock_calls is a list of calls
        # each call is a tuple (args, kwargs)
        # args is a tuple (arg1, arg2, arg3). We need the first arg [0]
        self.assertEqual("mac1", mock_calls[0][0][0].mac)
        self.assertEqual("mac2", mock_calls[1][0][0].mac)

    def test_append_to_boot_os_specific_parameters_empty(self):
        data = '1800,0,fa163ee49a98;'
        self.partition_inst.append_to_boot_os_specific_parameters(data)
        self.assertEqual(
            " " + data,
            self.partition_inst.get_partition().get_property(
                'boot-os-specific-parameters'))

    def test_append_to_boot_os_specific_parameters_value(self):
        data = '1800,0,fa163ee49a98;'
        self.partition_inst.partition.update_properties({
            'boot-os-specific-parameters': 'foo'
        })
        self.partition_inst.append_to_boot_os_specific_parameters(data)
        self.assertEqual(
            "foo " + data,
            self.partition_inst.get_partition().get_property(
                'boot-os-specific-parameters'))

    def test_append_to_boot_os_specific_parameters_too_long(self):
        data = 257 * 'a'
        self.assertRaises(
            exceptions.BootOsSpecificParametersPropertyExceededError,
            self.partition_inst.append_to_boot_os_specific_parameters, data)

    @mock.patch.object(vm.BlockDevice, "get_target_wwpn")
    @mock.patch.object(vm.PartitionInstance, "get_boot_hba")
    @mock.patch.object(vm.BlockDevice, "lun", new_callable=mock.PropertyMock)
    def test_set_boot_properties(self, mock_lun, mock_get_hba, mock_gtw):
        mock_lun.return_value = '1'

        wwpn = 'DDDDDDDDDDDDDDDD'
        mock_gtw.return_value = wwpn

        booturi = '/api/partitions/1/hbas/1'
        mock_hba = mock.Mock()
        mock_hba.get_property = lambda prop: {'element-uri': booturi,
                                              'wwpn': wwpn}[prop]
        mock_get_hba.return_value = mock_hba

        self.partition_inst.block_device_mapping = [BLOCK_DEVICE]
        self.partition_inst.set_boot_properties()

        mock_gtw.assert_called_once_with(wwpn)

        partition = self.cpc.partitions.find(**{"name": self.part_name})
        self.assertEqual(
            'storage-adapter',
            partition.get_property('boot-device'))
        self.assertEqual(
            wwpn,
            partition.get_property('boot-world-wide-port-name'))
        self.assertEqual(
            '1',
            partition.get_property('boot-logical-unit-number'))
        self.assertEqual(
            booturi,
            partition.get_property('boot-storage-device'))

    def test_attach_hbas(self):
        partition = self.cpc.partitions.find(**{"name": self.part_name})
        total_hbas = len(partition.hbas.list())
        self.partition_inst.attach_hbas()
        self.assertEqual(
            total_hbas + 1,
            len(partition.hbas.list()))

    def test_get_adapter_port_mappings(self):
        adapter_port_map = self.partition_inst.get_adapter_port_mappings()
        adapter_port = adapter_port_map.get_adapter_port_mapping()[0]
        self.assertEqual(self.adapter_object_id, adapter_port['adapter_id'])
        self.assertEqual(self.port_element_id, str(adapter_port['port']))

    def test_get_hba_uri(self):
        partition = self.cpc.partitions.find(**{"name": self.part_name})
        self.assertEqual(
            partition.get_property(
                'object-uri') + '/hbas/1',
            self.partition_inst.get_hba_uris()[0])

    def test_get_boot_hba(self):
        partition = self.cpc.partitions.find(**{"name": self.part_name})
        hba = self.partition_inst.get_boot_hba()
        self.assertEqual(partition.get_property('object-uri') + '/hbas/1',
                         hba.get_property('element-uri'))

    def test_power_on_vm_when_paused(self):
        instance = instance_obj.Instance()
        instance.uuid = 'cccccccc-cccc-cccc-cccc-cccccccccccc'
        partition_inst = vm.PartitionInstance(instance, self.cpc)
        partition_inst.power_on_vm()
        self.assertEqual(
            'active', partition_inst.get_partition().get_property('status'))

    def test_destroy_stopped_partition(self):
        instance = instance_obj.Instance()
        instance.save = mock.Mock()
        instance.uuid = '6511ee0f-0d64-4392-aaaa-bbbbbbbbbbbb'
        partition_inst = vm.PartitionInstance(instance, self.cpc)
        partition_inst.destroy()


class PhysicalAdapterModelTestCase(TestCase):

    def setUp(self):
        super(PhysicalAdapterModelTestCase, self).setUp()
        self.session = fake_session()
        self.client = zhmcclient.Client(self.session)
        self.cpc = self.client.cpcs.find(**{"name": "cpc_1"})
        self.flags(host="foo")
        self.fcp_adapter = self.cpc.adapters.find(**{'name': 'fcp_1'})
        self.phycal_adapter = vm.PhysicalAdapterModel(self.cpc)

    def test_get_adapter(self):
        adapter_id = self.fcp_adapter.get_property('object-id')
        adapter = self.phycal_adapter._get_adapter(adapter_id)
        self.assertEqual(adapter_id, adapter.get_property('object-id'))

    def test_add_adapter_por(self):
        adapter_id = self.fcp_adapter.get_property('object-id')
        port = self.fcp_adapter.ports.find(**{'name': 'fcp_1_1'})
        self.phycal_adapter._add_adapter_port(adapter_id, port)
        self.assertEqual(
            adapter_id,
            self.phycal_adapter._adapter_ports[0]['adapter_id'])
        self.assertEqual(
            port,
            self.phycal_adapter._adapter_ports[0]['port'])


class PartitionInstanceInfoTestCase(TestCase):

    def setUp(self):
        super(PartitionInstanceInfoTestCase, self).setUp()
        self.session = fake_session()
        self.client = zhmcclient.Client(self.session)
        self.cpcs = self.client.cpcs.list()
        self.flags(host="foo")
        self.instance = instance_obj.Instance()
        self.instance.uuid = '6511ee0f-0d64-4392-b9e0-aaaaaaaaaaaa'
        self.cpc = self.client.cpcs.find(**{"name": "cpc_1"})
        # Using Partition1 of fake cpc#1
        # vm.PartitionInstanceInfo class instance to get the information
        # of the status,memory etc..,

        self.instance_partition = vm.PartitionInstanceInfo(
            self.instance, self.cpc)

    def test_state(self):
        self.assertEqual(power_state.RUNNING, self.instance_partition.state)

    def test_paused_partition_state(self):
        instance = instance_obj.Instance()
        instance.uuid = 'cccccccc-cccc-cccc-cccc-cccccccccccc'
        instance_partition = vm.PartitionInstanceInfo(instance, self.cpc)
        self.assertEqual(power_state.SHUTDOWN, instance_partition.state)

    def test_mem(self):
        self.assertEqual(1, self.instance_partition.mem)

    def test_max_mem(self):
        self.assertEqual(512, self.instance_partition.max_mem)

    def test_num_cpu(self):
        self.assertEqual(3, self.instance_partition.num_cpu)
