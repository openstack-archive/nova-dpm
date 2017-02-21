=============
Release Notes
=============

1.0.0
=====

*nova-dpm* 1.0.0 is the first release of the Nova virtualization
driver for the PR/SM hypervisor of IBM z Systems and IBM LinuxOne
machines that are in the DPM (Dynamic Partition Manager)
administrative mode.

New Features
------------

* Configure a compute node to manage and consume only
  a subset of a *z Systems* CPC in DPM mode.
* CPC subsetting is hidden from users and they are treated
  like normal hosts in OpenStack.
* Spawn instance from FCP volume.
* Instance lifecycle management.
* Use flat networking.

Known Issues
------------

* VLAN and tunneled networks are not supported in this release.
* Cinder driver for Storwize V7000 Unified returns additional WWPN's
  which are tagged as NAS, which are used for internal connections.
  The invalid target WWPN's need to be blacklisted in nova
  configuration parameters.
* Fibre Channel Multipathing is not supported.
* The configuration parameter ``[DEFAULT].host`` cannot be more than
  17 characters in length.
* Networking: 12 ports per partition at the maximum.
* Networking: In the guest image, always port 0 of an network adapter gets
  autoconfigured. If port 1 should be used, manually deconfigure port 0 and
  configure port 1 in the operating system of the launched instance.
* Boot from image is not available. Boot from volume has to be used.
* Only a single fibre channel network is supported. Configured storage
  adapters and cinder fibre channel backends must all use the same fibre
  channel network.
* The configured maximum number of partitions (``[dpm].max_instances``)
  is not yet enforced.
* All bug reports are listed at: https://bugs.launchpad.net/nova-dpm
