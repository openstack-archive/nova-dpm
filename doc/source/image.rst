..


==========================================
Steps for creation of DPM qcow2 image
==========================================

Precondition
------------
Partition with RHEL-7.x installed and root user access

Update boot loader
------------------

1. Go to `/etc/zipl.conf` and remove all occurrences of `rd.zfcp=`

2. Add a new rd.zfcp entry

   `rd.zfcp=ipldev`

3. Empty /etc/zfcp.conf file

   `echo "" > /etc/zfcp.conf`

4. Create the dasd.conf file
 
   `touch /etc/dasd.conf`
.. In order to avoid error messages related to dasd configuration

5. Go to `/usr/lib/dracut/modules.d/95zfcp/parse-zfcp.sh`

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


6. Run `dracut -f`
.. To overwrite the existing image

7. Run `zipl -V`
.. To apply the above changes to the contents of boot loader script

Installation of Cloud-init
--------------------------

**Add the RHEL7.3 yum repository from iso**

Copy the iso image to your home directory.

   `mkdir /media/dvd`

   `mount -o loop RHEL-7.3-20161019.0-Server-s390x-dvd1.iso  /media/dvd/`

   `touch  /etc/yum.repos.d/rhel-dvd.repo`

   Add this to rhel-dvd.repo 

    ::

	[dvd]
	name=Red Hat Enterprise Linux Installation DVD
	baseurl=file:///media/dvd
	enabled=1
	gpgcheck=0


**Find the latest cloud-init tar** here_

* Install python setuptools

 `yum install python-setuptools`

* Extract it

 `tar -xf cloud-init-0.7.9.tar.gz`

* Enter the extracted directory

 `cd cloud-init-0.7.9`

* Build and install it:

 `python setup.py build`

  python setup.py install --init-system systemd`

**Configure cloud-init for autostart**

 `stemctl daemon-reload`

 `stemctl enable cloud-init.service`

 `stemctl enable cloud-init-local.service`

 `stemctl enable cloud-final.service`

 `stemctl enable cloud-config.service`


**Configuring cloud-init**

* Deactive Default dependencies

 `sed -i '/^\[Unit\]$/,/^\[/ s/^DefaultDependencies=no/#DefaultDependencies=no/' /usr/lib/systemd/system/cloud-init.service`

 `sed -i '/^\[Unit\]$/,/^\[/ s/^DefaultDependencies=no/#DefaultDependencies=no/' /usr/lib/systemd/system/cloud-init-local.service`

* Remove ordering for sysinit.target

 `sed -i '/^\[Unit\]$/,/^\[/ s/^Before=sysinit.target/#Before=sysinit.target/' /usr/lib/systemd/system/cloud-init.service`

 `sed -i '/^\[Unit\]$/,/^\[/ s/^Before=sysinit.target/#Before=sysinit.target/' /usr/lib/systemd/system/cloud-init-local.service`

* order with systemd-hostnamed.service

 `sed -i '/^\[Unit\]$/,/^\[/ s/^After=networking.service/After=networking.service\nAfter=systemd-hostnamed.service/' /usr/lib/systemd/system/cloud-init.service`

 
The result should look like this:
.................................
`# cat /usr/lib/systemd/system/cloud-init.service`

::

	[Unit]
	Description=Initial cloud-init job (metadata service crawler)
	#DefaultDependencies=no
	Wants=cloud-init-local.service
	Wants=sshd-keygen.service
	Wants=sshd.service
	After=cloud-init-local.service
	After=networking.service
	After=systemd-hostnamed.service
	Before=network-online.target
	Before=sshd-keygen.service
	Before=sshd.service
	#Before=sysinit.target
	Before=systemd-user-sessions.service
	Conflicts=shutdown.target

	[Service]
	Type=oneshot
	ExecStart=/usr/bin/cloud-init init
	RemainAfterExit=yes
	TimeoutSec=0

	# Output needs to appear in instance console output
	StandardOutput=journal+console

	[Install]
	WantedBy=cloud-init.target

`# cat /usr/lib/systemd/system/cloud-init-local.service`

::

	[Unit]
	Description=Initial cloud-init job (pre-networking)
	#DefaultDependencies=no
	Wants=network-pre.target
	After=systemd-remount-fs.service
	Before=NetworkManager.service
	Before=network-pre.target
	Before=shutdown.target
	#Before=sysinit.target
	Conflicts=shutdown.target
	RequiresMountsFor=/var/lib/cloud

	[Service]
	Type=oneshot
	ExecStart=/usr/bin/cloud-init init --local
	ExecStart=/bin/touch /run/cloud-init/network-config-ready
	RemainAfterExit=yes
	TimeoutSec=0

	# Output needs to appear in instance console output
	StandardOutput=journal+console

	[Install]
	WantedBy=cloud-init.target

use the following `/etc/cloud/cloud-cfg`:

::

	# The top level settings are used as module
	# and system configuration.

	# A set of users which may be applied and/or used by various modules
	# when a 'default' entry is found it will reference the 'default_user'
	# from the distro configuration specified below
	users:
	   - default

	# If this is set, 'root' will not be able to ssh in and they
	# will get a message to login instead as the above $user (ubuntu)
	disable_root: false

	# This will cause the set+update hostname module to not operate (if true)
	preserve_hostname: false

	#datasource_list: [ ConfigDrive, None ]

	# Example datasource config
	# datasource:
	#    Ec2:
	#      metadata_urls: [ 'blah.com' ]
	#      timeout: 5 # (defaults to 50 seconds)
	#      max_wait: 10 # (defaults to 120 seconds)

	# The modules that run in the 'init' stage
	cloud_init_modules:
	 - migrator
	# - ubuntu-init-switch
	 - seed_random
	 - bootcmd
	 - write-files
	 - growpart
	 - resizefs
	 - disk_setup
	 - mounts
	 - set_hostname
	 - update_hostname
	 - update_etc_hosts
	 - ca-certs
	 - rsyslog
	 - users-groups
	 - ssh

	# The modules that run in the 'config' stage
	cloud_config_modules:
	# Emit the cloud config ready event
	# this can be used by upstart jobs for 'start on cloud-config'.
	 - emit_upstart
	 - snap_config
	 - ssh-import-id
	 - locale
	 - set-passwords
	# - grub-dpkg
	# - apt-pipelining
	# - apt-configure
	 - ntp
	 - timezone
	 - disable-ec2-metadata
	 - runcmd
	 - byobu

	# The modules that run in the 'final' stage
	cloud_final_modules:
	 - snappy
	 - package-update-upgrade-install
	 - fan
	 - landscape
	 - lxd
	 - puppet
	 - chef
	 - salt-minion
	 - mcollective
	 - rightscale_userdata
	 - scripts-vendor
	 - scripts-per-once
	 - scripts-per-boot
	 - scripts-per-instance
	 - scripts-user
	 - ssh-authkey-fingerprints
	 - keys-to-console
	 - phone-home
	 - final-message
	 - power-state-change

	# System and/or distro specific settings
	# (not accessible to handlers/transforms)
	system_info:
	   # This will affect which distro class gets used
	   distro: rhel




Run it once to see if things are working

**Note:** This might take a few minutes, as cloud-init tries to access various network datasources,
which probably are not available in your image build environment.
But they should be available in your OpenStack cloud. For debugging you might wanna set
"datasource_list: [ ConfigDrive, None ]" in cloud.cfg.
This excludes those network data sources and boot is pretty fast.

   `cloud-init --init`

Cleanup
-------

* Cleanup logs and journalctl

* Unmout iso

 `umount /media/dvd/`

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

 `rm -f /etc/sysconfig/network-scripts/ifcfg-enccw*`

* Cleanup home directory

 `rm -rf ~/*`


Create qcow2 image
------------------

* Now stop the partition and access the LUN used for image creation from another partition

  LUNs are identified based on their UUIDs and listed using `multipath -ll` command.
  Figure out the LUN_ path `/dev/mapper/*` by matching the UUID.

* Run `qemu-img convert /dev/mapper/mpathn  new_rhel.qcow`


Test qcow2 image
----------------

* Run `qemu-img convert new_rhel.qcow /dev/mapper/mpatht`

* Use mpatht LUN as a storage device and boot up new partition

.. _here: https://launchpad.net/cloud-init/+download
.. _LUN: http://searchstorage.techtarget.com/essentialguide/LUN-storage-Working-with-a-SANs-logical-unit-numbers