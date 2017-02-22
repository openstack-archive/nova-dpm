.. _storage:

===============
Storage Support
===============

This section describes the storage setup for OpenStack DPM

Ephemeral storage vs. block storage
-----------------------------------

* Ephemeral storage is not supported by OpenStack DPM

* Only FC attached block storage is supported

Cinder setup
------------

The cinder volume service must be configured for Fibre Channel (FC).

DPM FC Architecture
-------------------

Only the storage node require a FC connectivity. It is required to deploy
images onto the volume. In addition the storage node requires IP connectivity
to the storage subsystem.

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
    |   +----------------+    +-+---+--+--+---+--+-+  +-------+---+--+------------------+-+----+----+
    |                               |         |                   |                       |
    |                               |         |                   |                       |
    |                               |         |                   |                       |
    |                               |         +---------+         |                       |
    |                               |                   |         |                       |
    |IP                             |                   |         |                       |
    |                      +--------+--------+     +----+---------+--+                    |
    |                      |    FC Switch    +-----+    FC Switch    +--------------------+
    |                      +-+---------+-----+     +----+-----+------+
    |                        |         |                |     |
    |                        | +------------------------+     |
    |                +-------+ |       |                      |
    |                |         |       +----------+           |
    |                |         |                  |           |
    |                |         |                  |           |
    |         +--+---+--+---+--+---+--+     +--+--+---+---+---+--+--+
    |         |  |  FC  |   |  FC  |  |     |  |  FC  |   |  FC  |  |
    |         |  +------+   +------+  |     |  +------+   +------+  |
    |         |                       |     |                       |
    |         |  Storage Subsystem 1  |     |  Storage Subsystem 2  |
    |         |                       |     |                       |
    |         |                       |     |                       |
    |         +------------+----------+     +------------+----------+
    |                      |                             |
    |                      |        IP                   |
    +----------------------+-----------------------------+

.. note::
  The controller Node is not shown on this picture. It does require any FC
  connectivity.

* FC Cinder drivers take care of LUN Masking and Zoning configuration

* Instances do not support multipathing between the adapter and the switch