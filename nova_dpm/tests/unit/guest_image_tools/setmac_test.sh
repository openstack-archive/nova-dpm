#! /bin/bash
# This is a test wrapper. It's only job is to overwrite variables used
# in the production script

# This script is called from the projects root directory. Therefore all pathes
# must be specified relative to it.
# Manual execution
# nova_dpm/tests/unit/guest_image_tools/setmac_test.sh test <method_name> <args>

# Set root dir to the test_root_dir which contains fake commands
ROOT_DIR=$(pwd)"/nova_dpm/tests/unit/guest_image_tools/test_root_dir"

source guest_image_tools/usr/bin/setmac.sh "$@"
