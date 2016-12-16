#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_log import log as logging

import nova.conf
from nova_dpm.virt.dpm.volume import volume as dpm_volume

CONF = nova.conf.CONF

LOG = logging.getLogger(__name__)


class DpmFibreChannelVolumeDriver(dpm_volume.DpmBaseVolumeDriver):
    """Driver to attach Fibre Channel Network volumes to zSystems DPM."""

    def __init__(self, connection):
        super(DpmFibreChannelVolumeDriver,
              self).__init__(connection, is_block_dev=False)

        LOG.debug("Volume Driver for DPM initialized")

    def connect_volume(self, connection_info, disk_info):
        """Attach the volume to instance_name."""

        LOG.debug("No need to do anything at the moment to attach FC Volume")
        LOG.debug("Attached FC volume %s", disk_info)

    def disconnect_volume(self, connection_info, disk_dev):
        """Detach the volume from instance_name."""

        LOG.debug("No need to do anything to detach FC Volume")
        LOG.debug("Disconnected FC Volume %s", disk_dev)
