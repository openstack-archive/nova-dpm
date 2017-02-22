.. _storage:

===============
Storage Support
===============

This section describes the storage setup for OpenStack DPM.

Supported Storage types
-----------------------

The following Storage types exist in OpenStack [1]:

* Ephemeral storage

  * Boot: Not supported by OpenStack DPM
  * Additional attachment: n/a

* Block storage

  * Boot: Only fibre channel protocol (FCP) block storage is supported by
    OpenStack DPM
  * Additional attachment: Only FCP block storage is supported by OpenStack DPM

* Object Storage

  * Boot: n/a
  * Additional attachment: Access happens via network - supported by OpenStack
    for DPM

* File Storage

  * Boot: n/a
  * Additional attachment: Access happens via network - supported by OpenStack
    for DPM

Block Storage setup
-------------------

The Block Storage service (Cinder) must be configured to use a FCP back-end
storage subsystem.

DPM FCP Architecture
--------------------

A CPC needs to be configured into CPC subsets. Each CPC subset defines the
amount of processors, memory and FCP adapter ports for OpenStack to manage.
For more details on CPC subsets see the chapter :ref:`topology`.

An instance requires access to a virtual Host Bus Adapter (vHBA) to be able
to access a FCP volume. Each vHBA behaves like a physical HBA. It has a World
Wide Port Number (WWPN) assigned to it. OpenStack DPM will create a vHBA
for each FCP adapter port configured to each instance.
It's important that all configured FCP adapter ports provide physical
connectivity to each target storage subsystem.

The *storage node* requires connectivity to FCP adapter ports on the target
storage subsystems to allow Cinder to deploy images. In addition, it
requires IP connectivity to the storage subsystem to trigger the creation of
a volume and to do the LUN (logical unit number) masking. An IP connection to
the FCP switches is required to configure FCP zoning.

The *compute node* itself does not require a FCP or IP connection to the
storage subsystem or the FCP switches at all.

The *controller node* does not require FCP connectivity at all.

::

  +  +--------------------+ +------------------------------------------------------------+
  |  |                    | |                                      ||                    |
  +--+  HMC               +-+            CPC Subset 1              ||  CPC Subset 2      |
  |  |                    | |                                      ||                    |
  |  +--------------------+ | +---------------+  +---------------+ || +---------------+  |
  |                         | |   Instance    |  |   Instance    | || |   Instance    |  |
  |  +--------------------+ | |               |  |               | || |               |  |
  |  |                    | | |               |  |               | || |               |  |
  +--+  Compute Node      | | | +----+ +----+ |  | +----+ +----+ | || | +----+ +----+ |  |
  |  |                    | | | |vHBA| |vHBA| |  | |vHBA| |vHBA| | || | |vHBA| |vHBA| |  |
  |  +--------------------+ | +-----+-----+---+  +----+----------+ || +----+------+---+  |
  |                         |       |     |           |    |       ||      |      |      |
  |  +--------------------+ |       |     +---------+ |    |       ||      |      |      |
  |  |                    | |       |               | |    |       ||      |      |      |
  |  |   Storage Node     | |       |     +-----------+    |       ||      |      |      |
  +--+                    | |       |     |         |      |       ||      |      |      |
  |  | +------+  +------+ | |     +-+-----+--+     ++------+--+    ||  +---+--+ +-+----+ |
  |  | |FC HBA|  |FC HBA| | |     |  FC HBA  |     |  FC HBA  |    ||  |FC HBA| |FC HBA| |
  |  +-----+--------+-----+ +-----+-+--------+-----+------+---+-----------+-------+------+
  |        |        |               |                     |               |       |
  |        |        +--------------------------------+    |               |       |
  |        |                        |                |    |               |       |
  |        +----------------+       |   +---------------------------------+       |
  |                         |       |   |            |    |                       |
  |                         |       |   |            |    |   +-------------------+
  |                         |       |   |            |    |   |
  |IP                    +--+-------+---+--+     +---+----+---+----+
  +----------------------+    FC Switch    |     |    FC Switch    +----------+
  |                      +-+---------+-----+     +----+-----+------+     IP   |
  |                        |         |                |     |                 |
  |                        | +------------------------+     |                 |
  |                +-------+ |       |                      |                 |
  |                |         |       +----------+           |                 |
  |                |         |                  |           |                 |
  |                |         |                  |           |                 |
  |         +------+---------+------+     +-----+-----------+-----+           |
  |         |  |FC HBA|   |FC HBA|  |     |  |FC HBA|   |FC HBA|  |           |
  |         |  +------+   +------+  |     |  +------+   +------+  |           |
  |         |                       |     |                       |           |
  |         |  Storage Subsystem 1  |     |  Storage Subsystem 2  |           |
  |         |                       |     |                       |           |
  |         |                       |     |                       |           |
  |         +------------+----------+     +------------+----------+           |
  |                      |                             |                      |
  |                      |        IP                   |                      |
  +----------------------+-----------------------------+----------------------+


.. note::
  The *controller node* is not shown on this picture. It just requires IP
  connectivity to the *storage node* as well as to the *compute node*. FCP
  connectivity is not required for the *controller node*.

* FCP Cinder drivers take care of LUN masking and zoning configuration.

* The nova-dpm driver creates a vHBA for each adapter configured in nova.conf.
  For more details see the chapter :ref:`configuration`.

* Instances do not support multipathing between the adapter and the switch
  during boot.

  Even though multiple FCP adapters are configured to the partition, only a
  single adapter is chosen for boot. After the operating system is up and
  running, the second vHBA can be enabled inband and used for multipathing.

References
----------

[1] https://docs.openstack.org/admin-guide/common/get-started-storage-concepts.html