#! /bin/bash
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

# Input parameter of this script is the device path of an existing qeth network
# interface. E.g.
#      ./setmac.sh "/devices/qeth/0.0.0001/net/enc1"
# This script sets the MAC address of this qeth network interface to the MAC
# provided in the kernels cmdline */proc/cmdline*.
# The format of the cmdline parameters must be
#     <devno>,<port>,<mac>;

# Exit on error
set -e
source $(dirname "$0")/dpm_guest_image_tools_common

LOG_PREFIX=$(basename "$0")

# e.g. /devices/qeth/0.0.0001/net/enc1
DEV_PATH="$1"
CMDLINE=$(get_cmdline)

log "Start with device path '$DEV_PATH'"
devno=$(extract_devno $DEV_PATH)
if_name=$(extract_interface_name $DEV_PATH)
mac=$(extract_mac $devno "$CMDLINE")
log "Using device number '$devno', interface '$if_name', mac '$mac'."

set_mac "$if_name" "$mac"
log "Finished"