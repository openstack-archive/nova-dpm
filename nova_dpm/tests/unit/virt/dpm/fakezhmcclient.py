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


"""Fake zhmcclient"""

# We have considered 3 fake partition for unit test in one CPC.
# DummyPartition1, DummyPartition2, DummyPartition3

# Data for Fake partition1

INSTANCE_NAME1 = "6511ee0f-0d64-4392-b9e0-cdbea10a17c4"
PARTITION_NAME1 = "OpenStack-foo-6511ee0f-0d64-4392-b9e0-cdbea10a17c4"
PARTITION_URI1 = "/api/partitions/00000000-aaba-bbbb-cccc-abcdabcdabcd"
PARTITION_CP_PROCESSOR1 = 1
PARTITION_INITIAL_MEMORY1 = 512

# Data for Fake partition2
INSTANCE_NAME2 = "6511ee0f-0d64-4392-b9e0-cdbea10a17c5"
PARTITION_NAME2 = "OpenStack-foo-6511ee0f-0d64-4392-b9e0-cdbea10a17c5"
PARTITION_URI2 = "/api/partitions/00000000-aaba-bcbb-cccc-abcdabcdabcd"
PARTITION_CP_PROCESSOR2 = 2
PARTITION_INITIAL_MEMORY2 = 1024

# Data for Fake partition3
INSTANCE_NAME3 = "6511ee0f-0d64-4392-b9e0-cdbea10a17c6"
PARTITION_NAME3 = "OpenStack-foo-6511ee0f-0d64-4392-b9e0-cdbea10a17c6"
PARTITION_URI3 = "/api/partitions/00000000-aaba-bbbb-cdcc-abcdabcdabcd"
PARTITION_CP_PROCESSOR3 = 1
PARTITION_INITIAL_MEMORY3 = 512

# In our scenario we have considered 3 partition.
# Here idea is the partition which will use maximum cp-processor
# we will consider that maximum cp-processor as used processor.
# We will use this Maximum cp-processor to test used cp-processor.
# For further details please see testcase
# nova_dpm.
# tests.unit.virt.dpm.test_host.HostTestCase.test_get_proc_used
# So in our above scenario partition2 ("DummyPartition2")
# is using maximum cp-processor
MAX_CP_PROCESSOR = PARTITION_CP_PROCESSOR2

# For used memory we are using fake partition1, partition2 and partition3
# For more info please check function getFakeInstanceList()
# in fakeutils.py
# So used memory will be
# PARTITION_INITIAL_MEMORY1
#  + PARTITION_INITIAL_MEMORY2
#  + PARTITION_INITIAL_MEMORY2
USED_MEMORY = (PARTITION_INITIAL_MEMORY1
               + PARTITION_INITIAL_MEMORY2
               + PARTITION_INITIAL_MEMORY3)


def getCpcmgr(ipaddress, username, password):
    session = Session(ipaddress, username, password)
    client = Client(session)
    cpcmgr = CpcManager(client)
    return cpcmgr


def getCpcmgrForClient(client):
    cpcmgr = CpcManager(client)
    return cpcmgr


def getdummyCpcmgr():
    zhmclientcpcmgr = getzhmclientCpcmgr("0.0.0.0",
                                         "dummyuser", "dummypassword")
    return zhmclientcpcmgr


def getzhmclientCpcmgr(ipaddress, username, password):
    session = Session(ipaddress, username, password)
    client = Client(session)
    cpcmgr = CpcManager(client)
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
            'cpc_object_id': "1232132",
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
    partition_props['name'] = (
        "OpenStack-foo-6511ee0f-0d64-4392-b9e0-cdbea10a17c3")
    partition_props['description'] = "OpenStack CPCSubset=foo"
    partition_props['object-uri'] = "/api/partitions/" \
                                    "00000000-aaaa-bbbb-cccc-abcdabcdabcd"
    partition_props['initial-memory'] = 0
    partition_props['ifl-processors'] = 0
    partition_props['boot-os-specific-parameters'] = "foo"
    partition_props['state'] = "Active"
    partition = Partition(getdummyCpcmgr(), partition_props['object-uri'],
                          partition_props)
    return partition


def get_fake_partition(properties):
    partition = Partition(
        getdummyCpcmgr(),
        properties['object-uri'], properties)
    return partition


def get_fake_partition_list():
    partition_list = []
    properties1 = {
        'name': PARTITION_NAME1,
        'object-uri': PARTITION_URI1,
        'initial-memory': PARTITION_INITIAL_MEMORY1,
        'ifl-processors': PARTITION_CP_PROCESSOR1
    }

    properties2 = {
        'name': PARTITION_NAME2,
        'object-uri': PARTITION_URI2,
        'initial-memory': PARTITION_INITIAL_MEMORY2,
        'ifl-processors': PARTITION_CP_PROCESSOR2
    }

    properties3 = {
        'name': PARTITION_NAME3,
        'object-uri': PARTITION_URI3,
        'initial-memory': PARTITION_INITIAL_MEMORY3,
        'ifl-processors': PARTITION_CP_PROCESSOR3
    }
    partition_list.append(get_fake_partition(properties1))
    partition_list.append(get_fake_partition(properties2))
    partition_list.append(get_fake_partition(properties3))
    partition_list.append(getFakePartition())

    return partition_list


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


class BaseResource(object):
    def __init__(self, manager, object_uri, properties):
        self.manager = manager
        self.object_uri = object_uri
        self.properties = properties

    def get_property(self, name):
        return self.properties[name]


class BaseManager(object):
    def __init__(self, resource):
        self.resource = resource


class CpcManager(BaseManager):
    """fake cpcmanager"""

    def __init__(self, client):
        # This function should not go into the docs.
        # Parameters:
        #   client (:class:`~zhmcclient.Client`):
        #      Client object for the HMC to be used.
        super(CpcManager, self).__init__(Cpc)
        self._session = client.session

    def list(self, full_properties=False):
        cpc_list = []
        cpc_list.append(getFakeCPC(getdummyCpcmgr()))
        return cpc_list

    def find(self, **kwargs):
        return getFakeCPC(getdummyCpcmgr())


class Cpc(BaseResource):
    def __init__(self, manager, uri, properties):
        super(Cpc, self).__init__(manager, uri, properties)

    @property
    def dpm_enabled(self):
        return True

    def pull_full_properties(self):
        self._pull_full_properties = True

    @property
    def partitions(self):
        return PartitionManager(self)

    @property
    def adapters(self):
        return getFakeAdapterManager()


class PartitionManager(BaseManager):
    """fake cpcmanager"""

    def __init__(self, cpc):
        # This function should not go into the docs.
        # Parameters:
        #   cpc (:class:`~zhmcclient.Cpc`):
        #     CPC defining the scope for this manager.
        super(PartitionManager, self).__init__(cpc)

    def list(self, full_properties=False):
        part_list = get_fake_partition_list()
        part_list.append(getFakePartition())
        return part_list

    def find(self, **kwargs):
        return getFakePartition()


class Partition(BaseResource):
    def __init__(self, manager, uri, properties):
        super(Partition, self).__init__(manager, uri, properties)

    def pull_full_properties(self):
        self._pull_full_properties = True


class NicManager(BaseManager):
    """fake cpcmanager"""

    def __init__(self, partition):
        # This function should not go into the docs.
        # Parameters:
        #   partition (:class:`~zhmcclient.Partition`):
        #     Partition defining the scope for this manager.
        super(NicManager, self).__init__(partition)

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
        super(Nic, self).__init__(manager, uri, properties)

    def pull_full_properties(self):
        self._pull_full_properties = True


class HbaManager(BaseManager):
    """fake cpcmanager"""

    def __init__(self, partition):
        # This function should not go into the docs.
        # Parameters:
        #   partition (:class:`~zhmcclient.Partition`):
        #     Partition defining the scope for this manager.
        super(HbaManager, self).__init__(partition)

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
        super(Hba, self).__init__(manager, uri, properties)

    def pull_full_properties(self):
        self._pull_full_properties = True


class AdapterManager(BaseManager):
    """fake cpcmanager"""

    def __init__(self, partition):
        # This function should not go into the docs.
        # Parameters:
        #   partition (:class:`~zhmcclient.Partition`):
        #     Partition defining the scope for this manager.
        super(AdapterManager, self).__init__(partition)

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
        super(Adapter, self).__init__(manager, uri, properties)

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
