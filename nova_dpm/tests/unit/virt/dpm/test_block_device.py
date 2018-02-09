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

from nova_dpm.virt.dpm.block_device import BlockDevice
from nova_dpm.virt.dpm import exceptions

PARTITION_WWPN = 'CCCCCCCCCCCCCCCC'
LUN = 0
BLOCK_DEVICE = {
    'connection_info': {
        'driver_volume_type': 'fibre_channel',
        'data': {
            'initiator_target_map': {
                PARTITION_WWPN: [
                    'AAAAAAAAAAAAAAAA',
                    'BBBBBBBBBBBBBBBB']},
            'target_discovered': False,
            'target_lun': LUN}}}


class BlockDeviceTest(TestCase):

    def test_volume_type_unsupported(self):
        bd = {'connection_info': {'driver_volume_type': 'fake_vol_type'}}
        try:
            BlockDevice(bd)
        except exceptions.UnsupportedVolumeTypeException:
            pass
        else:
            self.fail("UnsupportedVolumeTypeException not raised.")

    def test_volume_type_fc_supported(self):
        bd = {'connection_info': {'driver_volume_type': 'fibre_channel'}}
        bd_obj = BlockDevice(bd)
        self.assertIsNotNone(bd_obj)

    def test_get_target_wwpn(self):
        bd = BlockDevice(BLOCK_DEVICE)
        self.flags(group="dpm", target_wwpn_ignore_list=["AAAAAAAAAAAAAAAA"])
        self.assertEqual("BBBBBBBBBBBBBBBB",
                         bd.get_target_wwpn(PARTITION_WWPN))

    def test_lun(self):
        bd = BlockDevice(BLOCK_DEVICE)
        self.assertEqual(str(LUN), bd.lun)
