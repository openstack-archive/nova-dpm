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


Release Process
===============

.. note:: Be aware that the description below is only a simplified summary
   of the official release management documentation which can be found at
   https://docs.openstack.org/project-team-guide/release-management.html
   Reading the section below doesn't replace reading the official docs.

Model
-----

We follow the *Common cycle with development milestones* like Nova does.
In short, this mean we will produce:

* one *full release* at the end of each development cycle
* AND three *milestone releases* during each development cycle.

The versioning of those releases will also follow the rules Nova uses.
In short, this means we will have releases which looks like this:

* The first full release based on *Ocata* has version `1.0.0.`
* A (possible) 2nd full release based on *Ocata* has version `1.0.1`
* The first milestone release in *Pike* has version `2.0.0.0b1`
* The second milestone release in *Pike* has version `2.0.0.0b2`
* The third milestone release in *Pike* has version `2.0.0.0b3`
* The first release candidate for *Pike* has version `2.0.0.0rc1`
* The second full release based on *Pike* has version `2.0.0`

The versioning happens with *git* tags on specific commits which we will
define during the (full/milestone) release process.

------


braindump here ->

https://docs.openstack.org/project-team-guide/stable-branches.html


tagging

stable branches

   what happens with changes in gerrit

release candidate

how to backport

allowed backports