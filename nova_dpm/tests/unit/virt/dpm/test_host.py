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
import mock
import testtools

from nova_dpm.tests.unit.virt.dpm import fakecpcs
from nova_dpm.tests.unit.virt.dpm import fakezhmcclient
from nova_dpm.virt.dpm import host


"""
cpcsubset unit testcase
"""


class HostTestCase(testtools.TestCase):

    @mock.patch.object(host.LOG, 'warning')
    def test_host(self, mock_warning):

        session = fakezhmcclient.Session("dummy", "dummy", "dummy")
        client = fakezhmcclient.Client(session)

        cpcmanager = fakezhmcclient.getCpcmgrForClient(client)
        cpc = fakecpcs.getFakeCPC(cpcmanager)
        conf = fakecpcs.getFakeCPCconf()

        host.Host(conf, cpc, client)

        expected_arg = {'hostname': 'fakecpc'}
        assertlogs = False
        for call in mock_warning.call_args_list:

            if (len(call) > 0):
                if (len(call[0]) > 1 and call[0][1] == expected_arg):
                    assertlogs = True

        self.assertTrue(assertlogs)

    @mock.patch.object(host.LOG, 'warning')
    def test_host_properties(self, mock_warning):

        session = fakezhmcclient.Session("dummy", "dummy", "dummy")
        client = fakezhmcclient.Client(session)

        cpcmanager = fakezhmcclient.getCpcmgrForClient(client)
        cpc = fakecpcs.getFakeCPC(cpcmanager)
        conf = fakecpcs.getFakeCPCconf()

        host1 = host.Host(conf, cpc, client)
        host_properties = host1.properties
        self.assertEqual(host_properties['hypervisor_hostname'], 'S12subset',
                         'Hostname is S12subset')
        self.assertEqual(host_properties['dpm_name'], 'fakecpc', 'dpm_name')
