# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from lib import defaults
from lib import utils
from lib import json_manager
from lib.data_pack_files import blocks
from lib.data_pack_files import items



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def update(file_path: Path, source_file_path: Path, version: int, tag_type: str):
    global pack_version
    pack_version = version

    contents, load_bool = json_manager.safe_load(source_file_path)
    if not load_bool:
        return
    if "values" not in contents or not isinstance(contents["values"], list):
        return
    
    modified = False
    for i in range(len(contents["values"])):
        new_entry = contents["values"][i]
        if tag_type == "block":
            new_entry = blocks.update(
                {
                    "id": contents["values"][i],
                    "data_value": -1,
                    "block_states": {},
                    "nbt": {},
                    "read": True
                },
                pack_version, []
            )["id"]
        if tag_type in "item":
            new_entry = items.update(
                {
                    "id": contents["values"][i],
                    "data_value": -1,
                    "components": {},
                    "nbt": {},
                    "read": True
                },
                pack_version, []
            )["id"]
        if contents["values"][i] != new_entry:
            contents["values"][i] = new_entry
            modified = True

    if modified:
        utils.safe_file_write(file_path, json.dumps(contents, indent=4))