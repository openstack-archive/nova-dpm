=============
Release Notes
=============

1.0.0
=====

nova-dpm 1.0.0 is the first release of the  Nova virtualization
driver for the PR/SM hypervisor of IBM z Systems and IBM LinuxOne
machines that are in the DPM (Dynamic Partition Manager)
administrative mode.

New Features
------------

* Create multiple hosts/CPCSubsets on the same System z server.
* List hosts/CPCSubsets.
* Spawn instance from FCP volume.
* Instance lifecycle management.
* List instances

Known Issues
------------

* VLAN networks are not supported in this release.
* Cinder driver for Storwize V7000 Unified returns addtioinal WWPN's
  which are tagged as nas, which are used for internal connections.
  The invalid target WWPN's need to be blacklisted in nova
  configuration parameters.
* Fibre Channel Multipathing is not supported.
* The configuration parameter cfg.default.host cannot be more than
  17 characters in length.