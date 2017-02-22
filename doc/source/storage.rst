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

Only the storage node require a FC connectivity. It is required to deploy
images onto the volume. In addition the storage node requires IP connectivity
to the storage subsystem to trigger the creation of a volume and to do the
LUN Masking. An IP Connection to the switches is required to configure
zoning.

The compute node itself does not require FC or IP connectivity to the storage
subsystem at all.

The instances (partitions) get directly attached to storage adapters.

OpenStack DPM requires that all storage adapter ports and all Storage
Subsystems used are plugged to the same FC network.

::

  FC Architecture:
                                                    +---------------------------------------------+
                                       +----------+ |                           ||                |
                                       |          | |     CPC Subset 1          || CPC Subset 2   |
                                       |  HMC     +-+                           ||                |
                        IP             |          | |                           ||                |
  +-------------+-----------------+----+          | |                           ||                |
  |             |                 |    +----------+ | +----------+ +----------+ ||  +----------+  |
  |             |                 |                 | |          | |          | ||  |          |  |
  |   +---------+------+    +-----+--------------+  | | Instance | | Instance | ||  | Instance |  |
  |   |                |    |                    |  | |          | |          | ||  |          |  |
  |   |                |    |                    |  | +----+-----+ +--+-------+ ||  +----+-----+  |
  |   |                |    |                    |  |      |          |         ||       |        |
  |   |  Compute Node  |    |   Storage Node     |  |      +---+  +---+         ||       |        |
  |   |                |    |                    |  |          |  |             ||       |        |
  |   |                |    | +------+  +------+ |  |       +--+--++            ||    +--+---+    |
  |   |                |    | |  FC  |  |  FC  | |  |       |  FC  |            ||    |  FC  |    |
  |   +----------------+    +-+---+--+--+---+--+-+  +-------+---+--+------------------+--+---+----+
  |                               |         |                   |                        |
  |                               |         |                   |                        |
  |                               |         |                   |                        |
  |                               |         +---------+   +-----+                        |
  |                               |                   |   |    +-------------------------+
  |                               |                   |   |    |
  |IP                    +--------+--------+     +----+---+----+---+
  +----------------------+    FC Switch    |     |    FC Switch    +----------+
  |                      +-+---------+-----+     +----+-----+------+     IP   |
  |                        |         |                |     |                 |
  |                        | +------------------------+     |                 |
  |                +-------+ |       |                      |                 |
  |                |         |       +----------+           |                 |
  |                |         |                  |           |                 |
  |                |         |                  |           |                 |
  |         +--+---+--+---+--+---+--+     +--+--+---+---+---+--+--+           |
  |         |  |  FC  |   |  FC  |  |     |  |  FC  |   |  FC  |  |           |
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
  The controller Node is not shown on this picture. It does require any FC
  connectivity.

* FC Cinder drivers take care of LUN Masking and Zoning configuration

* Instances do not support multipathing between the adapter and the switch
  during boot

  TODO: Nova-dpm is able to attach multiple adapters to a partition, but uses
  just a single adapter for boot. There is a bug that can occur when having
  multiple adapters configured [1]. In addition the adapter that was not used
  for boot must be enabled from inside the operating system manually to
  allow multipathing.


[1] https://bugs.launchpad.net/nova-dpm/+bug/1662511