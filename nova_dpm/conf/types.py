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


from oslo_config import cfg

OBJECT_ID_REGEX = "[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}"
# A FCP adapter can have up to 4 ports
PORT_REGEX = "[0-3]"
MAPPING_REGEX = "^" + OBJECT_ID_REGEX + ":" + PORT_REGEX + "$"


class StorageAdapterMappingType(cfg.types.String):
    """Storage adapter mapping type.

    Values are returned as tuple (adapter-id, port)
    """
    def __init__(self, type_name='multi valued'):
        super(StorageAdapterMappingType, self).__init__(
            type_name=type_name,
            regex=MAPPING_REGEX,
            ignore_case=True
        )

    def format_defaults(self, default, sample_default=None):
        multi = cfg.types.MultiString()
        return multi.format_defaults(default, sample_default)

    def __call__(self, value):
        val = super(StorageAdapterMappingType, self).__call__(value)
        # No extra checking for None required here.
        # The regex ensures the format of the value in the super class.
        split_result = val.split(':')
        return split_result[0].lower(), split_result[1]
