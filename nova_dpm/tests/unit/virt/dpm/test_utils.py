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

import zhmcclient
import zhmcclient_mock

from nova.test import TestCase
from nova_dpm.virt.dpm import exceptions
from nova_dpm.virt.dpm import utils


class HostTestCase(TestCase):

    def setUp(self):
        super(HostTestCase, self).setUp()

        session = zhmcclient_mock.FakedSession(
            'fake-host', 'fake-hmc', '2.13.1', '1.8')

        session.hmc.cpcs.add({
            'name': 'cpc_1',
            'description': 'CPC #1',
            'dpm-enabled': True,
            'processor-count-ifl': 10,
            'storage-customer': 2048,
        })
        client = zhmcclient.Client(session)
        self.cpc = client.cpcs.find(**{"name": "cpc_1"})
        self.flags(host='foo')
        self.flags(group="dpm", max_processors=3)
        self.flags(group="dpm", max_memory=1024)

    def test_max_processor_correct(self):
        utils.validate_host_conf(self.cpc)

    def test_max_processor_exceded(self):
        self.flags(group="dpm", max_processors=11)
        self.assertRaises(
            exceptions.MaxProcessorExceededError,
            utils.validate_host_conf, self.cpc)

    def test_max_memory_correct(self):
        utils.validate_host_conf(self.cpc)

    def test_max_memory_exceded(self):
        self.flags(group="dpm", max_memory=4096)
        self.assertRaises(
            exceptions.MaxMemoryExceededError,
            utils.validate_host_conf, self.cpc)

    def test_dpm_enabled(self):
        utils.validate_host_conf(self.cpc)

    def test_dpm_enabled_false(self):

        session = zhmcclient_mock.FakedSession(
            'fake-host', 'fake-hmc', '2.13.1', '1.8')

        session.hmc.cpcs.add({
            'name': 'cpc_1',
            'description': 'CPC #1',
            'dpm-enabled': False,
            'processor-count-ifl': 10,
            'storage-customer': 2048,
        })
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(**{"name": "cpc_1"})
        self.flags(host='foo')
        self.flags(group="dpm", max_processors=3)
        self.flags(group="dpm", max_memory=1024)

        self.assertRaises(
            exceptions.CpcDpmModeNotEnabledException,
            utils.validate_host_conf, cpc)
