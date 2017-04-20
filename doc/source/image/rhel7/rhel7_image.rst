=================================
Creating a qcow2 image for RHEL
=================================

This section explains the qcow2 image creation for RHEL.

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

   Apply the following differences:

   ::

    $ diff old_parse-zfcp.sh new_parse-zfcp.sh
    8,9c8,10 < echo $zfcp_arg | grep '0\.[0-9a-fA-F]\.[0-9a-fA-F]\{4\},0x[0-9a-fA-F]\{16\},0x[0-9a-fA-F]\{16\}' >/dev/null
             < test $? -ne 0 && die "For argument 'rd.zfcp=$zfcp_arg'\nSorry, invalid format."
         --- > if [ "$zfcp_arg" == "ipldev" -a "$(cat /sys/firmware/ipl/ipl_type)" == "fcp" ] ; then
             > zfcp_arg="$(cat /sys/firmware/ipl/device),$(cat /sys/firmware/ipl/wwpn),$(cat /sys/firmware/ipl/lun)"
             > fi

   The result should look like this:

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

Add the RHEL7.3 yum repository
+++++++++++++++++++++++++++++++

* Add the yum repository file that points to a network resource

  ::

    cat <<EOT > /etc/yum.repos.d/rhel.repo
    [RHEL7.3]
    name=Red Hat Enterprise Linux Repository
    baseurl=https://x.x.x.x
    enabled=1
    gpgcheck=0
    EOT

Install cloud-init 0.7.9
++++++++++++++++++++++++

  Download latest cloud-init from https://launchpad.net/cloud-init/+download

* Install python setuptools

 `yum install python-setuptools`

* Extract it

 `tar -xf cloud-init-0.7.9.tar.gz`

* Enter the extracted directory

 `cd cloud-init-0.7.9`

* Build and install it:

 `python setup.py build`

 `python setup.py install --init-system systemd`

Update cloud-init service files
+++++++++++++++++++++++++++++++

* Remove Default dependencies

  ::

     sed -i '/^\[Unit\]$/,/^\[/ s/^DefaultDependencies=no/#DefaultDependencies=no/' /usr/lib/systemd/system/cloud-init.service

     sed -i '/^\[Unit\]$/,/^\[/ s/^DefaultDependencies=no/#DefaultDependencies=no/' /usr/lib/systemd/system/cloud-init-local.service

* Remove ordering for sysinit.target

  ::

     sed -i '/^\[Unit\]$/,/^\[/ s/^Before=sysinit.target/#Before=sysinit.target/' /usr/lib/systemd/system/cloud-init.service

     sed -i '/^\[Unit\]$/,/^\[/ s/^Before=sysinit.target/#Before=sysinit.target/' /usr/lib/systemd/system/cloud-init-local.service

* order with systemd-hostnamed.service

  ::

     sed -i '/^\[Unit\]$/,/^\[/ s/^After=networking.service/After=networking.service\nAfter=systemd-hostnamed.service/' /usr/lib/systemd/system/cloud-init.service

The result should look like this:

cat /usr/lib/systemd/system/cloud-init.service

  .. include:: cloud-init.service
     :literal:

cat /usr/lib/systemd/system/cloud-init-local.service

  .. include:: cloud-init-local.service
     :literal:

Configure cloud-init for autostart
++++++++++++++++++++++++++++++++++

 `systemctl daemon-reload`

 `systemctl enable cloud-init.service`

 `systemctl enable cloud-init-local.service`

 `systemctl enable cloud-final.service`

 `systemctl enable cloud-config.service`

Use the following cloud.cfg file
++++++++++++++++++++++++++++++++

* Keep this cloud.cfg file in /etc/cloud/

  .. include:: cloud.cfg
     :literal:

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

      cp nova-dpm/guest_image_tools/usr/bin/dpm_guest_image_tools_common  /usr/bin/

      cp nova-dpm/guest_image_tools/etc/udev/rules.d/80-setmac.rules /etc/udev/rules.d/80-setmac.rules

* Ensure permissions

  `chmod 644 /usr/lib/systemd/system/autoconfigure_networking.service`

* Enable the service for autostart

  `systemctl enable autoconfigure_networking.service`

Cleanup
-------

* Cleanup logs and journalctl

 `rm -rf /var/log/*`

* Remove repo file and update repo

 `rm -f /etc/yum.repos.d/rhel.repo`

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

* Now stop the partition and access the LUN used for image creation from other machine

* copy disk content byte-by-byte into a raw image

  `dd status=progress if=/path/to/installed/lun of=RHEL.img`

* Convert this raw image to qcow

  `qemu-img convert -f raw -O qcow2 RHEL.img RHEL.qcow`


Test qcow2 image
----------------

* Deploy this image on another LUN

  `qemu-img convert RHEL.qcow /path/to/new/lun`

* Use this new LUN to boot the machine



.. _nova-dpm: https://github.com/openstack/nova-dpm.git

