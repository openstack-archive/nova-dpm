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


def getFakeCPCconf():

    conf = {'cpcsubset_name': "S12subset",
            'cpc_object_id': "1232132",
            'max_processors': 10,
            'max_memory_mb': 200,
            'max_partitions': 10,
            'physical_storage_adapter_mappings':
                ["439da232-b18d-11e6-9c12-42f2e9ef1641:0"]
            }
    return conf


def getFakeInstance():
    props = {
        'hostname': 'DummyPartition',
        'uuid': '6511ee0f-0d64-4392-b9e0-cdbea10a17c3'
    }
    instance = PartitionInstance(props)
    return instance


class PartitionInstance(object):
    hostname = None

    def __init__(self, properties):
        self.properties = properties
        global hostname
        hostname = properties['hostname']

    def save(self):
        return

    @property
    def uuid(self):
        return self.properties['uuid']
