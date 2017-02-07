.. _creating Images:

OpenStack integrated with zSystems is expected to support booting instances from Operating system in qcow2 and raw file formats. 
This section explains the qcow2 image creation for RHEL, Ubuntu ... supporting S/390 architecture.

==========================================
Creating Images
==========================================

Creating a qcow2 image from RHEL
================================

Precondition
------------
Partition with RHEL-7.3 installed and root user access

Update boot loader
------------------

#. Go to `/etc/zipl.conf` and remove all occurrences of `rd.zfcp=`

#. Add a new rd.zfcp entry

   `rd.zfcp=ipldev`

#. Empty /etc/zfcp.conf file

   `echo "" > /etc/zfcp.conf`

#. Create the dasd.conf file # In order to avoid error messages related to dasd configuration

   `touch /etc/dasd.conf`

#. Go to `/usr/lib/dracut/modules.d/95zfcp/parse-zfcp.sh`

   From:

   ::


    #!/bin/sh
    # -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
    # ex: ts=8 sw=4 sts=4 et filetype=sh

    getargbool 1 rd.zfcp.conf -d -n rd_NO_ZFCPCONF || rm /etc/zfcp.conf

    for zfcp_arg in $(getargs rd.zfcp -d 'rd_ZFCP='); do
        echo $zfcp_arg | grep '0\.[0-9a-fA-F]\.[0-9a-fA-F]\{4\},0x[0-9a-fA-F]\{16\},0x[0-9a-fA-F]\{16\}' >/dev/null
        test $? -ne 0 && die "For argument 'rd.zfcp=$zfcp_arg'\nSorry, invalid format."
        (
            IFS=","
            set $zfcp_arg
            echo "$@" >> /etc/zfcp.conf
        )
    done

    zfcp_cio_free

   To:

   ::

    #!/bin/sh
    # -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
    # ex: ts=8 sw=4 sts=4 et filetype=sh

    getargbool 1 rd.zfcp.conf -d -n rd_NO_ZFCPCONF || rm /etc/zfcp.conf

    for zfcp_arg in $(getargs rd.zfcp -d 'rd_ZFCP='); do
        if [ "$zfcp_arg" == "ipldev" -a "$(cat /sys/firmware/ipl/ipl_type)" == "fcp" ] ; then
            zfcp_arg="$(cat /sys/firmware/ipl/device),$(cat /sys/firmware/ipl/wwpn),$(cat /sys/firmware/ipl/lun)"
        fi
        (
           IFS=","
            set $zfcp_arg
            echo "$@" >> /etc/zfcp.conf
        )
    done

    zfcp_cio_free

#. Rebuild the ramdisk
    `dracut -f`


#. To apply the above changes to the contents of boot loader script
    `zipl -V`

Installation of Cloud-init
--------------------------

Add the RHEL7.3 yum repository from ISO
++++++++++++++++++++++++++++++++++++++++

1. Copy the ISO Image to your home directory.

2. Mount the ISO Image to /mnt

  `mount -o loop RHEL-7.3-20161019.0-Server-s390x-dvd1.iso  /mnt`

3. Add the yum repository

  ::

    cat <<EOT > /etc/yum.repos.d/rhel-dvd.repo
    [dvd]
    name=Red Hat Enterprise Linux Installation DVD
    baseurl=file:///mnt
    enabled=1
    gpgcheck=0
    EOT

Download cloud-init 0.7.9 from https://launchpad.net/cloud-init/+download
++++++++++++++++++++++++++++++
 

* Install python setuptools

 `yum install python-setuptools`

* Extract it

 `tar -xf cloud-init-0.7.9.tar.gz`

* Enter the extracted directory

 `cd cloud-init-0.7.9`

* Build and install it:

 `python setup.py build`

 `python setup.py install --init-system systemd`


Add DPM-Guest Tools
+++++++++++++++++++

* Place the following files in the guest image

 * dpm_guest_tools/usr/bin/autoconfigure_networking.sh

   -> /usr/bin/autoconfigure_networking.sh

 * dpm_guest_tools/usr/lib/systemd/system/autoconfigure_networking.service

   -> /usr/lib/systemd/systemd/autoconfigure_networking.service
  
 * dpm_guest_tools/usr/bin/setmac.sh

   -> /usr/bin/setmac.sh

 * dpm_guest_tools/etc/udev/rules.d/80-setmac.rules

   -> /etc/udev/rules.d/80-setmac.rules

* Enable the service for autostart

 * systemctl enable autoconfigure_networking.service


Update cloud-init service files
+++++++++++++++++++++++++++++++

* Deactive Default dependencies

::


   `sed -i '/^\[Unit\]$/,/^\[/ s/^DefaultDependencies=no/#DefaultDependencies=no/' /usr/lib/systemd/system/cloud-init.service`

   `sed -i '/^\[Unit\]$/,/^\[/ s/^DefaultDependencies=no/#DefaultDependencies=no/' /usr/lib/systemd/system/cloud-init-local.service`

* Remove ordering for sysinit.target

::

   `sed -i '/^\[Unit\]$/,/^\[/ s/^Before=sysinit.target/#Before=sysinit.target/' /usr/lib/systemd/system/cloud-init.service`

   `sed -i '/^\[Unit\]$/,/^\[/ s/^Before=sysinit.target/#Before=sysinit.target/' /usr/lib/systemd/system/cloud-init-local.service`

* order with systemd-hostnamed.service

::

   `sed -i '/^\[Unit\]$/,/^\[/ s/^After=networking.service/After=networking.service\nAfter=systemd-hostnamed.service/' /usr/lib/systemd/system/cloud-init.service`

Configure cloud-init for autostart
++++++++++++++++++++++++++++++++++

 `stemctl daemon-reload`

 `stemctl enable cloud-init.service`

 `stemctl enable cloud-init-local.service`

 `stemctl enable cloud-final.service`

 `stemctl enable cloud-config.service`

The result should look like this:

`# cat /usr/lib/systemd/system/cloud-init.service`

.. include:: cloud-init.service
   :literal:

`# cat /usr/lib/systemd/system/cloud-init-local.service`

.. include:: cloud-init-local.service
   :literal:

Use the following cloud.cfg file
++++++++++++++++++++++++++++++++

* Keep this file in /etc/cloud/

.. include:: cloud-cfg
   :literal:

Test-It
+++++++

Run it once to see if things are working
    `cloud-init --init`

 .. note::
    This might take a few minutes, as cloud-init tries to access various network datasources, which probably are not available in your image build environment.
But they should be available in your OpenStack cloud. For debugging you might need to set "datasource_list: [ ConfigDrive, None ]" in cloud.cfg.
This excludes those network data sources and boot is pretty fast.

Cleanup
-------

* Cleanup logs and journalctl

 `rm -rf /var/log/*`

* Unmout iso

 `umount /mnt`

* Remove repo file and update repo

 `rm -f /etc/yum.repos.d/rhel-dvd.repo`

 `yum clean all`

 `yum update`

 `yum repolist`

* Remove data from last cloud-init run

 `rm -rf /var/lib/cloud/*`

* Remove persistent mac address interface mappings

 `rm -f /etc/udev/rules.d/70-persistent-net.rules`

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

* Now stop the partition and access the LUN used for image creation from another partition

  LUNs are identified based on their UUIDs and listed using `multipath -ll` command they are given some specific names like mpatha,mpathb,mpathq,etc.,
  mpath* the last letter varies.Figure out the LUN path `/dev/mapper/*` by matching the UUID.

* copying disk content byte-by-byte into a raw image.

  `dd status=progress if=/dev/mapper/mpathn of=/mnt/images/new_RHEL.img`

* Convert this raw image to qcow 
   
  `qemu-img convert -f raw -O qcow2 new_RHEL.img new_RHEL.qcow`


Test qcow2 image
----------------

* Run `qemu-img convert new_rhel.qcow /dev/mapper/mpatht`

* Use mpatht LUN as a storage device and boot up new partition




