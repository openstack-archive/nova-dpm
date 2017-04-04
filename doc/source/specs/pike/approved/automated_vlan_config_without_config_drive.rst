..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=================================================
Automated VLAN configuration without config Drive
=================================================

https://blueprints.launchpad.net/nova-dpm/+spec/neutron-integration-vlan

This blueprint proposes an automated way for VLAN device and IP configuration
in the operating system using cloud-init.

Problem Description
===================

Nova-DPM instances should be able to participate in VLAN networks. As VLAN
tagging is not available in z13 DPM rel. 1, VLANs can only be configured
from inside the operation system. This can be done manually. This blueprint
proposes an automated way of achieving this.

Spec [1] proposes how to achieve this in a clean way using the Config Drive.
As the Config Drive is not available in Pike, another workaround is required.

Use Cases
---------

* Automated VLAN device and IP configuration using cloud-init without config
  drive

Proposed Change
===============

* provide the VLAN via the kernels cmdline
* create the VLAN device via guest-image tools
* exploit the cloud-init fallback datasource to do dhcp configuration on top
  of it

Known restrictions:

* The fallback datasource provides DHCP connectivity for a single interface
  only


Provide the VLAN id to the kernels cmdline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The VLAN id must be provided to the operating system. The current way of doing
that is using the partitions 'boot-os-specific-parameters' property which gets
appended to the kernels cmdline. As of today, the mac address and the port
number is passed in using this way. The format for each Port/NIC is::

  <devno>,<port-no>,<mac>;

Nova-dpm needs to extend this string by the VLAN id that should be used for
each Port/NIC::

  <devno>,<port-no>[,<vlan-id>],<mac>;

.. note::
   The VLAN id is placed before the mac, as the mac attribute might go away
   one day.

Nova-dpm can retrieve the VLAN id of the interface from the vif dict:

.. code-block:: python

    vif_details = vif['details'] = {
        "vswitch_id":"dff0b71c-d491-11e4-a555-020000003058",
        "vlan":"1",
        "vlan_mode": "inband"
        }
    vlan = vif_details['vlan'] = 1
    vlan_mode = vif_details['vlan_mode'] = "inband"

If the *vlan_mode* is set to *inband*, the VLAN property should be added.
At the moment only the mode *inband* is supported at all.

Create the VLAN device via guest-image tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The guest-image-tools should create a VLAN interface for the NIC, if the
VLAN parameter is present in the kernels cmdline.

OSA and hipersockets network interface are named like this

* Ubuntu: enc<devno>, e.g. enc1, encabcd
* SLES: enccw0.0.<devno>, e.g. enccw0.0.0001, enccw0.0.abcd
* SLES: enccw0.0.<devno>, e.g. enccw0.0.0001, enccw0.0.abcd

The cloud-init fallback network configuration configures the first interface
in the alphabetical sorted list of interfaces [2]. We need to ensure that
the VLAN interface becomes the first one in this list by its name.

The proposal is to name the vlan device like this::

  _<base-interface-name>.<vlan-id>

E.g. _enc1.99, _encabcd.200

This works out fine for Ubuntu device names, but will cause troubles with the
long device names used on SLES and RHEL. 2 Options exist

1. Rename the base device to the Ubuntu naming scheme (this is what [1]
   proposes as well)

2. Just name the vlan device along the Ubuntu naming scheme but keep the base
   device untouched. E.g. _enc1.99, _encabcd.200

Regardless which option is chose, it will not be backwards compatible to the
approach described with using the Config Drive in [1]. Cloud-init has a fix
naming scheme for VLAN devices, which is <base-interface-name>.<vlan-id>.

Cloud-init fallback datasource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Basically described in the paragraph above!


Alternatives
------------

Use the cmdline to pass in network config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is supported by cloud-init. However the network configuration for the
creation of a VLAN device and assigning an IP to it is > 300 chars. But the
*boot-os-specific-parameters* property (which is the way of how to append
something to the cmdline) only supports 256 chars.


cmdline argument (base64 encoded)::

  network-config=Y29uZmlnOgotIG1hY19hZGRyZXNzOiBmYToxNjozZTplZDo5YTo1OQogIG10dTogMTQ1MAogIG5hbWU6IGZvbzMKICBzdWJuZXRzOiBbXQogIHR5cGU6IHBoeXNpY2FsCi0gbWFjX2FkZHJlc3M6IGZhOjE2OjNlOmVkOjlhOjU5CiAgbmFtZTogZm9vMy4xMDEKICBzdWJuZXRzOgogIC0ge3R5cGU6IGRoY3A0fQogIHR5cGU6IHZsYW4KICB2bGFuX2lkOiAxMDEKICB2bGFuX2xpbms6IGZvbzMKdmVyc2lvbjogMQo=

decoded::

    config:
    - mac_address: fa:16:3e:ed:9a:59
      mtu: 1450
      name: foo3
      subnets: []
      type: physical
    - mac_address: fa:16:3e:ed:9a:59
      name: foo3.101
      subnets:
      - {type: dhcp4}
      type: vlan
      vlan_id: 101
      vlan_link: foo3
    version: 1

Upgrade impact
--------------

None

But there might be issues in the future, once the VLAN device gets created
by cloud-init [1].

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

* Enhance guest-image-tools
* add code to nova-dpm

Dependencies
============

None

Testing
=======

* Unittest

Documentation Impact
====================

TBD

References
==========

[1] https://review.openstack.org/410726
[2] https://git.launchpad.net/cloud-init/tree/cloudinit/net/__init__.py?id=0.7.9#n121