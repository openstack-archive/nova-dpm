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
PORT_REGEX = "[0,1]"
MAPPING_REGEX = "^" + OBJECT_ID_REGEX + ":" + PORT_REGEX + "$"


class MultiStringWithKwargsType(cfg.types.String):
    """Multi String with kwargs type

    This type is basically the same as the oslo_config.types.MultiString type.
    The only difference is that this type allows setting additional attributes
    via **kwargs for the super String type, which the MultiString type does
    not.

    Once **kwargs are allowed in oslo_config.types.MultiString type, this
    type can be eliminated.

    TODO(andreas_s): Move to os-dpm
    """
    def __init__(self, type_name='multi valued', **kwargs):
        super(MultiStringWithKwargsType, self).__init__(
            type_name=type_name, **kwargs)

    NONE_DEFAULT = ['']

    def format_defaults(self, default, sample_default=None):
        """Return a list of formatted default values.

        Called when generating the description of a config option in the
        config file.
        """
        if sample_default is not None:
            default_list = self._formatter(sample_default)
        elif not default:
            default_list = self.NONE_DEFAULT
        else:
            default_list = self._formatter(default)
        return default_list

    def _formatter(self, value):
        return [self.quote_trailing_and_leading_space(v) for v in value]


class StorageAdapterMappingType(MultiStringWithKwargsType):
    """Storage adapter mapping type.

    Values are returned as tuple (adapter-id, port)
    """
    def __init__(self, type_name='multi valued'):
        super(StorageAdapterMappingType, self).__init__(
            type_name=type_name,
            regex=MAPPING_REGEX,
            ignore_case=True
        )

    def __call__(self, value):
        val = super(StorageAdapterMappingType, self).__call__(value)
        # No extra checking required, as regex ensures the format of the value
        # in the super class
        split_result = val.split(':')
        return split_result[0].lower(), split_result[1]
