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


import zhmcclient_mock

HOST = 'foo'
PARTITION1 = {
    'name': "OpenStack-" + HOST + "-6511ee0f-0d64-4392-b9e0-cdbea10a17c4",
    'ifl-processors': 1,
    'initial-memory': 512
}

PARTITION2 = {
    'name': "OpenStack-" + HOST + "-6511ee0f-0d64-4392-b9e0-cdbea10a4444",
    'ifl-processors': 2,
    'initial-memory': 1024
}

PARTITION3 = {
    'name': "OpenStack-" + HOST + "-6511ee0f-0d64-4392-b9e0-cdbea10accc4",
    'ifl-processors': 1,
    'initial-memory': 512
}

# Maximum processor used by any of the partition is 2
# i.e - PARTITION2 is having max processor among above partitions
MAX_PROC_USED = max(PARTITION1['ifl-processors'],
                    PARTITION2['ifl-processors'],
                    PARTITION3['ifl-processors'])

# Total memory used by partitions created by openstack
TOTAL_MEM_USED = (PARTITION1['initial-memory']
                  + PARTITION2['initial-memory']
                  + PARTITION3['initial-memory'])


def create_session_1():
    session = zhmcclient_mock.FakedSession('fake-host', 'fake-hmc',
                                           '2.13.1', '1.8')
    session.hmc.add_resources({
        'cpcs': [
            {
                'properties': {
                    # object-id is auto-generated
                    # object-uri is auto-generated
                    'name': 'cpc_1',
                    'dpm-enabled': False,
                    'description': 'CPC #1',
                },
                'lpars': [
                    {
                        'properties': {
                            # object-id is auto-generated
                            # object-uri is auto-generated
                            'name': 'lpar_1',
                            'description': 'LPAR #1 in CPC #1',
                        },
                    },
                ],
            },
            {
                'properties': {
                    # object-id is auto-generated
                    # object-uri is auto-generated
                    'name': 'cpc_2',
                    'dpm-enabled': True,
                    'description': 'CPC #2',
                    'processor-count-ifl': 10,
                    'storage-customer': 2048,
                    'se-version': '2.13.1'
                },
                'partitions': [
                    {
                        'properties': {
                            # object-id is auto-generated
                            # object-uri is auto-generated
                            'name': 'OpenStack-fake-mini-1',
                            'description': 'Partition #1 in CPC #2',
                        },
                    },
                    {
                        'properties': PARTITION1
                    },
                    {
                        'properties': PARTITION2
                    },
                    {
                        'properties': PARTITION3
                    },
                ],
                'adapters': [
                    {
                        'properties': {
                            # object-id is auto-generated
                            # object-uri is auto-generated
                            'name': 'osa_1',
                            'description': 'OSA #1 in CPC #2',
                            'type': 'osd',
                        },
                        'ports': [
                            {
                                'properties': {
                                    # element-id is auto-generated
                                    # element-uri is auto-generated
                                    'name': 'osa_1_port_1',
                                    'description': 'Port #1 of OSA #1',
                                },
                            },
                        ],
                    },
                ],
            },
            {
                'properties': {
                    # object-id is auto-generated
                    # object-uri is auto-generated
                    'name': 'cpc_3',
                    'dpm-enabled': True,
                    'description': 'CPC #3',
                    'processor-count-ifl': 10,
                    'storage-customer': 1024,
                },
                'partitions': [
                    {
                        'properties': {
                            # object-id is auto-generated
                            # object-uri is auto-generated
                            'name':
                                'OpenStack-fakemini-38400000-'
                                '8cf0-11bd-b23e-10b96e4ef00d',
                            'description': 'Partition #1 in CPC #3',
                            'initial-memory': 512,
                            'ifl-processors': 1,
                        },

                        'hbas': [
                            {
                                'properties': {
                                    'name': 'hba1',
                                    'wwpn': '0x5565656565656565',
                                    'adapter-port-uri':
                                        '/api/cpcs/3/adapters/3',
                                    'hba-uris': 'test-hba',
                                }
                            },
                        ],
                    },

                ],
                'adapters': [
                    {
                        'properties': {
                            # object-id is auto-generated
                            # object-uri is auto-generated
                            'name': 'osa_1',
                            'description': 'OSA #1 in CPC #3',
                            'type': 'osd',
                        },
                        'ports': [
                            {
                                'properties': {
                                    # element-id is auto-generated
                                    # element-uri is auto-generated
                                    'name': 'osa_1_port_1',
                                    'description': 'Port #1 of OSA #1',
                                },
                            },
                        ],
                    },
                ],
            },
        ],
    })
    return session
