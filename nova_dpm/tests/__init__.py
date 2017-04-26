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

from nova.test import TestCase
from oslo_config import cfg


class TestCase(TestCase):

    def setUp(self):
        cfg.CONF.set_override("max_processors", 3, enforce_type=True,
                              group="dpm")
        cfg.CONF.set_override("max_instances", 3, enforce_type=True,
                              group="dpm")
        cfg.CONF.set_override("max_memory", 2048, enforce_type=True,
                              group="dpm")
        storage = "48602646-b18d-11e6-9c12-42f2e9ef1641:0"
        cfg.CONF.set_override("physical_storage_adapter_mappings", [storage],
                              group="dpm", enforce_type=True)
        super(TestCase, self).setUp()
