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

from os_dpm.config import config as os_dpm_conf
from os_dpm.config.types import DPMObjectIdType
from oslo_config import cfg

from nova_dpm.conf.cfg import MultiStorageAdapterMappingOpt

os_dpm_conf.DPM_GROUP.help += """

DPM config options for the Nova compute service (one for each OpenStack
hypervisor host) specify the target CPC, the HMC managing it, and limits on the
resource usage on the target CPC. These limits ensure that only a subset of the
target CPC is used for the OpenStack hypervisor host. To use the Nova driver
for DPM, the `[DEFAULT].compute_driver` config option needs to be set to the
value `dpm.DPMDriver`.
"""

ALL_DPM_OPTS = [
    cfg.IntOpt('max_processors', help="""
    Maximum number of shared physical IFL processors on the target CPC that can
    be used for this OpenStack hypervisor host"""),
    cfg.IntOpt('max_memory', min=512, help="""
    Maximum amount of memory (in MiB) on the target CPC that can be used for
    this OpenStack hypervisor host"""),
    MultiStorageAdapterMappingOpt('physical_storage_adapter_mappings', help="""
    Physical storage adapter with port details for hba creation"""),
    cfg.ListOpt('target_wwpn_ignore_list', default='', help="""
    list of target/remote wwpns can be used for example to exclude NAS/file
    WWPNs returned by the V7000 Unified."""),
    cfg.ListOpt("physical_crypto_adapters", default="", sample_default="",
                item_type=DPMObjectIdType(),
                help="""
    List of crypto adapter uuids that are managed by this CPCSubset. If a
    Crypto Feature is requested, Domains will be assigned only from this
    list of adapters.

    The crypto adapter 'mode' must have been preconfigured. OpenStack won't set
    or update it. The list can contain adapters in different 'modes'.
    The users always requests a Crypto Feature in a certain mode. Depending on
    that the adpater to be used is chosen.
    """
                )
]


def register_opts(conf):
    os_dpm_conf.register_opts()
    conf.register_opts(ALL_DPM_OPTS, group=os_dpm_conf.DPM_GROUP)


def list_opts():
    return [(os_dpm_conf.DPM_GROUP,
             ALL_DPM_OPTS + os_dpm_conf.COMMON_DPM_OPTS)]
