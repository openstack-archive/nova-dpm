..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

================
Boot from Volume
================

https://blueprints.launchpad.net/nova-dpm/+spec/destroy-instance-spawn

The following use cases should be enabled

* Destroying an instance with an attached Cinder volume

Background terminate instance with volume attached
==================================================

To understand this spec, some Nova-cinder insights are required.

In classical OpenStack environments (e.g. with focus on libvirt/kvm), the
nova compute service (n-cpu) runs in the Linux operating system of the
hypervisor. The compute node is the hypervisor!

The nova destroy instance with volume flow looks like this:

.. seqdiag::
   :scale: 80
   :alt: pxe_ipmi

   diagram {
      nova; virt-driver; cinder; host; storage

      nova => virt-driver [leftnote = "terminate_instance",
        label = "destroy(instance)", rightnote="virt-driver deconfigures
            the volume from the hypervisor"];
      nova => virt-driver [label = "get_volume_connector",
          return = "connector information: wwpns=[..], host=cfg.host"] {
        virt-driver => host [label = "get host WWPNs"];
      }

      nova => cinder [label = "terminate_connection(volume_id, connector)"] {
        cinder => storage [rightnote = "destroy LUN Masking"];
      }
      nova => cinder [label = "detach(volume_id, instance_id)",
          rightnote="remove volume mapping from DB"];
      nova => cinder [label="delete volume if flag set"];
   }


* Nova conductor calls ``terminate_instance`` of nova compute
* Nova manager calls the virt-driver to delete the instance and to deconfigure
  the volume attached to the hypervisor
* Nova manger asks the virt-driver for the host WWPNs used.
  The virt-driver returns the WWPNs of the hypervisor itself.
* Nova manager calls cinder to cleanup the LUN masking (for the hypervisor)
* Nova manager calls cinder to remove the mapping from the volume
  (DB operation)

Note: The instance itself is not aware of WWPNs, HBAs and LUNs at all. It just
sees a virtio-blk device.


Problem description
===================

The PR/SM hypervisor cannot attach storage locally. Storage is directly
attached to the instances/partitions. Therefore each partition has its own
WWPNs. This results in the following problem when deleting an instance with an
attached volume:

Once the partition (with its vHBAs) got deleted the information about its
host WWPNs is lost. But Nova manager needs this information still after
the virt drivers ``destroy`` method got called in order remove remove the host
mapping from he storage subsystem (and optionally delete the volume).

Proposed change
===============

Short term
----------

Right after the partition was actually deleted (but still in the virt-drivers
``destroy`` method, the mapping between instance_id and WWPNs gets stored in
the virt-driver object. This way it is still available.

If the drivers ``get_connector_properties`` method is called and an entry
for the requested partition exists in the virt-driver object, it will be
returned (volume can be unmapped) and deleted from the virt-driver object.

This concept has the following problems

* if the nova service dies between the deletion of the partition and the
  unmapping of the volume, this information gets lost!

* If ``get_connector_properties`` is called another time for this instance
  after its deletion (for whatever reason), this approach fails.


Long term
---------

2 options exist

* Introduce the concept of WWPN aware Instances to Nova

* Find a way to store the WWPNs as metadata in Novas instance object (and thus
  in the Nova DB).

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


Dependencies
============


Testing
=======
* Unittest


Documentation Impact
====================
TBD

References
==========

History
=======


