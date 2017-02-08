.. _developer guide:

===============
Developer Guide
===============

Release Notes
=============

Guidelines
----------

* Release note files MUST be part of the code changes which introduce the
  noteworthy behavior change. Noteworthy behavior changes are:

  * a deprecation of a config option
  * a change of the default value of a config option
  * the removal of a config option
  * upgrade relevant actions (e.g. new required config options)
  * security fixes

* When important bug fixes or features are done, release note files
  COULD be part of those code changes.


How-To
------

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
