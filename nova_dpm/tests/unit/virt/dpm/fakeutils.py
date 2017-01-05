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


from nova_dpm.tests.unit.virt.dpm import fakezhmcclient


# Data for fake Instance1
INSTANCE_HOST_NAME1 = fakezhmcclient.PARTITION_NAME1

# Data for fake Instance2
INSTANCE_HOST_NAME2 = fakezhmcclient.PARTITION_NAME2


def getFakeCPCconf():

    conf = {'cpcsubset_name': "S12subset",
            'cpc_uuid': "1232132",
            'max_processors': 10,
            'max_memory_mb': 200,
            'max_partitions': 10
            }
    return conf


def getFakeInstance():
    props = {
        'hostname': 'DummyPartition',
        'uuid': '6511ee0f-0d64-4392-b9e0-cdbea10a17c3'
    }
    instance = Instance(props)
    return instance


def get_fake_instance(props):
    instance = Instance(props)
    return instance


def get_fake_instance_list():
    instance_list = []
    props1 = {
        'hostname': INSTANCE_HOST_NAME1}
    instance1 = get_fake_instance(props1)
    props2 = {
        'hostname': INSTANCE_HOST_NAME2}
    instance2 = get_fake_instance(props2)
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

    @property
    def uuid(self):
        return self.properties['uuid']
