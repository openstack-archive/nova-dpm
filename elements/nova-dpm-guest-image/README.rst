====================
nova-dpm-guest-image
====================

This element prepares an image for the usage with nova-dpm.

The following key aspects are considered

* Installation of nova-dpm guest-image-tools
* Installation of cloud-init
* Installation of ssh server

This element has been tested with the `ubuntu-minimal` distro.

Arguments
=========

* ``DIB_NOVA_DPM_GUEST_TOOLS_BRANCH``. The nova-dpm guest-image-tools will
  be downloaded in the provided version. It defaults to 'master'.

