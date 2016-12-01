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
from nova.i18n import _LW
from nova_dpm.virt.dpm import host as Host
from nova_dpm.virt.dpm import utils

from nova.virt import driver
from oslo_log import log as logging
from oslo_utils import importutils

import nova_dpm.conf
import requests.packages.urllib3


LOG = logging.getLogger(__name__)
CONF = nova_dpm.conf.CONF

zhmcclient = None


class DPMDriver(driver.ComputeDriver):

    def __init__(self, virtapi):
        super(DPMDriver, self).__init__(virtapi)
        LOG.warning(_LW("__init__"))
        self.virtapi = virtapi
        self._compute_event_callback = None

        self._host = None
        self._client = None

        '''Retrieve zhmc ipaddress, username, password from the nova.conf'''
        zhmc = CONF.dpm.hmc_host
        userid = CONF.dpm.hmc_username
        password = CONF.dpm.hmc_password

        self._get_zhmclient(zhmc, userid, password)
        LOG.warning(_LW("HMC details %(zhmc)s %(userid)s"),
                    {'zhmc': zhmc, 'userid': userid})

    def _get_zhmclient(self, zhmc, userid, password):
        LOG.warning(_LW("_get_zhmclient"))
        '''TODO the below line will be removed once the warnings are
        supressed within zhmclient code'''
        requests.packages.urllib3.disable_warnings()

        global zhmcclient
        if zhmcclient is None:
            zhmcclient = importutils.import_module('zhmcclient')

        session = zhmcclient.Session(zhmc, userid, password)
        self._client = zhmcclient.Client(session)

    def init_host(self, host):
        """Driver initialization of the hypervisor node"""
        LOG.warning(_LW("init_host"))

        '''retrieve from ncpu service configurationfile'''
        conf = {'hostname': CONF.dpm.host,
                'uuid': CONF.dpm.uuid,
                'max_processors': CONF.dpm.max_processors,
                'max_memory_mb': CONF.dpm.max_memory,
                'max_partitions': CONF.dpm.max_instances
                }

        cpc = self._client.cpcs.find(**{"object-id": conf['uuid']})
        LOG.debug("Matching hypervisor found %(host)s for UUID "
                  "%(uuid)s and CPC %(cpcname)s",
                  {'host': conf['host'],
                   'uuid': conf['uuid'],
                   'cpcname': cpc.properties['name']})

        utils.valide_host_conf(conf, cpc)
        self._host = Host.Host(conf, cpc, self._client)

    def get_available_resource(self, nodename):
        """Retrieve resource information.

        This method is called when nova-compute launches, and
        as part of a periodic task that records the results in the DB.

        :param nodename:
            node which the caller want to get resources from
            a driver that manages only one node can safely ignore this
        :returns: Dictionary describing resources
        """
        LOG.warning(_LW("get_available_resource"))

        dictval = self._host.properties

        return dictval

    def get_available_nodes(self, refresh=False):
        """Returns nodenames of all nodes managed by the compute service.

        This method is for multi compute-nodes support. If a driver supports
        multi compute-nodes, this method returns a list of nodenames managed
        by the service. Otherwise, this method should return
        [hypervisor_hostname].
        TODO:Refresh parameter should be handled to freshly fetch the nodenames
        """
        LOG.warning(_LW("get_available_nodes return node %(hostname)s"),
                    {'hostname': self._host.properties["hypervisor_hostname"]})
        nodenames = [self._host.properties["hypervisor_hostname"]]

        return nodenames

    def node_is_available(self, nodename):
        """Return whether this compute service manages a particular node."""
        LOG.warning(_LW("node_is_available"))

        if nodename in self.get_available_nodes():
            return True
        # Refresh and check again.
        return nodename in self.get_available_nodes(refresh=True)

    def get_num_instances(self):
        LOG.warning(_LW("get_num_instances"))
        '''TODO: Will be updated with actual number of instances'''
        return 0
