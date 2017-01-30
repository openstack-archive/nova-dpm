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

# e.g. /devices/qeth/0.0.0001/net/enc1
DEV_PATH=$1
LOG_PREFIX="$0"

REGEX_MAC="[0-9A-Fa-f]{12}"
REGEX_EXTRACT_DEVNO="qeth\/0.0.([0-9A-Fa-f]{4})\/net"
REGEX_EXTRACT_IFNAME="/net/(.{1,15})"
#CMDLINE="some stuff nics=0001,0,aabbccddeeff;abcd,1,001122334455;"
CMDLINE=`cat /proc/cmdline`


function log {
  # $1 message to log
  logger "$LOG_PREFIX: $1"
}

function extract_devno {
  if [[ $DEV_PATH =~ $REGEX_EXTRACT_DEVNO ]]; then
    devno="${BASH_REMATCH[1]}"
  else
     log "Could not extract devno from '$DEV_PATH'. Skipping!"
     exit
  fi
}

function extract_interface_name {
  if [[ $DEV_PATH =~ $REGEX_EXTRACT_IFNAME ]]; then
    if_name="${BASH_REMATCH[1]}"
  else
     log "Could not find interface for device number '$devno' in path '$DEV_PATH'. Skipping!"
     exit
  fi
}


function extract_mac {
  # Sets the global $mac variable
  # Regex matches: <devno>,<port>,<mac>;
  regex=${devno}",[0-1],("${REGEX_MAC}");"
  if [[ $CMDLINE =~ $regex ]]; then
          mac_tmp="${BASH_REMATCH[1]}"
          # Insert ':' into MAC again
          mac=${mac_tmp:0:2}:${mac_tmp:2:2}:${mac_tmp:4:2}:${mac_tmp:6:2}:${mac_tmp:8:2}:${mac_tmp:10:2}
  else
     log "No MAC for devno '$devno' found in cmdline '$CMDLINE'. Exit."
     exit
  fi
}

function is_locally_administered_mac {
  # Only Unicast MACs that have the "locally administered" bit set are allowed
  # by OSA. The "locally administered" bit is the "second least significant"
  # bit of the most significant MAC byte. In addition only unicast addresses
  # are allowed. The unicast bit is the least significant bit of the most
  # significant byte.
  # Example:               AA:BB:CC:DD:EE:FF
  # Most significant Byte: ^^
  # In Binary:                   1010 1010
  # Second least significant bit:       ^         = locally administered = 1
  # Least significant bit:               ^        = unicast = 0
  # Therefore the only MACs are allowed, that have the 10 as those 2 bits.
  # This results in the following possible MACs (where X can be any hex char):
  #  X2:XX:XX:XX:XX:XX
  #  X6:XX:XX:XX:XX:XX
  #  XA:XX:XX:XX:XX:XX
  #  XE:XX:XX:XX:XX:XX
  regex="^[0-9A-Fa-f][26AaEe]"
  if [[ $mac =~ $regex ]]; then
    return 0
  else
    return 1
  fi
}

function set_ip_command_path {
  paths=("/usr/sbin/ip" "/sbin/ip")

  for path in "${paths[@]}"; do
    if [[ -e $path ]]; then
       ip_cmd=$path
     fi
  done

  if [ -z "$ip_cmd" ]; then
    log "'ip' command not found. Exiting."
    exit
  fi
}

function set_mac {
  if ! is_locally_administered_mac $mac ; then
      log "MAC $mac is not a locally administered MAC. Aborting!"
      exit
  fi

  cmd="$ip_cmd link set $if_name address $mac 2>&1 > /dev/null"
  stderr=$(eval $cmd)
  rc=$?
  if [[ $rc != 0 ]]; then
    log "Operation '$cmd' failed with exit rc '$rc': $stderr. Aborting!"
    exit 1
  fi
  log "Successfully set MAC of interface '$if_name' to '$mac'"

}

log "Start"
extract_devno
extract_interface_name
extract_mac
set_ip_command_path
log "Using device number '$devno', interface '$if_name', mac '$mac'."

set_mac
log "Finished"