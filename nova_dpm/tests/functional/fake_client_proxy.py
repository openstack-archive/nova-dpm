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

from nova_dpm.tests.unit.virt.dpm import test_utils as utils
import zhmcclient
import zhmcclient_mock

def fake_session_functional_test():
    session = zhmcclient_mock.FakedSession('fake-host', 'fake-hmc',
                                           '2.13.1', '1.8')
    session.hmc.add_resources({
        'cpcs': [
            {
                'properties': {
                    # object-id is auto-generated
                    # object-uri is auto-generated
                    'name': 'cpc',
                    'dpm-enabled': True,
                    'description': 'CPC #2',
                    'processor-count-ifl': 10,
                    'storage-customer': 2048,
                    'se-version': '2.13.1'
                },
                'partitions': [

                ],
                'adapters': [
                    {
                        'properties': {
                            # object-id is auto-generated
                            # object-uri is auto-generated
                            'name': 'fcp_adapter',
                            'description': 'FCP',
                            'type': 'fcp',
                        },
                        'ports': [
                            {
                                'properties': {
                                    # element-id is auto-generated
                                    # element-uri is auto-generated
                                    'name': 'fcp_1_port_1',
                                    'description': 'Port #1 of FCP #1',
                                },
                            },
                        ],
                    },
                ],
            },
        ],
    })
    return session

def get_client_for_session(zhmc, userid, password):
    session = fake_session_functional_test()
    client = zhmcclient.Client(session)
    return client
