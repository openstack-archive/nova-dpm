..
      Copyright 2016 IBM
      All Rights Reserved.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

Welcome to nova-dpm's documentation!
====================================

On IBM z Systems and IBM LinuxOne machines, certain workloads run better in a
partition of the firmware-based PR/SM (Processor Resource/System Manager)
hypervisor, than in a virtual machine of a software hypervisor such as KVM or
z/VM.

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

Overview
========

.. toctree::
    :maxdepth: 2

    history
    topology
    support-matrix

Using the driver
================

.. toctree::
    :maxdepth: 2

    installation
    configuration
    guest_image_tools


Creating DPM Images
===================

.. toctree::
    :maxdepth: 2

    image/rhel7/rhel7_image


Contributing to the project
===========================

.. toctree::
    :maxdepth: 2

    contributing
    devref
    specs/ocata/index
    specs/pike/index
    specs/queens/index



Links
=====

* Documentation: `<http://nova-dpm.readthedocs.io/en/latest/>`_
* Source: `<http://git.openstack.org/cgit/openstack/nova-dpm>`_
* Github shadow: `<https://github.com/openstack/nova-dpm>`_
* Bugs: `<http://bugs.launchpad.net/nova-dpm>`_
* Gerrit: `<https://review.openstack.org/#/q/project:openstack/nova-dpm>`_
