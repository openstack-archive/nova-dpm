# Copyright 2016 IBM Corp. All Rights Reserved.
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

"""Constants and helper APIs for dealing with virtualization types

The constants provide the standard names for all known guest
virtualization types. This is not to be confused with the Nova
hypervisor driver types, since one driver may support multiple
virtualization types and one virtualization type (eg 'xen') may
be supported by multiple drivers ('XenAPI' or  'Libvirt-Xen').
"""

from nova.compute import hv_type

PRSM = ("prsm",)

ALL = hv_type.ALL + PRSM


def is_valid(name):
    """Check if a string is a valid hypervisor type

    :param name: hypervisor type name to validate

    :returns: True if @name is valid
    """
    return hv_type.is_valid(name)


def canonicalize(name):
    """Canonicalize the hypervisor type name

    :param name: hypervisor type name to canonicalize

    :returns: a canonical hypervisor type name
    """

    return hv_type.canonicalize(name)
