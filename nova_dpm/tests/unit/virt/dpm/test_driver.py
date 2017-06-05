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
from nova.virt import driver as basedriver
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
BLOCK_DEVICE = [{
    'connection_info': {
        'driver_volume_type': 'fibre_channel',
        'connector': {
            'wwpns': [PARTITION_WWPN],
            'host': '3cfb165c-0df3-4d80-87b2-4c353e61318f'},
        'data': {
            'initiator_target_map': {
                PARTITION_WWPN: [
                    '500507680B214AC1',
                    '500507680B244AC0']},
            'target_discovered': False,
            'target_lun': 0}}}]


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
                              group="dpm", enforce_type=True)

        self.flags(
            group="dpm",
            cpc_object_id="6511ee0f-0d64-4392-b9e0-bbbbbbbbbbbb")
        self.flags(group="dpm", max_processors=1)
        self.flags(group="dpm", max_memory=512)
        self.dpmdriver.init_host(None)

    def test_cpc_not_exists(self):
        self.flags(group="dpm", cpc_object_id="abc")
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

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(basedriver, 'block_device_info_get_mapping')
    def test_get_fc_boot_props(self, mock_block_device,
                               mock_get_partition):
        mock_get_partition.return_value = self.partition
        mock_block_device.return_value = BLOCK_DEVICE
        inst = vm.PartitionInstance(mock.Mock(), mock.Mock())
        target_wwpn, lun = self.dpmdriver.get_fc_boot_props(
            mock.Mock(), inst)
        self.assertEqual(target_wwpn, '500507680B214AC1')
        self.assertEqual(lun, '0')

    def test_validate_volume_type_unsupported(self):

        bdms = [
            {'connection_info': {'driver_volume_type': 'fake_vol_type'}}]
        self.assertRaises(exceptions.UnsupportedVolumeTypeException,
                          self.dpmdriver._validate_volume_type, bdms)

        bdms = [
            {'connection_info': {'driver_volume_type': 'fake_vol_type'}},
            {'connection_info': {'driver_volume_type': 'fake_vol_type'}}]
        self.assertRaises(exceptions.UnsupportedVolumeTypeException,
                          self.dpmdriver._validate_volume_type, bdms)

        bdms = [
            {'connection_info': {'driver_volume_type': 'fibre_channel'}},
            {'connection_info': {'driver_volume_type': 'fake_vol_type'}}]
        self.assertRaises(exceptions.UnsupportedVolumeTypeException,
                          self.dpmdriver._validate_volume_type, bdms)

    def test_validate_volume_type_supported(self):
        bdms = [
            {'connection_info': {'driver_volume_type': 'fibre_channel'}},
            {'connection_info': {'driver_volume_type': 'fibre_channel'}}]
        self.dpmdriver._validate_volume_type(bdms)

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(basedriver, 'block_device_info_get_mapping')
    def test_get_fc_boot_props_ignore_list(self, mock_block_device,
                                           mock_get_partition):
        mock_get_partition.return_value = self.partition
        mock_block_device.return_value = BLOCK_DEVICE
        self.flags(group="dpm", target_wwpn_ignore_list=["500507680B214AC1"])
        self.dpmdriver.init_host(None)
        inst = vm.PartitionInstance(mock.Mock(), mock.Mock())
        target_wwpn, lun = self.dpmdriver.get_fc_boot_props(
            mock.Mock(), inst)
        self.assertEqual(target_wwpn, '500507680B244AC0')
        self.assertEqual(lun, '0')

    @mock.patch.object(flavor_object.Flavor, 'get_by_id')
    @mock.patch.object(context_object, 'get_admin_context')
    @mock.patch.object(vm.PartitionInstance, 'create')
    @mock.patch.object(vm.PartitionInstance, 'attach_hbas')
    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(vm.PartitionInstance, 'properties')
    def test_prep_for_spawn_volume(self, mock_properties,
                                   mock_partition,
                                   mock_attac_hbas,
                                   mock_create,
                                   mock_context,
                                   mock_flavor):

        instance = mock.Mock()
        instance.image_ref = ''
        self.dpmdriver.prep_for_spawn(mock.Mock, instance)
        mock_create.assert_called_once()
        mock_attac_hbas.assert_called_once()

    @mock.patch.object(flavor_object.Flavor, 'get_by_id')
    @mock.patch.object(context_object, 'get_admin_context')
    @mock.patch.object(vm.PartitionInstance, 'create')
    @mock.patch.object(vm.PartitionInstance, 'attach_hbas')
    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(vm.PartitionInstance, 'properties')
    def test_prep_for_spawn_image(self, mock_properties,
                                  mock_partition,
                                  mock_attac_hbas,
                                  mock_create,
                                  mock_context,
                                  mock_flavor):
        instance = mock.Mock()
        instance.image_ref = '6c77503d-4bff-4205-9e90-d75373c3c689'
        self.assertRaises(
            exceptions.BootFromImageNotSupported,
            self.dpmdriver.prep_for_spawn,
            mock.Mock(), instance)

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    def test_get_volume_connector(self, mock_get_partition):
        self.dpmdriver.get_volume_connector(mock.Mock())

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

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(vm.PartitionInstance, 'create')
    @mock.patch.object(vm.PartitionInstance, 'properties')
    def test_spawn_max_nics(self, mock_prop, mock_create, mock_get_part):
        dpmdriver = driver.DPMDriver(None)
        network_info = [x for x in range(0, 13)]
        self.assertRaises(exceptions.MaxAmountOfInstancePortsExceededError,
                          dpmdriver.spawn, None, None, None, None, None,
                          network_info, flavor=mock.Mock())

    @mock.patch.object(driver.DPMDriver, 'get_fc_boot_props',
                       return_value=(None, None))
    @mock.patch.object(vm.PartitionInstance, 'get_boot_hba_uri')
    @mock.patch.object(vm.PartitionInstance, 'launch')
    @mock.patch.object(vm.PartitionInstance, 'attach_hbas')
    @mock.patch.object(vm.PartitionInstance, 'properties')
    @mock.patch.object(driver.DPMDriver, '_get_nic_string_for_guest_os')
    def test_spawn_attach_nic(self, mock_prop, mock_attachHba, mock_launch,
                              mock_hba_uri, mock_get_bprops, mock_nic_string):

        cpc = self.client.cpcs.find(**{"object-id": "2"})
        self.dpmdriver._cpc = cpc
        self.flags(host="fake-mini")

        mock_instance = mock.Mock()
        mock_instance.uuid = "1"

        vif = {"address": "aa:bb:cc:dd:ee:ff",
               "id": "foo-id",
               "type": "dpm_vswitch",
               "details": {"object_id": "oid"}}
        vif2 = {"address": "11:22:33:44:55:66",
                "id": "foo-id2",
                "type": "dpm_vswitch",
                "details": {"object_id": "oid2"}}
        network_info = [vif, vif2]
        self.dpmdriver.spawn(None, mock_instance, None, None, None,
                             network_info, flavor=mock.Mock())

        partition = cpc.partitions.find(**{
            "object-id": "1"})
        nics = partition.nics.list()
        self.assertEqual(nics[0].name, "OpenStack_Port_foo-id")
        self.assertEqual(nics[1].name, "OpenStack_Port_foo-id2")

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
