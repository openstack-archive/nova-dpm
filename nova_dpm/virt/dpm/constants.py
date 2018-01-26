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

# Background for MAX_NIC calculation:
# The boot-os-specific-parameters property of a partition is used to pass
# additional information for a NIC into the Operating System.
# The boot-os-specific-parameters property is limited to 256 chars.
# The format for a nic is <devno>,<portno>,<mac>;
# len(" ") = 1 # space
# len(<devno>) = 4
# len(<portno>) = 1
# len(<mac>) = 12
# len (,,;) = 3
# total len per NIC: 21
# Max number of NICs = 256/20 = 12
MAX_NICS_PER_PARTITION = 12

BOOT_OS_SPECIFIC_PARAMETERS_MAX_LEN = 256

ZHMC_ADAPTER_TYPE_CRYPTO = "crypto"

ZHMC_CRYPTO_TYPE_ACCELERATOR = "accelerator"
ZHMC_CRYPTO_TYPE_CCA = "cca-coprocessor"
ZHMC_CRYPTO_TYPE_EP11 = "ep11-coprocessor"

FLAVOR_CRYPTO_TYPE_ACCELERATOR = ZHMC_CRYPTO_TYPE_ACCELERATOR
FLAVOR_CRYPTO_TYPE_CCA = "cca"
FLAVOR_CRYPTO_TYPE_EP11 = "ep11"

FLAVOR_CRYPTO_TYPES = [FLAVOR_CRYPTO_TYPE_ACCELERATOR, FLAVOR_CRYPTO_TYPE_CCA,
                       FLAVOR_CRYPTO_TYPE_EP11]

# Remove
FLAVOR_PROPERTY_CRYPTO_DOMAIN_COUNT = "crypto_domain_count"
FLAVOR_PROPERTY_CRYPTO_ADAPTERS = "crypto_adapters"


FLAVOR_TO_ZHMC_CRYPTO_TYPE_MAP = {
    FLAVOR_CRYPTO_TYPE_EP11: ZHMC_CRYPTO_TYPE_EP11,
    FLAVOR_CRYPTO_TYPE_CCA: ZHMC_CRYPTO_TYPE_CCA,
    FLAVOR_CRYPTO_TYPE_ACCELERATOR: ZHMC_CRYPTO_TYPE_ACCELERATOR
}
