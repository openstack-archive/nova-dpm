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
            'cpc_uuid': "1232132",
            'max_processors': 10,
            'max_memory_mb': 200,
            'max_partitions': 10
            }
    return conf


def getFakeInstance():
    props = {'hostname': 'DummyPartition'}
    instance = Instance(props)
    return instance


def getFakeInstanceList():
    property1 = {'hostname': 'DummyPartition1'}
    property2 = {'hostname': 'DummyPartition2'}

    instance1 = Instance(property1)
    instance2 = Instance(property2)

    instance_list = []
    instance_list.append(instance1)
    instance_list.append(instance2)

    return instance_list


class Instance(object):
    hostname = None

    def __init__(self, properties):
        self.properties = properties
        global hostname
        hostname = properties['hostname']

    def save(self):
        return

    @property
    def hostname(self):
        return self.properties['hostname']
