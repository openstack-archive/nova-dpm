=====================
DPM Guest Image Tools
=====================

The DPM Guest Image Tools must be installed within a DPM OpenStack image.
The purpose of the tools are to dynamically configure the network interfaces.

Doing IP configuration is not part of the tools. This is handled like usual
with cloud-init.

autoconfigure_networking
------------------------
Description
+++++++++++
Is used to configure all network interfaces that are listed in the kernels
cmdline */proc/cmdline* with the given adapter port. All interfaces are
configured in layer2 mode.

The format of the data in the cmdline must be

  <devno>,<port>[,<mac>];

Example

  0001,1,0a0000000011;0004,0;

This will result in

* 0001 being configured with port 1

* 0004 being configured with port 0

Content
+++++++
* systemd service autoconfigure_networking.service

* shell script autoconfigure_networking.sh

Trigger
+++++++

The systemd service autoconfigure_networking.service is configured to
run before cloud-init during boot. It's job is to trigger the shell script.

Manual execution of the shell script

  /usr/bin/autoconfigure_networking.sh

Installation
++++++++++++

* Place the following files in the guest image

  * dpm_guest_tools/usr/bin/autoconfigure_networking.sh

    -> /usr/bin/autoconfigure_networking.sh

  * dpm_guest_tools/usr/lib/systemd/system/autoconfigure_networking.service

    -> /usr/lib/systemd/systemd/autoconfigure_networking.service

* Ensure permissions

    chmod 644 /usr/lib/systemd/system/autoconfigure_networking.service

* Enable the service for autostart

  * systemctl enable autoconfigure_networking.service

setmac
------
Description
+++++++++++

Is used to reconfigure the MAC address of a network interface. The mapping
must be provided via the kernels cmdline */proc/cmdline*.

The format of the data in the cmdline must be

    <devno>,<portno>,<mac>;

Example

    0001,1,0a0000000011;0004,0;

* 0001: corresponding interface will be set to mac 0a:00:00:00:00:11

* 0004: mac will not be changed

Content
+++++++

* shell script setmac.sh

* udev rule 80-setmac.rules

Trigger
+++++++

If a new network interface gets configured (e.g. for device 0.0.0001),
the udev rules triggers the shell script passing in the device-bus-id.

If a service instance for a certain device-bus-id already exists, it will not
get started again.

Manual execution of the shell script

  /usr/bin/setmac.sh <dev-bus-id>

Installation
++++++++++++

* Place the following files in the guest image

  * dpm_guest_tools/usr/bin/setmac.sh

    -> /usr/bin/setmac.sh

  * dpm_guest_tools/etc/udev/rules.d/80-setmac.rules

    -> /etc/udev/rules.d/80-setmac.rules
