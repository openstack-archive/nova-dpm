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
from zhmcclient._cpc import Cpc


def getFakeCPC(cpcmanager):
    cpc_props = dict()

    cpc_props['object-uri'] = "/api/cpc/dummy"
    cpc_props['name'] = "fakecpc"
    cpc_props['storage-customer'] = 100
    cpc_props['processor-count-pending-ifl'] = 6
    cpc_props['processor-count-ifl'] = 12
    cpc_props['storage-customer-available'] = 50

    cpc = Cpc(cpcmanager, cpc_props['object-uri'], cpc_props)
    return cpc


def getFakeCPCconf():

    conf = {'host': "S12subset",
            'cpc_uuid': "1232132",
            'max_processors': 10,
            'max_memory_mb': 200,
            'max_partitions': 10
            }
    return conf


def getFakeCPCwithProp(cpcmanager, cpc_props):

    cpc = Cpc(cpcmanager, cpc_props['object-uri'], cpc_props)
    return cpc
