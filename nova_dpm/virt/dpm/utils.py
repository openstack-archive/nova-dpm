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

from nova.i18n import _
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


def valide_host_conf(conf, cpc):
    LOG.debug('valide_host_conf')
    if (cpc.dpm_enabled):
        cpc.pull_full_properties()
    else:
        # TODO(preethipy): Exception infrastructure to be finalized
        raise Exception("Host not in DPM mode")

    if (conf['max_processors'] > cpc.properties['processor-count-ifl']):
        # TODO(preethipy): Exception infrastructure to be finalized
        errormsg = (_("max_processors %(config_proc)d configured for "
                      "CpcSubset %(host)s is greater than the "
                      "available amount of processors %(max_proc)d on "
                      "CPC uuid %(cpcuuid)s and CPC name %(cpcname)s")
                    % {'config_proc': conf['max_processors'],
                       'host': conf['host'],
                       'max_proc': cpc.properties['processor-count-ifl'],
                       'cpcuuid': conf['cpc_uuid'],
                       'cpcname': cpc.properties['name']})
        raise Exception(errormsg)
    if (conf['max_memory_mb'] > cpc.properties['storage-customer']):
        # TODO(preethipy): Exception infrastructure to be finalized
        errormsg = (_("max_memory_mb %(config_mem)d configured for "
                      "CpcSubset %(host)s is greater than the "
                      "available amount of memory %(max_mem)d on CPC "
                      "uuid %(cpcuuid)s and CPC name %(cpcname)s")
                    % {'config_mem': conf['max_processors'],
                       'host': conf['host'],
                       'max_proc': cpc.properties['processor-count-ifl'],
                       'max_mem': conf['cpc_uuid'],
                       'cpcname': cpc.properties['name']})
        raise Exception(errormsg)
