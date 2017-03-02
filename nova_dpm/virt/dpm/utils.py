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

from nova import exception
from nova.i18n import _
from oslo_log import log as logging

LOG = logging.getLogger(__name__)
CONF = nova_dpm.conf.CONF


def valide_host_conf(cpc):
    LOG.debug('valide_host_conf')
    if not cpc.dpm_enabled:
        # TODO(preethipy): Exception infrastructure to be finalized
        raise Exception("Host not in DPM mode")

    if (CONF.dpm.max_processors > cpc.get_property('processor-count-ifl')):
        # TODO(preethipy): Exception infrastructure to be finalized
        errormsg = (_("max_processors %(config_proc)s configured for "
                      "CpcSubset %(cpcsubset_name)s is greater than the "
                      "available amount of processors %(max_proc)s on "
                      "CPC object-id %(cpcid)s and CPC name %(cpcname)s")
                    % {'config_proc': CONF.dpm.max_processors,
                       'cpcsubset_name': CONF.host,
                       'max_proc': cpc.get_property('processor-count-ifl'),
                       'cpcid': CONF.dpm.cpc_object_id,
                       'cpcname': cpc.get_property('name')})
        raise exception.ValidationError(errormsg)

    if (CONF.dpm.max_memory > cpc.get_property('storage-customer')):
        # TODO(preethipy): Exception infrastructure to be finalized
        errormsg = (_("max_memory_mb %(config_mem)s configured for "
                      "CpcSubset %(cpcsubset_name)s is greater than the "
                      "available amount of memory %(max_mem)s on CPC "
                      "object-id %(cpcid)s and CPC name %(cpcname)s")
                    % {'config_mem': CONF.dpm.max_processors,
                       'cpcsubset_name': CONF.host,
                       'max_mem': cpc.get_property('processor-count-ifl'),
                       'cpcid': CONF.dpm.cpc_object_id,
                       'cpcname': cpc.get_property('name')})
        raise exception.ValidationError(errormsg)


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
