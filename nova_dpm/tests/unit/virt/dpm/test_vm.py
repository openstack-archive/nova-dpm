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

    def test_get_partition(self):
        partition_inst = vm.PartitionInstance(
            self.instance, self.cpc, self.flavor)
        partition_inst.create(partition_inst.properties())
        self.assertEqual(
            self.part_name,
            partition_inst.get_partition().get_property('name'))

    def test_attach_nic(self):
        vif = {
            "details":
                {"port_filter": False,
                 "object_id": "3ea09d2a-b18d-11e6-89a4-42f2e9ef1641"},
            "address": "fa:16:3e:e4:9a:98",
            "type": "dpm_vswitch",
            "id": "703da361-9d4d-4441-b99b-e081c3e9cfbb"}
        partition_inst = vm.PartitionInstance(
            self.instance, self.cpc, self.flavor)
        partition_inst.create(partition_inst.properties())
        nic_interface = partition_inst.attach_nic(vif)
        self.assertEqual(
            'OpenStack_Port_703da361-9d4d-4441-b99b-e081c3e9cfbb',
            nic_interface.properties['name'])

    def test_set_boot_os_specific_parameters(self):
        data = '1800,0,fa163ee49a98;'
        partition_inst = vm.PartitionInstance(
            self.instance, self.cpc, self.flavor)
        partition_inst.create(partition_inst.properties())
        partition_inst.set_boot_os_specific_parameters(data)
        self.assertEqual(
            data,
            partition_inst.get_partition().get_property(
                'boot-os-specific-parameters'))


class VmHbasTestCase(TestCase):

    def setUp(self):
        super(VmHbasTestCase, self).setUp()
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

        self.partition_inst = vm.PartitionInstance(
            self.instance, self.cpc, self.flavor)
        self.partition_inst.create(self.partition_inst.properties())

        adapter = self.cpc.adapters.find(**{'name': 'fcp_1'})
        self.adapter_object_id = adapter.get_property('object-id')
        self.port_element_id = adapter.ports.list()[0].get_property(
            'element-id')
        storage = self.adapter_object_id + ":" + self.port_element_id
        self.flags(group="dpm", physical_storage_adapter_mappings=[storage])

        self.partition_inst.attach_hbas()

    def test_attach_hbas(self):
        self.assertEqual(
            1,
            len(self.partition_inst.get_partition().hbas.list()))

    def test_get_adapter_port_mappings(self):
        adapter_port_map = self.partition_inst.get_adapter_port_mappings()
        adapter_port = adapter_port_map.get_adapter_port_mapping()[0]
        self.assertEqual(self.adapter_object_id, adapter_port['adapter_id'])
        self.assertEqual(self.port_element_id, str(adapter_port['port']))

    def test_get_hba_uri(self):
        self.assertEqual(
            self.partition_inst.get_partition().get_property(
                'object-uri') + '/hbas/1',
            self.partition_inst.get_hba_uris()[0])

    def test_get_boot_hba_uri(self):
        self.assertEqual(
            self.partition_inst.get_partition().get_property(
                'object-uri') + '/hbas/1',
            self.partition_inst.get_boot_hba_uri())
