# Copyright 2011 OpenStack Foundation
# (c) Copyright 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
#
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

"""Volume drivers for libvirt."""

from oslo_log import log as logging

import nova.conf

LOG = logging.getLogger(__name__)

CONF = nova.conf.CONF

SHOULD_LOG_DISCARD_WARNING = True


class DpmBaseVolumeDriver(object):
    """Base class for volume drivers."""
    def __init__(self, connection, is_block_dev):
        self.connection = connection
        self.is_block_dev = is_block_dev

    def connect_volume(self, connection_info, disk_info):
        """Connect the volume."""
        pass

    def disconnect_volume(self, connection_info, disk_dev):
        """Disconnect the volume."""
        pass


class DpmVolumeDriver(DpmBaseVolumeDriver):
    """Class for volumes backed by local file."""
    def __init__(self, connection):
        super(DpmVolumeDriver,
              self).__init__(connection, is_block_dev=True)


class DpmFakeVolumeDriver(DpmBaseVolumeDriver):
    """Driver to attach fake volumes to libvirt."""
    def __init__(self, connection):
        super(DpmFakeVolumeDriver,
              self).__init__(connection, is_block_dev=True)
