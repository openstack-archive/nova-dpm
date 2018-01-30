.. _crypto:

==============
Crypto Support
==============

This section describes the crypto support for OpenStack DPM.

Concept
-------

First, the OpenStack administrator must specify the set of crypto adapters
that can be used by OpenStack. This is done via a nova-dpm configuration
option.

The OpenStack administrator must define new flavors that specify the crypto
adapter and crypto domain needs.

The OpenStack user can then request crypto adapters and crypto domains by
selecting the corresponding flavor.


Configuration
-------------

The config option `physical_crypto_adapters` specifies which crypto adapters
can be used by this OpenStack compute node. For more details see the chapter
:ref:`configuration`.

.. note::
  Crypto adapters of all crypto modes can be added to this list. OpenStack
  will never change the crypto type of an adapter but always use the current
  type.

Expressing crypto demands
-------------------------

The OpenStack flavor specifies the crypto adapter and crypto domain needs.
The flavor must be created with the following extra-specs:

* crypto_adapters

  Specifies how many crypto adapters of which type are required.

* crypto_domain_count

  Specifies how many crypto domains are required. This parameter is optional.
  If not given, no crypto domains are supplied. It requires the parameter
  `crypto_adapters` to be present. If not, it will be silently ignored.

**Examples**


One crypto adapter in "EP11" mode without any crypto domain:

.. code::

  $ openstack flavor create --ram 512 --vcpus 1 \
    --property crypto_adapters="ep11" \
    flavor_ep11_no_domain

One crypto adapter in "EP11" mode using one crypto domain:

.. code::

  $ openstack flavor create --ram 512 --vcpus 1 \
    --property crypto_adapters="ep11" \
    --property crypto_domain_count=1 \
    flavor_ep11_single_domain

One crypto adapter in "EP11" mode, one crypto adapter in "CCA" mode and two
crypto adapters in "Accelerator" mode. Also add 2 crypto domains.

.. code::

  $ openstack flavor create --ram 512 --vcpus 1 \
    --property crypto_adapters="ep11,cca:1,accelerator:2" \
    --property crypto_domain_count=2 \
    flavor_all_cryptos


Requesting cryptos features
---------------------------

To request crypto features, simply launch an instance with a flavor that
matches your needs.


Error cases
-----------

If the crypto request cannot be satisfied, the instance build is aborted.
Possible reasons can be

**Not enough crypto adapters of the requested type available**

Solution: Add more crypto adapters of the requested type to the nova
configuration.

**Not enough free crypto domains found**

OpenStack must find crypto domains that are free for use cross all adapters.
If 8 adapters and 2 domains are requested, OpenStack must find 2 domains
that are still available for usage ('control-usage') on all 8 adapters.

Solution: At the moment there is no good solution. Normally the solution would
be to add more crypto adapters to the configuration. But the current
algorithm for finding  a free domain does not consider all possible
combinations of adapters, but is always picking the first possible combination.
To solve the issue, we would need to enhance this algorithm.
