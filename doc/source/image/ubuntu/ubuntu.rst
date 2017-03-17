=================================
Creating a qcow2 image for Ubuntu
=================================

This section explains the qcow2 image creation for Ubuntu.

Precondition
------------
Partition with Ubuntu-16.04 installed and root user access

Modify /etc/fstab so that it remouts the rootfile system with read,write access

It should look like this

::
 
     # /etc/fstab: static file system information.
     #
     # Use 'blkid' to print the universally unique identifier for a
     # device; this may be used with UUID= as a more robust way to name devices
     # that works even if disks are added and removed. See fstab(5).
     #
     # <file system> <mount point>   <type>  <options>       <dump>  <pass>
      /dev/mapper/mpathb-part1 /               ext4    defaults  0       0


Install cloud-init 0.7.9
++++++++++++++++++++++++

`sudo apt-get install cloud-init`

Test-It
+++++++

Run it once to see if things are working
   
 `cloud-init --init`

 .. note::
     
        This might take a few minutes, as cloud-init tries to access various network datasources, which
        probably are not available in your image build environment.But they should be available in your
        OpenStack cloud. For debugging you might need to set "datasource_list: [ ConfigDrive, None ]" in cloud.cfg.
        This excludes those network data sources and boot is pretty fast.

Add DPM-Guest Tools
--------------------

* Install `git` and clone nova-dpm_ repository into the guest image.

  `git clone https://github.com/openstack/nova-dpm.git`

* Copy the following files from nova-dpm directory into the guest image

  ::

      cp nova-dpm/guest_image_tools/usr/bin/autoconfigure_networking.sh  /usr/bin/autoconfigure_networking.sh

      cp nova-dpm/guest_image_tools/usr/lib/systemd/system/autoconfigure_networking.service  /usr/lib/systemd/system/autoconfigure_networking.service

      cp nova-dpm/guest_image_tools/usr/bin/setmac.sh  /usr/bin/setmac.sh

      cp nova-dpm/guest_image_tools/etc/udev/rules.d/80-setmac.rules /etc/udev/rules.d/80-setmac.rules

* Ensure permissions

  `chmod 644 /usr/lib/systemd/system/autoconfigure_networking.service`

* Enable the service for autostart

  `systemctl enable autoconfigure_networking.service`

Cleanup
-------

* Cleanup logs and journalctl

 `rm -rf /var/log/*`

* Remove data from last cloud-init run

 `rm -rf /var/lib/cloud/*`

* Remove persistent mac address interface mappings

 `rm -f /etc/udev/rules.d/70-persistent-net.rules`
  
 `rm -f /etc/udev/rules.d/41-qeth-0.0.1800.rules`

 `rm -f /etc/udev/rules.d/41-zfcp-host-0.0.9999.rules`

* The following lines need  to be removed from /etc/network/interfaces

  ::

     # The primary network interface

     auto enc1800

     iface enc1800 inet static

         address 9.152.151.179

         netmask 255.255.254.0

         network 9.152.150.0

         broadcast 9.152.151.255

         gateway 9.152.150.1

         # dns-* options are implemented by the resolvconf package, if installed

         dns-nameservers 9.152.64.172

         dns-search boeblingen.de.ibm.com

* Remove everything from here

 `rm -f /etc/network/interfaces.d/*`

* Remove persistent network configs

 `rm -f /etc/sysconfig/network-scripts/ifcfg-enc*`

* Clear /etc/hostname

  `echo "" > /etc/hostname`

* Cleanup home directory

  `rm -rf ~/*`


Create qcow2 image
------------------

* In order to nullify space

  `dd if=/dev/zero of=~/tmpfile`

  `rm -rf ~/tmpfile`

* Now stop the partition and access the LUN used for image creation from other machine

* copy disk content byte-by-byte into a raw image

  `dd status=progress if=/path/to/installed/lun of=Ubuntu.img`

* Convert this raw image to qcow

  `qemu-img convert -f raw -O qcow2 Ubuntu.img Ubuntu.qcow`


Test qcow2 image
----------------

* Deploy this image on another LUN

  `qemu-img convert Ubuntu.qcow /path/to/new/lun`

* Use this new LUN to boot the machine



.. _nova-dpm: https://github.com/openstack/nova-dpm.git
