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
                    'storage-customer': 1024,
                },
                'partitions': [
                    {
                        'properties': {
                            # object-id is auto-generated
                            # object-uri is auto-generated
                            'name': 'partition_1',
                            'description': 'Partition #1 in CPC #2',
                        },
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
        ],
    })
    return session
