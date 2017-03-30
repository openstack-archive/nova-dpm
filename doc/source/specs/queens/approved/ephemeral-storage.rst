..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==============================================================
Cinder-based ephemeral storage in Nova driver for DPM on IBM Z
==============================================================

This spec describes the support for ephemeral storage for the DPM on IBM Z
hypervisor.

Ephemeral storage overview
==========================

OpenStack supports *ephemeral storage* [1]_ [2]_. Ephemeral storage is
associated with an instance, and exists only for the life of this very
instance. Ephemeral storage persists across reboots of the instances's
operating sytsem and across power-off cycles of the underlying hardware, and is
automatically removed when its instance is deleted.

Ephemeral storage includes a root ephemeral volume and an additional ephemeral
volume [1]_.

The size of the root ephemeral volume is defined by the flavor of an instance.
Generally, it is used to store an instance’s root file system.

Flavors can optionally define an additional ephemeral volume, and its size. It
is represented to the instance's operating system as a raw block device that
initially has no partition table or file system. A cloud-aware operating system
in the instance can discover, format, and mount such a block device.

Today, ephemeral volumes can be backed by two types of storage:

* As files in the file system of the operating system on the compute node
* As block devices in Ceph RBD.

If ephemeral volumes are backed by files in the file system of the compute
node, the location will be where all instance specific state is stored, i.e. in
the path defined with Nova config option "state_path" [3]_.


Problem description
===================

Backing ephemeral volumes as files in the file system of the compute node
requires that the compute node runs on the host operating system of the
hypervisor.

That works for type-2 hypervisors (e.g. KVM, Xen), because by definition they
have a host operating system that is open for general access and thus has a
file system or can run the Ceph RBD client software.

However, for type-1 hypervisors (e.g. VMware ESX, HyperV, z/VM, or DPM on
IBM Z), ephemeral volumes often cannot be backed by the file system of the
compute node, because these hypervisors do not have a host operating system
that is open for general access, and therefore the compute node runs on a
separate physical node in such cases.

At the OpenStack summit in Boston in 2/2017, agreement was reached in the Nova
team that support for ephemeral storage based upon Cinder should be pursued
[4]_.

Using Cinder to back ephemeral storage has several advantages:

* It addresses the difficulties to support ephemeral storage for some type-1
  hypervisors,
* It benefits from the large set of storage subsystems supported for Cinder,
* It centralizes all persisted storage to one place and can subsequently
  benefit from fast copy mechanisms (e.g. when an instance is launched from
  snapshot or from volume).

This spec proposes to support ephemeral storage backed by Cinder for the
Nova driver for DPM on IBM Z. Its scope is only DPM for IBM Z, and it builds
on the general work to enable ephemeral storage backed by Cinder
(blueprint [7]_). Note there is a similar blueprint for EMC ScaleIO [8]_.


Use Cases
---------

The use cases for this spec are the general use cases for ephemeral storage:

* An OpenStack user can launch an instance with boot source "boot from image",
  without first creating a new Cinder volume.

  The image is a Glance image, i.e. it is stored in the Glance image store. As
  part of launching the instance with "boot from image", ephemeral storage is
  allocated for the instance, and the Glance image is copied onto that storage.
  Thus, if the instance changes the file system it booted from, the original
  image in the Glance image store will remain unchanged.

* An OpenStack user can launch an instance with boot source "boot from
  snapshot", without first creating a new Cinder volume.

  The snapshot is stored in Glance [5]_ [6]_. As part of launching the
  instance with "boot from snapshot", ephemeral storage is allocated for the
  instance, and the snapshot is copied onto that storage. Thus, if the instance
  changes the file system it booted from, the original snapshot in Glance will
  remain unchanged.

* An OpenStack CI system can run more tempest tests. Nearly all of the tempest
  tests for Nova rely on ephemeral storage.


Proposed change
===============

Assumptions about the general support
-------------------------------------

Because the general blueprint [5]_ does not yet contain specific details about
the proposal, this section states some assumptions, for discussion with the
owners of that blueprint:

* It needs to be described which interfaces a Nova driver would use to allocate
  and deallocate Cinder volumes.

* In order not to confuse OpenStack users by showing the additional Cinder
  volumes that are actually ephemeral volumes with an automatically managed
  lifetime, a means is needed to distinguish ephemeral Cinder volumes from
  other Cinder volumes, e.g. by adding a public read-only boolean attribute
  "is_ephemeral" to Cinder volumes. Such an attribute allows a user that needs
  to manually manage normal Cinder volumes, to exclude ephemeral Cinder volumes
  from a listing of Cinder volumes.

Change for Nova DPM
-------------------

* The Nova driver for DPM is updated to allocate the root ephemeral volume (if
  needed) and the additional ephemeral volume (if needed) by allocating
  ephemeral Cinder volumes. The driver also needs to make sure that the backing
  Cinder volumes are deleted when the instance is deleted.

* The use of Cinder volumes as a back end for ephemeral volumes is controlled
  by a DPM-specific Nova config option.

Alternatives
------------

There was no alternative found that provides persistent storage and that
benefits from the support of many storage subsystems without having to write
drivers for these subsystems.

Also, the proposal is in line with the agreement reached in the Nova team that
support for ephemeral storage based upon Cinder should be pursued [4]_.

Data model impact
-----------------

Assuming that the "is_ephemeral" attribute on Cinder volumes is handled by
the general blueprint [5]_, this spec does not have an impact on the data
model.

In an OpenStack release migration scenario, a Cinder volume that does not have
the new attribute yet, can get it added with a value of False. This simple rule
is possible because the new attribute is introduced in the same release where
the support for ephemeral volumes backed by Cinder is introduced.


REST API impact
---------------

TODO: Find out whether volume related API functions can already show
the new attribute and filter by the new attribute.

TODO: Needs to be worked out, replacing the template text below.

Each API method which is either added or changed should have the following

* Specification for the method

  * A description of what the method does suitable for use in
    user documentation

  * Method type (POST/PUT/GET/DELETE)

  * Normal http response code(s)

  * Expected error http response code(s)

    * A description for each possible error code should be included
      describing semantic errors which can cause it such as
      inconsistent parameters supplied to the method, or when an
      instance is not in an appropriate state for the request to
      succeed. Errors caused by syntactic problems covered by the JSON
      schema definition do not need to be included.

  * URL for the resource

    * URL should not include underscores, and use hyphens instead.

  * Parameters which can be passed via the url

  * JSON schema definition for the request body data if allowed

    * Field names should use snake_case style, not CamelCase or MixedCase
      style.

  * JSON schema definition for the response body data if any

    * Field names should use snake_case style, not CamelCase or MixedCase
      style.

* Example use case including typical API samples for both data supplied
  by the caller and the response

* Discuss any policy changes, and discuss what things a deployer needs to
  think about when defining their policy.

Example JSON schema definitions can be found in the Nova tree
http://git.openstack.org/cgit/openstack/nova/tree/nova/api/openstack/compute/schemas

Note that the schema should be defined as restrictively as
possible. Parameters which are required should be marked as such and
only under exceptional circumstances should additional parameters
which are not defined in the schema be permitted (eg
additionaProperties should be False).

Reuse of existing predefined parameter types such as regexps for
passwords and user defined names is highly encouraged.

Security impact
---------------

This change does not affect security.

Notifications impact
--------------------

TODO: Find out about existing notifications on Cinder volumes.

TODO: Needs to be worked out, replacing the template text below.

Please specify any changes to notifications. Be that an extra notification,
changes to an existing notification, or removing a notification.

Other end user impact
---------------------

TODO: Describe how an end user can exclude ephemeral volumes in listings
of Cinder volumes.

TODO: Needs to be worked out, replacing the template text below.

Aside from the API, are there other ways a user will interact with this
feature?

* Does this change have an impact on python-novaclient? What does the user
  interface there look like?

Performance Impact
------------------

The code to allocate and deallocate Cinder volumes will now also be
called for ephemeral volumes when instances are launched or destroyed.
However, this will be called by the Nova driver for DPM only, so
any other code in openStack is not affected at all.

The number of allocated Cinder volumes will be larger by the number of
instances. However, in a DPM on IBM Z scenario, there should be noi
measurable impact on performance because the number of DPM-powered instances
is quite limited (<100 per box).

Other deployer impact
---------------------

No new Cinder or general Nova config options are added.

For the Nova driver for DPM, config options specific to DPM are added:

* Cinder driver to be used for ephemeral storage.

  TODO: Define more details.

  In an OpenStack release migration, the new config option will be
  added with its default value, which turns off ephemeral volumes.


TODO: Does the new config option take immediate effect after the change
is merged?

TODO: The config option could be used by any Nova driver that also
wants to support Cinder-based ephemeral storage. Does this need to
be described?

Developer impact
----------------

The change does not affect the Nova driver API.


Implementation
==============

Assignee(s)
-----------

The Nova DPM team will be working on this.

Primary assignee:
  sreeram-vancheeswaran

Other contributors:
  pranjank

Work Items
----------

* In Nova DPM driver, call Cinder to allocate / deallocate ephemeral volumes.
* In Nova DPM configuration, add new config option for ephemeral volumes.


Dependencies
============

* Implementation of blueprint [5]_.


Testing
=======

The important scenarios to test are:

- Creation of normal Cinder volume with same name as automatically
  generated ephemeral volume.

- Concurrent creation and deletion of normal Cinder volumes and
  ephemeral volumes, against the same Cinder driver.

- Release migration from a release without support for ephemeral
  volumes to a release that supports it.

All these scenarios require Cinder being set up, in a Nova CI environment.


Documentation Impact
====================

The following documentation needs to be updated:

* Nova-DPM: Describe new config option for ephemeral volumes.


References
==========

.. [1] `OpenStack Admin Guide for Compute (Pike) - Block Storage <https://docs.openstack.org/nova/pike/admin/arch.html#block-storage>`_

.. [2] `OpenStack High Availability Guide - Storage back ends <https://docs.openstack.org/ha-guide/storage-ha-backend.html>`_

.. [3] `OpenStack Config Reference for Compute (Pike) <https://docs.openstack.org/pike/config-reference/compute/config-options.html>`_

.. [4] `Using Cinder for Nova Ephemeral Storage Backend <https://www.openstack.org/summit/boston-2017/summit-schedule/events/18738/using-cinder-for-nova-ephemeral-storage-backend>`_

.. [5] `OpenStack User Guide - Migration <https://docs.openstack.org/user-guide/cli-use-snapshots-to-migrate-instances.html>`_

.. [6] `OpenStack Admin Guide - Instances <https://docs.openstack.org/admin-guide/compute-images-instances.html>`_

.. [7] `Blueprint: Nova using ephemeral storage with cinder <https://blueprints.launchpad.net/nova/+spec/nova-ephemeral-cinder>`_

.. [8] `Blueprint: EMC ScaleIO as ephemeral storage backend <https://blueprints.launchpad.net/nova/+spec/scaleio-ephemeral-storage-backend>`_


History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Pike
     - Initial version with problem description and use cases
   * - Queens
     - Rebased the spec to be based upon blueprint [5]_.
