============================================
Creating a Ubuntu 16.04 nova-dpm guest image
============================================

This document describes how to create an Ubuntu 16.04 guest image for
OpenStack nova-dpm usage.

Install Diskimage-Builder
-------------------------

The Diskimage-Builder is required to create the image.

One way to install it is via pip

$ pip install diskimage-builder>=2.10.0

Clone nova-dpm which contains the dib elements
----------------------------------------------

$ git clone https://github.com/openstack/nova-dpm.git


Building images
---------------

export ELEMENTS_PATH="$PWDnova-dpm"

disk-image-create -t raw ubuntu-minimal vm nova-dpm-guest-image

