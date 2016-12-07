========================
Installing with DevStack
========================

What is DevStack?
--------------------------

DevStack is a script to quickly create an OpenStack development environment.

Find out more `here <http://docs.openstack.org/developer/devstack/>`_.


What are DevStack plugins?
--------------------------

DevStack plugins act as project-specific extensions of DevStack. They allow external projects to
execute code directly in the DevStack run, supporting configuration and installation changes as
part of the normal local.conf and stack.sh execution. The devstack plugin setup in this project
is for nova-dpm. Without any additional scripting required the nova-dpm plugin would be plugged
to devstack environment.

More details can be `found here. <http://docs.openstack.org/developer/devstack/plugins.html>`_


How to use the nova-dpm DevStack plugins:
-----------------------------------------

1. Download DevStack::

    $ git clone https://git.openstack.org/openstack-dev/devstack /opt/stack/devstack

2. Set up your local.conf file to pull in our projects:
    1. If you have an existing DevStack local.conf, modify it to pull in this project by adding::

        [[local|localrc]]
        enable_plugin nova-dpm http://git.openstack.org/openstack/nova-dpm
    2. nova-dpm driver requires zhmcclient to be installed and hence add the following line to
    install zhmcclient.

	INSTALL_ZHMCCLIENT=TRUE

3. A few notes:

   * By default this will pull in the latest/trunk versions of all the projects. If you want to
     run a stable version instead, you can either check out that stable branch in the DevStack
     repo (git checkout stable/liberty) which is the preferred method, or you can do it on a
     project by project basis in the local.conf file as needed.

   * If you need any special services enabled for your environment, you can also specify those
     in your local.conf file. In our example files we demonstrate enabling and disabling services
     (n-cpu, q-agt, etc) required for our drivers.

6. Run ``stack.sh`` from DevStack::

    $ cd /opt/stack/devstack
    $ FORCE=yes ./stack.sh

   ``FORCE=yes`` is needed on Ubuntu 15.10 since only Ubuntu LTS releases are officially supported
   by DevStack. If you're running a control only node on a different, supported OS version you can
   skip using ``FORCE=yes``.

7. At this point DevStack will run through stack.sh, and barring any DevStack issues, you should
   end up with a standard link to your Horizon portal at the end of the stack run. Congratulations!
