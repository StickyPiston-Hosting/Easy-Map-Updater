# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from lib import defaults
from lib.log import log
from lib.data_pack_files import nbt_paths



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def update(argument: dict[str, str], version: int, issues: list[dict[str, str | int]]) -> str:
    global pack_version
    pack_version = version

    data_type = argument["data_type"]
    path = argument["path"]
    source = argument["source"]

    # Update path
    path = nbt_paths.update(path, version, issues, source)

    # Currently, only custom model data changing type is handled
    # The system will be made more robust when needed
    if defaults.DEBUG_MODE:
        log(f"Path: {path}")
    if path.endswith('"minecraft:custom_model_data".floats[0]') and data_type == "int":
        return "float"
    
    return data_type
