..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=========================================================
Base Support Nova Cinder Communication
=========================================================

https://blueprints.launchpad.net/nova-dpm/+spec/cinder-integration

The nova-dpm virt driver requires Cinder integration to be able spawn
an instance which should boot from FCP LUN with pre-installed image.


Problem description
===================

The nova-dpm virt driver requires Cinder integration to accomplish the
below mentioned use cases:

* Attaching FC Volumes to Instances

* Support boot from the FC volume

Use Cases
---------

* Spawn Instance attaching a Volume created using Cinder interfaces.
* Instance spawned boots from the pre-installed image on the volume
  attached.

Proposed change
===============

Attaching Volumes to Instances
------------------------------

* Once volumes with pre-installed image are available, they can be
  attached to an instance. One of these volumes may serve as a boot
  volume.
* The OpenStack administrator assigns Fibre Channel adapters
  to the CPCSubset via the nova-compute configuration file.
* The configuration parameters used for setting the Fibre Channel Adapter
  details are as follow::
  physical_storage_adapter_mappings = "<storage-adapter-id>:<port-element-id>"

  * <storage-adapter-id> is the UUID of Fibre channel adapter eg: "48602646-b18d-11e6-9c12-42f2e9ef1641"
  * <port-element-id> defines the port number on the fibre channel adapter eg: "0"

* Instance spawn flow triggers pre-spawn functionality on nova-dpm
  driver which should create Partition on DPM(Dynamic Partition Manager)
  and attach storage adapter -vHBA for each physical fibre channel port
  configured for CPCSubset/host.
* Each vHBA attached to the partition gets a WWPN and nova-dpm
  driver will return all the WWPNs to Cinder created for partition
  which will require access to the volume(s).
* Cinder needs to modify access permissions in the storage subsystem
  and potentially in SAN switches.
* Cinder then needs to pass the target WWPNs and LUN of the FCP volume to
  nova-dpm driver.
* nova-dpm virt driver uses this information in order to configure target
  WWPN and LUN as boot parameters for the DPM partition
* Other options are under discussion. A new 'auto-onfiguration' service
  is under discussion. This service would allow DPM OpenStack to pass
  device numbers, WWPNs, or LUNs to the Operating System and have it
  perform the configuration.

The differences between a KVM & DPM environment:

* A KVM hypervisor has access to Fibre Channel adapters. FCP volumes
  are first of all added to the KVM hypervisor configuration.
  The resulting block device is then added as a virtio-blk volume
  to the guest instance configuration.
  The guest instance thus does not require direct access to a
  Fibre Channel adapter. Any volume access happens through the
  hypervisor.
* In DPM there is no such virtualization layer, therefore the
  partition is aware of FC. The DPM partition has access to the HBA,
  has its own WWPNs and is also aware of target WWPNs and LUNs.
  Hence, OpenStack with DPM needs to add vHBAs to the guest
  partition definition in DPM.


Support boot from the FC volume
-------------------------------
* Spawn flow in nova-dpm driver is invoked with the details of
  HBAs, LUNs and target WWPNs which is then used to activate
  the DPM partition setting the boot-device option as
  "storage-adapter".

* The boot parameters are picked like this:

  * Boot vHBA: The first adapter port of the storage_adapter_mappings
    configuraiton is picked as boot HBA
  * Target WWPN: The first target WWPN returned by cinder is used
    as target WWPN
  * LUN: LUN id returned by Cinder

.. note::

  As of now the retry on boot from storage failure to next working
  combination of HBA, LUN and WWPN is not supported because there is
  no direct way to determine that the boot failed due to HBA or LUN
  or WWPN.

Base Flow for Attaching Volumes to Instances and Boot from Storage
-------------------------------------------------------------------

Spawn
~~~~~

.. seqdiag::
   :scale: 80
   :alt: pxe_ipmi

   diagram {
      // Do not show activity line
      #activation = none;
      nova; nova-dpm-driver; nova-volume; cinder; HMC; storage

      nova -> nova-dpm-driver [leftnote = _build_and_run_instance,
        label = "default_device_names_for_instance(instance,
        root_device_name, *block_device_lists)"] {
         nova-dpm-driver => HMC [leftnote = prep_for_spawn,
         label = create_partition];
         nova-dpm-driver => HMC [label = attach_HBAs];
      }
      nova <- nova-dpm-driver;
      nova -> nova-dpm-driver [label = get_volume_connector,
        return = "Host WWPNs"] {
        nova-dpm-driver => HMC [label = getHbas_partition];
      }
      nova <- nova-dpm-driver;

      nova => cinder [label = "initialize_connection(host_wwpns,
              instance_uuid)",
        return = "Target WWPNs, LUN"] {
        cinder => storage [return = "Target WWPNs, LUN",
          rightnote = "LUN Masking"];
      }
      nova -> nova-dpm-driver [label = "spawn(context, instance, image_meta,
              injected_files, admin_password, network_info=None,
              block_device_info=None, flavor=None)"]{
        nova-dpm-driver => HMC [label = start_partition];
      }
      nova <- nova-dpm-driver;
   }

Note: above flow differs from what is done for libvirt. DPM
OpenStack creates the partition definition in DPM during the
spawn sequence. Nova manager code flow is bifurcated into
prep_for_spawn flow and spawn flow invokation on nova-dpm
driver. prep_for_spawn is used for partition creation and
attaching vHBA which will help return host WWPNs. spawn flow
on nova-dpm driver will further boot the partition from the
attached LUNs.

Attach Volume to Instance
~~~~~~~~~~~~~~~~~~~~~~~~~

.. seqdiag::
   :scale: 80
   :alt: pxe_ipmi

   diagram {
      // Do not show activity line
      #activation = none;
      nova; nova-dpm-driver; nova-volume; cinder; HMC; storage

      nova -> nova-dpm-driver [leftnote = _attach_volume,
        label = "get_volume_connector"];
      nova -> cinder [label = "initialize_connection"];
      cinder -> storage [rightnote = "LUN Masking"];
      cinder <- storage [label = "Target WWPNs, LUN"];
      nova <- cinder [label = "Target WWPNs, LUN"];
      nova-dpm-driver -> nova-volume [label = "connect_volume"];
      nova-dpm-driver <- nova-volume;
   }


Assumtions:

* A storage administrator has assigned one or multiple physical
  Fibre-Channel adapters to the CPCSubset/Host.

The base flow for attaching a volume as part of spawn looks as follows:

* Spawn instance flow triggers "default_device_names_for_instance"
  which has been implemented by nova-dpm driver to create a DPM
  partition and attach vHBA for each Fibre channel port configured.

* nova-dpm driver returns all the WWPN attached to the partition
  as part of get_volume_connector function invoked by Cinder.

* Cinder updates Zoning and LUN Masking

* The storage subsystem returns target WWPNs and the LUN number for
  each volume and Cinder returns this information to
  nova-dpm driver

* Nova performs connect_volume. This function would normally add
  the volume to a (KVM) hypervisor.
  We will not do anything in the initial release. We may communicate
  volume information (WWPN, LUN) to the partition in a future release.

* spawn function is invoked on nova_dpm driver with one of the parameters
  as block_device_info which again contains Block device mapping with
  dictionary of information contain various attributes of which the following
  will be used in code to derive the list of Target WWPNs and LUN.

  block_device_mapping[{'connection_info':
                        {'data':
                         {'initiator_target_map':
                          {'<host_wwpn>': ["<list of targetwwpns>"]
                         {'target_lun': "<targetLun>"
                      ...]

* The partition is then started with first HBA(of multiple), first
  WWPN(of multiple) and LUN::

  HBA = first one from list of HBAs queried for the Partition from DPM API
  TargetWWPN = block_device_mapping[0]['connection_info']['data']['initiator_target_map'][host_wwpn][0]
  LUN = str(block_device_mapping[0]['connection_info']['data']['target_lun'])

.. note::
  Many of the operations executed as part of spawning an instance
  are usually implemented as part of os-brick. We however want to avoid
  any dependency to os-brick initially. Integrating the few required
  operations in Nova simplifies the management of the files a lot.
  Cinder will never execute any of the operations that will
  be implemented for DPM. Those are specific to the support of Nova
  in a DPM environment.
  We will instead create Nova volume drivers which will provide the
  support to attach / detach volumes.


Nova Cinder detailed communication flow
---------------------------------------

For those who love the details:

::

 __init__                                            nova.compute.manager.py
  load_compute_driver                                nova.virt.driver.py

   __init__                                          nova.virt.dpm.driver.py
    _get_volume_drivers                              -> 'nova.virt.dpm.volume.fibrechannel.' 'DpmFibreChannelVolumeDriver',
                                                      ** determines / gets volume driver to be used in Nova for Fibre-Channel
   ...
   ...

 _build_and_run_instance                              nova.compute.manager.py
  _build_resources                                    nova.compute.manager.py
                                                      ** this function needs to be changed to only call
                                                      _default_block_device_names
   _default_block_device_names
    _default_device_names_for_instance                nova_dpm.virt.dpm.driver.py
     prep_for_spawn                                   nova_dpm.virt.dpm.driver.py
   ...
   ...

 _prep_block_device                                   nova.compute.manager.py
  get_block_device_info                               nova.virt.driver.py
  block_device_info_get_mapping                       nova.virt.driver.py
                                                      -then continue with what is normally done in nova.compute.manager._build_resources:
                                                       LOG.debug('Start building block device mappings for instance.',
                                                                 instance=instance)
                                                       instance.vm_state = vm_states.BUILDING
                                                       instance.task_state = task_states.BLOCK_DEVICE_MAPPING
                                                       instance.save()

                                                       block_device_info = self._prep_block_device(context, instance,
                                                               block_device_mapping)
                                                       resources['block_device_info'] = block_device_info

  attach_block_devices                                nova.virt.block_device.py
    _log_and_attach
     attach
      get_volume_connector                            nova.virt.libvirt.driver.py
                                                          ** returns wwpns of DPM partition

      initialize_connection                           nova.volume.cinder
       initialize_connection                          cinder.volume.manager
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

  self.driver.spawn                                   - gets block device info as parm. Including connection_info (WWPNs, ...)
    spawn                                             nova_dpm.virt.dpm.driver.py
                                                      - needs to get context, instance, block_device_info as parm (same as for libvirt)
                                                      - then execute block_device_mapping = driver.block_device_info_get_mapping( block_device_info)



And here the same details for attaching a volume to an instance:

::

  attach_volume                                       nova.compute.api.py
                                                      gets a disk_bus and device_type and volume_id
   _attach_volume
    _create_volume_bdm                                create block_device_mapping, containing information about the device to be attached
    :
     attach_volume                                    nova.compute.manager.py
      _attach_volume
       attach                                         nova.virt.block_device.py
        get_volume_connector                          nova_dpm.virt.dpm.driver
        initialize_connection                         nova.volume.cinder
        :
        attach_volume                                 nova_dpm.virt.dpm.driver
                                                      sets up bdm (block_device_mapping):
         _connect_volume
          _get_volume_driver
           vol_driver.connect_volume
            connect_volume                            nova_dpm.virt.dpm.volume.fibrechannel.py


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


History
=======


