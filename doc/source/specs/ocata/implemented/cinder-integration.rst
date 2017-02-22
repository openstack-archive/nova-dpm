..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=========================================================
Base Support Nova Cinder Communication
=========================================================

Include the URL of your launchpad blueprint:

https://blueprints.launchpad.net/nova-dpm/+spec/cinder-integration

The nova-dpm virt driver requires Cinder integration to be able spawn
an instance which should boot from FCP LUN with pre-installed image.


Problem description
===================

The nova-dpm virt driver requires Cinder integration to accomplish the
below mentioned use cases:

* Image Deployment on an FCP LUN

* Attaching Volumes to Instances

* Support boot from the volume

Use Cases
---------

* Create volume and install bootable Operating System
* Attach storage adapters to the Instance which should enable DPM 
partition to access the LUN.
* Starting DPM instance which will boot from pre-installed FCP LUN

Proposed change
===============

Image Deployment
----------------

The deployment of a bootable image is done by Cinder without
any involvement by Nova. Cinder typically creates a new volume,
modifies access permission (storage subsystem and potentially
SAN switches) to allow access by the WWPNs assigned to its node, 
attaches it to its own node, deploys the image, detaches
the volume, and finally changes SAN and storage subsystem 
access permission back again.
The Cinder service is typically deployed on a controller node.
But it maybe running on any node. It will typically run on
a Linux Operating System. No special support is required for
DPM OpenStack.

Attaching Volumes to Instances
------------------------------
 
Once volumes are available, they can be attached to an instance.
One of these volumes may serve as a boot volume.
Making a volume available to an instance requires interaction
between Cinder and Nova. Nova needs to pass Cinder the WWPNs
which will require access to the volume(s).
Cinder needs to modify access permissions in the storage subsystem
and potentially in SAN switches.
Cinder then needs to pass the WWPNs and LUN of the FCP volume to
Nova. Nova uses this information in order to change
a Hypervisor configuration to add the WWPNs and LUN and attach
the volume to the guest. Since the steps to add a volume to 
a Hypervisor configuration are the same for Cinder and Nova,
Cinder and Nova use the os-brick library for this purpose.

There are a couple of differences between a KVM environment, and
a DPM environment:

* a KVM hypervisor has access to Fibre Channel adapters. FCP volumes
  are first of all added to the KVM hypervisor configuration. 
  The resulting block device is then added as a virtio-blk volume
  to the guest instance configuration.
  The guest instance thus does require direct access to a
  Fibre Channel adapter. Any volume access happens through the
  hypervisor.
  FCP volumes to the guest configuration as virtio-block devices.
* the LPAR hypervisor does not have access to any of the 
  Fibre Channel adapters. In order to allow a guest instance access
  a Fibre Channel volume, the guest instance (LPAR) requires
  vHBAs.
  The OpenStack DPM support needs to add vHBAs to the guest 
  intances definition in DPM. The operating system running in the
  guest instance needs to also have these vHBAs in its
  configuration.
* since the LPAR hypvervisor does not have access to any 
  FCP volume, the volume needs to be access directly by the 
  guest instance. It thus needs to be configured in the 
  operating system running in the guest instance.

DPM OpenStack somehow needs to determine which vHBAs to assign and
use for guest instance. One option would have been to have the
OpenStack administrator add Fibre Channel adapters (physical adapters)
to the Nova configuration. And then have Nova instruct DPM to 
create a vHBA for each Fibre Channel adapter for an instance as it
is created. We, however, did not want Nova to manage resources, such
as Fibre Channel adapters and thus took the following approach:
the OpenStack administrator assigns Fibre Channel adapters to the 
OpenStack 'domain'. Within the domain, Nova will create a vHBA for
each of the physical Fibre-Channel adapters as an instance is defined.

vHBAs as well as Fibre Channel volumes need to be added to the 
configuration of the operating system running in the guest instance.
If the volume is used as boot and root volume, this information
can be passed to the SCSI IPL loader. The image needs to be prepared
to use the information passed to the SCSI IPL loader for the root
volume.

For other volumes added either prior to IPL, or to a running instance,
things are more complex.
The recommendation will initially be to activate auto-discovery in the
operating system.
Other options are under discussion. A new 'auto-onfiguration' service
is under discussion. This service would allow DPM OpenStack to pass
device numbers, WWPNs, or LUNs to the Operating System and have it
perform the configuration.

Base Flow for Attaching Volumes to Instances
--------------------------------------------

Assumtions:

* a storage administrator has assigned one or multiple physical
  Fibre-Channel adapters to the OpenStack domain.
* a user has defined an instance
* DPM OpenStack has instructed to add a vHBA for each of the
  Fibre-Channel adapters to the instance definition

The base flow for attaching a volume looks as follows:

* Nova identifies the WWPNs assigned the vHBAs in the DPM
  guest configuration

* Nova passes this information to Cinder through initialize_connection

* Cinder updates Zoning and LUN Masking

* the storage subsystem returns target WWPNs and the LUN number for
  each volume

* Cinder returns this information to Nova

* Nova performs connect_volume. This function would normally add
  the volume to a (KVM) hypervisor. 
  We will not do anything in the initial release.
  We may communicate volume information (WWPN, LUN) to the partition
  in a future release.


Nova Cinder Simplified Communication Flow
-----------------------------------------

Many of the operations executed as part of spawning an instance are
usually implemented as part of os-brick. We however want to avoid
any dependency to os-brick initially. Integrating the few required
operations in Nova simplifies the management of the files a lot.
Besides - Cinder will never execute any of the operations that will
be implemented for DPM. Those are specific to the support of Nova
in a DPM environment.
We will instead create Nova volume drivers which will provide the
support to attach / detach volumes.


Spawn
~~~~~

.. seqdiag::
   :scale: 80
   :alt: pxe_ipmi

   diagram {
      // Do not show activity line
      #activation = none;
      nova; nova-driver; nova-volume; cinder; HMC; storage

      nova -> nova-driver [label = spawn];
      nova-driver -> nova [label = _prep_block_device];
      
      nova => nova-driver [label = "get_volume_connector",
        return = "Host WWPNs"] {
        nova-driver => HMC;
      }

      nova => cinder [label = "initialize_connection",
        return = "Target WWPNs, LUN"] {
        cinder => storage [return = "Target WWPNs, LUN",
          rightnote = "LUN Masking"];
      }

      nova => nova-driver [label = "connect_volume"] {
        nova-driver => nova-volume [label = connect_volume]
      }

      nova-driver <- nova;

      nova <- nova-driver;
   }

Note: above flow differs from what is done for libvirt. DPM
OpenStack creates the partition definition in DPM during the 
spawn sequence. It thus does not know host WWPNs before that point
in time. 
prep_block_device will thuse be executed at a later point in time.

Attach Volume to Running Instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. seqdiag::
   :scale: 80
   :alt: pxe_ipmi

   diagram {
      // Do not show activity line
      #activation = none;
      nova; nova-driver; nova-volume; cinder; HMC; storage

      nova -> nova-driver [leftnote = _attach_volume,
        label = "get_volume_connector"];
      nova-driver -> HMC;
      nova-driver <- HMC;
      nova-driver -> cinder [label = "initialize_connection"];
      cinder -> storage [rightnote = "LUN Masking"];
      cinder <- storage [label = "Target WWPNs, LUN"];
      nova-driver <- cinder [label = "Target WWPNs, LUN"];
      nova-driver -> nova-volume [label = "connect_volume"];
      nova-driver <- nova-volume;
   }




As said, most of the changes need to be done to os-brick. The following
is a list of required changes.

Required code changes
---------------------

To be added


Nova Cinder detailed communication flow
---------------------------------------

For those who love the details:

::

  __init__                                            nova.compute.manager.py
   load_compute_driver                                nova.virt.driver.py

    __init__                                          nova.virt.dpm.driver.py
     _get_volume_drivers  -> 'nova.virt.dpm.volume.fibrechannel.' 'DpmFibreChannelVolumeDriver',
                                                      ** determines / gets volume driver to be used in Nova for Fibre-Channel
   ...
   ...

 _build_and_run_instance                              nova.compute.manager.py
  _build_resources                                    nova.compute.manager.py
                                                      ** this function needs to be changed to only call
                                                      _default_block_device_names
   _default_block_device_names
   ...
   ...

  self.driver.spawn                                   - gets block device info as parm. Including connection_info (WWPNs, ...)
    spawn                                             nova.virt.dpm.driver.py
                                                      - needs to get context, instance, block_device_info as parm (same as for libvirt)
                                                      - then execute block_device_mapping = driver.block_device_info_get_mapping( block_device_info)
     block_device_info_get_mapping                    nova.virt.driver.py
                                                      - then continue with what is normally done in nova.compute.manager._build_resources:
                                                        LOG.debug('Start building block device mappings for instance.',
                                                                  instance=instance)
                                                        instance.vm_state = vm_states.BUILDING
                                                        instance.task_state = task_states.BLOCK_DEVICE_MAPPING
                                                        instance.save()
                                                       
                                                        block_device_info = self._prep_block_device(context, instance,
                                                                block_device_mapping)
                                                        resources['block_device_info'] = block_device_info
     _prep_block_device                                 nova.compute.manager.py
      get_block_device_info                             nova.virt.driver.py
      block_device_info_get_mapping                     nova.virt.driver.py
      attach_block_devices                              nova.virt.block_device.py
       _log_and_attach
        attach
         get_volume_connector                           nova.virt.libvirt.driver.py
                                                          ** returns wwpns of DPM partition
    
         initialize_connection                          nova.volume.cinder
          initialize_connection                         cinder.volume.manager
                                                        -> nova hands over host wwpn, volume id to cinder
                                                        -> cinder talks to driver to update LUN masking! For SVC
                                                           - tries to identify SVC hostname by host wwpn. Creates new one, if it does not exist
                                                           - maps volume to host
                                                        -> cinder driver is supposed to return something like as connection_info
                                                           'data': {
                                                              'target_lun': '2',
                                                              'initiator_target_map':
                                                                 {'c05076ffe680a590': ['5005076802160417', '5005076802260417'],
                                                                 'c05076ffe6809fc8': ['5005076802160417', '5005076802260417']},
                                                              'target_wwn': '5005076802160417',
                                                              'target_discovered': False,
                                                              'volume_id': u'2bb89d80-a0be-4a57-a939-7395967d790c'}
    
         attach_volume is not called when the instance is not active (do_driver_attach = false)
    
    

     _connect_volume                                  nova.virt.dpm.driver.py
                                                      - the disk_info parm can be left empty
      _get_volume_driver
      connect_volume                                  nova.virt.dpm.volume.fibrechannel.py


And here the same details for attaching a volume to a running instance:

::

  attach_volume                                       nova.compute.api.py
                                                      gets a disk_bus and device_type and volume_id
   _attach_volume
    _create_volume_bdm                                create block_device_mapping, containing information about the device to be attached
    :
     attach_volume                                    nova.compute.manager.py
      _attach_volume
       attach                                         nova.virt.block_device.py
        get_volume_connector                          nova.virt.dpm.driver
        initialize_connection                         nova.volume.cinder
        :
        attach_volume                                 nova.virt.dpm.driver
                                                      sets up bdm (block_device_mapping):
         _connect_volume
          _get_volume_driver
           vol_driver.connect_volume
            connect_volume                            nova.virt.dpm.volume.fibrechannel.py


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



History
=======


