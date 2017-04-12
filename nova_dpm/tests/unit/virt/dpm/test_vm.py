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


from nova.compute import power_state
from nova.objects import instance as instance_obj
from nova.test import TestCase
from nova_dpm.tests.unit.virt.dpm import test_utils as utils
from nova_dpm.virt.dpm import vm
import requests.packages.urllib3
import zhmcclient


class PartitionInstanceInfoTestCase(TestCase):

    def setUp(self):
        super(PartitionInstanceInfoTestCase, self).setUp()
        requests.packages.urllib3.disable_warnings()
        self.session = utils.create_session_1()
        self.client = zhmcclient.Client(self.session)
        self.cpc = self.client.cpcs.find(**{"name": "cpc_2"})
        self.flags(host="foo")
        self.instance = instance_obj.Instance()
        self.instance.uuid = '6511ee0f-0d64-4392-b9e0-aaaaaaaaaaaa'
        self.part_name = "OpenStack-foo-" + self.instance.uuid
        self.part_description = 'OpenStack CPCSubset=foo'
        self.state = 'aCTIVE'
        self.create_partition_properties = {
            'name': self.part_name,
            'description': self.part_description,
            'initial-memory': 1,
            'status': self.state,
            'maximum-memory': 512,
            'ifl-processors': 2
        }

        # Create partition in a cpc not from openstack
        # and used same uuid of instance to create
        # vm.PartitionInstanceInfo class instance to get the information
        # of the status,memory etc..,

        self.partition = self.cpc.partitions.create(
            self.create_partition_properties)
        self.instance_partition = vm.PartitionInstanceInfo(
            self.instance, self.cpc)

    def test_state(self):
        self.assertEqual(power_state.RUNNING, self.instance_partition.state)

    def test_mem(self):
        self.assertEqual(1, self.instance_partition.mem)

    def test_max_mem(self):
        self.assertEqual(512, self.instance_partition.max_mem)

    def test_num_cpu(self):
        self.assertEqual(2, self.instance_partition.num_cpu)

    def test_cpu_time(self):
        pass

