..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=============================
Support for ephemeral storage
=============================

There is no corresponding Launchpad blueprint yet.

This spec describes the support for ephemeral storage for the DPM (PR/SM) on
z Systems hypervisor.

Problem description
===================

OpenStack supports "ephemeral storage" (for details, see
`<https://docs.openstack.org/ha-guide/storage-ha-backend.html>`_).

The definition there reads:

* Ephemeral storage is allocated for an instance and is deleted when the
  instance is deleted. The Compute service manages ephemeral storage and by
  default, Compute stores ephemeral drives as files on local disks on the
  compute node. As an alternative, you can use Ceph RBD as the storage back end
  for ephemeral storage.

This definition assumes that the compute node runs on the host operating system
of the hypervisor. That only works for type-2 hypervisors (e.g. KVM, Xen),
because by definition they have a host operating system that is open for
general access and thus can run OpenStack services and has a file system or
can run the Ceph RBD client software.

For type-1 hypervisors (e.g. VMware ESX, HyperV, z/VM, DPM (PR/SM) on z
Systems), this approach does not easily work. Type-1 hypervisors are in some
way also operating systems, but they are not normally open for general access,
and therefore need a different approach for backing the block storage that is
provided to virtual systems as ephemeral storage.

Use Cases
---------

The use cases for this spec are the general use cases for ephemeral storage.

These are:

* An OpenStack user can launch an instance with boot source "boot from image"
  (without creating a new volume).

  The image is a Glance image, i.e. it is stored in the Glance image store
  (which is out of scope for this spec). As part of launching the instance
  from image, ephemeral storage is allocated for the instance, and the Glance
  image is copied onto that storage. Thus, if the instance changes the file
  system it booted from, the original image will remain unchanged.

* An OpenStack user can launch an instance with boot source "boot from
  snapshot" (without creating a new volume).

  The snapshot is stored (TBD: where? local file system on the hypervisor host
  OS?). As part of launching the instance from snapshot, ephemeral storage is
  allocated for the instance, and the snapshot is copied onto that storage.
  Thus, if the instance changes the file system it booted from, the original
  snapshot will remain unchanged.

Proposed change
===============

TODO: Needs to be worked out, replacing the template text below.

Here is where you cover the change you propose to make in detail. How do you
propose to solve this problem?

If this is one part of a larger effort make it clear where this piece ends. In
other words, what's the scope of this effort?

At this point, if you would like to just get feedback on if the problem and
proposed change fit in nova, you can stop here and post this for review to get
preliminary feedback. If so please say:
Posting to get preliminary feedback on the scope of this spec.

Alternatives
------------

TODO: Needs to be worked out, replacing the template text below.

What other ways could we do this thing? Why aren't we using those? This doesn't
have to be a full literature review, but it should demonstrate that thought has
been put into why the proposed solution is an appropriate one.

Data model impact
-----------------

TODO: Needs to be worked out, replacing the template text below.

Changes which require modifications to the data model often have a wider impact
on the system.  The community often has strong opinions on how the data model
should be evolved, from both a functional and performance perspective. It is
therefore important to capture and gain agreement as early as possible on any
proposed changes to the data model.

Questions which need to be addressed by this section include:

* What new data objects and/or database schema changes is this going to
  require?

* What database migrations will accompany this change.

* How will the initial set of new data objects be generated, for example if you
  need to take into account existing instances, or modify other existing data
  describe how that will work.

REST API impact
---------------

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

TODO: Needs to be worked out, replacing the template text below.

Describe any potential security impact on the system.  Some of the items to
consider include:

* Does this change touch sensitive data such as tokens, keys, or user data?

* Does this change alter the API in a way that may impact security, such as
  a new way to access sensitive information or a new way to login?

* Does this change involve cryptography or hashing?

* Does this change require the use of sudo or any elevated privileges?

* Does this change involve using or parsing user-provided data? This could
  be directly at the API level or indirectly such as changes to a cache layer.

* Can this change enable a resource exhaustion attack, such as allowing a
  single API interaction to consume significant server resources? Some examples
  of this include launching subprocesses for each connection, or entity
  expansion attacks in XML.

For more detailed guidance, please see the OpenStack Security Guidelines as
a reference (https://wiki.openstack.org/wiki/Security/Guidelines).  These
guidelines are a work in progress and are designed to help you identify
security best practices.  For further information, feel free to reach out
to the OpenStack Security Group at openstack-security@lists.openstack.org.

Notifications impact
--------------------

TODO: Needs to be worked out, replacing the template text below.

Please specify any changes to notifications. Be that an extra notification,
changes to an existing notification, or removing a notification.

Other end user impact
---------------------

TODO: Needs to be worked out, replacing the template text below.

Aside from the API, are there other ways a user will interact with this
feature?

* Does this change have an impact on python-novaclient? What does the user
  interface there look like?

Performance Impact
------------------

TODO: Needs to be worked out, replacing the template text below.

Describe any potential performance impact on the system, for example
how often will new code be called, and is there a major change to the calling
pattern of existing code.

Examples of things to consider here include:

* A periodic task might look like a small addition but if it calls conductor or
  another service the load is multiplied by the number of nodes in the system.

* Scheduler filters get called once per host for every instance being created,
  so any latency they introduce is linear with the size of the system.

* A small change in a utility function or a commonly used decorator can have a
  large impacts on performance.

* Calls which result in a database queries (whether direct or via conductor)
  can have a profound impact on performance when called in critical sections of
  the code.

* Will the change include any locking, and if so what considerations are there
  on holding the lock?

Other deployer impact
---------------------

TODO: Needs to be worked out, replacing the template text below.

Discuss things that will affect how you deploy and configure OpenStack
that have not already been mentioned, such as:

* What config options are being added? Should they be more generic than
  proposed (for example a flag that other hypervisor drivers might want to
  implement as well)? Are the default values ones which will work well in
  real deployments?

* Is this a change that takes immediate effect after its merged, or is it
  something that has to be explicitly enabled?

* If this change is a new binary, how would it be deployed?

* Please state anything that those doing continuous deployment, or those
  upgrading from the previous release, need to be aware of. Also describe
  any plans to deprecate configuration values or features.  For example, if we
  change the directory name that instances are stored in, how do we handle
  instance directories created before the change landed?  Do we move them?  Do
  we have a special case in the code? Do we assume that the operator will
  recreate all the instances in their cloud?

Developer impact
----------------

TODO: Needs to be worked out, replacing the template text below.

Discuss things that will affect other developers working on OpenStack,
such as:

* If the blueprint proposes a change to the driver API, discussion of how
  other hypervisors would implement the feature is required.


Implementation
==============

Assignee(s)
-----------

TODO: Needs to be worked out, replacing the template text below.

Who is leading the writing of the code? Or is this a blueprint where you're
throwing it out there to see who picks it up?

If more than one person is working on the implementation, please designate the
primary author and contact.

Primary assignee:
  <launchpad-id or None>

Other contributors:
  <launchpad-id or None>

Work Items
----------

TODO: Needs to be worked out, replacing the template text below.

Work items or tasks -- break the feature up into the things that need to be
done to implement it. Those parts might end up being done by different people,
but we're mostly trying to understand the timeline for implementation.


Dependencies
============

TODO: Needs to be worked out, replacing the template text below.

* Include specific references to specs and/or blueprints in nova, or in other
  projects, that this one either depends on or is related to.

* If this requires functionality of another project that is not currently used
  by Nova (such as the glance v2 API when we previously only required v1),
  document that fact.

* Does this feature require any new library dependencies or code otherwise not
  included in OpenStack? Or does it depend on a specific version of library?


Testing
=======

TODO: Needs to be worked out, replacing the template text below.

Please discuss the important scenarios needed to test here, as well as
specific edge cases we should be ensuring work correctly. For each
scenario please specify if this requires specialized hardware, a full
openstack environment, or can be simulated inside the Nova tree.

Please discuss how the change will be tested. We especially want to know what
tempest tests will be added. It is assumed that unit test coverage will be
added so that doesn't need to be mentioned explicitly, but discussion of why
you think unit tests are sufficient and we don't need to add more tempest
tests would need to be included.

Is this untestable in gate given current limitations (specific hardware /
software configurations available)? If so, are there mitigation plans (3rd
party testing, gate enhancements, etc).


Documentation Impact
====================

TODO: Needs to be worked out, replacing the template text below.

Which audiences are affected most by this change, and which documentation
titles on docs.openstack.org should be updated because of this change? Don't
repeat details discussed above, but reference them here in the context of
documentation for multiple audiences. For example, the Operations Guide targets
cloud operators, and the End User Guide would need to be updated if the change
offers a new feature available through the CLI or dashboard. If a config option
changes or is deprecated, note here that the documentation needs to be updated
to reflect this specification's change.

References
==========

TODO: Needs to be worked out, replacing the template text below.

Please add any useful references here. You are not required to have any
reference. Moreover, this specification should still make sense when your
references are unavailable. Examples of what you could include are:

* Links to mailing list or IRC discussions

* Links to notes from a summit session

* Links to relevant research, if appropriate

* Related specifications as appropriate (e.g.  if it's an EC2 thing, link the
  EC2 docs)

* Anything else you feel it is worthwhile to refer to


History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Pike
     - Initial version with problem description and use cases
