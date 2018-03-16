============================================
Creating a Ubuntu 16.04 nova-dpm guest image
============================================

This document describes how to create an Ubuntu 16.04 guest image for
OpenStack nova-dpm usage.


Install Diskimage-Builder
-------------------------

Important: Images for the target architecture s390x can only be build on
s390x itself.

The Diskimage-Builder is required to create the image.

One way to install it is via pip

.. code-block:: console

    $ pip install "diskimage-builder>=2.10.0"

Clone nova-dpm which contains the dib elements
----------------------------------------------
.. code-block:: console

    $ git clone https://github.com/openstack/nova-dpm.git


Building Images
---------------
.. code-block:: console

    $ export ELEMENTS_PATH="$PWD/nova-dpm/elements"

    # Build a minimum cloud image
    $ disk-image-create -t raw ubuntu-minimal vm nova-dpm-guest-image

    # Build a cloud image including a user configured
    $ export DIB_DEV_USER_USERNAME=devuser
    $ export DIB_DEV_USER_PWDLESS_SUDO=1
    $ export DIB_DEV_USER_PASSWORD=devuser

    $ disk-image-create -t raw ubuntu-minimal vm nova-dpm-guest-image devuser