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
import nova_dpm.conf

from nova import context as context_object
from nova import exception
from nova.objects import flavor as flavor_object
from nova.test import TestCase
from nova.virt import driver as driv
from nova_dpm.tests.unit.virt.dpm import fakezhmcclient
from nova_dpm.tests.unit.virt.dpm import test_host as testhost
from nova_dpm.virt.dpm import client_proxy
from nova_dpm.virt.dpm import driver
from nova_dpm.virt.dpm import exceptions
from nova_dpm.virt.dpm import host as dpmHost
from nova_dpm.virt.dpm import vm
from nova_dpm.virt.dpm.volume import fibrechannel

"""
cpcsubset unit testcase
"""

CONF = nova_dpm.conf.CONF

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


def getMockNovaInstanceForPartion():
    mock_nova_inst = mock.Mock()
    mock_nova_inst.uuid = fakezhmcclient.INSTANCE_NAME1
    return mock_nova_inst


class DPMdriverTestCase(TestCase):

    def setUp(self):
        super(DPMdriverTestCase, self).setUp()
        client_proxy.zhmcclient = fakezhmcclient
        self.flags(group="dpm", max_processors=5)
        self.flags(group="dpm", max_memory=50)

    @mock.patch.object(driver.LOG, 'debug')
    def test_host(self, mock_warning):
        self.flags(group="dpm", hmc="1.1.1.1")
        self.flags(group="dpm", hmc_username="dummyuser")
        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        self.assertIsNotNone(dpmdriver)

        expected_arg = 'HMC details 1.1.1.1 dummyuser'
        assertlogs = False
        for call in mock_warning.call_args_list:
            if (len(call) > 0):
                if (len(call[0]) > 0 and call[0][0] == expected_arg):
                    assertlogs = True

        self.assertTrue(assertlogs)

    @mock.patch.object(driver.LOG, 'debug')
    @mock.patch.object(dpmHost, 'Host', return_value=testhost.fakeHost())
    def test_init_host(self, mockhost, mock_warning):
        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        dpmdriver.init_host(None)
        host_properties = dpmdriver.get_available_resource(None)

        self.assertEqual(host_properties['hypervisor_hostname'],
                         'S12subset')

    @mock.patch.object(driver.LOG, 'debug')
    def test_invalid_mem_config(self, mock_warning):
        self.flags(group="dpm", max_memory=1000)

        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        self.assertRaises(exception.ValidationError,
                          dpmdriver.init_host,
                          None)

    @mock.patch.object(driver.LOG, 'debug')
    def test_invalid_proc_config(self, mock_warning):
        self.flags(group="dpm", max_processors=50)

        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        self.assertRaises(exception.ValidationError,
                          dpmdriver.init_host,
                          None)

    def test_get_volume_drivers(self):
        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)
        driver_reg = dpmdriver._get_volume_drivers()
        self.assertTrue(isinstance(driver_reg['fibre_channel'],
                                   fibrechannel.DpmFibreChannelVolumeDriver))

    @mock.patch.object(fibrechannel.DpmFibreChannelVolumeDriver,
                       'connect_volume')
    def test_attach_volume(self, mock_connect_volume):
        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        connection_info = {'driver_volume_type': 'fibre_channel'}

        dpmdriver.attach_volume(None, connection_info, None, None)
        mock_connect_volume.assert_called_once()

    @mock.patch.object(fibrechannel.DpmFibreChannelVolumeDriver,
                       'disconnect_volume')
    def test_detach_volume(self, mock_disconnect_volume):
        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        connection_info = {'driver_volume_type': 'fibre_channel'}

        dpmdriver.detach_volume(connection_info, None, None)
        mock_disconnect_volume.assert_called_once()

    def test_attach_volume_Exception(self):
        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        connection_info = {'driver_volume_type': 'Dummy_channel'}

        self.assertRaises(exception.VolumeDriverNotFound,
                          dpmdriver.attach_volume, None,
                          connection_info, None, None)

    def test_detach_volume_Exception(self):
        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        connection_info = {'driver_volume_type': 'Dummy_channel'}

        self.assertRaises(exception.VolumeDriverNotFound,
                          dpmdriver.detach_volume,
                          connection_info, None, None)

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(vm.PartitionInstance,
                       'get_partition_wwpns', return_value=[PARTITION_WWPN])
    @mock.patch.object(driv, 'block_device_info_get_mapping',
                       return_value=BLOCK_DEVICE)
    def test_get_fc_boot_props(self, mock_block_device,
                               mock_get_partition_wwpns,
                               mock_get_partition):
        dummy_virt_api = None
        dpm_driver = driver.DPMDriver(dummy_virt_api)
        dpm_driver.init_host(None)
        inst = vm.PartitionInstance(mock.Mock(), mock.Mock())
        target_wwpn, lun = dpm_driver.get_fc_boot_props(
            mock.Mock(), inst)
        self.assertEqual(target_wwpn, '500507680B214AC1')
        self.assertEqual(lun, '0')

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(vm.PartitionInstance,
                       'get_partition_wwpns', return_value=[PARTITION_WWPN])
    @mock.patch.object(driv, 'block_device_info_get_mapping',
                       return_value=BLOCK_DEVICE)
    def test_get_fc_boot_props_ignore_list(self, mock_block_device,
                                           mock_get_partition_wwpns,
                                           mock_get_partition):
        self.flags(group="dpm", target_wwpn_ignore_list=["500507680B214AC1"])
        dummy_virt_api = None
        dpm_driver = driver.DPMDriver(dummy_virt_api)
        dpm_driver.init_host(None)
        inst = vm.PartitionInstance(mock.Mock(), mock.Mock())
        target_wwpn, lun = dpm_driver.get_fc_boot_props(
            mock.Mock(), inst)
        self.assertEqual(target_wwpn, '500507680B244AC0')
        self.assertEqual(lun, '0')

    @mock.patch.object(flavor_object.Flavor, 'get_by_id')
    @mock.patch.object(context_object, 'get_admin_context')
    @mock.patch.object(vm.PartitionInstance, 'create')
    @mock.patch.object(vm.PartitionInstance, 'attach_hbas')
    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(vm.PartitionInstance, 'properties')
    def test_prep_for_spawn(self, mock_properties,
                            mock_partition, mock_attac_hbas,
                            mock_create, mock_context, mock_flavor):
        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)
        dpmdriver._conf = mock.Mock()
        dpmdriver.prep_for_spawn(mock.Mock, mock.Mock())
        mock_create.assert_called_once()
        mock_attac_hbas.assert_called_once()

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    def test_get_volume_connector(self, mock_get_partition):
        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)
        dpmdriver.get_volume_connector(mock.Mock())


class DPMPartitionSpawnNicTestCase(TestCase):
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
    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(vm.PartitionInstance, 'properties')
    def test_spawn_attach_nic(self, mock_prop, mock_get_part,
                              mock_attachHba, mock_launch, mock_hba_uri,
                              mock_get_bprops):
        mock_nic = mock.Mock()
        mock_nic.properties = {"name": "foo-name",
                               "virtual-switch-uri": "foo-uri",
                               "device-number": "0001"}
        mock_nic.get_property = lambda key: {"device-number": "0001"}[key]

        mock_nic2 = mock.Mock()
        mock_nic2.properties = {"name": "foo-name2",
                                "virtual-switch-uri": "foo-uri2"}
        mock_nic2.get_property = lambda key: {"device-number": "0002"}[key]

        mock_part = mock.Mock()
        mock_part.nics.create.side_effect = [mock_nic, mock_nic2]

        mock_get_part.return_value = mock_part
        dpmdriver = driver.DPMDriver(None)
        dpmdriver._conf = {"cpcsubset_name": "foo-name",
                           "physical_storage_adapter_mappings": "mapping"}

        vif = {"address": "aa:bb:cc:dd:ee:ff",
               "id": "foo-id",
               "type": "dpm_vswitch",
               "details": {"object_id": "oid"}}
        vif2 = {"address": "11:22:33:44:55:66",
                "id": "foo-id2",
                "type": "dpm_vswitch",
                "details": {"object_id": "oid2"}}
        network_info = [vif, vif2]
        dpmdriver.spawn(None, mock.Mock(), None, None, None, network_info,
                        flavor=mock.Mock())
        mock_launch.assert_called_once()
        self.assertEqual(2, mock_part.nics.create.call_count)
        call = mock.call({
            "boot-os-specific-parameters":
                "0001,0,aabbccddeeff;0002,0,112233445566;"})
        self.assertIn(call, mock_part.update_properties.mock_calls)

    def test_get_available_nodes(self):
        dpmdriver = driver.DPMDriver(None)
        dpmdriver._host = testhost.fakeHost()
        nodes = dpmdriver.get_available_nodes()
        self.assertEqual(nodes, ['S12subset'])

    def test_node_is_available(self):
        dpmdriver = driver.DPMDriver(None)
        dpmdriver._host = testhost.fakeHost()
        self.assertTrue(dpmdriver.node_is_available('S12subset'))

    @mock.patch.object(vm, "cpcsubset_partition_list",
                       return_value=fakezhmcclient.
                       get_fake_partition_list())
    def test_list_instances(self, mock_partition_list):
        dpmdriver = driver.DPMDriver(None)
        instancelist = []
        for partition in fakezhmcclient.get_fake_partition_list():
            instancelist.append(partition.get_property('name'))

        self.assertEqual(instancelist, dpmdriver.list_instances())

    @mock.patch.object(vm, "CONF")
    def test_get_info(self, mock_conf):
        mock_conf.host = "foo"

        mock_partition_instance_info = mock.Mock(vm.PartitionInstanceInfo)
        mock_partition_instance_info.return_value =\
            vm.PartitionInstanceInfo(getMockNovaInstanceForPartion(),
                                     fakezhmcclient.getFakeCPC())

        dpmdriver = driver.DPMDriver(None)
        dpmdriver._cpc = fakezhmcclient.getFakeCPC()
        partitionInfo = dpmdriver.get_info(getMockNovaInstanceForPartion())
        self.assertEqual(partitionInfo.mem, 512)
        self.assertEqual(partitionInfo.num_cpu, 1)

    @mock.patch.object(vm.PartitionInstance, 'destroy')
    def test_destroy(self, mock_destroy):
        dpmdriver = driver.DPMDriver(None)
        dpmdriver._cpc = fakezhmcclient.getFakeCPC()
        dpmdriver.destroy(mock.Mock, getMockNovaInstanceForPartion(),
                          mock.Mock)
        mock_destroy.assert_called_once()

    @mock.patch.object(vm.PartitionInstance, 'power_off_vm')
    def test_power_off(self, mock_power_off_vm):
        dpmdriver = driver.DPMDriver(None)
        dpmdriver._cpc = fakezhmcclient.getFakeCPC()
        dpmdriver.power_off(getMockNovaInstanceForPartion())
        mock_power_off_vm.assert_called_once()

    @mock.patch.object(vm.PartitionInstance, 'power_on_vm')
    def test_power_on(self, mock_power_on_vm):
        dpmdriver = driver.DPMDriver(None)
        dpmdriver._cpc = fakezhmcclient.getFakeCPC()
        dpmdriver.power_on(mock.Mock, getMockNovaInstanceForPartion(),
                           mock.Mock)
        mock_power_on_vm.assert_called_once()

    @mock.patch.object(vm.PartitionInstance, 'reboot_vm')
    def test_reboot(self, mock_reboot):
        dpmdriver = driver.DPMDriver(None)
        dpmdriver._cpc = fakezhmcclient.getFakeCPC()
        dpmdriver.reboot(mock.Mock, getMockNovaInstanceForPartion(), mock.Mock,
                         mock.Mock)
        mock_reboot.assert_called_once()
