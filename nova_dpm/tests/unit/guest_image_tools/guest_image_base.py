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


class GuestImageBaseTestCase(base.BaseTestCase):

    def _execute_command(self, cmd):
        proc = Popen(cmd, stdout=PIPE, encoding='utf-8')
        stdout, stderr = proc.communicate()
        stdout = stdout.strip("\n")
        rc = proc.returncode
        return rc, stdout, stderr
