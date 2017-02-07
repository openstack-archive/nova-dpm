..
 
 
==========================================
Image for DPM-Nova  
==========================================
OpenStack integrated with zSystems is expected to support booting instances from Operating system in qcow2 and raw file formats. This spec explains the qcow2 image format creation for RHEL, Ubuntu ... supporting S/390 architecture.

OpenStack-Glance:
-----------------

* Glance_ which is expected to maintain image files for instances created using OpenStack.

* The images generated for OpenStack dpm integration will be uploaded to Glance which can be later used to create Volume.

OpenStack-Cinder:
-----------------

* Bootable-volume_ is created out of the image using OpenStack-Cinder_ drivers and used to launch an Instance in OpenStack.

Restrictions:
-------------

* Commonly used methodologies like snapshot creation using LVM_ are not supported by PR/SM hypervisor on zSystems.

Image Creation:
---------------

* The image creation requires generalizing the boot volume attributes on an existing installed operation system(S/390 architecture) to be able to easily port the image from one partition to another based on the volume chosen.

* **Image boot parameters** that are generated during the image installation process are Target-WWPN_ and LUN_.
  Usually image installed on a partion on zSystem will contain the FCP attributes in zipl.conf_
          rd.zfcp = 0.0.fc00,0x5105074308c212e9,0x401040a300000000 
  The above attribute will be generalized to rd.zfcp = ipldev and image creation procedure will update the ipldev parameter to relevant WWPN, LUN  based on the volume chosen for installation.

* **Cloud-init** is installed on this volume as it  handles the early initialization process like setting hostname,generating ssh keys,assigning IP address,etc.,

* Using qemu-img,qcow2 is extracted from this image installed volume and uploaded to Glance.

Assignee(s)
-----------

Primary assignee:
  sreeteja

Other contributors:
  None


Testing
=======
     
Upload the qcow2 image to the glance and try to launch an instance using this image file .

References
==========


.. _Glance: http://docs.openstack.org/developer/glance/
.. _Target-WWPN: https://www-912.ibm.com/supporthome.nsf/document/51455410
.. _LUN: http://searchstorage.techtarget.com/essentialguide/LUN-storage-Working-with-a-SANs-logical-unit-numbers
.. _zipl.conf: https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/Installation_Guide/ap-s390info-Adding_FCP-Attached_LUNs-Persistently.html
.. _Bootable-volume: http://docs.openstack.org/user-guide/cli-nova-launch-instance-from-volume.html
.. _LVM: https://www.centos.org/docs/5/html/Cluster_Logical_Volume_Manager/snapshot_command.html
.. _OpenStack-Cinder: http://docs.openstack.org/kilo/config-reference/content/section_block-storage-overview.html
| http://searchdatacenter.techtarget.com/definition/S-390
| https://wiki.archlinux.org/index.php/disk_cloning
| https://www.kernel.org/pub/linux/utils/boot/dracut/dracut.html




History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Ocata
     - Introduced
