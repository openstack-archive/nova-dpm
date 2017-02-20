# Copyright 2017 IBM Corp.
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from oslotest import base

from subprocess import PIPE
from subprocess import Popen


class TestSetMac(base.BaseTestCase):

    def _execute_command(self, cmd):
        proc = Popen(cmd, stdout=PIPE)
        stdout, stderrr = proc.communicate()
        stdout = stdout.strip("\n")
        rc = proc.returncode
        return rc, stdout, stderrr

    def _setmac_test(self, func_name, args):
        """Calling setmac test function

        :param func_name: The function of setmac.sh to be called
        :param args: List of arguments to be passed into the function
        """
        setmac_path = "guest_image_tools/usr/bin/setmac.sh"
        cmd = [setmac_path, "test", func_name] + args
        return self._execute_command(cmd)

    def test_extract_interface_name(self):
        args = ["/devices/qeth/0.0.0001/net/enc1"]
        rc, stdout, stderr = self._setmac_test("extract_interface_name", args)
        self.assertEqual(0, rc)
        self.assertEqual("enc1", stdout)
        self.assertIsNone(stderr)

    def test_extract_interface_name_invalid_input(self):
        args = ["foobar"]
        rc, stdout, stderr = self._setmac_test("extract_interface_name", args)
        self.assertEqual(1, rc)
        self.assertEqual('', stdout)
        self.assertIsNone(stderr)
