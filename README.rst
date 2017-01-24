===============================
nova-dpm
===============================

OpenStack Nova driver and agent for IBM z Systems PR/SM hypervisor in DPM mode

On IBM z Systems, certain workloads run better in a logical partition than
in a virtual machine of a software hypervisor such as KVM or z/VM.

The IBM z13 system (and IBM LinuxONE) introduced a new administrative mode
named "Dynamic Partition Manager" (DPM) that allows for managing the
firmware-based logical partition hypervisor (PR/SM) with the dynamic
capabilities known from software-based hypervisors.

These new dynamic capabilities provided by the DPM mode enables PR/SM to
act as a hypervisor managed by OpenStack using Nova.

This project supports adding the PR/SM hypervisor in DPM mode as a
Nova hypervisor platform, by implementing a new Nova driver.

The other hypervisors on z Systems such as z/VM and KVM are already
supported by OpenStack via Nova drivers. These drivers will continue to be
supported. Adding support for PR/SM DPM allows addressing customers that
need or want to run their workloads in logical partitions, and provides the
advantage for them of using OpenStack as a uniform, standard, cloud
management platform on z Systems.


* Free software: Apache license
* Documentation: http://nova-dpm.readthedocs.io/en/latest/
* Source: http://git.openstack.org/cgit/openstack/nova-dpm
* Bugs: http://bugs.launchpad.net/nova-dpm

Features
--------

* TODO
