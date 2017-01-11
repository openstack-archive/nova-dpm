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

from zhmcclient._logging import _log_call
from zhmcclient._manager import BaseManager
from zhmcclient._resource import BaseResource

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


def getFakeCPC(cpcmanager=None):
    cpc_props = dict()

    cpc_props['object-uri'] = "/api/cpc/dummy"
    cpc_props['name'] = "fakecpc"
    cpc_props['storage-customer'] = 100
    cpc_props['processor-count-pending-ifl'] = 6
    cpc_props['processor-count-ifl'] = 12
    cpc_props['storage-customer-available'] = 500

    if not cpcmanager:
        cpcmanager = getdummyCpcmgr()

    cpc = Cpc(cpcmanager, cpc_props['object-uri'], cpc_props)
    return cpc


def getFakeCPCconf():

    conf = {'cpcsubset_name': "S12subset",
            'cpc_uuid': "1232132",
            'max_processors': 10,
            'max_memory_mb': 200,
            'max_partitions': 10
            }
    return conf


def getFakeCPCwithProp(cpcmanager, cpc_props):

    cpc = Cpc(cpcmanager, cpc_props['object-uri'], cpc_props)
    return cpc


def getFakePartition():
    partition_props = dict()
    partition_props['name'] = "DummyPartition"
    partition_props['object-uri'] = "/api/partitions/" \
                                    "00000000-aaaa-bbbb-cccc-abcdabcdabcd"
    partition = Partition(getdummyCpcmgr(), partition_props['object-uri'],
                          partition_props)
    return partition


def getFakeNicManager():
    nics = NicManager(getFakePartition())
    return nics


def getFakeNic(properties=None):
    if not properties:
        properties = {}
    properties['element-uri'] = "/api/partitions/" \
                                "00000000-aaaa-bbbb-cccc-abcdabcdabcd" \
                                "/nics/00000000-nics-bbbb-cccc-abcdabcdabcd"
    nic = Nic(getFakeNicManager(), properties['element-uri'],
              properties)
    return nic


def getFakeHbaManager():
    hbas = HbaManager(getFakePartition())
    return hbas


def getFakeHba(properties=None):
    if not properties:
        properties = {}
    properties['element-uri'] = "/api/partitions/" \
                                "00000000-aaaa-bbbb-cccc-abcdabcdabcd" \
                                "/hbas/00000000-nics-bbbb-cccc-abcdabcdabcd"
    hba = Hba(getFakeHbaManager(), properties['element-uri'],
              properties)
    return hba


def getFakeAdapterManager():
    adapters = AdapterManager(getFakeCPC())
    return adapters


def getFakeAdapter(properties=None):
    if not properties:
        properties = {}
    properties['object-uri'] = "/api/adapters/" \
                               "9b926334-8e01-11e5-b1a4-9abe94228ee1"
    properties['type'] = "fcp"
    adapter = Adapter(getFakeAdapterManager(), properties['object-uri'],
                      properties)
    return adapter


class CpcManager(BaseManager):
    """fake cpcmanager"""

    def __init__(self, client):
        # This function should not go into the docs.
        # Parameters:
        #   client (:class:`~zhmcclient.Client`):
        #      Client object for the HMC to be used.
        query_props = [
            'name',
        ]
        super(CpcManager, self).__init__(Cpc, None, None,
                                         None, query_props)
        self._session = client.session

    def list(self, full_properties=False):
        cpc_list = []
        cpc_list.append(getFakeCPC(getdummyCpcmgr()))
        return cpc_list

    def find(self, **kwargs):
        return getFakeCPC(getdummyCpcmgr())


class Cpc(BaseResource):
    def __init__(self, manager, uri, properties):
        super(Cpc, self).__init__(manager, uri, None, properties,
                                  uri_prop='object-uri',
                                  name_prop='name')

    @property
    @_log_call
    def dpm_enabled(self):
        return True

    def pull_full_properties(self):
        self._pull_full_properties = True

    @property
    @_log_call
    def adapters(self):
        return getFakeAdapterManager()


class PartitionManager(BaseManager):
    """fake cpcmanager"""

    def __init__(self, cpc):
        # This function should not go into the docs.
        # Parameters:
        #   cpc (:class:`~zhmcclient.Cpc`):
        #     CPC defining the scope for this manager.
        query_props = [
            'name',
        ]
        super(PartitionManager, self).__init__(cpc, None,
                                               None, None, query_props)

    def list(self, full_properties=False):
        partition_list = []
        partition_list.append(getFakePartition())
        return partition_list

    def find(self, **kwargs):
        return getFakePartition()


class Partition(BaseResource):
    def __init__(self, manager, uri, properties):
        super(Partition, self).__init__(
            manager, uri, None, properties,
            uri_prop='object-uri', name_prop='name')

    def pull_full_properties(self):
        self._pull_full_properties = True


class NicManager(BaseManager):
    """fake cpcmanager"""

    def __init__(self, partition):
        # This function should not go into the docs.
        # Parameters:
        #   partition (:class:`~zhmcclient.Partition`):
        #     Partition defining the scope for this manager.
        query_props = [
            'name',
        ]
        super(NicManager, self).__init__(partition, None,
                                         None, None, query_props)

    def list(self, full_properties=False):
        nic_list = []
        nic_list.append(getFakeNic())
        return nic_list

    def create(self, properties):
        return getFakeNic(properties)

    def find(self, **kwargs):
        return getFakeNic()


class Nic(BaseResource):
    def __init__(self, manager, uri, properties):
        super(Nic, self).__init__(manager, uri, None, properties,
                                  uri_prop='object-uri',
                                  name_prop='name')

    def pull_full_properties(self):
        self._pull_full_properties = True


class HbaManager(BaseManager):
    """fake cpcmanager"""

    def __init__(self, partition):
        # This function should not go into the docs.
        # Parameters:
        #   partition (:class:`~zhmcclient.Partition`):
        #     Partition defining the scope for this manager.
        query_props = [
            'name',
        ]
        super(HbaManager, self).__init__(partition, None, None,
                                         None, query_props)

    def list(self, full_properties=False):
        hba_list = []
        hba_list.append(getFakeHba())
        return hba_list

    def create(self, properties):
        return getFakeHba(properties)

    def find(self, **kwargs):
        return getFakeHba()


class Hba(BaseResource):
    def __init__(self, manager, uri, properties):
        super(Hba, self).__init__(manager, uri, None, properties,
                                  uri_prop='object-uri',
                                  name_prop='name')

    def pull_full_properties(self):
        self._pull_full_properties = True


class AdapterManager(BaseManager):
    """fake cpcmanager"""

    def __init__(self, partition):
        # This function should not go into the docs.
        # Parameters:
        #   partition (:class:`~zhmcclient.Partition`):
        #     Partition defining the scope for this manager.
        query_props = [
            'name',
        ]
        super(AdapterManager, self).__init__(partition, None, None,
                                             None, query_props)

    def list(self, full_properties=False):
        adapter_list = []
        adapter_list.append(getFakeAdapter())
        return adapter_list

    def create(self, properties):
        return getFakeAdapter(properties)

    def find(self, **kwargs):
        return getFakeAdapter()


class Adapter(BaseResource):

    def __init__(self, manager, uri, properties):
        super(Adapter, self).__init__(manager, uri, None, properties,
                                      uri_prop='object-uri',
                                      name_prop='name')

    def pull_full_properties(self):
        self._pull_full_properties = True


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
