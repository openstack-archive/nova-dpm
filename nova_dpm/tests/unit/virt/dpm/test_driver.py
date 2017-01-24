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
from nova_dpm.virt.dpm import exceptions
from nova_dpm.virt.dpm import host as dpmHost
from nova_dpm.virt.dpm import vm

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


class DPMPartitionSpawnTestCase(TestCase):
    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(vm.PartitionInstance, 'create')
    @mock.patch.object(vm.PartitionInstance, 'properties')
    def test_spawn_max_nics(self, mock_prop, mock_create, mock_get_part):
        dpmdriver = driver.DPMDriver(None)
        network_info = [x for x in range(0, 13)]
        self.assertRaises(exceptions.MaxAmountOfInstancePortsExceededError,
                          dpmdriver.spawn, None, None, None, None, None,
                          network_info, flavor=mock.Mock())

    @mock.patch.object(vm.PartitionInstance, 'launch')
    @mock.patch.object(vm.PartitionInstance, 'attachHba')
    @mock.patch.object(vm.PartitionInstance, 'get_partition')
    @mock.patch.object(vm.PartitionInstance, 'create')
    @mock.patch.object(vm.PartitionInstance, 'properties')
    def test_spawn_attach_nic(self, mock_prop, mock_create, mock_get_part,
                              mock_attachHba, mock_launch):
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

        mock_part.get_property =\
            lambda key: {"boot-os-specific-parameters": "boot-data"}[key]

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
        mock_create.assert_called_once()
        self.assertEqual(2, mock_part.nics.create.call_count)
        mock_part.update_properties.assert_called_once_with(**{
            "boot-os-specific-parameters":
                "boot-data0001,0,aabbccddeeff;0002,0,112233445566;"})
