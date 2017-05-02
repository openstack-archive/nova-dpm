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

import nova_dpm.conf

from nova_dpm.virt.dpm import exceptions
from oslo_log import log as logging

LOG = logging.getLogger(__name__)
CONF = nova_dpm.conf.CONF


def validate_host_conf(cpc):
    LOG.debug('validate_host_conf')
    if not cpc.dpm_enabled:
        raise exceptions.CpcDpmModeNotEnabledException(
            cpc_name=cpc.get_property('name'))

    if (CONF.dpm.max_processors > cpc.get_property('processor-count-ifl')):
        raise exceptions.MaxProcessorExceededError(
            config_proc=CONF.dpm.max_processors,
            cpcsubset_name=CONF.host,
            max_proc=cpc.get_property('processor-count-ifl'),
            cpcid=CONF.dpm.cpc_object_id,
            cpcname=cpc.get_property('name'))

    if (CONF.dpm.max_memory > cpc.get_property('storage-customer')):
        raise exceptions.MaxMemoryExceededError(
            config_mem=CONF.dpm.max_memory,
            cpcsubset_name=CONF.host,
            max_mem=cpc.get_property('storage-customer'),
            cpcid=CONF.dpm.cpc_object_id,
            cpcname=cpc.get_property('name'))


class PartitionState(object):

    COMMUNICATION_NOT_ACTIVE = 'communications-not-active'
    DEGRADED = 'degraded'
    PAUSED = 'paused'
    RESERVATION_ERROR = 'reservation-error'
    RUNNING = 'active'
    SHUTTING_DOWN = 'stopping'
    STARTING = 'starting'
    STOPPED = 'stopped'
    TERMINATED = 'terminated"'
    UNKNOWN = 'status-check'
