.. _storage:

===============
Storage Support
===============

This section describes the storage setup for OpenStack DPM.

Ephemeral storage vs. block storage
-----------------------------------

* Ephemeral storage is not supported by OpenStack DPM

* Only FC attached block storage is supported

Cinder setup
------------

The cinder volume service on the storage node must be configured for fibre
channel (FC).

DPM FC Architecture
-------------------

A CPC needs to be configured into CPC subsets. Each Subset defines the amount
of processors, memory, as well as Fibre-Channel ports for OpenStack to manage.
For more details on subsets see the chapter :ref:`topology`.
In order to allow a guest instance connect to a Fibre-Channel volume,
the instance requires access to a virtual Host Bus Adapter (vHBAs).
Each vHBA behaves like a physical HBA and is assigned a world-wide-unique WWPN.
OpenStack DPM will create vHBAs for Fibre-Channel ports within the CPC Subset
and assign it to each guest instance. In order to ensure all guest instances
will have access to attached Storage Subsystems, all Fibre-Channel ports need
to provide physical connectivity to each target Storage Subsystem.

The *storage node* requires connectivity to Fibre-Channel ports on the target
storage subsystem to allow Cinder to deploy images. In addition it
requires IP connectivity to the storage subsystem to trigger the creation of
a volume and to do the LUN Masking. An IP connection to the FC switches is
required to configure zoning.

The *compute node* itself does not require FC or IP connectivity to the
Storage Subsystem or the FC switches at all.

The *controller node* does not require FC connectivity.

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
  connectivity to the *storage* as well as to the *compute node*. FC
  connectivity is not required.

* FC Cinder drivers take care of LUN masking and zoning configuration

* The nova-dpm driver creates a vHBA for each adapter configured in nova.conf.
  For more details see the chapter :ref:`configuration`.

* Instances do not support multipathing between the adapter and the switch
  during boot.

  Although multiple adapters configured to the partition, only a single adapter
  is chosen for boot. After the operating system is up and running, the second
  vHBA can be enabled inband and used for multipathing.

* There is a bug with the multiple adapter suppport [1], therefore it's
  not recommended to use multiple adapters for a CPC subset.

[1] https://bugs.launchpad.net/nova-dpm/+bug/1662511
