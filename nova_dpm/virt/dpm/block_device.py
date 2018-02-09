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

from nova_dpm import conf
from nova_dpm.virt.dpm import exceptions

CONF = conf.CONF


class BlockDevice(object):
    def __init__(self, block_device):
        self.bd = block_device
        self._validate_volume_type()

    def _validate_volume_type(self):
        vol_type = self.bd['connection_info']['driver_volume_type']
        if vol_type != 'fibre_channel':
            raise exceptions.UnsupportedVolumeTypeException(
                vol_type=vol_type)

    @property
    def host_wwpns(self):
        return (
            self.bd['connection_info']['data']['initiator_target_map'].keys()
        )

    def get_target_wwpn(self, partition_wwpn):
        if partition_wwpn not in self.host_wwpns:
            raise Exception('Partition WWPN not found from cinder')

        bd_target_wwpns = (
            self.bd['connection_info']['data']['initiator_target_map']
            [partition_wwpn])

        # Some storage systems return a complete list of target WWPNs on
        # cinders request. Only some of them might be available in our FC
        # network. Therefore we need to filter out the invalid ones. The user
        # defines the invalid ones via a config setting.
        valid_target_wwpns = [
            wwpn for wwpn in bd_target_wwpns
            if wwpn not in CONF.dpm.target_wwpn_ignore_list]

        # target_wwpns is a list of wwpns which will be accessible
        # from host wwpn. So we can use any of the target wwpn in the
        # list.
        target_wwpn = (valid_target_wwpns[0]
                       if len(valid_target_wwpns) > 0 else '')
        return target_wwpn

    @property
    def lun(self):
        return str(self.bd['connection_info']['data']['target_lun'])
