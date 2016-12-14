..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==================================================
Neutron Integration - Automated VLAN configuration
==================================================

https://blueprints.launchpad.net/nova-dpm/+spec/neutron-integration-vlan

This blueprint proposes an automated way for VLAN device and IP configuration
in the operating system using cloud-init and ConfigDrive.

Problem Description
===================

Nova-DPM instances should be able to participate in VLAN networks. As VLAN
tagging is not available in z13 DPM rel. 1, VLANs can only be configured
from inside the operation system. This can be done manually. This blueprint
proposes an automated way of achieving this.

Use Cases
---------

* Automated VLAN device and IP configuration

Proposed Change
===============

Use the cloud-init built in features to create the VLAN devices and the
proper ip configuration for the network interfaces.

For the VLAN case the relevant keys of the nova vif dict are the following

.. code-block:: python

    port_id = vif['id'] = a3578bdc-d491-11e4-a555-020000843678
    mac = vif['address'] = aa:aa:aa:bb:bb:bb
    vif_type = vif['type'] = dpm
    vif_details = vif['details'] = {
        "vswitch_id":"dff0b71c-d491-11e4-a555-020000003058",
        "vlan":"1",
        "vlan_mode": "inband"
        }
    vlan = vif_details['vlan'] = 1
    vlan_mode = vif_details['vlan_mode'] = "inband"
    vswitch_id = vif_details['vswitch_id'] = dff0b71c-d491-11e4-a555-020000003058
    vnic_type = vif['vnic_type'] = normal



One way to provide MetaData to the OpenStack instance is the ConfigDrive.
The Nova virt driver is responsible for the creation of the ConfigDrive.

The *network_data.json* needs to be extended to provide cloud-init all the
information for setting up the VLAN.

The *vlan_mode* property of the Neutron ports *vif_details* set to *inband*
indicates that the ConfigDrive metadata should be enriched with the VLAN
information.

* Set the *name* for the underlying *link* object to 'enc<dev-no>'
  (e.g. encabcd). This will become the device name in linux). This is
  important, as the VLAN device will be named along the scheme
  *<dev-name>.<vlan-id>*. With the long default names (enccw.0.0abcd) this
  will lead to issues, as a device name can only consist of 15 chars.

  .. note::
    The device number is available right after NIC creation. Starting
    the partition is not required.

* Add a new link representing the VLAN device. Link it to the corresponding
  existing underlying link.

* Update the corresponding *network* to link to the newly created VLAN *link*
  instead

*Example*

.. note::
  This example also contains the changes required to set the MAC address!
  Those are included in the highlighting!

VIFs passed into Nova spawn call

.. code-block:: python

    vif1['id'] = 00000000-cccc-cccc-cccc-cccccccccccc
    vif1['address'] = cc:cc:cc:cc:cc:cc
    vif1['type'] = dpm
    vif1['details'] = {
        "vswitch_id":"dff0b71c-d491-11e4-a555-020000003058"
        }
    vif1['vnic_type'] = Normal


    vif2['id'] = 00000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa
    vif2['address'] = aa:aa:aa:aa:aa:aa
    vif2['type'] = dpm
    vif2['details'] = {
        "vswitch_id":"dff0b71c-d491-11e4-a555-020000003058",
        "vlan":"1"
        }
    vif2['vnic_type'] = Normal

Result in this *network_data.json* file, if the libvirt generated config drive
method is used.

.. code-block:: json

  {
     "services":[

     ],
     "networks":[
        {
           "network_id":"<UUID-of-net-0>",
           "link":"tap00000000-cc",
           "type":"ipv4_dhcp",
           "id":"network0"
        },
        {
           "network_id":"<UUID-of-net-1>",
           "link":"tap00000000-aa",
           "type":"ipv4_dhcp",
           "id":"network1"
        }
     ],
     "links":[
        {
           "ethernet_mac_address":"cc:cc:cc:cc:cc:cc",
           "mtu":1450,
           "type":"ovs",
           "id":"tap00000000-cc",
           "vif_id":"00000000-cccc-cccc-cccc-cccccccccccc"
        },
        {
           "ethernet_mac_address":"aa:aa:aa:aa:aa:aa",
           "mtu":1450,
           "type":"ovs",
           "id":"tap00000000-aa",
           "vif_id":"00000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        }
     ]
  }


Now the DPM NIC gets created by the Nova virt driver. The properties of this
new NIC are:

.. code-block:: json

  {
    "class":"nic",
    "description":"",
    "device-number":"1234",
    "name":"00000000-cccc-cccc-cccc-cccccccccccc",
    "type":"osd",
  }

  {
    "class":"nic",
    "description":"",
    "device-number":"5678",
    "name":"00000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "type":"osd",
  }


Now the *network_data.json* should be modified to look like this

.. note::
  This also includes the changes for updating the MAC address!

.. code-block:: json
  :emphasize-lines: 8,14,24,26,32,34,37,38,39,40,41,42

  {
     "services":[

     ],
     "networks":[
        {
           "network_id":"<UUID-of-net-0>",
           "link":"0.0.1234",
           "type":"ipv4_dhcp",
           "id":"network0"
        },
        {
           "network_id":"<UUID-of-net-0>",
           "link":"0.0.5678.1",
           "type":"ipv4_dhcp",
           "id":"network1"
        }
     ],
     "links":[
        {
           "ethernet_mac_address":"cc:cc:cc:cc:cc:cc",
           "mtu":1450,
           "type":"ovs",
           "id":"0.0.1234",
           "vif_id":"00000000-cccc-cccc-cccc-cccccccccccc",
           "name":"enc1234"
        },
        {
           "ethernet_mac_address":"aa:aa:aa:aa:aa:aa",
           "mtu":1450,
           "type":"ovs",
           "id":"0.0.5678",
           "vif_id":"00000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
           "name":"enc5678"
        },
        {
           "id": "0.0.5678.1",
           "type": "vlan",
           "vlan_link": "0.0.5678",
           "vlan_id": "1",
           "vlan_mac_address": "aa:aa:aa:aa:aa:aa",
           "neutron_port_id": "00000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        },
     ]
  }



Alternatives
------------

* VLAN tagging in hardware - which is not available with z13.

* Configuring the VLAN device and its IP configuraiton manually from within
  the instance operating system

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

To take use of the feature, the *force_config_drive* parameter should be
set to true in each nova.conf file.

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

* Neutron integration - Set MAC: https://blueprints.launchpad.net/nova-dpm/+spec/neutron-integration-set-mac

Testing
=======

* Unittest

Documentation Impact
====================

TBD

References
==========
