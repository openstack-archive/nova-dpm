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


# Matches MAC in format: xxxxxxxxxxxx
REGEX_MAC="[0-9A-Fa-f]{12}"
REGEX_EXTRACT_DEVNO="qeth/0\.0\.([0-9A-Fa-f]{4})/net"
REGEX_EXTRACT_IFNAME="/net/(.{1,15})"
LOG_PREFIX=$(basename "$0")


function log {
  # $1 = message to log

  # Logging to syslog
  logger "$LOG_PREFIX: $1"
}

function extract_devno {
  # Extracts the device number out of a device path
  # $1 = the device path, e.g. "/devices/qeth/0.0.0001/net/enc1"
  # Returns: device number, e.g. "0001"

  local dev_path="$1"
  if [[ $dev_path =~ $REGEX_EXTRACT_DEVNO ]]; then
    echo "${BASH_REMATCH[1]}"
  else
     log "Could not extract devno from '$dev_path'. Skipping!"
     exit 1
  fi
}

function extract_interface_name {
  # Extracts the interface name out of a device path
  # $1 = the device path, e.g. "/devices/qeth/0.0.0001/net/enc1"
  # Returns: interface name, e.g. "enc1"

  local dev_path="$1"
  if [[ $dev_path =~ $REGEX_EXTRACT_IFNAME ]]; then
    echo "${BASH_REMATCH[1]}"
  else
     log "Could not find interface for device number '$devno' in path 'dev_path'. Skipping!"
     exit 1
  fi
}


function extract_mac {
  # Get the mac address to a given device number from the cmdline
  # $1 = the device number, e.g. "0001"
  # $2 = the cmdline, e.g. "0001,0,aabbccddeeff;"
  # Returns: The MAC address in format xx:xx:xx:xx:xx:xx

  local devno="$1"
  local cmdline="$2"
  # Regex matches: <devno>,<port>,<mac>;
  regex=${devno}",[0-1],("${REGEX_MAC}");"
  if [[ $cmdline =~ $regex ]]; then
          local mac_tmp="${BASH_REMATCH[1]}"
          # Insert ':' into MAC again
          echo ${mac_tmp:0:2}:${mac_tmp:2:2}:${mac_tmp:4:2}:${mac_tmp:6:2}:${mac_tmp:8:2}:${mac_tmp:10:2}
  else
     log "No MAC for devno '$devno' found in cmdline '$cmdline'. Exit."
     exit 1
  fi
}

function is_locally_administered_mac {
  # Verifies if a MAC is a locally administered unicast MAC
  # $1 = MAC, e.g. "00:11:22:33:44:55"
  # Returns <nothing>
  # rc 0 = True, rc 1 = False

  local mac="$1"

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
  local regex="^[0-9A-Fa-f][26AaEe]"
  if [[ $mac =~ $regex ]]; then
    return 0
  else
    return 1
  fi
}

function get_ip_cmd {
  # Determines the path of the ip cmd
  # Returns: Path to ip cmd

  # When this script is called from a udev rule, it is not able to find
  # the ip command. Also the 'which' command is not working. As different
  # distros install it to different locations, we need to try out which
  # path is working.
  local paths=("/usr/sbin/ip" "/sbin/ip")

  for path in "${paths[@]}"; do
    if [[ -x $path ]]; then
       echo "$path"
       return 0
     fi
  done

  log "'ip' command not found. Exiting."
  exit 1
}

function set_mac {
  # This function sets the given MAC on the given interface
  # $1 = Interface name to set the mac on, e.g. "enc1"
  # $2 = The mac address, e.g. "00:11:22:33:44:55"

  local if_name="$1"
  local mac="$2"
  if ! is_locally_administered_mac "$mac" ; then
      log "MAC $mac is not a locally administered MAC. Aborting!"
      exit 1
  fi

  local ip_cmd=$(get_ip_cmd)
  local cmd="$ip_cmd link set $if_name address $mac 2>&1 > /dev/null"
  stderr=$(eval "$cmd")
  local rc=$?
  if [[ $rc != 0 ]]; then
    log "Operation '$cmd' failed with exit rc '$rc': $stderr. Aborting!"
    exit 1
  fi
  log "Successfully set MAC of interface '$if_name' to '$mac'"

}

function get_cmdline {
  #Example: "some stuff nics=0001,0,aabbccddeeff;abcd,1,001122334455;"
  echo $(cat /proc/cmdline)
}

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