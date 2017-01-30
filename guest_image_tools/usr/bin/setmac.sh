#! /bin/bash
dev_bus_id=$1
LOG_PREFIX="$0"

REGEX_DEV_BUS_ID="0\.0\.[0-9a-f]{4}"
REGEX_MAC="[0-9A-Fa-f]{12}"
SYS_DEVICE_PATH="/sys/bus/ccwgroup/devices/$dev_bus_id"
#CMDLINE="some stuff nics=0001,0,aabbccddeeff;abcd,1,001122334455;"
CMDLINE=`cat /proc/cmdline`

function log {
  # $1 message to log
  logger "$LOG_PREFIX: $1"
  echo "$LOG_PREFIX: $1"
}

function validate_dev_bus_id {
  if ! [[ $dev_bus_id =~ $REGEX_DEV_BUS_ID ]]; then
     log "$dev_bus_id is not a regular device number. Skipping!"
     exit
  fi

  if [ ! -d "$SYS_DEVICE_PATH" ]; then
     log "No network interface for device $dev_bus_id found. Skipping!"
     exit 1
  fi
}

function get_interface_name {
  if_name=`cat $SYS_DEVICE_PATH/if_name`
  echo $if_name
}


function extract_mac {
  # Sets the global $mac variable
  devno=${dev_bus_id#*"0.0."}
  # Regex matches: <devno>,<port>,<mac>;
  regex=${devno}",[0-1],("${REGEX_MAC}")";
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


function set_mac {
  extract_mac
  if ! is_locally_administered_mac $mac ; then
      log "MAC $mac is not a locally administered MAC. Aborting!"
      exit
  fi
  if_name=$(get_interface_name)

  cmd="ip link set $if_name address $mac 2>&1 > /dev/null"
  stderr=$(eval $cmd)
  rc=$?
  if [[ $rc != 0 ]]; then
    log "Operation '$cmd' failed with exit rc '$rc': $stderr. Aborting!"
    exit 1
  fi
  log "Successfully set MAC of interface '$if_name' to '$mac'"

}

log "Start"
validate_dev_bus_id
set_mac
log "Finished"