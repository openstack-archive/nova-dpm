#!/bin/bash
#
# plugin.sh - Devstack extras script to install and configure the nova compute
# driver for dpm

# This driver is enabled in override-defaults with:
#  VIRT_DRIVER=${VIRT_DRIVER:-dpm}

# The following entry points are called in this order for nova-dpm:
#
# - install_nova_dpm
# - configure_nova_dpm
# - start_nova_dpm
# - stop_nova_dpm
# - cleanup_nova_dpm

# Save trace setting
MY_XTRACE=$(set +o | grep xtrace)
set +o xtrace

# Defaults
# --------

# Set up base directories
NOVA_DIR=${NOVA_DIR:-$DEST/nova}
NOVA_CONF_DIR=${NOVA_CONF_DIR:-/etc/nova}
NOVA_CONF=${NOVA_CONF:-NOVA_CONF_DIR/nova.conf}

# nova-dpm directories
NOVA_DPM_DIR=${NOVA_DPM_DIR:-${DEST}/nova-dpm}
NOVA_DPM_PLUGIN_DIR=$(readlink -f $(dirname ${BASH_SOURCE[0]}))

# Support entry points installation of console scripts
if [[ -d $NOVA_DIR/bin ]]; then
    NOVA_BIN_DIR=$NOVA_DIR/bin
    echo_summary $NOVA_BIN_DIR
else
    NOVA_BIN_DIR=$(get_python_exec_prefix)
    echo_summary $NOVA_BIN_DIR
fi

# Source functions
source $NOVA_DPM_PLUGIN_DIR/dpm-functions.sh

# Entry Points
# ------------

# configure_nova_dpm() - Configure the system to use nova_dpm
function configure_nova_dpm {

    # Default configuration
    iniset $NOVA_CONF DEFAULT compute_driver $DPM_DRIVER
    # dpm configuration
    iniset $NOVA_CONF dpm hmc $HMC
    iniset $NOVA_CONF dpm hmc_username $HMC_USERNAME
    iniset $NOVA_CONF dpm hmc_password $HMC_PASSWORD
    iniset $NOVA_CONF dpm cpc_object_id $CPC_OBJECT_ID
    iniset $NOVA_CONF dpm max_processors $MAX_PROC
    iniset $NOVA_CONF dpm max_memory $MAX_MEM
    iniset $NOVA_CONF dpm max_instances $MAX_INSTANCES
}

# install_nova_dpm() - Install nova_dpm and necessary dependencies
function install_nova_dpm {
    if [[ "$INSTALL_ZHMCCLIENT" == "True" ]]; then
        echo_summary "Installing zhmcclient"
        install_zhmcclient
    fi

    # Install the nova-dpm package
    setup_develop $NOVA_DPM_DIR
}

# start_nova_dpm() - Start the nova_dpm process
function start_nova_dpm {
    # This function intentionally functionless as the
    # compute service will start normally
    :
}

# stop_nova_dpm() - Stop the nova_dpm process
function stop_nova_dpm {
    # This function intentionally left blank as the
    # compute service will stop normally
    :
}

# cleanup_nova_dpm() - Cleanup the nova_dpm process
function cleanup_nova_dpm {
    # This function intentionally left blank
    :
}

# Core Dispatch
# -------------
if is_service_enabled nova-dpm; then
    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        # Perform installation of nova-dpm
        echo_summary "Installing nova-dpm"
        install_nova_dpm

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        # Lay down configuration post install
        echo_summary "Configuring nova-dpm"
        configure_nova_dpm

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # Initialize and start the nova-dpm/nova-compute service
        echo_summary "Starting nova-dpm"
        start_nova_dpm
    fi

    if [[ "$1" == "unstack" ]]; then
        # Shut down nova-dpm/nova-compute
        echo_summary "Stopping nova-dpm"
        stop_nova_dpm
    fi

    if [[ "$1" == "clean" ]]; then
        # Remove any lingering configuration data
        # clean.sh first calls unstack.sh
        echo_summary "Cleaning up nova-dpm and associated data"
        cleanup_nova_dpm
        cleanup_zhmcclient
    fi
fi

# Restore xtrace
$MY_XTRACE

# Local variables:
# mode: shell-script
# End:
