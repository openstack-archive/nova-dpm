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


class DPMVIF(object):
    def __init__(self, vif):
        # The vif dictionary
        self.vif = vif

    @property
    def port_id(self):
        return self.vif['id']

    @property
    def type(self):
        return self.vif['type']

    @property
    def mac(self):
        return self.vif['address']

    @property
    def details(self):
        return self.vif['details']

    @property
    def dpm_nic_object_id(self):
        return self.details['object_id']

    @property
    def vlan_id(self):
        """VLAN ID of VIF

        @:returns vlan-id or None
        """
        return self.details.get('vlan')
