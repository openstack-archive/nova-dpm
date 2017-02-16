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
from nova_dpm.tests.unit.virt.dpm import test_utils as utils
from nova_dpm.virt.dpm import driver
from nova_dpm.virt.dpm import vm
from nova_dpm.virt.dpm.volume import fibrechannel


import mock
import requests.packages.urllib3
import zhmcclient

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


class DPMdriverInitHostTestCase(TestCase):

    def setUp(self):
        super(DPMdriverInitHostTestCase, self).setUp()
        requests.packages.urllib3.disable_warnings()
        self.session = utils.create_session_1()
        self.client = zhmcclient.Client(self.session)
        self.dpmdriver = driver.DPMDriver(None)
        self.dpmdriver._client = self.client

        self.flags(group="dpm", cpc_object_id="2")
        self.flags(group="dpm", max_processors=1)
        self.flags(group="dpm", max_memory=512)
        self.dpmdriver.init_host(None)

    @mock.patch.object(driver.LOG, 'debug')
    def test_init_host(self, mock_warning):
        host_properties = self.dpmdriver.get_available_resource(None)
        self.assertEqual(host_properties['cpc_name'], 'cpc_2')

    @mock.patch.object(driver.LOG, 'debug')
    def test_invalid_mem_config(self, mock_warning):
        self.flags(group="dpm", max_memory=2000)

        self.assertRaises(exception.ValidationError,
                          self.dpmdriver.init_host,
                          None)

    @mock.patch.object(driver.LOG, 'debug')
    def test_invalid_proc_config(self, mock_warning):
        self.flags(group="dpm", max_processors=50)

        self.assertRaises(exception.ValidationError,
                          self.dpmdriver.init_host,
                          None)

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(vm.PartitionInstance,
                       'get_partition_wwpns', return_value=[PARTITION_WWPN])
    @mock.patch.object(basedriver, 'block_device_info_get_mapping',
                       return_value=BLOCK_DEVICE)
    def test_get_fc_boot_props(self, mock_block_device,
                               mock_get_partition_wwpns,
                               mock_get_partition):

        inst = vm.PartitionInstance(mock.Mock(), mock.Mock())
        target_wwpn, lun = self.dpmdriver.get_fc_boot_props(
            mock.Mock(), inst)
        self.assertEqual(target_wwpn, '500507680B214AC1')
        self.assertEqual(lun, '0')

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(vm.PartitionInstance,
                       'get_partition_wwpns', return_value=[PARTITION_WWPN])
    @mock.patch.object(basedriver, 'block_device_info_get_mapping',
                       return_value=BLOCK_DEVICE)
    def test_get_fc_boot_props_ignore_list(self, mock_block_device,
                                           mock_get_partition_wwpns,
                                           mock_get_partition):
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
    def test_prep_for_spawn(self, mock_properties,
                            mock_partition, mock_attac_hbas,
                            mock_create, mock_context, mock_flavor):
        self.dpmdriver._conf = mock.Mock()
        self.dpmdriver.prep_for_spawn(mock.Mock, mock.Mock())
        mock_create.assert_called_once()
        mock_attac_hbas.assert_called_once()

    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    def test_get_volume_connector(self, mock_get_partition):
        self.dpmdriver.get_volume_connector(mock.Mock())


class DPMdriverVolumeTestCase(TestCase):

    def setUp(self):
        super(DPMdriverVolumeTestCase, self).setUp()
        self.dpmdriver = driver.DPMDriver(None)

    def test_get_volume_drivers(self):

        driver_reg = self.dpmdriver._get_volume_drivers()
        self.assertTrue(isinstance(driver_reg['fibre_channel'],
                                   fibrechannel.DpmFibreChannelVolumeDriver))

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
