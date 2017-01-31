==========================
openstack/nova-dpm Project
==========================

About this project
------------------

This project provides a Nova virtualization driver for the PR/SM hypervisor of
IBM z Systems and IBM LinuxOne machines that are in the DPM (Dynamic Partition
Manager) administrative mode.

The DPM mode enables dynamic capabilities of the firmware-based PR/SM
hypervisor that are usually known from software-based hypervisors, such as
creation, deletion and modification of partitions (i.e. virtual machines) and
virtual devices within these partitions, and dynamic assignment of these
virtual devices to physical I/O adapters.

The z/VM and KVM hypervisors on z Systems and LinuxONE machines are supported
by separate Nova virtualization drivers:

* KVM is supported by the standard libvirt/KVM driver in the
  `openstack/nova <http://git.openstack.org/cgit/openstack/nova>`_
  project.

* z/VM is supported by the z/VM driver in the
  `openstack/nova-zvm-virt-driver <http://git.openstack.org/cgit/openstack/nova-zvm-virt-driver>`_
  project.

Links
-----

* Documentation: `<http://nova-dpm.readthedocs.io/en/latest/>`_
* Source: `<http://git.openstack.org/cgit/openstack/nova-dpm>`_
* Github shadow: `<https://github.com/openstack/nova-dpm>`_
* Bugs: `<http://bugs.launchpad.net/nova-dpm>`_
* Gerrit: `<https://review.openstack.org/#/q/project:openstack/nova-dpm>`_
* License: Apache 2.0 license
