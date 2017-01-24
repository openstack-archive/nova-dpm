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

from nova_dpm.virt.dpm.constants import MAX_NICS_PER_PARTITION


class MaxAmountOfInstancePortsExceededError(NovaException):
    """The maximum number of Ports attached to a DPM instance was exceeded"""
    msg_fmt = _("Exceeded the maximum number of Ports per DPM Instance. "
                "A single instance can only be attached to {max_ports} Ports.")\
        .format(max_ports=MAX_NICS_PER_PARTITION)


class BootOsSpecificParametersPropertyExceededError(NovaException):
    """The boot-os-specific-parameters property would exceed the allowed max"""
    msg_fmt = _("Exceeded the maximum len for the partitions "
                "'boot-os-specific-parameters' property.")
