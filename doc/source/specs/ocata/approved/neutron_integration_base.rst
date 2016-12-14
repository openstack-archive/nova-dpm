..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=======================================
Base support Nova Neutron Communication
=======================================

https://blueprints.launchpad.net/nova/+spec/neutron-integration

The nova-dpm virt driver needs integration into Neutron to allow instance
networking.

Problem Description
===================

The nova-dpm virt driver needs integration into Neutron to allow instance
networking. The initial integration comes with the following restrictions:

* MAC address of Neutron port is not equal the actual used MAC address of the
  NIC. This has the following known impact

  * Addresses from Neutron DHCP server do not get assigned

  * Workaround: Set the Neutron port dpm manually from within the operating
    system

* Only flat networking supported

* No live attach of an interface (attaching only works on boot)

Use Cases
---------

* Starting a DPM instance with NICs attached

Proposed Change
===============

*Worksplit Nova Neutron*

* Nova is responsible for the partition object and all its sub resources.
  This includes the NIC object.

* Neutron is responsible for the vSwitch and the (network) adapter objects and
  all its sub resources.

* In addition to that, Neutron should manage everything networking related
  that can be changed while a port is attached to an instance. Therefore
  some overlap in the NIC object might exist.


Background::

    * Attaching the instance to the network is job of Nova, also in other virt
      drivers like for libvirt.

    * In fully virtualized systems there's is a differentiation between the
      actual NIC (managed by Nova) and the virtual switch port (managed by
      Neutron). DPM does not offer this differentiation.

*DPM Objects manged by Nova*

* Partition

  * Create NIC: POST /api/partitions/{partition-id}/nics

  * Delete NIC: DELETE /api/partitions/{partition-id}/nics/{nic-id}

  * Get NIC Properties: GET /api/partitions/{partition-id}/nics/{nic-id}

    ::

      "class":"nic",
      "description":"",
      "device-number":"000A",
      "element-id":"97de6092-c049-11e5-8f1f-020000000108",
      "element-uri":"/api/partitions/67782eb8-c041-11e5-92b8-020000000108/nics/
      97de6092-c049-11e5-8f1f-020000000108",
      "name":"jn",
      "parent":"/api/partitions/67782eb8-c041-11e5-92b8-020000000108",
      "type":"osd",
      "virtual-switch-uri":"/api/virtual-switches/6a428720-b9d3-11e5-9e34-020000000108"

  * Update NIC Properties: POST /api/partitions/{partition-id}/nics/{nic-id}

*DPM Objects managed by Neutron*

* Adapter

  * Get Adapter Properties: GET /api/adapters/{adapter-id}

    ::

      "adapter-family":"ficon",
      "adapter-id":"141",
      "allowed-capacity":32,
      "card-location":"Z22B-D207-J.01",
      "channel-path-id":"01",
      "class":"adapter",
      "configured-capacity":1,
      "description":"",
      "detected-card-type":"ficon-express-8",
      "maximum-total-capacity":255,
      "name":"FCP 0141 Z22B-07",
      "object-id":"d71902a4-c930-11e5-a978-020000000338",
      "object-uri":"/api/adapters/d71902a4-c930-11e5-a978-020000000338",
      "parent":"/api/cpcs/87dbe268-0b43-362f-9f80-c79923cc4a29",
      "physical-channel-status":"operating",
      "port-count":1,
      "state":"online",
      "status":"active",
      "storage-port-uris":[
      "/api/adapters/d71902a4-c930-11e5-a978-020000000338/storage-ports/0"
      ],
      "type":"fcp",
      "used-capacity":1

  * Update Adapter Properties: POST /api/adapters/{adapter-id}

  * Create Hipersockets: POST /api/cpcs/{cpc-id}/adapters

  * Delete Hipersockets: DELETE /api/adapters/{adapter-id}

  * Get Network Port Properties: GET /api/adapters/{adapter-id}/network-ports/{network-port-id}

    ::

      "class":"network-port",
      "description":"",
      "element-id":"0",
      "element-uri":"/api/adapters/e77d39f8-c930-11e5-a978-020000000338/network-ports/0",
      "index":0,
      "name":"Port 0",
      "parent":"/api/adapters/e77d39f8-c930-11e5-a978-020000000338"

  * Update Network Port Properties: POST /api/adapters/{adapter-id}/network-ports/{network-port-id}

* Virtual Switch

  * Get Virtual Switch Properties: GET /api/virtual-switches/{vswitch-id}

    ::

      "backing-adapter-uri":"/api/adapters/f718c7a0-d490-11e4-a555-020000003058","class":"virtual-switch",
      "description":"",
      "name":"PrimeIQDVSwitch1",
      "object-id":"f6b4c70e-d491-11e4-a555-020000003058",
      "object-uri":"/api/virtual-switches/f6b4c70e-d491-11e4-a555-020000003058",
      "parent":"/api/cpcs/8e543aa6-1c26-3544-8197-4400110ef5ef",
      "port":0,
      "type":"hipersockets"

  * Update Virtual Switch Properties: POST /api/virtual-switches/{vswitch-id}


*Potential overlap between Nova and Neutron*

There's no doubt about that Nova should create the NIC object. However some
attributes of the NIC object might need to be managed by Neutron.

The questionable attribute would be

* device-number

The plan is, to use the device number auto assignment offered by DPM.
Neutron is not aware of the device numbers at all. Only Nova needs to know
about device numbers for adding this information to the metadata.

.. note::
  In future dpm releases there might additional questionable attributes
  like the a anti spoofing feature or setting the link up/down.

*Mapping OpenStack API - DPM API*

This is a mapping of OpenStack API calls and resulting DPM API calls.

.. list-table:: OpenStack API - DPM API Mapping
    :header-rows: 1

    * - OpenStack API
      - DPM API
    * - Nova: Create instance on network
      - Create NIC
    * - Nova: Delete instance with attached
      - Delete NIC
    * - Nova: Attach interface
      - Create NIC
    * - Nova: Detach interface
      - Delete NIC
    * - Neutron: Create Port
      - n/a
    * - Neutron: Delete Port
      - n/a
    * - Neutron: Update Port - change MAC
      - n/a ( 1 )

Out of scope are

* Quality of service ( 2 )

* Security Groups ( 2 )

* Setting MTU ( 3 )


( 1 ) If a port is bound to a certain host (the corresponding DPM NIC object
exists), changing the MAC is denied by Neutron. If the port is unbound,
updating the MAC is allowed by Neutron.

( 2 ) Not available in z13, DPM rel. 1

( 3 ) Not required. Automatically done by Operating System. MTU is part of
DHCP offers or cloud-init configuration.

*The 'host' identifier*

The 'host' attribute is an unique identifier for a hypervisor. It is used
by Nova and by Neutron. During spawn call, Nova requests a Neutron port to
be created for a certain hypervisor. The hypervisor is identified by this
host identifier. It's part of the create port call. For more details, see
the flow diagram further below.

*Boot Instance*

The Nova call "boot instance" attaches the partition to the networks. The
following steps are required:

* Retrieve the relevant information from Neutron

* Create the NIC

*Retrieving the relevant information from Neutron*

The nova compute manager already does this. Then it calls the virt drivers
"spawn" method passing a list of VIF (Virtual Interface) dicts.
This list is named *network_info*. A VIF dict represents a Neutron port and
contains all relevant information that Nova needs.

::
  for vif in network_info:
     # do something with vif


.. note::
    There is currently a transition going on, to transform all VIF dicts
    into an os-vif object `[6]`_. Nova already started that transition in the
    VIFDriver (see below). The final goal is to use this object for
    Neutron as well. But Neutron did not yet adopt to it and only a few
    Nova vif_types already switched to the new object.

Generation of the *network_info* list and its VIF dicts happens in
*neutronv2/api.py* method *_build_network_info_model* `[7]`_.

The VIF dict is defined in *network/model.py* `[8]`_.

In the DPM case the relevant keys of the vif dict are the following::

    port_id = vif['id'] = a3578bdc-d491-11e4-a555-020000843678
    vif_type = vif['type'] = dpm
    vif_details = vif['details'] = {
        "vswitch_id":"dff0b71c-d491-11e4-a555-020000003058",
        }
    vswitch_id = vif_details['vswitch_id'] = dff0b71c-d491-11e4-a555-020000003058
    vnic_type = vif['vnic_type'] = normal


*Create the NIC*

Nova needs to create the NIC on the partition object.

First Nova need to check the *vif_type* to assess if it can support such a
network attachment. At the beginning, the nova dpm driver will only support
the type "dpm". If a port has another *vif_type*, processing should fail.

The following pseudo code should do the job
::

    if vif_type != "dpm":
       raise Exception

.. note::
  The Nova libvirt driver implements a VIFDriver framework, to support
  different *vif_type* attachments `[5]`_. A vif driver does 3 things:
  Define the configuration of the NIC, do some plumbing that is required
  to do the NIC creation (plug) and do some cleanup after a NIC got deleted
  (unplug). As we do not need any plumbing for dpm done, the plan is to not
  implement such a framework in the initial release. This will also speeds up
  development.

  Support for the VIFDriver framework and os-vif will be introduced
  in a later release.


The NIC can be created via the following DPM API for OSA and Hipersockets:::

    POST /api/partitions/{partition-id}/network-adapters/
    {
      "name": {port_id},
      "description": "Managed by OpenStack CPCSubset {host-identifier}",
      "virtual-switch-uri": "/api/virtual-switches/{vswitch_id}",
    }


.. note::
  Having the port_id in the name attribute is important. It will later on be
  used by the Neutron agent to map a NIC object to a Neutron port! Also Novas
  detach interface probably needs to identify the NIC along the ports UUID.

.. note::
   Having the host-identifier at the NIC is also of importance. The same
   adapter might be used by different CPCSubsets. Adding the host-identifier
   we can ensure, that only the neutron agent that is responsible for the
   CPCSubset handles those NICs. Otherwise those NICs would be reported on
   both agents a "up" which leads to confusion in the neutron-server. The
   proposal is to add the host-identifier somewhere in the description field.
   Neutron will check for this.

.. note::
  There is no need for Nova to know if the vswitch object corresponds to an
  OSA adapter or an Hipersockets adapter. The DPM API for attaching those
  types is the same.

.. note::
  The RoCE adapter is not supported at all. Once it becomes supported, the
  *vif_details* dictionary will contain extra information to identify it as
  RoCE.


*Boot Instance Flow*

.. seqdiag::
   :scale: 80
   :alt: pxe_ipmi

   diagram {
      // Do not show activity line
      #activation = none;
      n-manager; n-virt-drv; q-svc; HMC

      n-manager -> q-svc [label = "create port
        {network:private,
        host_id:host}",
        leftnote = "_build_and_run_instance"];
      n-manager <-- q-svc [label = "port {vif_type:dpm,
          vif_details={vswitch_id:uuid}"];

      n-manager -> n-manager [label = "create network_info"];

      n-manager -> n-virt-drv [label= "spawn(network_info)"];

      n-virt-drv -> HMC [label = "create partition"];
      n-virt-drv <-- HMC;

      n-virt-drv -> n-virt-drv [label = "With wait for vif-plugged-event:"];

      n-virt-drv -> HMC [label = "add NIC to partition"];
      n-virt-drv <-- HMC;

      q-svc ->> n-virt-drv [label = "vif-plugged-event",
          note = "NIC object detected"];
      q-svc <<-- n-virt-drv

      n-virt-drv -> HMC [label = "start partition"];
      n-virt-drv <-- HMC

      n-manager <- n-virt-drv;

    }

.. note::
  There's an effort going on to move the Port creation from nova-manager to
  nova conductor [9].

* On _build_and_run_instance, nova compute manager (n-manager) asks Neutron
    to create a port with the following relevant details

  * host = the host identifier (hypervisor) on which the instance should be
    spawned

  * network = the network that the instance was launched on

* Nova manager creates the *network_info* list out of this information

* Nova manager calls the nova virt-driver (n-virt-drv) to spawn the instance
  passing in the *network_info* list

* Nova virt-driver creates the Partition (This can also done before the port
  details are requested).

* Nova virt-driver attaches the NIC to the partition and waits for the
  vif-plugged-event

* The Neutron server sends the vif-plugged-event to Nova (detects that the VIF
  has been created)

* Nova virt-driver starts the partition.

Alternatives
------------

None

Data model impact
-----------------

None

REST API impact
---------------

None

Security impact
---------------

None

Notifications impact
--------------------

None

Other end user impact
---------------------

None

Performance Impact
------------------

None

Other deployer impact
---------------------

None

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <launchpad-id or None>

Other contributors:
  <launchpad-id or None>

Work Items
----------

* All in one :)

Dependencies
============

Neutron DPM ML2 mechanism driver and agent
https://bugs.launchpad.net/networking-dpm/+bug/1646095

Testing
=======

* Unittest

Documentation Impact
====================

TBD

References
==========

.. _[5]: https://github.com/openstack/nova/blob/master/nova/virt/libvirt/vif.py
.. _[6]: https://github.com/openstack/os-vif
.. _[7]: https://github.com/openstack/nova/blob/master/nova/network/neutronv2/api.py#L2136
.. _[8]: https://github.com/openstack/nova/blob/master/nova/network/model.py#L347
.. _[9]: http://lists.openstack.org/pipermail/openstack-dev/2016-November/107476.html