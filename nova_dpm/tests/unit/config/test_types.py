# Copyright 2017 IBM Corp. All Rights Reserved.
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

from nova.test import TestCase

from nova_dpm.conf import types

from nova_dpm.conf.types import StorageAdapterMappingType
from nova_dpm.conf.types import MAPPING_REGEX

VALID_DPM_OBJECT_ID = "fa1f2466-12df-311a-804c-4ed2cc1d656b"
VALID_DPM_OBJECT_ID_UC = "FA1F2466-12DF-311A-804C-4ED2CC1D656B"
VALID_STORAGE_MAPPING = VALID_DPM_OBJECT_ID + ":0"


class TestStorageAdapterMappingType(TestCase):
    conf_type = StorageAdapterMappingType()

    def test_valid_mapping(self):
        adapter_id, port = self.conf_type(VALID_STORAGE_MAPPING)
        self.assertEqual("0", port)
        self.assertEqual(VALID_DPM_OBJECT_ID, adapter_id)

    def test_upper_case_to_lower_case_adapter_id(self):
        adapter_id, port = self.conf_type(VALID_DPM_OBJECT_ID_UC + ":0")
        self.assertEqual("0", port)
        self.assertEqual(VALID_DPM_OBJECT_ID, adapter_id)

    def test_empty_value_fail(self):
        self.assertRaises(ValueError, self.conf_type, '')

    def test_invalid_value_fail(self):
        self.assertRaises(ValueError, self.conf_type, 'foobar')

    def test_missing_port_fail(self):
        self.assertRaises(ValueError, self.conf_type, VALID_DPM_OBJECT_ID)

    def test_missing_port_fail(self):
        self.assertRaises(ValueError, self.conf_type,
                          VALID_DPM_OBJECT_ID + ":")

    def test_invalid_port_fail(self):
        self.assertRaises(ValueError, self.conf_type,
                          VALID_DPM_OBJECT_ID + ":2")

    def test_invalid_port_type_fail(self):
        self.assertRaises(ValueError, self.conf_type,
                          VALID_DPM_OBJECT_ID + ":a")

    def test_invalid_adapter_id_fail(self):
        self.assertRaises(ValueError, self.conf_type, "foo:1")

    def test_repr(self):
        self.assertEqual(
            "String(regex='" + MAPPING_REGEX + "')",
            repr(self.conf_type))

    def test_equal(self):
        self.assertTrue(
            StorageAdapterMappingType() == StorageAdapterMappingType())


# TODO(andreas_s): Remove once available in os-dpm
class MultiStringWithKwargsType(TestCase):

    def setUp(self):
        super(MultiStringWithKwargsType, self).setUp()
        self.mm_type = types.MultiStringWithKwargsType()

    def test_format_default_none(self):
        result = self.mm_type.format_defaults(None)
        self.assertEqual([''], result)

    def test_format_defaults_default_only(self):
        result = self.mm_type.format_defaults(['foo', 'bar'])
        self.assertEqual(['foo', 'bar'], result)

    def test_format_defaults_sample_default_over_default(self):
        result = self.mm_type.format_defaults(['foo', 'bar'], ['sample'])
        self.assertEqual(['sample'], result)

    def test_quote_trailing_and_leading_space_default(self):
        result = self.mm_type.format_defaults([' foo ', ' bar '])
        self.assertEqual(['" foo "', '" bar "'], result)

    def test_quote_trailing_and_leading_space_sample_default(self):
        result = self.mm_type.format_defaults([' foo ', ' bar '], [' sample '])
        self.assertEqual(['" sample "'], result)
