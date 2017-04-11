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
from nova_dpm.virt.dpm import vm


class ValidPartitionNameTestCase(TestCase):

    def setUp(self):
        super(ValidPartitionNameTestCase, self).setUp()

    def test_is_valid_partition_name(self):
        self.flags(host='foo')
        name1 = 'OpenStack-foo-6511ee0f-0d64-4392-b9e0-cdbea10a17c3'
        self.assertTrue(vm.is_valid_partition_name(name1))

        self.flags(host='foo-bar')
        name2 = 'OpenStack-foo-bar-6511ee0f-0d64-4392-b9e0-cdbea10a17c3'
        self.assertTrue(vm.is_valid_partition_name(name2))

        self.flags(host='foo-bar')
        name3 = 'invalid_name'
        self.assertFalse(vm.is_valid_partition_name(name3))
