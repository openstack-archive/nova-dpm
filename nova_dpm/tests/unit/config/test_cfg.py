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
from nova_dpm.tests.unit.config.test_types import VALID_STORAGE_MAPPING
from nova_dpm.tests.unit.config.test_types import VALID_DPM_OBJECT_ID


class TestStorageAdapterMappingOpt(TestCase):

    def create_tempfiles(self, files, ext='.conf'):
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
        conf = self.useFixture(Config())
        conf.load_raw_values(mapping=VALID_STORAGE_MAPPING)
        opt = MultiStorageAdapterMappingOpt("mapping")
        conf.register_opt(opt)
        self.assertEqual([(VALID_DPM_OBJECT_ID, "0")], cfg.CONF.mapping)

    def test_config_multiple(self):
        other_object_id = 'aaaaaaaa-12df-311a-804c-aaaaaaaaaaaa'
        other_mapping = other_object_id + ':1'
        paths = self.create_tempfiles([
            ('test', '[DEFAULT]\nmapping = ' + VALID_STORAGE_MAPPING + '\n'
             'mapping = ' + other_mapping + '\n')])

        conf = self.useFixture(Config())
        conf.register_opt(MultiStorageAdapterMappingOpt("mapping"))
        conf.conf(args=['--config-file', paths[0]])
        self.assertEqual([(VALID_DPM_OBJECT_ID, "0"), (other_object_id, "1")],
                         cfg.CONF.mapping)
