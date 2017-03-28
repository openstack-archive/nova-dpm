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

import fixtures
import mock
import requests.packages.urllib3
import zhmcclient

from nova.tests.functional.test_servers import ServersTestBase
from nova_dpm.tests.functional import fake_cinder
from nova_dpm.tests.functional import fake_client_proxy
from nova_dpm.tests.unit.virt.dpm import test_utils as utils


class ServersTest(ServersTestBase):

    def setUp(self):
        super(ServersTest, self).setUp()
        self.useFixture(fixtures.MonkeyPatch('nova.api.openstack.compute.volumes.cinder', fake_cinder))
        self.useFixture(fixtures.MonkeyPatch('nova_dpm.virt.dpm.driver.client_proxy',fake_client_proxy))

        requests.packages.urllib3.disable_warnings()
        self.session = utils.create_session_1()
        self.client = zhmcclient.Client(self.session)
        self.cpc = self.client.cpcs.find(**{"name": "cpc_2"})
        self.flags(compute_driver='dpm.driver.DPMDriver')
        self.flags(host=utils.HOST)
        self.flags(group="dpm", max_processors=3)
        self.flags(group="dpm", max_memory=2048)
        self.flags(group="dpm",
                   cpc_object_id=self.cpc.get_property('object-id'))
        self.flags(group="cinder", os_region_name="RegionOne")

    def _setup_compute_service(self):
        self.flags(compute_driver='dpm.driver.DPMDriver')

    def test_success(self):

        self.compute = self.start_service('compute', host='foo')
        volumes = self.api.get_volumes()
        print volumes
