..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================
HMC Connection Error Handling Concept
==========================

Problem Description
===================

There are situations where the connection to the Hardware Management Console
(HMC) is lost. Those errors are not handled properly today.

Proposed Change
===============

Timeout/Retry
-------------

zhmcclient allows specifying the following timeout/retry related parameters
[1]. This is based on zhmcclient version: 0.12.1.dev25


* connect_timeout

  * when zhmcclient is initiating a connecting to the HMC, this connection
    will timeout after ``connect_timeout`` seconds.
  * default: 30  [3]
  * Exception: zhmcclient.ConnectTimeout [2]
    (derived from zhmcclient.ConnectionError)
  * Proposal: use default

* connect_retries

  * if zhmcclient fails to establish a connection to the HMC (e.g. due to the
    timeout set in ``connect_timeout``), ``connect_retries`` retries will be
    made. Otherwise an exception is being thrown.
  * default: 3 [3]
  * Exception:
    * zhmcclient.ConnectTimeout [2] (derived from zhmcclient.ConnectionError)
    * zhmcclient.RequestRetriesExceeded for all other reasons [2]
      (derived from zhmcclient.ConnectionError)
  * Proposal: 120

* read_timeout

  * when zhmcclient reads an HMC http response, this will timeout after
    ``read_timeout`` seconds.
  * default: 3600  [3]
  * Exception: zhmcclient.ReadTimeout [2]
    (derived from zhmcclient.ConnectionError)
  * Proposal: 300

* read_retries

  * if zhmcclient fails to read the http response (e.g. due to the timeout
    setting ``read_timeout``), ``read_retries`` retries will be made. If non
    of the retries was successful an exception is raised.

    .. note::
      The retry is not only trying to read the result again! Also the request
      is being issued again!
  * default: 0  [3]
  * Exception:
    * zhmcclient.ReadTimeout [2] (derived from zhmcclient.ConnectionError)
    * zhmcclient.RequestRetriesExceeded for all other reasons [2]
      (derived from zhmcclient.ConnectionError)
  * Proposal: use default

* max_redirects

  * The maximum number of http redirects.
  * default: 30  [3]
  * Exception: ?
  * Proposal: use default

* operation_timeout

  * How long the zhmcclient should wait for an asyncronous HMC operation to
    complete. The zhmcclient is polling on the corresponding 'job' object until
    the state transitions to 'complete'. It can be enabled with the parameter
    ``wait_for_completion`` on zhmcclient resource operations. The timeout is
    specified via the ``operations_timeout`` attribute. If ``None`` is given
    (default), the default value is used.
  * default: 3600  [3]
  * Exception: zhmcclient.OperationTimeout (derived from Error)
  * Proposal: default

    TBD: When we spawn several instances at same time it may take time.
      (I experienced in Z/VM cloud)

* status_timeout

  * This is a special parameter only used by the LPAR object. The timeout
    specifies how long to wait until the partition switches into
    ``not-operating`` state.

    -> not relevant for DPM
  * default: 60  [3]
  * Exception:
  * Proposal: use default


The proposal is to let the zhmcclient handle timeouts and retries!

How to deal with Connection errors?
-----------------------------------

What should if all zhmcclient retries failed and a connection error is raised?

Service Start
+++++++++++

Scenario: The nova-dpm service gets started.

Proposal: If the service fails to establish a connection to the HMC during it's
start, the agent should terminate with a appropriate error message.

Running Service
+++++++++++++

Scenario: A running nova-dpm service loses the connection to the HMC

Proposal: Keep the service running and retry connection 120 times using
``connect_retries``.


References
==========

[1] http://python-zhmcclient.readthedocs.io/en/stable/general.html#retry-timeout-configuration
[2] http://python-zhmcclient.readthedocs.io/en/stable/general.html#exceptions
[3] http://python-zhmcclient.readthedocs.io/en/latest/general.html#constants
