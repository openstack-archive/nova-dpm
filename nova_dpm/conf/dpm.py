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
    cfg.IntOpt('max_memory', help="""
    Maximum amount of memory (in MiB) on the target CPC that can be used for
    this OpenStack hypervisor host"""),
    cfg.IntOpt('max_instances', default=-1, min=-1, help="""
    Maximum number of instances (partitions) that can be created for this
    OpenStack hypervisor host. Valid values are:
    -1: The number of instances is  only limited by the
        number of free partitions on this CPC
     0: A technically valid upper bound but useless.
    >0: If this value is reached,
        this host won't be able to spawn new instances."""),
    MultiStorageAdapterMappingOpt('physical_storage_adapter_mappings', help="""
    Physical storage adapter with port details for hba creation"""),
    cfg.ListOpt('target_wwpn_ignore_list', default='', help="""
    list of target/remote wwpns can be used for example to exclude NAS/file
    WWPNs returned by the V7000 Unified.""")
]


def register_opts(conf):
    os_dpm_conf.register_opts()
    conf.register_opts(ALL_DPM_OPTS, group=os_dpm_conf.DPM_GROUP)


def list_opts():
    return [(os_dpm_conf.DPM_GROUP,
             ALL_DPM_OPTS + os_dpm_conf.COMMON_DPM_OPTS)]
