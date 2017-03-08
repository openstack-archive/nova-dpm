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

from nova_dpm.conf import types


class MultiStorageAdapterMappingOpt(cfg.MultiOpt):
    def __init__(self, name, **kwargs):
        """Option with DPM AdapterPortMapping type

           Option with ``type`` :class:`StorageAdapterMappingType`

        :param name: the option's name
        """
        super(MultiStorageAdapterMappingOpt, self).__init__(
            name, item_type=types.StorageAdapterMappingType(), **kwargs)
