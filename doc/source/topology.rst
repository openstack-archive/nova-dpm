.. _topology:

========
Topology
========

This section describes the topology between the OpenStack compute node for DPM,
the z Systems Hardware Management Console (HMC) and the managed machines
(CPCs).

Topology for a single OpenStack cloud
-------------------------------------

To keep it simple, we start with explaining the topology for a single OpenStack
cloud with compute nodes for DPM. The controller node is only shown as
a means to denote the OpenStack cloud.

The following entity-relationship diagram shows the entities related to
OpenStack compute nodes for DPM for a single OpenStack cloud.

The diagram presents multiplicities (cardinalities) on the relations using the
look-across semantics known from UML associations (e.g. The "1" on the left
side of the relation between controller node and compute node means that one
compute node is related to "1" controller node, and the "*" on the right side
of that relation means that one controller node is related to "*" (= 0 to N)
compute nodes.

::

  +---------------------+               +-----------------------+
  |                     |               |                       |
  |   Controller Node   | 1           * |     Compute Node      |
  |    (= OS cloud)     +---------------+        for DPM        |
  |                     |               |                       |
  +---------------------+               +-----------+-----------+
                                                    | 1
                                                    |
                                                    |
                                                    | *
                                        +-----------+-----------+
                                        |                       |
                                        |        Pair of:       | 1
                                        |  nova-compute (DPM)   +----+
                                        |  neutron-dpm-agent    |    |
                                        |                       |    |
                                        +-----------+-----------+    |
                                                    | *              |
                                                    |                |
                                                    |                |
                                                    | 1              |
                                              +-----+-----+          |
                                              |           |          |
                                              |    HMC    |          |
                                              |           |          |
                                              +-----+-----+          |
                                                    | 1              |
                                                    |                |
                                                    |                |
                                                    | *              |
                                              +-----+-----+          |
                                              |           |          |
                                              |    CPC    |          |
                                              | (machine) |          |
                                              |           |          |
                                              +-----+-----+          |
                                                    | 1              |
                                                    |                |
                                                    |                |
                                                    | *              |
                                            +-------+-------+        |
                                            |               |        |
                                            |  CPC subset   | 1      |
                                            |   (OS host)   +--------+
                                            |               |
                                            +-------+-------+
                                                    | 1
                                                    |
                                                    |
                                                    | *
                                            +-------+-------+
                                            |               |
                                            | DPM partition |
                                            | (OS instance) |
                                            |               |
                                            +---------------+

Explanation:

* The controller node is the management plane of the OpenStack cloud - it is
  only shown to relate the compute nodes to an OpenStack cloud. It can run on
  any (supported) operating system and hardware architecture.

* Within an OpenStack cloud, there can be many compute nodes for DPM (along
  with compute nodes for other hypervisor types and hardware architectures).

* Each compute node for DPM can run the services for multiple OpenStack
  "hosts". For OpenStack, a "host" is a hypervisor instance that can run
  multiple virtual systems (the OpenStack instances). The OpenStack instances
  are DPM partitions on a CPC.

* An OpenStack host is established by defining a subset of a CPC. A CPC
  subset is defined in the DPM-specific part of the Nova config files of its
  compute node with the following characteristics:

  - A maximum number of DPM partitions that can be created.
  - A maximum number of physical CPUs that can be used.
  - A maximum amount of physical memory that can be used.

  The construct of a CPC subset limits the resources used for an OpenStack
  host, ensuring that the OpenStack host cannot exhaust the resources of an
  entire CPC. This allows other OpenStack hosts or non-OpenStack workload
  to coexist on the same CPC.

* For each OpenStack host, the compute node needs a pair of:

  - the nova-compute service for DPM (that is, with the nova-dpm virtualization
    driver)
  - the neutron-dpm-agent service

  The multi-host capability at the level of the nova-compute service is not
  exploited for DPM; multiple hosts are supported by having multiple pairs of
  services.

* There is no need to run all pairs of nova-compute and neutron-dpm-agent
  services on the same compute node; they can also be spread across multiple
  compute nodes.

* The services on a compute node for DPM connect to an HMC over a network and
  therefore the compute node can run on any (supported) operating system and
  hardware architecture.

* The HMC can be duplicated into a primary and alternate HMC. In this OpenStack
  release, the nova-compute service for DPM and the neutron-dpm-agent service
  can be configured to connect to only one HMC.

* A particular HMC can manage multiple CPCs. Therefore, there may be multiple
  pairs of nova-compute and neutron-dpm-agent services on possibly multiple
  compute nodes connecting to the same or different HMCs, for managing
  OpenStack hosts (CPC subsets) on the same or on different CPCs.

* Finally, the OpenStack host (CPC subset) powers the OpenStack instances (DPM
  partitions), like on any other OpenStack Nova compute platform.

General Topology
----------------

The general case is nearly like the case of a single OpenStack cloud, except
that the compute nodes can now belong to different OpenStack clouds.

Interaction between OpenStack compute node and HMC
--------------------------------------------------

All interactions of OpenStack for DPM with an HMC go through a compute node for
DPM. On the compute node, the nova-dpm virtualization driver within the
nova-compute service and the neutron-dpm-agent service connect to the HMC.
These are the only OpenStack components that interface with the HMC.

The HMC supports a Web Services API that uses REST over HTTPS for client-driven
request/response style interactions, and JMS over STOMP for event-style
notifications.

The `zhmcclient` Python package is used to isolate the OpenStack code from the
details of the HMC Web Services API.

The following diagram shows how the OpenStack components on the compute node
use the zhmcclient package to connect to the HMC:

::

  +----------------------------------------------------------------+
  |                         Compute Node                           |
  |                                                                |
  |  +---------------------------+                                 |
  |  |   nova-compute service    |                                 |
  |  +---------------------------+  +---------------------------+  |
  |  |   nova-dpm virt driver    |  | neutron-dpm-agent service |  |
  |  +---------------------------+--+---------------------------+  |
  |  |                        zhmcclient                        |  |
  |  +-----------------------+----------^-----------------------+  |
  +--------------------------|----------|--------------------------+
                             |          |
                             |          |
                             | REST     | JMS
                             |          |
                             |          |
                        +----v----------+----+
                        |                    |
                        |        HMC         |
                        |                    |
                        +--------------------+
