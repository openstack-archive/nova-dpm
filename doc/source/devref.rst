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


Release Management
==================

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

* The first full release based on *Ocata* has version ``1.0.0.``
* A (possible) 2nd full release based on *Ocata* has version ``1.0.1``
* The first milestone release in *Pike* has version ``2.0.0.0b1``
* The second milestone release in *Pike* has version ``2.0.0.0b2``
* The third milestone release in *Pike* has version ``2.0.0.0b3``
* The first release candidate for *Pike* has version ``2.0.0.0rc1``
* The second full release based on *Pike* has version ``2.0.0``

The versioning happens with *git* tags on specific commits which we will
define during the (full/milestone) release process.

Process
-------

When creating a new full release, the usual order of action is:

* start during the RC phase (usually ~3 weeks before the release)
* merge the open changes which need to make the release into master
* create a ``stable/<release>`` branch from master (master is now open
  for changes for the next release)
* tag the last commit in that stable branch with the *release candidate* tag
* double-check if that release candidate needs fixes
* tag the final release candidate 1 week before the actual release
* tag the final full release


Stable Branches
===============

.. note:: Be aware that the description below is only a simplified summary
   of the official stable branch documentation which can be found at
   https://docs.openstack.org/project-team-guide/stable-branches.html
   Reading the section below doesn't replace reading the official docs.

Supported releases
------------------

We will have 3 simultaneously maintained branches as a maximum. These are:

* master (``N``)
* the latest stable release (``N-1``)
* the older stable release (``N-2``)

Branches older than these will be deleted after a ``<release-eol>`` tag was
applied to the last commit of that branch.

Backports
---------

Again, we follow the same rules Nova does. In short, this means:

* for the latest stable branch (``N-1``)

  * No backports of features are allowed
  * All kinds of bugfixes are allowed

* for the older stable branch (``N-2``)

  * Only critical bugfixes and security patches

Fixes need to be first done in the master branch (``N``) and then
cherry-picked into the stable branches (first N-1 and after that, if
necessary, ``N-2``).

The original ``Change-Id`` needs to be kept intact when a backport is
proposed for review.

The short version of the technical side of creating a backport::

   $ git checkout -t origin/stable/ocata
   $ git cherry-pick -x $master_commit_id
   $ git review stable/ocate

