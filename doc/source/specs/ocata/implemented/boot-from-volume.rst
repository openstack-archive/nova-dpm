..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

================
Boot from Volume
================

https://blueprints.launchpad.net/nova-dpm/+spec/boot-from-volume

The following use cases should be enabled

* Booting an instance based on a Cinder volume

Background boot from volume
===========================

To understand this spec, some Nova-cinder insights are required.

In classical OpenStack environments (e.g. with focus on libvirt/kvm), the
nova compute service (n-cpu) runs in the Linux operating system of the
hypervisor. The compute node is the hypervisor!

The nova spawn flow with boot from volume looks like this:

.. seqdiag::
   :scale: 80
   :alt: pxe_ipmi

   diagram {
      nova; virt-driver; cinder; host; storage

      nova -> virt-driver [leftnote = "_build_and_run_instance",
        label = "default_device_names_for_instance(instance,
        root_device_name, *block_device_lists)"]
      nova <- virt-driver;
      nova -> virt-driver [label = "get_volume_connector"] {
        virt-driver => host [label = "get host WWPNs"];
      }
      nova <- virt-driver[label = "connector information(wwpns=[..],
        host=cfg.host"];

      nova => cinder [label = "initialize_connection(host_wwpns,
              host)",
        return = "initiator_target_map"] {
        cinder => storage [rightnote = "LUN Masking"];
      }
      nova -> virt-driver [label = "spawn(instance, block_device_info)"]{
        virt-driver => host [label = "create and start instance"];
      }
      nova <- virt-driver;
   }

* Nova conductor calls ``_build_and_run_instance`` of nova compute (manager).
  This call includes a block device mapping for all volumes that should be
  attached.
* nova manager calls ``default_device_names_for_instance`` of the virt driver.
  This method allows the virt-driver to change the default device names for
  the block device mapping.
* nova manager calls ``get_volume_connector`` of the virt driver.
  The virt-driver will return the the hypervisors connector information
  (host WWPNs and it's cfg.host name).
* nova manager calls cinder using ``initialize_connection``. This causes
  cinder to go to the storage subsystem, create a host definition for the
  hypervisor considering its WWPNs and map the requested volumes to it.
* nova manager triggers the ``spawn`` method of the virt driver. Now the virt
  driver does the following actions

  * discover the LUNs
  * attach it locally to the hypervisor (using os-brick)
  * Create the instance. The hypervisor will virtualize this block device and
    offer it as virtio-blk to the instance.

The instance itself is not aware of WWPNs, HBAs and LUNs at all. It just
sees a virtio-blk device.

Problem description
===================

.. _problem1:

Problem 1
---------

DPM only supports Fibre channel (FC) attachments - only FC Cinder volumes
can be supported. Explicitly out of scope are

* iSCSI volumes (DPM lacks integration)
* ECDK volumes (Cinder and DPM lack integration)

.. _problem2:

Problem 2
---------


The PR/SM hypervisor cannot attach storage locally and cannot virtualize
the block devices as virtio-blk to its partitions.
The partitions (instances) have direct access to the FC network via an
Host Bus Adapter (HBA). They appear as FC host with its own host WWPNs.
They are aware of target WWPNs and LUNs.

This results in the following problem when booting an instance:

The host WWPNs to be used are only available after the vHBA got created for
the partition. Partition creation would happen in the drivers ``spawn``
method. But Nova expects this information already to be available
when calling ``get_volume_connector``.

Proposed change
===============

To solve :ref:`problem1`, checkings are put in place that boot from volume
only works with FC volumes.

Configuration
-------------

The administrator needs to define the set of HBAs that should be used via a
new nova DPM configuration option ``physical_storage_adapter_mappings``.
It is a multi line option and must be provided in the following format::

  physical_storage_adapter_mappings = "<storage-adapter-id>:<port-element-id>"
  physical_storage_adapter_mappings = "<storage-adapter-id>:<port-element-id>"

Where

* An HBA is represented by the combination of <storage-adapter-id> and <port>
* <storage-adapter-id> is the object-id of Fibre channel adapter,
  e.g. "48602646-b18d-11e6-9c12-42f2e9ef1641"
* <port-element-id> defines the port number on the fibre channel adapter,
  e.g. "0"
* There's one configuration entry per HBA to add

The following config configures 2 HBAs to the nova compute service. Each
partition created by that n-cpu service will be attached to both HBAs
(a vHBA is created for each of them):::

  physical_storage_adapter_mappings = "48602646-b18d-11e6-9c12-42f2e9ef1641:0"
  physical_storage_adapter_mappings = "11112646-b18d-11e6-9c12-42f2e9e98756:1"


.. note::
  The hypervisor host (PR/SM hypervisor) itself does not have access to those
  HBAs. Also the compute node itself is not attached to those HBAs. Only the
  partition (instance) is!

Boot instance
-------------

Short term
~~~~~~~~~~

The following sequence diagram shows the flow during spawn in the nova compute
(n-cpu) service. n-cpu mainly consists of the following entities

* the common compute.manager (nova)
* the implementation specific virt driver (nova-dpm-driver)

.. note::
  Nova assumes a existing bootable Cinder volume. Creating the volume and
  populating the image on iit is not in the responsibility of Nova.


.. seqdiag::
   :scale: 80
   :alt: pxe_ipmi

   diagram {
      // Do not show activity line
      #activation = none;
      nova; nova-dpm-driver; nova-volume; cinder; HMC; storage

      nova -> nova-dpm-driver [leftnote = "_build_and_run_instance",
        label = "default_device_names_for_instance(instance,
        root_device_name, *block_device_lists)"] {
         nova-dpm-driver => HMC [leftnote = prep_for_spawn,
         label = create_partition];
         nova-dpm-driver => HMC [label = attach_HBAs];
      }
      nova <- nova-dpm-driver;
      nova -> nova-dpm-driver [label = "get_volume_connector"] {
        nova-dpm-driver => HMC [label = getHbas_partition];
      }
      nova <- nova-dpm-driver[label = "Host WWPNs"];

      nova => cinder [label = "initialize_connection(host_wwpns,
              instance_uuid)",
        return = "Target WWPNs, LUN"] {
        cinder => storage [return = "Target WWPNs, LUN",
          rightnote = "LUN Masking, FC Zoning"];
      }
      nova -> nova-dpm-driver [label = "spawn(context, instance, image_meta,
              injected_files, admin_password, network_info=None,
              block_device_info=None, flavor=None)"]{
        nova-dpm-driver => HMC [label = start_partition];
      }
      nova <- nova-dpm-driver;
   }


* Nova conductor calls ``_build_and_run_instance`` of nova compute.
  This call includes a block device mapping for all volumes that should be
  attached.
* Nova manager calls ``default_device_names_for_instance`` of the virt driver.
  To solve :ref:`problem2a`, this method call is abused to create the partition
  and attach all the HBAs to it (create vHBAs)::

    POST /api/partitions/{partition-id}/hbas
    {
        "adapter-port-uri":"/api/adapters/{adapter-id}/storage-ports/0",
        "name":"MyHba_7"
    }

  The result of this operation is a virtual HBA (vHBA) with the following
  relevant properties:

  * ``device-number``, e.g. "1003"
  * ``wwpn``, e.g. "0000000000000007"

   At this point in time the host WWPNs are available.

* nova manager calls ``get_volume_connector`` of the virt driver.
  The virt-driver is able to query the partitions WWPNs. It will return those
  as part of the connector information dict. As host the UUID of the instance
  is chosen. ::

       {
       'wwpns': [WWPN1, WWPN2,...],
       'host': instance.uuid
       }

* Nova manager calls cinder using ``initialize_connection``. This causes
  cinder to go to the storage subsystem, create a host definition for the
  partition considering its WWPNs and map the requested volumes to it. Also
  FC zoning is done as part of this call.
* Nova manager triggers the ``spawn`` method of the virt driver. Relevant
  arguments of this call are

  * *instance*:  the nova Intstance object
  * *block_device_info*: the block device info dictionary::

        {
          'block_device_mapping':[
            {
              'connection_info':{
                'driver_volume_type':'fibre_channel',
                'connector':{
                  'wwpns':[
                    '<WWPN1>', '<WWPN2>'
                  ],
                  'host':'<instance.uuid>'
                },
                'data':{
                  'initiator_target_map':{
                    <WWPN1>:[
                      '500507680B214AC1',
                      '500507680B244AC0'
                    ],
                    <WWPN2>:[
                      '500507680B214AC1',
                      '500507680B244AC0'
                    ],
                  },
                  'target_discovered':False,
                  'target_lun':0
                  'boot_index': 0
                }}},
            {...}]
        }

  The nova virt driver determines the boot parameters to be used

    * ``boot-device``: 'storage-adapter'
    * ``boot-storage-device``: The vHBA belonging to the first adapter in the
      *physical_storage_adapter_mappings* config option
    * ``boot-logical-unit-number``: The first volume in the *block_device_info*
      list
    * ``boot-world-wide-port-name``: The first target WWPN that is listed for
      the host WWPN of the ``boot-storage-device``

TODO: Is the block_device_info list sorted along boot_index?? So is it safe
to always pick the first element? Should we continue with the second if
first is not working?

.. note::

  If boot from the chosen target WWPN is not working, ideally a retry with
  the next WWPN in the list is being done. The challenge is that there
  is no direct way to determine that the boot failed due to a FC issue.
  If none of the target WWPNs is working, probably the other adapter should
  be tried. This needs a separate design document.

.. note::
   virt-driver.attach_volume is NOT being called on ``spawn``. It's only called
   on attach instance which is handled by a different blueprint [4].


Long term
~~~~~~~~~

Introduce the concept of WWPN aware Instances to Nova

os-brick
--------

Some of the storage related operations of the spawn from volume flow
are usually implemented as part of os-brick. For nova-dpm there is no
need to use os-brick due to the following reasons

* os-brick was made to share common code between Nova and Cinder. However
  the PR/SM hypervisor will never host a cinder service. The implemented
  operations would never be required by Cinder.

* Most of the os-brick code is around attaching a volume. But DPM and
  its partitions are not aware of volumes. DPM just manages the HBAs and
  the host WWPNs, but not the volumes. Volumes (LUNs) must be handled from
  the operating system. Therefore the os-dpm changes would just do nothing
  as everything needs to be handled from inside the partition.

* Not depending on os-brick speeds up development

Destroy instance
----------------


TBD


Alternatives
------------

None

Data model impact
-----------------

None

REST API impact
---------------

None

Security impact
---------------

None

Notifications impact
--------------------

None

Other end user impact
---------------------

None

Performance Impact
------------------

None

Other deployer impact
---------------------

None

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <launchpad-id or None>

Other contributors:
  <launchpad-id or None>


Work Items
----------


Dependencies
============


Testing
=======
* Unittest


Documentation Impact
====================
TBD

References
==========
[1] https://blueprints.launchpad.net/nova-dpm/+spec/cinder-integration
[2] https://github.com/openstack/nova-dpm
[3] https://github.com/openstack/cinder
[4] attach volume blueprint

History
=======


