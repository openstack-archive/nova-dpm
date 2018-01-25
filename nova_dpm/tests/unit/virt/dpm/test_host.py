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

import json
import zhmcclient

from nova.test import TestCase
from nova_dpm.tests.unit.virt.dpm import test_data as utils
from nova_dpm.virt.dpm import host


class HostTestCase(TestCase):

    def setUp(self):
        super(HostTestCase, self).setUp()
        self.session = utils.create_session_1()
        client = zhmcclient.Client(self.session)
        self.cpc = client.cpcs.find(**{"name": "cpc_2"})
        self.flags(host=utils.HOST)
        self.flags(group="dpm", max_processors=3)
        self.flags(group="dpm", max_memory=2048)
        self.host = host.Host(self.cpc)

    def test_host_properties(self):

        host_properties = self.host.properties
        self.assertEqual(utils.HOST,
                         host_properties['hypervisor_hostname'])
        self.assertEqual('cpc_2', host_properties['cpc_name'])
        self.assertEqual(3, host_properties['vcpus'])
        self.assertEqual(2048, host_properties['memory_mb'])
        self.assertEqual(utils.MAX_PROC_USED, host_properties['vcpus_used'])
        self.assertEqual(utils.TOTAL_MEM_USED,
                         host_properties['memory_mb_used'])
        self.assertEqual(2013001, host_properties['hypervisor_version'])
        self.assertEqual('PRSM', host_properties['hypervisor_type'])
        cpu_info = host_properties['cpu_info']
        cpu_info_dict = json.loads(cpu_info)
        self.assertEqual('s390x', cpu_info_dict['arch'])
        self.assertEqual('IBM', cpu_info_dict['vendor'])

    def test_get_proc_used(self):
        proc_used = self.host._get_proc_used()
        self.assertEqual(utils.MAX_PROC_USED, proc_used)

    def test_mem_used(self):
        memory_used = self.host._get_mem_used()
        self.assertEqual(utils.TOTAL_MEM_USED, memory_used)

    def test_get_version_in_int(self):
        version = self.host._get_version_in_int()
        self.assertEqual(2013001, version)

    def test_initialize_crypto_adapters(self):
        cca_oid = "11111111-2222-3333-4444-aaaaaaaaaaaa"
        ep11_oid1 = "11111111-2222-3333-4444-bbbbbbbbbbb1"
        ep11_oid2 = "11111111-2222-3333-4444-bbbbbbbbbbb2"
        accel_oid = "11111111-2222-3333-4444-cccccccccccc"
        # OSD adapter should be ignored, as not of type crypto
        osd_oid = "11111111-2222-3333-4444-dddddddddddd"

        self.flags(physical_crypto_adapters=[cca_oid, ep11_oid1, ep11_oid2,
                                             accel_oid, osd_oid],
                   group="dpm")
        self.host.initialize_crypto_adapters()

        # accelerators
        self.assertEqual(1, len(self.host.cryptos["accelerator"]))
        self.assertEqual(
            accel_oid,
            self.host.cryptos["accelerator"][0].get_property("object-id"))

        # ep11
        self.assertEqual(2, len(self.host.cryptos["ep11-coprocessor"]))
        self.assertEqual(
            ep11_oid1,
            self.host.cryptos["ep11-coprocessor"][0].get_property("object-id"))
        self.assertEqual(
            ep11_oid2,
            self.host.cryptos["ep11-coprocessor"][1].get_property("object-id"))

        # cca
        self.assertEqual(1, len(self.host.cryptos["cca-coprocessor"]))
        self.assertEqual(
            cca_oid,
            self.host.cryptos["cca-coprocessor"][0].get_property("object-id"))

    def test_initialize_crypto_adapters_not_found(self):
        self.flags(
            physical_crypto_adapters=["00000000-0000-0000-0000-000000000000"],
            group="dpm")
        self.assertRaises(SystemExit, self.host.initialize_crypto_adapters)
