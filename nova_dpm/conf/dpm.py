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
dynamic capabilities known from software-based hypervisors.

The HMC (Hardware Management Console) provides a Web Services API which is used
as an access point by the OpenStack Nova driver for DPM. One HMC manages
multiple LinuxOne or z Systems CPCs (Central Processor Complexes).

The DPM options specify settings that are specific to DPM; they identify the
HMC managing the target CPC, and limit the resource usage on the target CPC
so that only a subset of the target CPC is used. That CPC subset is
represented as an OpenStack hypervisor host.

The DPM options are used when the compute_driver is set to use DPM
(compute_driver=dpm.HMCDriver).
""")


ALL_DPM_OPTS = [
    cfg.StrOpt('hmc', default='', required=True, help="""
    Hostname or IP address of the HMC that manages the target CPC"""),
    cfg.StrOpt('hmc_username', default='', required=True, help="""
    User name for connection to HMC."""),
    cfg.StrOpt('hmc_password', default='', required=True, help="""
    Password for connection to HMC."""),
    cfg.StrOpt('host', default='', required=True, help="""
    Name of the OpenStack hypervisor host backed by the specified subset of the
    target CPC"""),
    cfg.StrOpt('cpc_uuid', help="""
    Uuid of the target CPC"""),
    cfg.IntOpt('max_processors', help="""
    Maximum number of physical IFL processors on the target CPC that can be
    used for this CPC subset"""),
    cfg.IntOpt('max_memory', help="""
    Maximum amount of memory (in MiB) on the target CPC that can be used for
    this CPC subset"""),
    cfg.IntOpt('max_instances', help="""
    Maximum number of instances (partitions) that can be created for this CPC
    subset"""),
    cfg.StrOpt('physical_storage_adapter_mappings', help="""
    Physical storage adapter with port details for HBA creation""")
]


def register_opts(conf):
    conf.register_group(dpm_group)
    conf.register_opts(ALL_DPM_OPTS, group=dpm_group)


def list_opts():
    return {dpm_group: ALL_DPM_OPTS}
