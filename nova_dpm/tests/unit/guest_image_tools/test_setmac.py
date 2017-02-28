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

import os

from nova_dpm.tests.unit.guest_image_tools.guest_image_base import\
    GuestImageBaseTestCase


class TestSetMac(GuestImageBaseTestCase):

    def _setmac_test(self, func_name, args):
        """Calling setmac test function

        :param func_name: The function of setmac.sh to be called
        :param args: List of arguments to be passed into the function
        """
        setmac_path =\
            "nova_dpm/tests/unit/guest_image_tools/setmac_test_wrapper.sh"
        cmd = [setmac_path, "test", func_name] + args
        self.rc, self.stdout, self.stderr = self._execute_command(cmd)

    def _assert(self, rc, stdout="", stderr=None):
        self.assertEqual(rc, self.rc)
        self.assertEqual(stdout, self.stdout)
        self.assertEqual(stderr, self.stderr)

    def test_extract_interface_name(self):
        args = ["/devices/qeth/0.0.0001/net/enc1"]
        self._setmac_test("extract_interface_name", args)
        self._assert(0, stdout="enc1")

    def test_extract_interface_name_invalid_input(self):
        args = ["foobar"]
        self._setmac_test("extract_interface_name", args)
        self._assert(1)

    def test_extract_devno(self):
        args = ["/devices/qeth/0.0.0001/net/enc1"]
        self._setmac_test("extract_devno", args)
        self._assert(0, stdout="0001")

    def test_extract_devno_invalid_input(self):
        args = ["foobar"]
        self._setmac_test("extract_devno", args)
        self._assert(1)

    def test_extract_mac(self):
        args = ["0001", "foo 0001,0,aabbccddeeff;0004,1,112233445566;"]
        self._setmac_test("extract_mac", args)
        self._assert(0, stdout="aa:bb:cc:dd:ee:ff")

    def test_extract_mac_invalid_mac(self):
        args = ["0001", "foo 0001,0,aabbccddeeffaa;"]
        self._setmac_test("extract_mac", args)
        self._assert(1)

    def test_extract_mac_not_found(self):
        args = ["aaaa", "foo 0001,0,aabbccddeeff;0004,1,112233445566;"]
        self._setmac_test("extract_mac", args)
        self._assert(1)

    def test_is_locally_administered_mac_yes(self):
        local_macs = ["0a0000000000", "020000000000", "060000000000",
                      "0e0000000000"]
        for mac in local_macs:
            self._setmac_test("is_locally_administered_mac", [mac])
            self._assert(0)

    def test_is_locally_administered_mac_no(self):
        local_macs = ["010000000000", "030000000000", "040000000000",
                      "050000000000", "070000000000", "080000000000",
                      "090000000000", "0b0000000000", "0c0000000000",
                      "0d0000000000"]
        for mac in local_macs:
            self._setmac_test("is_locally_administered_mac", [mac])
            self._assert(1)

    def test_get_ip_cmd(self):
        test_root_dir =\
            os.path.dirname(os.path.realpath(__file__)) + "/test_root_dir"
        self._setmac_test("get_ip_cmd", [])
        self._assert(0, test_root_dir + "/sbin/ip")

    def test_set_mac(self):
        self._setmac_test("set_mac", ["eth0", "0a0000000000"])
        self._assert(0)
