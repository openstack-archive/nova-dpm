.. _installation:

============
Installation
============

The nova-dpm virtualization driver must be installed on every OpenStack compute
node that is supposed to manage a z Systems or LinuxONE machine in DPM mode.

This section describes the manual installation of the nova-dpm driver from
the upstream OpenStack Git repository.

Normally, you should use the stable Git branch for the OpenStack release you
have on the compute node (e.g. for Ocata)::

    $ nova_dpm=https://github.com/openstack/nova-dpm/tree/stable/ocata

If you want to use the latest development code level of the next OpenStack
release, use the ``master`` Git branch::

    $ nova_dpm=https://github.com/openstack/nova-dpm/tree/master

If the Python packages of your OpenStack installation are in the system Python
on the compute node, install the nova-dpm driver with::

    $ sudo pip install $nova_dpm

If the Python packages of your OpenStack installation are in a virtual Python
environment named ``venv`` that was established with ``virtualenvwrapper``,
install the nova-dpm driver with::

    $ workon venv
    $ pip install $nova_dpm

After installing the driver, proceed with its :ref:`configuration`.
