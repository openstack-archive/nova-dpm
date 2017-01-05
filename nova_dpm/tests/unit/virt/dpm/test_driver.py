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

from nova import exception
from nova.test import TestCase
from nova_dpm.tests.unit.virt.dpm import fakezhmcclient
from nova_dpm.tests.unit.virt.dpm import test_host as testhost
from nova_dpm.virt.dpm import client_proxy
from nova_dpm.virt.dpm import driver
from nova_dpm.virt.dpm import host as dpmHost
from nova_dpm.virt.dpm.volume import fibrechannel


"""
cpcsubset unit testcase
"""

CONF = nova_dpm.conf.CONF


class mockData(object):
    def __init__(self):
        return

    def populateMockConf(self, mockconf):
        mockconf.hmc_username = "dummyuser"
        mockconf.hmc_password = "dummy"
        mockconf.hmc = "1.1.1.1"
        mockconf.host = "dummysubset"
        mockconf.cpc_uuid = "00000000-aaaa-bbbb-cccc-abcdabcdabcd"
        mockconf.max_processors = 5
        mockconf.max_memory = 50
        mockconf.max_instances = 10
        return mockconf


class DPMdriverTestCase(TestCase):

    def setUp(self):
        super(DPMdriverTestCase, self).setUp()
        client_proxy.zhmcclient = fakezhmcclient

    @mock.patch.object(driver.LOG, 'debug')
    @mock.patch.object(CONF, 'dpm')
    def test_host(self, mockdpmconf, mock_warning):
        mockdpmconf = mockData().populateMockConf(mockdpmconf)

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
    @mock.patch.object(CONF, 'dpm')
    @mock.patch.object(dpmHost, 'Host', return_value=testhost.fakeHost())
    def test_init_host(self, mockhost, mockdpmconf, mock_warning):
        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        mockdpmconf = mockData().populateMockConf(mockdpmconf)

        dpmdriver.init_host(None)
        host_properties = dpmdriver.get_available_resource(None)

        self.assertEqual(host_properties['hypervisor_hostname'],
                         'S12subset')

    @mock.patch.object(driver.LOG, 'debug')
    @mock.patch.object(CONF, 'dpm')
    def test_invalid_mem_config(self, mockdpmconf, mock_warning):
        mock_dpmconf = mockData().populateMockConf(mockdpmconf)

        mock_dpmconf.max_memory = 1000

        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        self.assertRaises(exception.ValidationError,
                          dpmdriver.init_host,
                          None)

    @mock.patch.object(driver.LOG, 'debug')
    @mock.patch.object(CONF, 'dpm')
    def test_invalid_proc_config(self, mockdpmconf, mock_warning):
        mock_dpmconf = mockData().populateMockConf(mockdpmconf)

        mock_dpmconf.max_processors = 50

        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        self.assertRaises(exception.ValidationError,
                          dpmdriver.init_host,
                          None)

    @mock.patch.object(driver.LOG, 'debug')
    def test_get_volume_drivers(self, mock_debug):
        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)
        driver_reg = dpmdriver._get_volume_drivers()
        self.assertTrue(isinstance(driver_reg['fibre_channel'],
                                   fibrechannel.DpmFibreChannelVolumeDriver))

    @mock.patch.object(driver.LOG, 'debug')
    @mock.patch.object(fibrechannel.LOG, 'debug')
    def test_attach_volume(self, mock_debug_fibrechannel, mock_debug_driver):
        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        connection_info = {'driver_volume_type': 'fibre_channel'}

        dpmdriver.attach_volume(None, connection_info, None, None)
        assertlogs = False

        for call in mock_debug_fibrechannel.call_args_list:
            if("Attached FC volume" in call[0][0]):
                assertlogs = True
        self.assertTrue(assertlogs)

    @mock.patch.object(driver.LOG, 'debug')
    @mock.patch.object(fibrechannel.LOG, 'debug')
    def test_detach_volume(self, mock_debug_fibrechannel, mock_debug_driver):
        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        connection_info = {'driver_volume_type': 'fibre_channel'}

        dpmdriver.detach_volume(connection_info, None, None)
        assertlogs = False

        for call in mock_debug_fibrechannel.call_args_list:
            if ("Disconnected FC Volume" in call[0][0]):
                assertlogs = True
        self.assertTrue(assertlogs)

    @mock.patch.object(driver.LOG, 'debug')
    @mock.patch.object(fibrechannel.LOG, 'debug')
    def test_attach_volume_Exception(self, mock_debug_fibrechannel,
                                     mock_debug_driver):
        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        connection_info = {'driver_volume_type': 'Dummy_channel'}

        self.assertRaises(exception.VolumeDriverNotFound,
                          dpmdriver.attach_volume, None,
                          connection_info, None, None)

    @mock.patch.object(driver.LOG, 'debug')
    @mock.patch.object(fibrechannel.LOG, 'debug')
    def test_detach_volume_Exception(self, mock_debug_fibrechannel,
                                     mock_debug_driver):
        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        connection_info = {'driver_volume_type': 'Dummy_channel'}

        self.assertRaises(exception.VolumeDriverNotFound,
                          dpmdriver.detach_volume,
                          connection_info, None, None)
