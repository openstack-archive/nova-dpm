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
from nova_dpm.tests.unit.virt.dpm import fakezhmcclient
from nova_dpm.tests.unit.virt.dpm import test_host as testhost
from nova_dpm.virt.dpm import client_proxy
from nova_dpm.virt.dpm import driver
from nova_dpm.virt.dpm import host as dpmHost
from nova_dpm.virt.dpm import vm
from nova_dpm.virt.dpm.volume import fibrechannel


"""
cpcsubset unit testcase
"""

CONF = nova_dpm.conf.CONF


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

    def test_extract_fc_boot_props(self):
        partition_wwpn = 'C05076FFEB8000D6'
        block_device_mapping = [{
            'connection_info': {
                'driver_volume_type': 'fibre_channel',
                'connector': {
                    'wwpns': [partition_wwpn],
                    'host': '3cfb165c-0df3-4d80-87b2-4c353e61318f'},
                'data': {
                    'initiator_target_map': {
                        partition_wwpn: [
                            '500507680B214AC1',
                            '500507680B244AC0']},
                    'target_discovered': False,
                    'target_lun': 0}}}]

        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)
        target_wwpn, lun = dpmdriver._extract_fc_boot_props(
            block_device_mapping, partition_wwpn)
        self.assertEqual(target_wwpn, '500507680B214AC1')
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
