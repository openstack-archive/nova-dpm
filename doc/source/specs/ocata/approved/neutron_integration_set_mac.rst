..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=============================================
Neutron Integration - Setting the MAC address
=============================================

https://blueprints.launchpad.net/nova-dpm/+spec/neutron-integration-set-mac

DPM does not support setting the MAC address for a NIC on its NIC creation.
To workaround that, this blueprint proposes to set the MAC address from
inside of the guest operating system.

Problem Description
===================

DPM does not support setting the MAC address for a NIC on its NIC creation.
It does also not offer a way to query the MAC address of an already created
NIC. Therefore the MAC of the DPM NIC should be changed from within the
operating system to ensure that the actual used MAC is equal the MAC of
the Neutron port. That happens via a udev rule and a corresponding shell
script.

Use Cases
---------

* Attaching an instance to the network while using the correct MAC address

* Assignment of IP addresses from the OpenStack DHCP

* Using cloud-init to setup the networking with static ips (requires the MAC
  to be set correctly)

Proposed Change
===============

Nova adds the relevant data to the 'boot-os-specific-parameters' property
of an instance. This gets attached to the kernels cmdline during boot.
The boot process itself ignores this data. Finally it's available in the
guest operating system under `/proc/cmdline`.
If a new qeth interface gets defined in the guest, a udev rule triggers
a script which is able to read the relevant information from the
cmdline and set the MAC for that interface accordingly. This also works for
interfaces that are brought up during boot.

.. note::
    Updating the 'boot-os-specific-parameters' property on a running partition
    will not be reflected in /proc/cmdline. This requires the partition to
    stopped and started again (A inband reboot is not sufficient).

The format of the parameters is the following::

  <devno>,<port-no>,<mac>;

Where

* <devno> is the first device number, of the qeth device added, e.g. '0001'

* <port-no> is the port number of the adapter, e.g. '0' or '1'

* <mac> is the MAC address to be set, without the ':' delimiter,
  e.g. 'aabbccddeeff'

The udev rule should call the script to configure the MAC for qeth devices
only. As argument it passes in something that contains the interfaces device
number.

Due to the limitations of the 'boot-os-specific-parameters' property the
maximum amount of Ports (NICs) per instance (partiton) is limited.

* Max len of 'boot-os-specifc-parameters' = 256

* len required per NIC = 20 (0001,1,aabbccddeeff;)

* Max number of NICs = 256/20 = 12,8

-> A single partition can not have more than 12 NICs.

.. note::
  This number goes with the assumption that the 'boot-os-specific-parameters'
  property is used by this feature exclusively.

Alternatives
------------

Using the ConfigDrive to provide the relevant information. This would add
certain complexity to the scripts in the operating system. Those scripts would
need to find and mount that ConfigDrive. A bunch of code would be required for
that. In addition the ConfigDrive is not available in Ocata.

Keeping the DPM chosen MAC and pushing this one back to Neutron.
The problem with this approach is, that the Neutron port is created in the
nova manager before any virt-driver gets invoked. Nova manager requests the
port creation and binds it to the target host. Once the port is bound, changing
the MAC is not possible anymore. That means, that the nova-dpm driver would
need to unbind the port, change the MAC, bind it again.

In addition there's no way to get the DPM chosen MAC address, as an
appropriate attribute on the DPM NIC object does not exist.

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

The max number of Ports (NICs) per Instance (partition) is limited to 12.

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
  <andreas-scheuring>

Other contributors:
  None

Work Items
----------

* All in one :)

Dependencies
============

* Initial Neutron integration: https://blueprints.launchpad.net/nova-dpm/+spec/neutron-integration

Testing
=======

* Unittest

Documentation Impact
====================

Document the limitation of maximum 12 Ports per Instance.

References
==========

* Nova ConfigDrive support: https://blueprints.launchpad.net/nova-dpm/+spec/config-drive