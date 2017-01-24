# Copyright 2017 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from nova.exception import NovaException
from nova.i18n import _


class BootOsSpecificParametersExceededError(NovaException):
    """Length of boot-os-specficic-parameters would exceed

    This exception indicates that adding the given data to a
    partitions 'boot-os-specific-parameters' property would fail as the
    properties max length would be exceeded.

    """
    msg_fmt = _("Maximum size of 'boot-os-specific-parameters' attribute "
                "exceeded.")
