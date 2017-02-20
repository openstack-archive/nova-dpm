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

# This is a test wrapper. It's only job is to overwrite variables used
# in the production script

# This script is called from the projects root directory. Therefore all paths
# must be specified relative to it.
# Manual execution
# nova_dpm/tests/unit/guest_image_tools/setmac_test.sh test <method_name> <args>

# Set root dir to the test_root_dir which contains fake commands
ROOT_DIR=$(pwd)"/nova_dpm/tests/unit/guest_image_tools/test_root_dir"

source guest_image_tools/usr/bin/dpm_guest_image_tools_common


# Check if script runs in testmode
if [[ "$1" == "test" ]];then
  # $1 = "test" if script should run in testmode
  # $2 = The function to be called
  # $3,4... = the parameters for the function
  func="$2"
  # Remove the first 2 arguments from $@
  shift 2
  # Make sure only defined function are called
  if [[ $(type -t $func) == "function" ]]; then
    # Call function with arguments passed in as $3,4,...
    $func "$@"
    exit $?
  else
    exit 1
  fi
fi
