#!/bin/bash

# devstack/dpm-functions.sh
# Functions to control the installation and configuration of the DPM compute services

GITREPO["zhmcclient"]=${ZHMCCLIENT_REPO:-https://github.com/zhmcclient/python-zhmcclient}
GITBRANCH["zhmcclient"]=${ZHMCCLIENT_BRANCH:-develop}
GITDIR["zhmcclient"]=$DEST/zhmcclient



function install_zhmcclient {
    # Install the latest zhmcclient from git
    echo_summary "Installing zhmcclient"
    git_clone_by_name "zhmcclient"
    setup_dev_lib "zhmcclient"
    echo_summary "zhmcclient install complete"
}

function cleanup_zhmcclient {
    echo_summary "Cleaning zhmcclient"
    rm -rf ${GITDIR["zhmcclient"]}
}

function check_dpm_install {
    echo_summary "Checking dpm installation"
    # The user that nova runs as should be a member of **dpm_admin** group
    if ! getent group $DPM_ADMIN_GROUP >/dev/null; then
        sudo groupadd $DPM_ADMIN_GROUP
    fi
    add_user_to_group $STACK_USER $DPM_ADMIN_GROUP
}
