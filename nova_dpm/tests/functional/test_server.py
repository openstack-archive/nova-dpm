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
import requests.packages.urllib3
import zhmcclient

from nova.test import TestCase
from nova_dpm.tests.unit.virt.dpm import test_utils as utils


class RealTimeServersTest(TestCase):

    def setUp(self):
        super(RealTimeServersTest, self).setUp()
        requests.packages.urllib3.disable_warnings()
        self.session = utils.create_session_1()
        self.client = zhmcclient.Client(self.session)
        self.cpc = self.client.cpcs.find(**{"name": "cpc_2"})
        self.flags(host=utils.HOST)
        self.flags(group="dpm", max_processors=3)
        self.flags(group="dpm", max_memory=2048)
        self.flags(group="dpm",
                   cpc_object_id=self.cpc.get_property('object-id'))

    def _setup_compute_service(self):
        self.flags(compute_driver='dpm.driver.DPMDriver')

    def test_success(self):
        with mock.patch(
                'dpm.driver.DPMDriver.client_proxy.get_client_for_sesion',
                return_value=self.client):
            self.compute = self.start_service('compute', host='test_compute0')
