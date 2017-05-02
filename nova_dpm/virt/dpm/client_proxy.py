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

"""
Client helps in dynamiclly importing zhmcclient and
also getting client object for given hmc credentials.
This will also help initialize the Client module with
fakezhmcclient for unit testcases
"""

import requests.packages.urllib3

from oslo_log import log as logging
from oslo_utils import importutils

zhmcclient = None
LOG = logging.getLogger(__name__)


def import_zhmcclient():
    """Lazy initialization for zhmcclient

    This function helps in lazy loading zhmclient. The zhmcclient can
    otherwise be set to fakezhmcclient for unittest framework
    """

    LOG.debug("get_zhmcclient")
    requests.packages.urllib3.disable_warnings()

    global zhmcclient
    if zhmcclient is None:
        zhmcclient = importutils.import_module('zhmcclient')

    return zhmcclient


def get_client_for_session(zhmc, userid, password):
    LOG.debug("get_client_for_session")
    zhmcclient = import_zhmcclient()
    session = zhmcclient.Session(zhmc, userid, password)
    return zhmcclient.Client(session)
