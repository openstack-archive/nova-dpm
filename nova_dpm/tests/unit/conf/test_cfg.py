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

import os
from oslo_config import cfg
from oslo_config.fixture import Config
import tempfile

from nova.test import TestCase

from nova_dpm.conf.cfg import MultiStorageAdapterMappingOpt
from nova_dpm.conf.types import StorageAdapterMappingType


class TestStorageAdapterMappingOpt(TestCase):

    def create_tempfiles(self, files, ext='.conf'):
        """Create temp files for testing

        :param files: A list of files of tuples in the format
           [('filename1', 'line1\nline2\n'), ('filename2', 'line1\nline2\n')]
        :param ext: The file extension to be used
        :return: List of file paths
           paths[0] = path of filename1
           paths[1] = path of filename2
        """
        # TODO(andreas_s): Make a mixin in os-dpm and move this there
        # (also required in nova-dpm)
        tempfiles = []
        for (basename, contents) in files:
            if not os.path.isabs(basename):
                # create all the tempfiles in a tempdir
                tmpdir = tempfile.mkdtemp()
                path = os.path.join(tmpdir, basename + ext)
                # the path can start with a subdirectory so create
                # it if it doesn't exist yet
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
            else:
                path = basename + ext
            fd = os.open(path, os.O_CREAT | os.O_WRONLY)
            tempfiles.append(path)
            try:
                os.write(fd, contents.encode('utf-8'))
            finally:
                os.close(fd)
        return tempfiles

    def test_object(self):
        opt = MultiStorageAdapterMappingOpt("mapping", help="foo-help")
        self.assertEqual("foo-help", opt.help)
        self.assertEqual("mapping", opt.name)
        self.assertEqual(StorageAdapterMappingType, type(opt.type))

    def test_config_single(self):
        mapping = ["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa:0"]
        opt = MultiStorageAdapterMappingOpt("mapping")
        cfg.CONF.register_opt(opt)
        cfg.CONF.set_override("mapping", mapping, enforce_type=True)
        self.assertEqual([("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "0")],
                         cfg.CONF.mapping)

    def test_config_multiple_set_override(self):
        mapping = ["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa:0",
                   "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb:1"]
        opt = MultiStorageAdapterMappingOpt("mapping")
        cfg.CONF.register_opt(opt)
        cfg.CONF.set_override("mapping", mapping, enforce_type=True)
        expected_mapping = [
            ("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "0"),
            ("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", "1")]
        self.assertEqual(expected_mapping, cfg.CONF.mapping)

    def test_config_multiple_config_file(self):
        mapping = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa:0"
        other_mapping = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb:1"
        paths = self.create_tempfiles([
            ('test', '[DEFAULT]\nmapping = ' + mapping + '\n'
             'mapping = ' + other_mapping + '\n')])

        conf = self.useFixture(Config())
        conf.register_opt(MultiStorageAdapterMappingOpt("mapping"))
        conf.conf(args=['--config-file', paths[0]])
        self.assertEqual([("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "0"),
                          ("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", "1")],
                         cfg.CONF.mapping)
