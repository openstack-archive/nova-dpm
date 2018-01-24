# Copyright 2018 IBM Corp. All Rights Reserved.
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

from nova_dpm.virt.dpm.vif import DPMVIF

VIF_DICT = {
    "details":
        {"port_filter": False,
         "object_id": "3ea09d2a-b18d-11e6-89a4-42f2e9ef1641",
         "vlan": 1},
    "address": "fa:16:3e:e4:9a:98",
    "type": "dpm_vswitch",
    "id": "703da361-9d4d-4441-b99b-e081c3e9cfbb"}


class DPMVIFTestCase(TestCase):

    def setUp(self):
        super(DPMVIFTestCase, self).setUp()
        self.vif_obj = DPMVIF(VIF_DICT)

    def test_get_port_id(self):
        self.assertEqual('703da361-9d4d-4441-b99b-e081c3e9cfbb',
                         self.vif_obj.port_id)

    def test_get_type(self):
        self.assertEqual('dpm_vswitch', self.vif_obj.type)

    def test_get_mac(self):
        self.assertEqual('fa:16:3e:e4:9a:98', self.vif_obj. mac)

    def test_get_details(self):
        details = {"port_filter": False,
                   "object_id": "3ea09d2a-b18d-11e6-89a4-42f2e9ef1641",
                   "vlan": 1}
        self.assertEqual(details, self.vif_obj.details)

    def test_get_dpm_nic_object_id(self):
        self.assertEqual('3ea09d2a-b18d-11e6-89a4-42f2e9ef1641',
                         self.vif_obj.dpm_nic_object_id)

    def test_get_vlan_id(self):
        self.assertEqual(1, self.vif_obj.vlan_id)

    def test_get_vlan_id_none(self):
        vif_obj = DPMVIF({"details": {}})
        self.assertIsNone(vif_obj.vlan_id)
