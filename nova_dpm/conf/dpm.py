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

from oslo_config import cfg


dpm_group = cfg.OptGroup('dpm',
                         title='DPM options',
                         help="""
The IBM z13 system generation (and IBM LinuxONE) introduced a new
administrative mode named "Dynamic Partition Manager" (DPM) that allows for
managing the firmware-based logical partition hypervisor (PR/SM) with the
dynamic capabilities known from software-based hypervisors. A z13 or LinuxONE
machine is termed CPC (Central Processor Complex). Its management access point
is the z Systems HMC (Hardware Management Console) which exposes a Web Services
API that is used by the Nova driver for DPM and by the Neutron agent for DPM.
One HMC can manage multiple CPCs.

DPM config options for the Nova compute service (one for each OpenStack
hypervisor host) specify the target CPC, the HMC managing it, and limits on the
resource usage on the target CPC. These limits ensure that only a subset of the
target CPC is used for the OpenStack hypervisor host. To use the Nova driver
for DPM, the `[DEFAULT].compute_driver` config option needs to be set to the
value `dpm.DPMDriver`.
""")


ALL_DPM_OPTS = [
    cfg.StrOpt('hmc', default='', required=True, help="""
    Hostname or IP address of the HMC that manages the target CPC"""),
    cfg.StrOpt('hmc_username', default='', required=True, help="""
    User name for connection to the HMC"""),
    cfg.StrOpt('hmc_password', default='', required=True, help="""
    Password for connection to the HMC"""),
    cfg.StrOpt('host', default='', required=True, help="""
    Name of the OpenStack hypervisor host"""),
    cfg.StrOpt('cpc_uuid', help="""
    Object-id of the target CPC"""),
    cfg.IntOpt('max_processors', help="""
    Maximum number of shared physical IFL processors on the target CPC that can
    be used for this OpenStack hypervisor host"""),
    cfg.IntOpt('max_memory', help="""
    Maximum amount of memory (in MiB) on the target CPC that can be used for
    this OpenStack hypervisor host"""),
    cfg.IntOpt('max_instances', help="""
    Maximum number of instances (partitions) that can be created for this
    OpenStack hypervisor host"""),
    cfg.StrOpt('physical_storage_adapter_mappings', help="""
    Physical storage adapter with port details for hba creation""")
]


def register_opts(conf):
    conf.register_group(dpm_group)
    conf.register_opts(ALL_DPM_OPTS, group=dpm_group)


def list_opts():
    return [(dpm_group, ALL_DPM_OPTS)]
