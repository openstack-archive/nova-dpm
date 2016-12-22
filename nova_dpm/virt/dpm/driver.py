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

"""
A connection to a z Systems through Dynamic Partition Manager( DPM) APIs.

Supports DPM APIs for virtualization in z Systems
"""
from nova_dpm.virt.dpm import host as Host
from nova_dpm.virt.dpm import partition
from nova_dpm.virt.dpm import utils
from nova_dpm.virt.dpm import vm

from nova import context as context_object
from nova.objects import flavor as flavor_object
from nova.virt import driver
from oslo_log import log as logging
from oslo_utils import importutils

import nova_dpm.conf
import requests.packages.urllib3


LOG = logging.getLogger(__name__)
CONF = nova_dpm.conf.CONF

CPCSUBSET_NAME = 'cpcsubset_name'
CPC_UUID = 'cpc_uuid'
MAX_PROCESSORS = 'max_processors'
MAX_MEMORY_MB = 'max_memory_mb'
MAX_PARTITIONS = 'max_partitions'
OBJECT_ID = 'object-id'
HYPERVISOR_HOSTNAME = 'hypervisor_hostname'

zhmcclient = None


class DPMDriver(driver.ComputeDriver):

    def __init__(self, virtapi):
        super(DPMDriver, self).__init__(virtapi)
        LOG.debug("__init__")
        self.virtapi = virtapi
        self._compute_event_callback = None

        self._host = None
        self._client = None
        self._cpc = None

        # Retrieve zhmc ipaddress, username, password from the nova.conf
        zhmc = CONF.dpm.hmc
        userid = CONF.dpm.hmc_username
        password = CONF.dpm.hmc_password

        self._get_zhmclient(zhmc, userid, password)
        LOG.debug("HMC details %(zhmc)s %(userid)s"
                  % {'zhmc': zhmc, 'userid': userid})

    def _get_zhmclient(self, zhmc, userid, password):
        LOG.debug("_get_zhmclient")
        # TODO(preethipy): The below line will be removed once the warnings are
        # supressed within zhmclient code
        requests.packages.urllib3.disable_warnings()

        global zhmcclient
        if zhmcclient is None:
            zhmcclient = importutils.import_module('zhmcclient')

        session = zhmcclient.Session(zhmc, userid, password)
        self._client = zhmcclient.Client(session)

    def init_host(self, host):
        """Driver initialization of the hypervisor node"""
        LOG.debug("init_host")

        # retrieve from ncpu service configurationfile
        self._conf = {CPCSUBSET_NAME: CONF.dpm.host,
                      CPC_UUID: CONF.dpm.cpc_uuid,
                      MAX_PROCESSORS: CONF.dpm.max_processors,
                      MAX_MEMORY_MB: CONF.dpm.max_memory,
                      MAX_PARTITIONS: CONF.dpm.max_instances
                      }

        self._cpc = self._client.cpcs.find(**{OBJECT_ID: self._conf[CPC_UUID]})
        LOG.debug("Matching hypervisor found %(cpcsubset_name)s for UUID "
                  "%(uuid)s and CPC %(cpcname)s" %
                  {'cpcsubset_name': self._conf[CPCSUBSET_NAME],
                   'uuid': self._conf[CPC_UUID],
                   'cpcname': self._cpc.properties['name']})

        utils.valide_host_conf(self._conf, self._cpc)
        self._host = Host.Host(self._conf, self._cpc, self._client)

    def get_available_resource(self, nodename):
        """Retrieve resource information.

        This method is called when nova-compute launches, and
        as part of a periodic task that records the results in the DB.

        :param nodename:
            node which the caller want to get resources from
            a driver that manages only one node can safely ignore this
        :returns: Dictionary describing resources
        """
        LOG.debug("get_available_resource")

        dictval = self._host.properties

        return dictval

    def get_available_nodes(self, refresh=False):
        """Returns nodenames of all nodes managed by the compute service.

        This method is for multi compute-nodes support. If a driver supports
        multi compute-nodes, this method returns a list of nodenames managed
        by the service. Otherwise, this method should return
        [hypervisor_hostname].
        """
        # TODO(preethipy): Refresh parameter should be handled to fetch
        # updated nodenames
        LOG.debug("get_available_nodes return node %(cpcsubset_name)s" %
                  {'cpcsubset_name': self._host.properties[
                      HYPERVISOR_HOSTNAME]})
        nodenames = [self._host.properties[HYPERVISOR_HOSTNAME]]

        return nodenames

    def node_is_available(self, nodename):
        """Return whether this compute service manages a particular node."""
        LOG.debug("node_is_available")

        if nodename in self.get_available_nodes():
            return True
        # Refresh and check again.
        return nodename in self.get_available_nodes(refresh=True)

    def get_num_instances(self):
        LOG.debug("get_num_instances")
        # TODO(preethipy): Will be updated with actual number of instances
        return 0

    def get_info(self, instance):

        info = vm.InstanceInfo()

        return info

    def spawn(self, context, instance, image_meta, injected_files,
              admin_password, network_info=None, block_device_info=None,
              flavor=None):

        if not flavor:
            context = context_object.get_admin_context(read_deleted='yes')
            flavor = (
                flavor_object.Flavor.get_by_id(context,
                                               instance.instance_type_id))
        LOG.debug("Flavor = %(flavor)s" % {'flavor': flavor})

        part = partition.Partition(instance, flavor)
        partition_manager = zhmcclient.PartitionManager(self._cpc)
        _partition = partition_manager.create(part.properties())
        self._create_nic(_partition, network_info=network_info)

        # TODO(pranjank): implement start partition

    def _create_nic(self, _partition, network_info):
            # TODO(preethipy): This function can be moved to Partition.py
            # TODO(preethipy): Implement the listener flow to register for
            # nic creation events
            LOG.debug("Creating nic interface for the instance")

            for vif in network_info:

                port_id = vif['id']
                vif_type = vif['type']
                mac = vif['address']
                vif_details = vif['details']
                dpm_object_id = vif_details[OBJECT_ID]

                # Only dpm_vswitch attachments are supported for now
                if vif_type != "dpm_vswitch":
                    raise Exception

                dpm_nic_dict = {
                    "name": "OpenStack_Port_" + port_id,
                    "description": "OpenStack mac= " + mac +
                                   ", CPCSubset= " +
                                   self._conf[CPCSUBSET_NAME],
                    "virtual-switch-uri": "/api/virtual-switches/"
                                          + dpm_object_id
                }
                nic_interface = _partition.nics.create(dpm_nic_dict)
                LOG.debug("NIC created successfully %(nic_name) "
                          "with URI %(nic_uri)"
                          % {'nic_name': nic_interface.properties['name'],
                             'nic_uri': nic_interface.properties[
                                 'virtual-switch-uri']})
