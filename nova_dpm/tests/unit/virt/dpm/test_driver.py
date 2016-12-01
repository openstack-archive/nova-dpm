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
import testtools

from nova_dpm.tests.unit.virt.dpm import fakezhmcclient
from nova_dpm.virt.dpm import driver
from nova_dpm.virt.dpm import driver as dpm_driver


"""
cpcsubset unit testcase
"""

dpm_driver.zhmcclient = fakezhmcclient
CONF = nova_dpm.conf.CONF


class DPMdriverTestCase(testtools.TestCase):

    @mock.patch.object(driver.LOG, 'warning')
    @mock.patch.object(CONF, 'dpm')
    def test_host(self, mock_dpmconf, mock_warning):

        mock_dpmconf.hmc_username = "dummyuser"
        mock_dpmconf.hmc_password = "dummy"
        mock_dpmconf.hmc_host = "1.1.1.1"

        dummyvirtapi = None
        dpmdriver = driver.DPMDriver(dummyvirtapi)

        self.assertIsNotNone(dpmdriver)

        expected_arg = {'zhmc': '1.1.1.1', 'userid': 'dummyuser'}
        assertlogs = False
        for call in mock_warning.call_args_list:

            if (len(call) > 0):
                if (len(call[0]) > 1 and call[0][1] == expected_arg):
                    assertlogs = True

        self.assertTrue(assertlogs)
