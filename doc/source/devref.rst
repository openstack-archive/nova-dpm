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

Getting Started
---------------

Milestone release
+++++++++++++++++

* Checkout the master branch
* Create a tag ``<version>.0b<milestone>``, e.g. ``1.0.0.0b1`` for the first
  milestone of the Ocata release. For more details, see :ref:`tag_releases`.
* Push the tag along :ref:`tag_releases`.
* Update the launchpad project

  * Release the corresponding milestone along :ref:`release_milestone`.


First release candidate
+++++++++++++++++++++++

* Checkout the master branch
* Create a tag ``<version>.0rc1``, e.g. ``1.0.0.0rc1``. For more details, see
  :ref:`tag_releases`.
* Push the tag along :ref:`tag_releases`.
* Create a stable branch ``stable/<release>``, e.g. ``stable/ocata``. For more
  details, see :ref:`new_stable_branch`.
* Update the launchpad project

  * Create a Milestone for the release candidate along
    :ref:`create_milestone`.
  * Release the milestone along :ref:`release_milestone`.
  * Change the Focus of development along :ref:`focus_of_development`.
* Make the documentation for the new stable branch available on RTD along
  :ref:`rtd_branch`.

Follow up release candidates
++++++++++++++++++++++++++++

* Checkout the ``stable/<release>`` branch
* Create a tag ``<version>.0rc2``, e.g. ``1.0.0.0rc2``. For more details, see
  :ref:`tag_releases`.
* Push the tag along :ref:`tag_releases`.
* Update the launchpad project

  * Create a Milestone for the release candidate along
    :ref:`create_milestone`.
  * Release the milestone along :ref:`release_milestone`.

Release
+++++++

* Checkout the ``stable/<release>`` branch::

    git fetch
    git checkout -t stable/<release>

* Create a tag ``<version>`` e.g. ``1.0.0`` with the description *<release>
  release*. For more details, see :ref:`tag_releases`.
* Push the tag along :ref:`tag_releases`.

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
* tag the last commit in ``master`` with the *release candidate* tag
* create a ``stable/<release>`` branch from that tag (master is now open
  for changes for the next release)
* double-check if that release candidate needs fixes
* tag the final release candidate 1 week before the actual release
* tag the final full release

.. note:: As a project which is not under the Openstack governance, we
   don't use the ``openstack/releases`` repository to create releases and
   stable branches. See `New stable branch`_ for the HOW-TO.

.. _tag_releases:

Tag releases
------------

Releases are done via *Git tags*. The list of releases can be found at
https://github.com/openstack/nova-dpm/releases . To tag the first release
candidate (RC) for the next release, follow the steps below. We use the
*Ocata* release as an example:

#. You need a key to sign the tag::

   $ gpg --list-keys

#. If this is not yet done, create one::

   $ gpg --gen-key

#. Go to the commit you want to tag (usually the latest one in ``master``)::

   $ git checkout master
   $ git pull

#. (Optional) Double-check the list of current tags::

   $ git tag -l

#. Create a signed tag::

   $ git tag -s 1.0.0.0rc1 -m "RC1 for the Ocata release"

#. Push that tag via the *gerrit* remote (no Gerrit change will be created)::

   $ git push gerrit 1.0.0.0rc1

#. (Optional) Wait for ~5m, then you can check if the automatic release
   process was executed::

   $ git os-job 1.0.0.0rc1

At this point we are done with the release of a version. You might want to
check if the artifacts show the new version number:

* The read-only github repo: https://github.com/openstack/nova-dpm/releases
* The package on PyPi: https://pypi.python.org/pypi/nova-dpm
* The docs on RTD: http://nova-dpm.readthedocs.io/en/latest/

.. note:: RTD uses ``pbr`` to determine the version number and shows
   a version number higher than that you pushed before, that's fine and
   nothing to worry about.

.. warning:: Further release candidates and the final release must be
   tagged in the ``stable/<release>`` branch and **not** in the ``master``
   branch.


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
   $ git review stable/ocata

.. _new_stable_branch:

New stable branch
-----------------

After the first release candidate is tagged in ``master``, you should create
the stable branch in *Gerrit* based on that:

#. Check if you are a member of the Gerrit group ``nova-dpm-release``:
   https://review.openstack.org/#/admin/groups/1633,members
#. This release group is allowed to create references and tags:
   https://review.openstack.org/#/admin/projects/openstack/nova-dpm,access
#. Go to https://review.openstack.org/#/admin/projects/openstack/nova-dpm,branches
   and enter the branch name ``stable/<release>`` and the initial revision
   it is based on (the release candidate tag).

   #. Example for Ocata::

         Branch Name: stable/ocata
         Initial Revision: 1.0.0.0rc1

   #. Example for Pike::

         Branch Name: stable/pike
         Initial Revision: 2.0.0.0rc1

After this is done, every open change in Gerrit which uses ``master`` as
target branch will be (if it will merge) part of the next release.


Launchpad
=========

Create a new Series with milestones
-----------------------------------

#. Go to https://launchpad.net/nova-dpm/+addseries to register a new
   release series using

   * name: ``<release>``, e.g. ``pike``
   * description: ``Development series for the Pike release <version>.``, e.g.
     ``Development series for the Pike release 2.0.0.``

#. Create the milestones for the new release along :ref:`create_milestone`.
   Information about the milestones can be found at
   https://releases.openstack.org/<release>/schedule.html . E.g.
   https://releases.openstack.org/pike/schedule.html for the 'Pike' release.

   Do this for all 3 milestones.

.. _create_milestone:

Create a Milestone for a Series
-------------------------------

Go to https://launchpad.net/nova-dpm/<release> and click on
   "Create milestone". Provide the following information

   * name

     * Milestone: ``<release>-<milestone>``, e.g. ``pike-1``
     * Release candidate: ``<release>-rc<candidate>``, e.g. ``pike-rc1``
   * code name

     * Milestone: ``<short-release><milestone>``, e.g. ``p1``
     * Release candidate: ``RC<candidate>``, e.g. ``RC1``
   * date targeted

.. _release_milestone:

Release a Milestone
-------------------

#. Open the Milestone using
   https://launchpad.net/nova-dpm/+milestone/ocata-rc1/+addrelease.

#. Specify the release date

.. _focus_of_development:

Change focus of development
---------------------------

Go to the projects edit page https://launchpad.net/nova-dpm/+edit. Set
'Development focus' to the upcoming release series.

Read The Docs (RTD)
===================

.. _rtd_branch:

Activate/deactivate docs for a branch or tag
--------------------------------------------

To create documentation for the stable stable branch, go to
https://readthedocs.org/projects/nova-dpm/versions/.
Edit the version you want to change and tick or untick "Active". Exit with
"Save".

.. note::
  The strategy is to provide documentation for stable branches only (instead
  of release tags). Doing so, the backported documentation is available without
  having a new release required.

Requirements
============

This chapter describes how requirements are handled. The most important
requirements are the library ``os-dpm`` and the ``zhmcclient``.

Each project specifies its requirements using the ``requirements.txt`` and
``test-requirements.txt`` files.

In addition to that, requirements are also managed OpenStack wide
in the requirements repository https://github.com/openstack/requirements.
The following files are of importance

* ``global-requirements.txt``

  Specifies a requirement and its minimum version. All requirements that
  are listed in a projects ``requirements.txt`` file must be listed in this
  file as well. There's a Jenkins job ensuring that the version in the projects
  ``requirements.txt`` always matches the exact version listed in this file.

  .. note::
     Exact really means exact, including white spaces and so on!

  This file has to be updated manually.


* upper-constraints.txt

  This file specifies the upper version limit for a package.
  For each requirement listed in ``global-requirements.txt`` a corresponding
  entry must exist in this file. In addition an upper constraint for
  all indirect requirements must be specified in this file as well
  (e.g. zhmccclient uses ``click-spinner``. An upper constraint must be
  specified for ``click-spinner`` as well, although no entry in
  ``global-requirements.txt`` exists).

  This file is being updated by the OpenStack Proposal Bot.

  * OpenStack libraries: The release job will trigger the Bot directly
  * External libraries: Bot is triggered on a daily bases (except if the
    branch is frozen due to a pending release)

  Also manual updates can be proposed.

* projects.txt

  The OpenStack Proposal Bot proposes changes made to *global-requirements*
  to the listed projects ``requirements.txt`` and ``test-requirements.txt``
  file.

How to use a new version of a package?
--------------------------------------

The new version must be specified in ``upper-constraints.txt`` of the
requirements repository. Usually the OpenStack Proposal Bot takes care about
that. Alternatively a patch can be submitted manually.

TBD: When is the OpenStack Proposal Bot being triggered for OpenStack
libraries vs. external libraries.

How to increase the minimum version for a package?
--------------------------------------------------

Propose a patch to the ``global-requirements.txt`` file of the requirements
repository. The OpenStack Proposal Bot will propose a change to your project
once that patch is merged.

If also the version in ``upper-constraints.txt`` should be bumped, do both with
the same commit.

.. note::
   The OpenStack Proposal Bot proposes changes made to *global-requirements*
   only to projects listed in ``projects.txt`` of the requirements repo.

How to avoid that a new version of a package gets applied to a project?
-----------------------------------------------------------------------

The upper constraint cannot be controlled on a project basis.

The only way to mark a invalid version is to propose a change to the
``global-requirements.txt`` file of the requirements repository to exclude
the invalid version.

.. note::
  If you plan to use that version in the future do not propose an update
  to ``global-requirements.txt``. Rather focus on fixing the issue with the
  new version in your project right now!

.. note::
  On a version bump, the unittests of the main projects are run to ensure
  those are not breaking. But this is only for the major projects.
