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

# This script configures all qeth network interfaces that are listed in the
# kernels cmdline */proc/cmdline* with the given adapter port. All interfaces
# are configured in layer2 mode.
# The format of the cmdline parameters must be either
#     <devno>,<port>;
# or
#     <devno>,<port>,<mac>;

# Exit on error
set -e
source $(dirname "$0")/dpm_guest_image_tools_common

LOG_PREFIX=$(basename "$0")
# This script usually gets called by systemd. Systemd takes care of writing
# stdout and stderr into the journal. Using "echo" here ensures, that
# all the messages show up under the corresponding systemd unit and not as
# separate entity.
LOG_TARGET="stdout"

# Regex to match
# <devno>,<port>;
# <devno>,<port>,<mac>;
REGEX="($REGEX_DEV_NO),([0-1])(,$REGEX_MAC)?;"

#CMDLINE="some stuff 0001,1,000000000011;0004,;0007,0; more stuff"
CMDLINE=$(get_cmdline)

log "Start"
ensure_ccwgroup_module

# Default return code
rc=0

# Bash does not support global matching, therefore
# we remove the current match from the cmdline to
# allow matching the next value
while [[ $CMDLINE =~ $REGEX ]]; do
  dev_no="${BASH_REMATCH[1]}"
  port_no="${BASH_REMATCH[2]}"

  # remove current match from variable, to allow next match in next iteration
  CMDLINE=${CMDLINE#*"${dev_no}"}

  dev_bus_id=$(get_device_bus_id "$dev_no")

  log "Configuring dev_bus_id $dev_bus_id with port $port_no."

  # Check if device is already configured
  if device_exists "$dev_bus_id"; then
     log "Interface for $dev_bus_id already configured. Skipping."
     continue
  fi

  if ! configure_device "$dev_bus_id" "$port_no"; then
    rc=1
  fi

done
log "Finished with rc '$rc'"
exit $rc