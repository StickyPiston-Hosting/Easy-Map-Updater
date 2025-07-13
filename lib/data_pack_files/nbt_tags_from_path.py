# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from typing import Any
from pathlib import Path
from lib.log import log
from lib import defaults
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import nbt_paths



# Initialize variables

pack_version = defaults.PACK_VERSION

PROGRAM_PATH = Path(__file__).parent
with (PROGRAM_PATH / "nbt_tree.json").open("r", encoding="utf-8") as file:
    NBT_TREE: dict[str, Any] = json.load(file)



# Define functions

def update(argument: dict[str, str], version: int, issues: list[dict[str, str | int]], source: str) -> str:
    global pack_version
    pack_version = version

    nbt = argument["nbt"]
    path = argument["path"]
    mode = argument["mode"]

    if path.startswith("{"):
        return nbt_tags.update(nbt, pack_version, issues, source)
    
    path_parts = nbt_paths.unpack(f'{path}{"[0]" if mode in ["insert", "append", "prepend"] else ""}')
    if defaults.DEBUG_MODE:
        log(f'Path: {path_parts}')
    nested_nbt, path_parts = nbt_paths.build_nbt_from_path(nbt_tags.unpack(nbt), path_parts)
    if defaults.DEBUG_MODE:
        log(f'Old NBT: {nbt_tags.pack(nested_nbt)}')
    nested_nbt = nbt_tags.direct_update(nested_nbt, pack_version, issues, source, "", True)
    if defaults.DEBUG_MODE:
        log(f'New NBT: {nbt_tags.pack(nested_nbt)}')
    path_parts = nbt_paths.direct_update(path_parts, pack_version, issues, source)
    new_data = nbt_paths.extract_nbt_from_path(nested_nbt, path_parts)
    if new_data is None:
        return nbt
    return nbt_tags.pack(new_data)
