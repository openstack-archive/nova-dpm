# Copyright 2017 IBM Corp. All Rights Reserved.
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

from oslo_config import cfg

import nova_dpm.conf

from nova.test import TestCase


class TestConfigParameters(TestCase):

    def setUp(self):
        super(TestConfigParameters, self).setUp()
        self.CONF = nova_dpm.conf.CONF

    def test_max_memory_min_value(self):
        self.assertRaises(ValueError, self.CONF.set_override, "max_memory",
                          500, group="dpm")

    def test_physical_crypto_adapters_default(self):
        try:
            self.assertEqual([], self.CONF.dpm.physical_crypto_adapters)
        except cfg.NoSuchOptError as ex:
            self.fail("Option not registered. %s" % ex)

    def test_physical_crypto_adapters(self):
        oid_lc1 = "11111111-2222-3333-4444-aaaaaaaaaaaa"
        oid_lc2 = "11111111-2222-3333-4444-bbbbbbbbbbbb"
        cfg.CONF.set_override("physical_crypto_adapters",
                              "%s,%s" % (oid_lc1, oid_lc2),
                              "dpm")
        self.assertEqual([oid_lc1, oid_lc2],
                         self.CONF.dpm.physical_crypto_adapters)

    def test_physical_crypto_adapters_to_lower_case(self):
        oid_uc = "11111111-2222-3333-4444-AAAAAAAAAAAA"
        cfg.CONF.set_override("physical_crypto_adapters", oid_uc, "dpm")
        self.assertEqual(["11111111-2222-3333-4444-aaaaaaaaaaaa"],
                         self.CONF.dpm.physical_crypto_adapters)

    def test_physical_crypto_adapters_invalid(self):
        self.assertRaises(ValueError, cfg.CONF.set_override,
                          "physical_crypto_adapters", "no-objec-tid", "dpm")
