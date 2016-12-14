..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=============================================
Neutron Integration - Setting the MAC address
=============================================

https://blueprints.launchpad.net/nova-dpm/+spec/neutron-integration-set-mac

DPM does not support setting the MAC address for a NIC on its NIC creation.
This blueprint adds this support.

Problem Description
===================

DPM does not support setting the MAC address for a NIC on its NIC creation.
It does also not offer a way to query the MAC address of an already created
NIC. Therefore the the MAC of the DPM NIC should be changed from within the
operating system that the actual used MAC is equal the MAC of the Neutron port.
That happens via a special systemd service during boot.

Use Cases
---------

* Attaching an instance to the network while using the correct MAC address

* Using cloud-init to setup the networking with static ips

Proposed Change
===============

Nova adds the relevant data to the ConfigDrives metadata. The systemd service
is able to read this information and set the MAC on the right interface
during boot.

In the DPM case the relevant keys of the nova vif dict are the following::

    mac = vif['address'] = aa:aa:aa:bb:bb:bb

In addition the device-number from the DPM NIC is of importance::

  devno = nic.get_property('device-number')



The metadata of the ConfigDrive needs to be updated. Namely the
*network_data.json* file. It is used by cloud-init to do the network
configuration and by the special systemd service for setting the mac address.

The systemd service requires a way to map an entry of the *network_data.json*
file to an actual Linux network interface. As the MAC address cannot be used
(metadata MAC does not match the NICs MAC) some other identifier
- the NICs device number - is required.

The *id* of all *link* objects in *network_data.json* should be replaced by
the the NICs device number. Also all other occurrences of that old *id*
need to be updated.

*Example*

VIFs::

    vif1['id'] = 00000000-cccc-cccc-cccc-cccccccccccc
    vif1['address'] = cc:cc:cc:cc:cc:cc

    vif2['id'] = 00000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa
    vif2['address'] = aa:aa:aa:aa:aa:aa

Result of DPM get NIC Properties::

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



*network_data.json* before edit

::

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

Becomes::

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
           "network_id":"<UUID-of-net-1>",
           "link":"0.0.5678",
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
           "vif_id":"00000000-cccc-cccc-cccc-cccccccccccc"
        },
        {
           "ethernet_mac_address":"aa:aa:aa:aa:aa:aa",
           "mtu":1450,
           "type":"ovs",
           "id":"0.0.5678",
           "vif_id":"00000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        }
     ]
  }


Alternatives
------------

Keeping the DPM chosen MAC and pushing this one back to Neutron.
The problem with this approach is, that the Neutron port is created in the
nova manager before any virt-driver gets invoked. Nova manager requests the
port creation and binds it to the target host. Once the port is bound, changing
the MAC is not possible anymore. That means, that the nova-dpm driver would
need to unbind the port, change the MAC, bind it again.

In addition there's no way to get the DPM chosen MAC address, as this field
is not externalized on the API.

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

* Initial Neutron integration: https://blueprints.launchpad.net/nova-dpm/+spec/neutron-integration

* Nova ConfigDrive support: https://blueprints.launchpad.net/nova-dpm/+spec/config-drive

Testing
=======

* Unittest

Documentation Impact
====================

To take use of the feature, the *force_config_drive* parameter should be
set to true in each nova.conf file.

References
==========
