===============
Developer Guide
===============

Release Notes
=============

Before a new version is released, the release notes should be double-checked
if they are up-to-date.

To create a new release note::

    $ reno --rel-notes-dir=doc/source/releasenotes/ new file-name-goes-here

To list existing release notes::

    $ reno --rel-notes-dir=doc/source/releasenotes/ list .

To build the release notes::

    $ tox -e docs

.. note:: If you build the release notes locally, please be aware that
   *reno* only scans release note files (`*.yaml`) which are committed
   in your local repository of this project.

More information about *reno* can be found at:
http://docs.openstack.org/developer/reno/index.html