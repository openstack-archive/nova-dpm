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
from nova.test import TestCase
from nova_dpm.tests.unit.virt.dpm import test_utils as utils
from nova_dpm.virt.dpm import driver

import mock
import requests.packages.urllib3
import zhmcclient


class DPMdriverTestCase(TestCase):

    def setUp(self):
        super(DPMdriverTestCase, self).setUp()
        requests.packages.urllib3.disable_warnings()
        self.session = utils.create_session_1()
        self.client = zhmcclient.Client(self.session)

        self.dpmdriver = driver.DPMDriver(None)
        self.dpmdriver._client = self.client

    @mock.patch.object(driver.LOG, 'debug')
    def test_init_host(self, mock_warning):
        self.flags(group="dpm", cpc_object_id="2")

        self.dpmdriver.init_host(None)
        host_properties = self.dpmdriver.get_available_resource(None)
        self.assertEqual(host_properties['cpc_name'], 'cpc_2')
