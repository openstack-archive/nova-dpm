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
========================================

This project will be used for development of nova driver for supporting IBM System z PR/SM hypervisor in DPM mode as a valid nova hypervisor platform.

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

Nova-DPM Overview
=====================

Contents:

.. toctree::
    :maxdepth: 2

    readme
    installation
    usage
    contributing
    devref


Release Notes
=============

.. toctree::
   :maxdepth: 1

   releasenotes/source/unreleased


Specifications
==============

Here you can find the specs, and spec template, for each release:

.. toctree::
   :glob:
   :maxdepth: 1

   specs/ocata/index



