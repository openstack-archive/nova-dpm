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
import nova
import requests.packages.urllib3
import time
import zhmcclient

from nova.tests.functional.test_servers import ServersTestBase
from nova_dpm.tests.functional import fake_cinder
from nova_dpm.tests.functional import fake_client_proxy
from nova_dpm.tests.unit.virt.dpm import test_utils as utils
from nova_dpm.virt.dpm import vm


class ServersTest(ServersTestBase):

    def setUp(self):
        super(ServersTest, self).setUp()
        self.stub_out(
            "nova.volume.cinder.API.get_all",
            fake_cinder.stub_volume_get_all)
        self.stub_out(
            "nova.volume.cinder.API.get",
            fake_cinder.stub_volume_get)
        self.stub_out(
            "nova.volume.cinder.API.reserve_volume",
            mock.Mock())
        self.stub_out(
            "nova.compute.manager.ComputeManager._prep_block_device",
            fake_cinder.BLOCK_DEVICE_INFO)
        self.useFixture(fixtures.MonkeyPatch(
            'nova_dpm.virt.dpm.driver.client_proxy',
            fake_client_proxy))

        requests.packages.urllib3.disable_warnings()
        self.session = fake_client_proxy.fake_session_functional_test()
        self.client = zhmcclient.Client(self.session)
        self.cpc = self.client.cpcs.find(**{"name": "cpc"})
        adaptar_object_id = self.cpc.adapters.list()[0].get_property('object-id')
        port_id = self.cpc.adapters.list()[0].ports.list()[0].get_property('element-id')
        self.flags(compute_driver='dpm.driver.DPMDriver')
        self.flags(host=utils.HOST)
        self.flags(group="dpm", max_processors=3)
        self.flags(group="dpm", max_memory=2048)
        self.flags(group="dpm",
                   cpc_object_id=self.cpc.get_property('object-id'))
        self.flags(group="dpm", physical_storage_adapter_mappings=adaptar_object_id+":"+port_id)

    def _setup_compute_service(self):
        self.flags(compute_driver='dpm.driver.DPMDriver')

    def _wait_for_state_change(self, server, from_status):
        for i in range(0, 50):
            server = self.api.get_server(server['id'])
            if server['status'] != from_status:
                break
            time.sleep(.1)

        return server

    @mock.patch.object(nova.compute.manager.ComputeManager,
                       '_prep_block_device', return_value=fake_cinder.BLOCK_DEVICE_INFO)
    @mock.patch.object(vm.PartitionInstance, 'set_boot_os_specific_parameters')
    def test_success(self, mock_os_boot, mock_bdm):

        self.compute = self.start_service('compute', host='foo')
        self.api.post_flavor(fake_cinder.FLAVOR)
        created_server = self.api.post_server(fake_cinder.SERVER)
        self.assertTrue(created_server['id'])
        created_server_id = created_server['id']
        found_server = self.api.get_server(created_server_id)
        self.assertEqual(created_server_id, found_server['id'])
        found_server = self._wait_for_state_change(found_server, 'BUILD')

        # self.assertEqual('ERROR', found_server['status'])
        print found_server
