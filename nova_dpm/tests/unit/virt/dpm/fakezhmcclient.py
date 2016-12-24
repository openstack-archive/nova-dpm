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
from nova_dpm.tests.unit.virt.dpm import fakecpcs
from zhmcclient._manager import BaseManager

import zhmcclient

"""Fake zhmcclient"""


def getCpcmgr(ipaddress, username, password):
    session = Session(ipaddress, username, password)
    client = Client(session)
    cpcmgr = CpcManager(client)
    return cpcmgr


def getCpcmgrForClient(client):
    cpcmgr = zhmcclient.CpcManager(client)
    return cpcmgr


def getdummyCpcmgr():
    zhmclientcpcmgr = getzhmclientCpcmgr("0.0.0.0",
                                         "dummyuser", "dummypassword")
    return zhmclientcpcmgr


def getzhmclientCpcmgr(ipaddress, username, password):
    session = Session(ipaddress, username, password)
    client = Client(session)
    cpcmgr = zhmcclient.CpcManager(client)
    return cpcmgr


class CpcManager(BaseManager):
    """fake cpcmanager"""

    def __init__(self, client):
        # This function should not go into the docs.
        # Parameters:
        #   client (:class:`~zhmcclient.Client`):
        #      Client object for the HMC to be used.
        super(CpcManager, self).__init__()
        self._session = client.session

    def list(self, full_properties=False):
        cpc_list = []
        cpc_list.append(fakecpcs.getFakeCPC(getdummyCpcmgr()))
        return cpc_list

    def find(self, **kwargs):
        return fakecpcs.getFakeCPC(getdummyCpcmgr())


class Session(object):
    """fake Session"""

    def __init__(self, host, userid=None, password=None):
        self._host = host
        self._userid = userid
        self._password = password

        return None

    @property
    def userid(self):
        return self._userid


class Client(object):
    """fake client"""

    def __init__(self, session):
        self._session = session
        self._cpcs = CpcManager(self)
        self._api_version = None

    @property
    def cpcs(self):
        cpcmgr = getCpcmgr("0.0.0.0", "dummyuser", "dummypassword")
        return cpcmgr

    @property
    def session(self):
        return self._session
