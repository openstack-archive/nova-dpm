===
dpm
===

This element prepares an image for the usage with z Systems DPM.
Therefore it configures the IPL hba device as boot device.

This element has been tested with the `ubuntu-minimal` distro.

Arguments
=========

* ``DIB_ZIPL_DEFAULT_CMDLINE`` sets the CMDLINE parameters that
  are appended to the zipl.conf parameter configuration. It defaults to
  'LANG=en_US.UTF-8'. It overrides the default settings of the element
  'zipl'.

Known Issues
============
**qcow2 format not supported**
For some reason the boot fails if the image got converted to qcow2.
Raw is working fine. When creating an dpm image use `-t raw` to
enforce a raw image is being created.

