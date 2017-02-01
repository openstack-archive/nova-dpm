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
