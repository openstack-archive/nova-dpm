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
        zhmc = CONF.DPM.hmc_ip
        userid = CONF.DPM.hmc_username
        password = CONF.DPM.hmc_password

        self._get_zhmclient(zhmc, userid, password)
        LOG.warning(_LW("hostmanagelist %(zhmc)s %(userid)s %(password)s"),
                    {'zhmc': zhmc, 'userid': userid,
                     'password': password})

    def _get_zhmclient(self, zhmc, userid, password):
        LOG.warning(_LW("_get_zhmclient"))
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
        conf = {'hostname': CONF.DPM.host,
                'cpcname': CONF.DPM.cpc_name,
                'uuid': CONF.DPM.uuid,
                'max_processors': CONF.DPM.max_processors,
                'max_memory_mb': CONF.DPM.max_memory,
                'max_partitions': CONF.DPM.max_instances
                }
        cpclist = self._client.cpcs.list()
        for cpc in cpclist:
            if (conf['cpcname'] == cpc.properties['name']):
                LOG.warning(_LW("Matching hypervisor found %(host)s"),
                            {'host': conf['cpcname']})
                if (utils.valide_host_conf(conf, cpc)):
                    self._host = Host.Host(conf, cpc, self._client)
                break
        if not self._host:
            raise Exception("Valid Host not configured")

    def get_info(self, instance):
        """Get the current status of an instance, by name (not ID!)

        :param instance: nova.objects.instance.Instance object

        Returns a InstanceInfo object
        """
        LOG.warning(_LW("get_info"))

    def get_num_instances(self):
        """Return the total number of virtual machines.

        Return the number of virtual machines that the hypervisor knows
        about.

        .. note::

            This implementation works for all drivers, but it is
            not particularly efficient. Maintainers of the virt drivers are
            encouraged to override this method with something more
            efficient.
        """
        LOG.warning(_LW("get_num_instances"))
        LOG.warning(_LW("Return: %(instances)s"),
                    {'instances': self.list_instances()})
        return len(self.list_instances())

    def instance_exists(self, instance):
        """Checks existence of an instance on the host.

        :param instance: The instance to lookup

        Returns True if an instance with the supplied ID exists on
        the host, False otherwise.

        .. note::

            This implementation works for all drivers, but it is
            not particularly efficient. Maintainers of the virt drivers are
            encouraged to override this method with something more
            efficient.
        """
        LOG.warning(_LW("instance_exists"))
        try:
            LOG.warning(_LW("instance uuid: %(UUID)s"),
                        {'UUID': instance.uuid})
            return instance.uuid in self.list_instance_uuids()
        except NotImplementedError:
            return instance.name in self.list_instances()

    def estimate_instance_overhead(self, instance_info):
        LOG.warning(_LW("estimate_instance_overhead"))
        instance_overhead = {'memory_mb': 0, 'disk_gb': 0}
        return instance_overhead

    def list_instances(self):
        LOG.warning(_LW("list_instances"))

        instances = list()

        LOG.warning(_LW('Return: %(instances)s'), {'instances': instances})
        return instances

    def list_instance_uuids(self):
        LOG.warning(_LW("list_instance_uuids"))

        return {}

    def spawn(self, context, instance, image_meta, injected_files,
              admin_password, network_info=None, block_device_info=None):
        """Create a new instance/VM/domain on the virtualization platform.

        Once this successfully completes, the instance should be
        running (power_state.RUNNING).

        If this fails, any partial instance should be completely
        cleaned up, and the virtualization platform should be in the state
        that it was before this call began.

        :param context: security context
        :param instance: nova.objects.instance.Instance
                         This function should use the data there to guide
                         the creation of the new instance.
        :param nova.objects.ImageMeta image_meta:
            The metadata of the image of the instance.
        :param injected_files: User files to inject into instance.
        :param admin_password: Administrator password to set in instance.
        :param network_info: instance network information
        :param block_device_info: Information about block devices to be
                                  attached to the instance.
        """

        LOG.warning(_LW("spawn"))
        LOG.warning(_LW("instance node %(node)s"), {'node': instance["node"]})
        LOG.warning(_LW("*********************"))

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
        """
        LOG.warning(_LW("get_available_nodes return node %(hostname)s"),
                    {'hostname': self._host.properties["hypervisor_hostname"]})
        self._nodenames = [self._host.properties["hypervisor_hostname"]]

        return self._nodenames

    def node_is_available(self, nodename):
        """Return whether this compute service manages a particular node."""
        LOG.warning(_LW("node_is_available"))

        if nodename in self.get_available_nodes():
            return True
        # Refresh and check again.
        return nodename in self.get_available_nodes(refresh=True)
