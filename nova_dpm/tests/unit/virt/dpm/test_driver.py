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


from __future__ import absolute_import
from __future__ import print_function
from nova import context as context_object
from nova import exception
from nova.objects import flavor as flavor_object
from nova.test import TestCase
from nova_dpm.tests.unit.virt.dpm import test_data as utils
from nova_dpm.virt.dpm import driver
from nova_dpm.virt.dpm import exceptions
from nova_dpm.virt.dpm import vm
from nova_dpm.virt.dpm.volume import fibrechannel
from oslo_config import cfg

import mock
import zhmcclient
import zhmcclient_mock

PARTITION_WWPN = 'C05076FFEB8000D6'


def fake_session():
    session = zhmcclient_mock.FakedSession(
        'fake-host', 'fake-hmc', '2.13.1', '1.8')

    cpc1 = session.hmc.cpcs.add({
        'object-id': '6511ee0f-0d64-4392-b9e0-bbbbbbbbbbbb',
        'name': 'cpc_1',
        'description': 'CPC #1',
        'dpm-enabled': True,
        'processor-count-ifl': 10,
        'storage-customer': 2048,
        'se-version': '2.13.1'
    })
    partition1 = cpc1.partitions.add({
        'name': 'OpenStack-foo-6511ee0f-0d64-4392-b9e0-aaaaaaaaaaaa',
        'description': 'OpenStack CPCSubset=foo',
        'initial-memory': 1,
        'status': 'ACTIVE',
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
        'element-id': '1',
        'name': 'fcp_1_1',
        'description': 'FCP #1 Port #1',
    })

    partition1.hbas.add({
        'object-d': '1',
        "adapter-port-uri":
            "/api/adapters/"
            + "6511ee0f-0d64-4392-b9e0-cdbea10a17c3"
            + "/storage-ports/"
            + "1",
        'wwpn': PARTITION_WWPN
    })

    return session


class DPMdriverInitHostTestCase(TestCase):

    def setUp(self):
        super(DPMdriverInitHostTestCase, self).setUp()
        self.session = fake_session()
        self.client = zhmcclient.Client(self.session)
        self.dpmdriver = driver.DPMDriver(None)
        self.dpmdriver._client = self.client

        self.client = zhmcclient.Client(self.session)
        self.cpc = self.client.cpcs.find(**{"name": "cpc_1"})
        self.partition = self.cpc.partitions.find(
            **{"name": "OpenStack-foo-6511ee0f-0d64-4392-b9e0-aaaaaaaaaaaa"})
        adapter = self.cpc.adapters.find(**{'name': 'fcp_1'})
        self.adapter_object_id = adapter.get_property('object-id')
        self.port_element_id = adapter.ports.list()[0].get_property(
            'element-id')

        storage = self.adapter_object_id + ":" + self.port_element_id
        cfg.CONF.set_override("physical_storage_adapter_mappings", [storage],
                              group="dpm")

        self.flags(
            group="dpm",
            cpc_object_id="6511ee0f-0d64-4392-b9e0-bbbbbbbbbbbb")
        self.flags(group="dpm", max_processors=1)
        self.flags(group="dpm", max_memory=512)
        self.dpmdriver.init_host(None)

    def test_cpc_not_exists(self):
        self.flags(group="dpm",
                   cpc_object_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        self.assertRaises(SystemExit,
                          self.dpmdriver.init_host, None)

    def test_get_available_resource(self):
        host_properties = self.dpmdriver.get_available_resource(None)
        self.assertEqual('cpc_1', host_properties['cpc_name'])

    def test_invalid_mem_config(self):
        self.flags(group="dpm", max_memory=3000)

        self.assertRaises(exceptions.MaxMemoryExceededError,
                          self.dpmdriver.init_host,
                          None)

    def test_invalid_proc_config(self):
        self.flags(group="dpm", max_processors=50)

        self.assertRaises(
            exceptions.MaxProcessorExceededError,
            self.dpmdriver.init_host,
            None)

    @mock.patch.object(flavor_object.Flavor, 'get_by_id')
    @mock.patch.object(context_object, 'get_admin_context')
    @mock.patch.object(vm.PartitionInstance, 'create')
    @mock.patch.object(vm.PartitionInstance, 'attach_hbas')
    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(vm.PartitionInstance, 'properties')
    def test__prep_for_spawn_volume(self, mock_properties,
                                    mock_partition,
                                    mock_attac_hbas,
                                    mock_create,
                                    mock_context,
                                    mock_flavor):

        instance = mock.Mock()
        instance.image_ref = ''
        self.dpmdriver._prep_for_spawn(instance)
        mock_create.assert_called_once()
        mock_attac_hbas.assert_called_once()

    @mock.patch.object(flavor_object.Flavor, 'get_by_id')
    @mock.patch.object(context_object, 'get_admin_context')
    @mock.patch.object(vm.PartitionInstance, 'create')
    @mock.patch.object(vm.PartitionInstance, 'attach_hbas')
    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(vm.PartitionInstance, 'properties')
    def test__prep_for_spawn_image(self, mock_properties,
                                   mock_partition,
                                   mock_attac_hbas,
                                   mock_create,
                                   mock_context,
                                   mock_flavor):
        instance = mock.Mock()
        instance.image_ref = '6c77503d-4bff-4205-9e90-d75373c3c689'
        self.assertRaises(
            exceptions.BootFromImageNotSupported,
            self.dpmdriver._prep_for_spawn, instance)

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    def test_get_volume_connector(self, mock_get_partition):
        instance = mock.Mock()
        instance.image_ref = ""
        self.dpmdriver.get_volume_connector(instance)

    def test_get_available_nodes(self):
        self.flags(host="fake-mini")
        nodes = self.dpmdriver.get_available_nodes()
        self.assertEqual(nodes, ['fake-mini'])

    def test_node_is_available(self):
        self.flags(host="fake-mini")
        self.assertTrue(self.dpmdriver.node_is_available('fake-mini'))


class DPMdriverVolumeTestCase(TestCase):

    def setUp(self):
        super(DPMdriverVolumeTestCase, self).setUp()
        self.dpmdriver = driver.DPMDriver(None)

    def test_get_volume_drivers(self):

        driver_reg = self.dpmdriver._get_volume_drivers()
        self.assertIsInstance(driver_reg['fibre_channel'],
                              fibrechannel.DpmFibreChannelVolumeDriver)

    @mock.patch.object(fibrechannel.DpmFibreChannelVolumeDriver,
                       'connect_volume')
    def test_attach_volume(self, mock_connect_volume):

        connection_info = {'driver_volume_type': 'fibre_channel'}

        self.dpmdriver.attach_volume(None, connection_info, None, None)
        mock_connect_volume.assert_called_once()

    @mock.patch.object(fibrechannel.DpmFibreChannelVolumeDriver,
                       'disconnect_volume')
    def test_detach_volume(self, mock_disconnect_volume):

        connection_info = {'driver_volume_type': 'fibre_channel'}

        self.dpmdriver.detach_volume(connection_info, None, None)
        mock_disconnect_volume.assert_called_once()

    def test_attach_volume_Exception(self):

        connection_info = {'driver_volume_type': 'Dummy_channel'}

        self.assertRaises(exception.VolumeDriverNotFound,
                          self.dpmdriver.attach_volume, None,
                          connection_info, None, None)

    def test_detach_volume_Exception(self):

        connection_info = {'driver_volume_type': 'Dummy_channel'}

        self.assertRaises(exception.VolumeDriverNotFound,
                          self.dpmdriver.detach_volume,
                          connection_info, None, None)


class DPMDriverInstanceTestCase(TestCase):

    def setUp(self):
        super(DPMDriverInstanceTestCase, self).setUp()
        self.session = utils.create_session_1()
        self.client = zhmcclient.Client(self.session)
        self.dpmdriver = driver.DPMDriver(None)
        self.dpmdriver._client = self.client

    def _test__get_partition_instance(self, context=None, bdm=None):
        self.dpmdriver._cpc = mock.Mock()

        mock_inst = mock.Mock()
        mock_inst.image_ref = ''

        part_inst = self.dpmdriver._get_partition_instance(
            mock_inst, context=context, block_device_mapping=bdm)
        self.assertEqual(mock_inst, part_inst.instance)
        self.assertEqual(self.dpmdriver._cpc, part_inst.cpc)
        self.assertEqual(context, part_inst.context)
        self.assertEqual(bdm, part_inst.block_device_mapping)

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    def test___get_partition_instance_minimal(self, mocked_gp):
        self._test__get_partition_instance()

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    def test___get_partition_instance_max(self, mocked_gp):
        mock_context = mock.Mock()
        mock_bdi = mock.Mock()

        self._test__get_partition_instance(context=mock_context,
                                           bdm=mock_bdi)

    def test__get_partition_instance_boot_from_image(self):
        mock_inst = mock.Mock()
        mock_inst.image_ref = 'something'

        self.assertRaises(exceptions.BootFromImageNotSupported,
                          self.dpmdriver._get_partition_instance, mock_inst)

    @mock.patch.object(driver.DPMDriver, '_get_block_device_mapping')
    @mock.patch.object(driver.DPMDriver, '_get_partition_instance')
    def test_spawn_context(self, mocked_get_part_inst, mocked_get_bdm):
        """Make sure that context is provided to the PartitionInstance"""
        mock_context = mock.Mock()
        mock_inst = mock.Mock()
        mocked_get_bdm.return_value = "bdm"
        self.dpmdriver.spawn(mock_context, mock_inst, None, None, None, None,
                             [])

        mocked_get_part_inst.assert_called_once_with(mock_inst, mock_context,
                                                     "bdm")

    @mock.patch.object(driver.DPMDriver, '_get_block_device_mapping')
    @mock.patch.object(driver.DPMDriver, '_get_partition_instance')
    def test_spawn_bdm(self, mocked_get_part_inst, mocked_get_bdm):
        """Ensure that block_device_mapping is provided to PartitionInstance"""
        mocked_get_bdm.return_value = "bdm"
        mock_inst = mock.Mock()
        self.dpmdriver.spawn(None, mock_inst, None, None, None, None,
                             [], block_device_info=mock.Mock())

        mocked_get_part_inst.assert_called_once_with(mock_inst, None, "bdm")

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(vm.PartitionInstance, 'create')
    @mock.patch.object(vm.PartitionInstance, 'properties')
    def test_spawn_max_nics(self, mock_prop, mock_create, mock_get_part):
        dpmdriver = driver.DPMDriver(None)
        network_info = [x for x in range(0, 13)]
        mock_instance = mock.Mock()
        mock_instance.image_ref = ""
        self.assertRaises(exceptions.MaxAmountOfInstancePortsExceededError,
                          dpmdriver.spawn, None, mock_instance, None, None,
                          None, None, network_info)

    @mock.patch.object(vm.PartitionInstance, 'set_boot_properties')
    @mock.patch.object(vm.PartitionInstance, 'get_boot_hba')
    @mock.patch.object(vm.PartitionInstance, 'launch')
    @mock.patch.object(vm.PartitionInstance, 'attach_hbas')
    @mock.patch.object(vm.PartitionInstance, 'properties')
    def test_spawn_attach_nic(self, mock_prop, mock_attachHba, mock_launch,
                              mock_hba_uri, mock_get_bprops):

        cpc = self.client.cpcs.find(**{"object-id": "2"})
        self.dpmdriver._cpc = cpc
        self.flags(host="fake-mini")

        mock_instance = mock.Mock()
        mock_instance.uuid = "1"
        mock_instance.image_ref = ""

        vif = {"address": "aa:bb:cc:dd:ee:ff",
               "id": "foo-id",
               "type": "dpm_vswitch",
               "details": {"object_id": "1"}}
        vif2 = {"address": "11:22:33:44:55:66",
                "id": "foo-id2",
                "type": "dpm_vswitch",
                "details": {"object_id": "2"}}
        network_info = [vif, vif2]
        self.dpmdriver.spawn(None, mock_instance, None, None, None, None,
                             network_info)
        partition = cpc.partitions.find(**{
            "object-id": "1"})
        nics = partition.nics.list()
        self.assertEqual(nics[0].name, "OpenStack_Port_foo-id")
        self.assertEqual(nics[1].name, "OpenStack_Port_foo-id2")

        self.assertIn("8001,0,aabbccddeeff;",
                      partition.get_property("boot-os-specific-parameters"))
        self.assertIn("8002,0,112233445566;",
                      partition.get_property("boot-os-specific-parameters"))

    def test_list_instances(self):
        self.flags(host="fakemini")
        cpc = self.client.cpcs.find(**{"object-id": "3"})
        self.dpmdriver._cpc = cpc
        self.assertTrue(
            'OpenStack-fakemini-38400000-8cf0-11bd-b23e-10b96e4ef00d'
            in self.dpmdriver.list_instances())

    def test_get_info(self):
        self.flags(host="fakemini")
        cpc = self.client.cpcs.find(**{"object-id": "3"})
        self.dpmdriver._cpc = cpc

        mock_instance = mock.Mock()
        mock_instance.uuid = "38400000-8cf0-11bd-b23e-10b96e4ef00d"

        partitionInfo = self.dpmdriver.get_info(mock_instance)
        self.assertEqual(partitionInfo.mem, 512)
        self.assertEqual(partitionInfo.num_cpu, 1)
