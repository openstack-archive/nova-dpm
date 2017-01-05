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
PR/SM2 (in DPM mode) is a hypervisor. By using PR/SM2 hypervisor we can create
partition on IBM z Systems or IBM LinuxONE system. A partition
is a virtual representation of the hardware resources of a
z Systems or LinuxONE system.
Hardware Management Console (HMC) is a component of DPM by
using which we can create partitions.

DPM options are used when the compute_driver is set to use
DPM (compute_driver=dpm.HMCDriver).

""")


ALL_DPM_OPTS = [
    cfg.StrOpt('hmc', default='', required=True, help="""
    Hostname or IP address for connection to HMC via zhmcclient"""),
    cfg.StrOpt('hmc_username', default='', required=True, help="""
    User name for connection to HMC Host."""),
    cfg.StrOpt('hmc_password', default='', required=True, help="""
    Password for connection to HMC Host."""),
    cfg.StrOpt('host', default='', required=True, help="""
    CpcSubset name"""),
    cfg.StrOpt('cpc_uuid', help="""
    Uuid of the CPC"""),
    cfg.IntOpt('max_processors', help="""
    Maximum number of shared IFL processors available on CpcSubset"""),
    cfg.IntOpt('max_memory', help="""
    Maximum amount of memory available on CpcSubset"""),
    cfg.IntOpt('max_instances', help="""
    Maximum number of instances that can be created on CpcSubset"""),
    cfg.StrOpt('physical_storage_adapter_mappings', help="""
    Physical storage adapter with port details for hba creation
    e.g.- physical_storage_adapter_mappings =
    "439da232-b18d-11e6-9c12-42f2e9ef1641:0"
    where '439da232-b18d-11e6-9c12-42f2e9ef164' is adapter id(uuid)
    and '0' is the port number of the adapter.
    Usually each adapter has multiple port so we need to use one port.
    """)
]


def register_opts(conf):
    conf.register_group(dpm_group)
    conf.register_opts(ALL_DPM_OPTS, group=dpm_group)


def list_opts():
    return {dpm_group: ALL_DPM_OPTS}
