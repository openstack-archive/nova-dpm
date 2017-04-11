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
        # All name should be in this format
        # OpenStack-hostname-[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}
        # where hostname is basically host of 'self.flags(host='foo').
        self.flags(host='foo')
        name1 = 'OpenStack-foo-6511ee0f-0d64-4392-b9e0-cdbea10a17c3'
        self.assertTrue(vm.is_valid_partition_name(name1))

        self.flags(host='foo-bar')
        name2 = 'OpenStack-foo-bar-6511ee0f-0d64-4392-b9e0-cdbea10a17c3'
        self.assertTrue(vm.is_valid_partition_name(name2))

        self.flags(host='foo-bar')
        name3 = 'invalid_name'
        self.assertFalse(vm.is_valid_partition_name(name3))

        self.flags(host='foo')
        name4 = 'fooOpenStack-foo-6511ee0f-0d64-4392-b9e0-cdbea10a17c3'
        self.assertFalse(vm.is_valid_partition_name(name4))

        self.flags(host='foo')
        # Name should be in this format
        # OpenStack-hostname-[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}
        #  but name5 is in
        # OpenStack-hostname-[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{13}
        # See at last instead of 12 character it is 13 character.
        name5 = 'OpenStack-foo-6511ee0f-0d64-4392-b9e0-cdbea10a17c31'
        self.assertFalse(vm.is_valid_partition_name(name5))
