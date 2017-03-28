# Copyright 2016 IBM Corp. All Rights Reserved.
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

import datetime


def stub_volume_get_all(context):
    id = get_volume_id()
    return [stub_volume(id)]


def stub_volume_get(st, context, volume_id):
    return stub_volume(volume_id)


def stub_volume(id,
                displayname="Volume Name",
                displaydesc="Volume Description",
                size=100):
    volume = {
        'id': id,
        'size': size,
        'availability_zone': 'zone1:host1',
        'status': 'in-use',
        'attach_status': 'attached',
        'name': 'vol name',
        'display_name': displayname,
        'display_description': displaydesc,
        'created_at': datetime.datetime(2008, 12, 1, 11, 1, 55),
        'snapshot_id': None,
        'volume_type_id': 'fakevoltype',
        'volume_metadata': [],
        'volume_type': {'name': 'Backup'},
        'multiattach': False}
    return volume


def get_volume_id():
    return "a26887c6-c47b-4654-abb5-dfadf7d3f803"


SERVER = {
    "server": {
        "name": "ubunt",
        "imageRef": "",
        "availability_zone": "nova",
        "flavorRef": "12345",
        "block_device_mapping": [{
            "volume_id": "26bb3438-cba0-4e4f-995c-7e70e24c4b0c",
            "delete_on_termination": "false",
            "device_name": "vda"}],
        "OS-DCF:diskConfig": "AUTO",
        "max_count": 1,
        "min_count": 1,
        "networks": [{"uuid": "5837e7a3-c154-4873-92d3-f85357e92346"}],
        "security_groups": []}}

FLAVOR = {
    "flavor": {
        "vcpus": 1,
        "disk": 0,
        "name": "dpm",
        "os-flavor-access:is_public": True,
        "rxtx_factor": 1.0,
        "OS-FLV-EXT-DATA:ephemeral": 0,
        "ram": 1024,
        "id": "12345",
        "swap": 0}}
