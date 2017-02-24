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
from subprocess import PIPE
from subprocess import Popen

from oslotest import base

base_path = os.path.dirname(os.path.realpath(__file__))
test_root_dir = base_path + "/root_dir_default"


class TestDPMGuestImageTools(base.BaseTestCase):

    def setUp(self):
        super(TestDPMGuestImageTools, self).setUp()
        # Change the root directory to the default root dir that contains the
        # fake commands
        self.env = dict(os.environ, ROOT_DIR=test_root_dir)

    def _execute_command(self, cmd):
        proc = Popen(cmd, stdout=PIPE, env=self.env)
        stdout, stderr = proc.communicate()
        # convert stdout from byte to unicode. Required for python 3
        stdout = stdout.decode("utf-8")
        self.stdout = stdout.strip("\n")
        self.stderr = stderr
        self.rc = proc.returncode
        print(self.stdout)

    def _test_function(self, func_name, args):
        """Calling a guest image tool bash function for test

        :param func_name: The bash function name to be called
        :param args: List of arguments to be passed into the function
        """
        tools_path =\
            "nova_dpm/tests/unit/guest_image_tools/test_wrapper.sh"
        cmd = [tools_path, func_name] + args
        self._execute_command(cmd)

    def _assert(self, rc, stdout="", stderr=None):
        self.assertEqual(rc, self.rc)
        self.assertEqual(stdout, self.stdout)
        self.assertEqual(stderr, self.stderr)

    def test_extract_interface_name(self):
        args = ["/devices/qeth/0.0.0001/net/enc1"]
        self._test_function("extract_interface_name", args)
        self._assert(0, stdout="enc1")

    def test_extract_interface_name_invalid_input(self):
        args = ["foobar"]
        self._test_function("extract_interface_name", args)
        self._assert(1)

    def test_extract_devno(self):
        args = ["/devices/qeth/0.0.0001/net/enc1"]
        self._test_function("extract_devno", args)
        self._assert(0, stdout="0001")

    def test_extract_devno_invalid_input(self):
        args = ["foobar"]
        self._test_function("extract_devno", args)
        self._assert(1)

    def test_extract_mac(self):
        args = ["0001", "foo 0001,0,aabbccddeeff;0004,1,112233445566;"]
        self._test_function("extract_mac", args)
        self._assert(0, stdout="aa:bb:cc:dd:ee:ff")

    def test_extract_mac_invalid_mac(self):
        args = ["0001", "foo 0001,0,aabbccddeeffaa;"]
        self._test_function("extract_mac", args)
        self._assert(1)

    def test_extract_mac_not_found(self):
        args = ["aaaa", "foo 0001,0,aabbccddeeff;0004,1,112233445566;"]
        self._test_function("extract_mac", args)
        self._assert(1)

    def test_is_locally_administered_mac_yes(self):
        local_macs = ["0a0000000000", "020000000000", "060000000000",
                      "0e0000000000"]
        for mac in local_macs:
            self._test_function("is_locally_administered_mac", [mac])
            self._assert(0)

    def test_is_locally_administered_mac_no(self):
        local_macs = ["010000000000", "030000000000", "040000000000",
                      "050000000000", "070000000000", "080000000000",
                      "090000000000", "0b0000000000", "0c0000000000",
                      "0d0000000000"]
        for mac in local_macs:
            self._test_function("is_locally_administered_mac", [mac])
            self._assert(1)

    def test_get_ip_cmd(self):
        self._test_function("get_ip_cmd", [])
        self._assert(0, test_root_dir + "/sbin/ip")

    def test_set_mac(self):
        self._test_function("set_mac", ["eth0", "0a0000000000"])
        self._assert(0)

    def test_device_exists(self):
        self._test_function("device_exists", ["0.0.0001"])
        self._assert(0)

    def test_device_exists_not(self):
        self._test_function("device_exists", ["0.0.0002"])
        self._assert(1)

    def test_get_cmdline(self):
        self._test_function("get_cmdline", [])
        self._assert(0, "this-is-the-cmd-line")

    def test_configure_device(self):
        self._test_function("configure_device", ["0.0.0001", "1"])
        self._assert(0)

    def test_configure_device_fail(self):
        self._test_function("configure_device", ["foo", "1"])
        self._assert(1)

    def test_get_device_bus_id(self):
        self._test_function("get_device_bus_id", ["0001"])
        self._assert(0, "0.0.0001")

    def test__change_root_cmd(self):
        self._test_function("_change_root", ["cmd"])
        self._assert(0, test_root_dir + "/cmd")

    def test__change_root_cmd_no_root_dir_set(self):
        # Unset the default root dir variable
        self.env = dict()
        self._test_function("_change_root", ["cmd"])
        self._assert(0, "cmd")

    def test__change_root_path(self):
        self._test_function("_change_root", ["/foo/bar"])
        self._assert(0, test_root_dir + "/foo/bar")

    def test__change_root_path_no_root_dir_set(self):
        # Unset the default root dir variable
        self.env = dict()
        self._test_function("_change_root", ["/foo/bar"])
        self._assert(0, "/foo/bar")

    def test_ensure_ccwgroup_module_already_loaded(self):
        # As /sys/bus/ccwgroup exists, modprobe is not being called. It does
        # not even exist in the default root dir, therefore a call would result
        # in a test failure
        self._test_function("ensure_ccwgroup_module", [])
        self._assert(0)

    def test_ensure_ccwgroup_module_good(self):
        # change the root dir as the directory /sys/bus/ccwgroup already
        # exists in the default root dir
        self.env = dict(os.environ, ROOT_DIR=base_path + "/root_dir_modprobe")
        self._test_function("ensure_ccwgroup_module", [])
        self._assert(0)
