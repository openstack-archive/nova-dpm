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

import nova_dpm.conf

from nova.test import TestCase

CONF = nova_dpm.conf.CONF


class TestConfigParameters(TestCase):
    def test_default_value(self):
        self.max_instance = CONF.dpm.max_instances
        self.assertEqual(-1, self.max_instance)

    def test_min_value(self):
        self.assertGreaterEqual(CONF.dpm.max_instances, -1)
