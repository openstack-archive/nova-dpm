.. _getting_started:

======================================
Getting Started with OpenStack for DPM
======================================

This section gets you started with OpenStack for DPM.

It assumes

* an existing OpenStack controller, in which the DPM parts will be
  integrated

* A system where the new compute node can be installed.

  This can either be a separate system but could also be the controller
  node itself (single node setup). Fore more information on topology see
  the doc :ref:`topology`.

Compute
-------

The following actions are done for the compute node.


#. Install the following packages

  * Nova

  * nova-dpm (see :ref:`installation`)

#. Configure the nova-compute service for DPM

    Make sure you can answer the following questions:

    * Which CPC managed by the HMC should be used by OpenStack?

    * How many partitions of this CPC should OpenStack be able to consume?

    * How many shared IFL processors should be available for instances created
      by OpenStack?

    * How much Memory should be available for instances created by OpenStack

    * Which Storage adapter ports should be used for attaching FC storage?

    * Which name should be used to identify this Subset of the CPC?

   With this information you should be able to create the corresponding
   configuration file with the help of the :ref:`configuration` documentation.

#. Start the nova-compute service

    ::

        /usr/bin/python /usr/local/bin/nova-compute --config-file /etc/nova/nova.conf

    .. note::
        The file *nova.conf* must contain all the DPM specific configuration
        options.

#. Verify if the service is running

    ::

        # openstack compute service list
        +----+------------------+----------+----------+---------+-------+----------------------------+
        | ID | Binary           | Host     | Zone     | Status  | State | Updated At                 |
        +----+------------------+----------+----------+---------+-------+----------------------------+
        |  4 | nova-conductor   | control1 | internal | enabled | up    | 2017-02-22T10:31:08.000000 |
        |  5 | nova-scheduler   | control1 | internal | enabled | up    | 2017-02-22T10:31:01.000000 |
        |  6 | nova-consoleauth | control1 | internal | enabled | up    | 2017-02-22T10:31:08.000000 |
        |  7 | nova-compute     | subset_1 | nova     | enabled | up    | 2017-02-22T10:30:59.000000 |
        +----+------------------+----------+----------+---------+-------+----------------------------+

    -> Amongst others a nova-compute service for the chosen subset host name
    (subset_1) should show up.

    ::

        # openstack hypervisor list
        +----+---------------------+-----------------+-----------------+-------+
        | ID | Hypervisor Hostname | Hypervisor Type | Host IP         | State |
        +----+---------------------+-----------------+-----------------+-------+
        |  1 | subset_1            | PRSM            | xxx.xxx.xxx.xxx | up    |
        +----+---------------------+-----------------+-----------------+-------+

    -> A hypervisor of type PRSM using the same hostname like above should
    show up.


Storage
-------

There is no storage related service required on the compute node. The compute
node does not require a FC storage attachment at all.

On the controller node the cinder volume service must be configured for
FC usage.

For more details see :ref:`storage`.

Networking
----------

#. Install the following packages on the compute and the existing controller
   node

  * Neutron

  * networking-dpm (see`documentation
    <http://networking-dpm.readthedocs.io/en/latest/installation.html>`_)

#. Configure the neutron DPM mechanism driver on the existing controller node

    The DPM mechanism driver must be configured to be used by the Neutron
    servers ML2 plug-in. Other drivers required by the network node might
    be configured in parallel.
    For more details see the `configuration documentation
    <http://networking-dpm.readthedocs.io/en/latest/configuration.html>`_.
    After the configuration change the Neutron server must be restarted
    to apply the changes.

#. Configure the neutron dpm agent for DPM for the compute node

    Make sure you can answer the following questions:

    * Which network adapter ports should be used for instances created by
      OpenStack?

        * The list of supported network adapters can be found
          `here <http://networking-dpm.readthedocs.io/en/latest/hardware_support.html>`_.

    * How many logical networks are required? A dedicated network adapter
      port is required for each logical network.

    With this information you should be able to create the corresponding
    configuration file with the help of the `configuration documentation
    <http://networking-dpm.readthedocs.io/en/latest/configuration.html>`_.

#. Start the neutron dpm agent for the compute node

    ::

        /usr/bin/python /usr/local/bin/neutron-dpm-agent --config-file /etc/neutron/plugins/ml2/neutron_dpm_agent.conf

    .. note::
        The file *neutron_dpm_agent.conf* must contain all the DPM specific
        configuration options. In addition it must specify the CPCSubset
        that it belongs to in the *host* variable of the *DEFAULT* section.

#. Verify if the agent is running

    ::

        # openstack network agent list
        +--------------------------------------+--------------------+----------+-------------------+-------+-------+---------------------------+
        | ID                                   | Agent Type         | Host     | Availability Zone | Alive | State | Binary                    |
        +--------------------------------------+--------------------+----------+-------------------+-------+-------+---------------------------+
        | 0d9ec043-9dcf-478c-a4df-56c93e516ca8 | DPM agent          | subset_1 | None              | True  | UP    | neutron-dpm-agent         |
        | 42264083-e90d-4e7e-9b4f-0675e282d1ef | Metadata agent     | control1 | None              | True  | UP    | neutron-metadata-agent    |
        | 6d2dbc59-db7b-4f34-9c5f-8fe9935ad824 | Open vSwitch agent | control1 | None              | True  | UP    | neutron-openvswitch-agent |
        | af25dea7-1895-4b81-b087-8e30101d2475 | DHCP agent         | control1 | nova              | True  | UP    | neutron-dhcp-agent        |
        +--------------------------------------+--------------------+----------+-------------------+-------+-------+---------------------------+

    -> Amongst others a neutron-dpm-agent for the chosen subset host name
    (subset_1) should be alive.

    ::

        # openstack network agent show 0d9ec043-9dcf-478c-a4df-56c93e516ca8
        +-------------------+-------------------------------------------------------------------------------------------------------------------+
        | Field             | Value                                                                                                             |
        +-------------------+-------------------------------------------------------------------------------------------------------------------+
        | admin_state_up    | UP                                                                                                                |
        | agent_type        | DPM agent                                                                                                         |
        | alive             | True                                                                                                              |
        | availability_zone | None                                                                                                              |
        | binary            | neutron-dpm-agent                                                                                                 |
        | configuration     | {u'extensions': [], u'adapter_mappings': {u'provider': [u'3ea09d2a-b18d-11e6-89a4-42f2e9ef1641']}, u'devices': 0} |
        | created_at        | 2017-02-22 11:47:57                                                                                               |
        | description       | None                                                                                                              |
        | host              | subset_1                                                                                                          |
        | id                | 0d9ec043-9dcf-478c-a4df-56c93e516ca8                                                                              |
        | last_heartbeat_at | 2017-02-22 12:12:57                                                                                               |
        | name              | None                                                                                                              |
        | started_at        | 2017-02-22 11:47:57                                                                                               |
        | topic             | N/A                                                                                                               |
        +-------------------+-------------------------------------------------------------------------------------------------------------------+

    -> The configuration option should show an adapter mapping. It's not
    exactly the same mapping as it was provided in the agents configuration
    file. It's a translated mapping, where the physical network is mapped
    to a vswitch object-id.

Spawning an instance
--------------------

#. Creating a initial network

    Assuming that a physical_network_adapter_mapping containing a physical
    network called *provider* has been defined.

    ::

        # openstack network create --provider-physical-network provider --provider-network-type flat provider
        +---------------------------+--------------------------------------+
        | Field                     | Value                                |
        +---------------------------+--------------------------------------+
        | admin_state_up            | UP                                   |
        | availability_zone_hints   |                                      |
        | availability_zones        |                                      |
        | created_at                | 2017-02-22T12:46:35Z                 |
        | description               |                                      |
        | dns_domain                | None                                 |
        | id                        | 49887552-ea35-41ca-aba2-2df2bb59896d |
        | ipv4_address_scope        | None                                 |
        | ipv6_address_scope        | None                                 |
        | is_default                | None                                 |
        | mtu                       | 1500                                 |
        | name                      | test-net                             |
        | port_security_enabled     | True                                 |
        | project_id                | 561a226832eb4eabb50b05d21c46d9bb     |
        | provider:network_type     | flat                                 |
        | provider:physical_network | provider                             |
        | provider:segmentation_id  | None                                 |
        | qos_policy_id             | None                                 |
        | revision_number           | 3                                    |
        | router:external           | Internal                             |
        | segments                  | None                                 |
        | shared                    | False                                |
        | status                    | ACTIVE                               |
        | subnets                   |                                      |
        | updated_at                | 2017-02-22T12:46:35Z                 |
        +---------------------------+--------------------------------------+


    ::

        # openstack subnet create --dhcp --subnet-range 192.168.222.0/24 --network provider provider_subnet
        +-------------------+--------------------------------------+
        | Field             | Value                                |
        +-------------------+--------------------------------------+
        | allocation_pools  | 192.168.222.2-192.168.222.254        |
        | cidr              | 192.168.222.0/24                     |
        | created_at        | 2017-02-22T12:47:09Z                 |
        | description       |                                      |
        | dns_nameservers   |                                      |
        | enable_dhcp       | True                                 |
        | gateway_ip        | 192.168.222.1                        |
        | host_routes       |                                      |
        | id                | d6e641a7-8c42-43a6-a3e1-193de297f494 |
        | ip_version        | 4                                    |
        | ipv6_address_mode | None                                 |
        | ipv6_ra_mode      | None                                 |
        | name              | provider_subnet                      |
        | network_id        | 49887552-ea35-41ca-aba2-2df2bb59896d |
        | project_id        | 561a226832eb4eabb50b05d21c46d9bb     |
        | revision_number   | 2                                    |
        | segment_id        | None                                 |
        | service_types     |                                      |
        | subnetpool_id     | None                                 |
        | updated_at        | 2017-02-22T12:47:09Z                 |
        +-------------------+--------------------------------------+


#. Check the existing images::

    # openstack image list
    +--------------------------------------+--------------------------+--------+
    | ID                                   | Name                     | Status |
    +--------------------------------------+--------------------------+--------+
    | a249ef36-74d1-48fb-8d65-c4d532fa68e6 | dpm_image                | active |
    +--------------------------------------+--------------------------+--------+

#. Create a volume based on an image::

    # openstack volume create  --image a249ef36-74d1-48fb-8d65-c4d532fa68e6  --size 15 dpm_volume1
    +---------------------+--------------------------------------+
    | Field               | Value                                |
    +---------------------+--------------------------------------+
    | attachments         | []                                   |
    | availability_zone   | nova                                 |
    | bootable            | true                                 |
    | consistencygroup_id | None                                 |
    | created_at          | 2017-02-22T14:42:27.013674           |
    | description         | None                                 |
    | encrypted           | False                                |
    | id                  | 25307859-e227-4f2b-82f8-b3ff3d5caefd |
    | migration_status    | None                                 |
    | multiattach         | False                                |
    | name                | vol_andreas                          |
    | properties          |                                      |
    | replication_status  | None                                 |
    | size                | 15                                   |
    | snapshot_id         | None                                 |
    | source_volid        | 3d5f72ec-9f1d-41fe-8bac-77bc0dc1e930 |
    | status              | creating                             |
    | type                | v7kuni                               |
    | updated_at          | None                                 |
    | user_id             | 0a6eceb0f73f4f37a0fce8936a1023c4     |
    +---------------------+--------------------------------------+

#. Wait until the volume status changed to "available"::

    # openstack volume list
    +--------------------------------------+--------------+-----------+------+-------------+
    | ID                                   | Display Name | Status    | Size | Attached to |
    +--------------------------------------+--------------+-----------+------+-------------+
    | 25307859-e227-4f2b-82f8-b3ff3d5caefd | dpm_volume1  | available |   15 |             |
    +--------------------------------------+--------------+-----------+------+-------------+


#. Check the existing flavors::

    # openstack flavor list
    +-------+-----------+-------+------+-----------+-------+-----------+
    | ID    | Name      |   RAM | Disk | Ephemeral | VCPUs | Is Public |
    +-------+-----------+-------+------+-----------+-------+-----------+
    | 1     | m1.tiny   |   512 |    1 |         0 |     1 | True      |
    | 2     | m1.small  |  2048 |   20 |         0 |     1 | True      |
    +-------+-----------+-------+------+-----------+-------+-----------+



#. Boot the instance::

    # openstack server create --flavor m1.small --volume 25307859-e227-4f2b-82f8-b3ff3d5caefd --nic net-id=49887552-ea35-41ca-aba2-2df2bb59896d dpm_server1
    +-------------------------------------+--------------------------------------+
    | Field                               | Value                                |
    +-------------------------------------+--------------------------------------+
    | OS-DCF:diskConfig                   | MANUAL                               |
    | OS-EXT-AZ:availability_zone         |                                      |
    | OS-EXT-SRV-ATTR:host                | None                                 |
    | OS-EXT-SRV-ATTR:hypervisor_hostname | None                                 |
    | OS-EXT-SRV-ATTR:instance_name       |                                      |
    | OS-EXT-STS:power_state              | NOSTATE                              |
    | OS-EXT-STS:task_state               | scheduling                           |
    | OS-EXT-STS:vm_state                 | building                             |
    | OS-SRV-USG:launched_at              | None                                 |
    | OS-SRV-USG:terminated_at            | None                                 |
    | accessIPv4                          |                                      |
    | accessIPv6                          |                                      |
    | addresses                           |                                      |
    | adminPass                           | TbLsiNT8rN3n                         |
    | config_drive                        |                                      |
    | created                             | 2017-02-22T14:46:24Z                 |
    | flavor                              | m1.small (2)                         |
    | hostId                              |                                      |
    | id                                  | 9b44589c-cd91-4b67-9a9f-2ec88ad1c27d |
    | image                               |                                      |
    | key_name                            | None                                 |
    | name                                | dpm_server1                          |
    | progress                            | 0                                    |
    | project_id                          | e2e0784ca1b64d6cae07d3c6e8d4bcff     |
    | properties                          |                                      |
    | security_groups                     | name='default'                       |
    | status                              | BUILD                                |
    | updated                             | 2017-02-22T14:46:24Z                 |
    | user_id                             | 0a6eceb0f73f4f37a0fce8936a1023c4     |
    | volumes_attached                    |                                      |
    +-------------------------------------+--------------------------------------+
