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

import requests.packages.urllib3
import zhmcclient

from nova.objects import flavor as flavor_obj
from nova.objects import instance as instance_obj
from nova.test import TestCase
from nova_dpm.tests.unit.virt.dpm import test_utils as utils
from nova_dpm.virt.dpm import vm


class VmCreateTestCase(TestCase):
    def setUp(self):
        super(VmCreateTestCase, self).setUp()
        requests.packages.urllib3.disable_warnings()
        self.session = utils.create_session_1()
        self.client = zhmcclient.Client(self.session)
        self.cpc = self.client.cpcs.find(**{"name": "cpc_2"})
        self.flags(host="foo")
        self.instance = instance_obj.Instance()
        self.instance.uuid = '6511ee0f-0d64-4392-b9e0-aaaaaaaaaaaa'
        self.flavor = flavor_obj.Flavor()
        self.flavor.vcpus = 1
        self.flavor.memory_mb = 512
        self.part_name = "OpenStack-foo-" + self.instance.uuid
        self.part_description = 'OpenStack CPCSubset=foo'

    def test_properties(self):
        partition_inst = vm.PartitionInstance(
            self.instance, self.cpc, self.flavor)
        properties = partition_inst.properties()
        self.assertEqual(self.part_name, properties['name'])
        self.assertEqual(self.part_description, properties['description'])
        self.assertEqual(1, properties['ifl-processors'])
        self.assertEqual(512, properties['initial-memory'])
        self.assertEqual(512, properties['maximum-memory'])

    def test_partition_create(self):
        partition_inst = vm.PartitionInstance(
            self.instance, self.cpc, self.flavor)
        partition_inst.create(partition_inst.properties())
        partition = self.cpc.partitions.find(**{"name": self.part_name})
        self.assertEqual(self.part_name, partition.get_property('name'))

    def test_partition_name(self):
        partition_inst = vm.PartitionInstance(
            self.instance, self.cpc, self.flavor)
        self.assertEqual(
            self.part_name, partition_inst.partition_name)

    def test_partition_description(self):
        partition_inst = vm.PartitionInstance(
            self.instance, self.cpc, self.flavor)
        self.assertEqual(
            self.part_description,
            partition_inst.partition_description)
