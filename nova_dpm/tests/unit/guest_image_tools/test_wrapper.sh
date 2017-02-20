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

# This is a test wrapper. It's only job is to help executing certain functions
# of other shell scripts.

# This script is called from the projects root directory. Therefore all paths
# must be specified relative to it.
# Manual execution
# nova_dpm/tests/unit/guest_image_tools/test_wrapper.sh <method_name> <args>

source guest_image_tools/usr/bin/dpm_guest_image_tools_common


# $1 = The function to be called
# $2,3... = the parameters for the function
func="$1"
# Remove the first argument from $@
shift 1
# Make sure only defined function are called
if [[ $(type -t $func) == "function" ]]; then
  # Call function with arguments passed in as $2,3,...
  $func "$@"
  exit $?
else
  exit 1
fi
