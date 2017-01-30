#! /bin/bash
LOG_PREFIX="$0"
REGEX_DEV_NO="([0-9a-f]{4})"
REGEX_MAC="[0-9A-Fa-f]{12}"

# Regex to match
# <devno>,<port>;
# <devno>,<port>,<mac>;
regex="$REGEX_DEV_NO,([0-1])(,$REGEX_MAC)?;"

#CMDLINE="some stuff 0001,1,000000000011;0004,;0007,0; more stuff"
CMDLINE=`cat /proc/cmdline`

function log {
   # $1 message to log
   echo "$LOG_PREFIX: $1"
}

log "Start"

# Bash does not support global matching, therefore
# we remove the current match from the cmdline to
# allow matching the next value
while [[ $CMDLINE =~ $regex ]]; do
  dev_no="${BASH_REMATCH[1]}"
  dev_bus_id="0.0.$dev_no"
  log "Configuring dev_bus_id $dev_bus_id."

  # remove current match from variable, to allow next match in next iteration
  CMDLINE=${CMDLINE#*"${dev_no}"}


  # Check if device is already configured
  path="/sys/bus/ccwgroup/devices/$dev_bus_id"
  if [ -d "$path" ]; then
     log "Interface for $dev_bus_id already configured. Skipping."
     continue
  fi

  # Determine port
  port="${BASH_REMATCH[2]}"
  log "Port $port used for dev_bus_id $dev_bus_id."

  cmd="znetconf -a $dev_bus_id -o portno=$port,layer2=1"
  eval $cmd

done
log "Finished"