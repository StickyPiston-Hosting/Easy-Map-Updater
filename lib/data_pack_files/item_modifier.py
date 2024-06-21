# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from typing import cast, Any
from lib.log import log
from lib import defaults
from lib import json_manager
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import nbt_paths
from lib.data_pack_files import predicate
from lib.data_pack_files import json_text_component
from lib.data_pack_files import loot_table



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def update(file_path: Path, og_file_path: Path, version: int):
    global pack_version
    pack_version = version

    # Read file
    contents, load_bool = json_manager.safe_load(og_file_path)
    if not load_bool:
        return

    # Write to new location
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(item_modifier(contents, version), file, indent=4)



def item_modifier(contents: dict[str, Any] | list, version: int, object_id: str = "") -> dict[str, Any] | list:
    global pack_version
    pack_version = version

    # Handle lists
    if isinstance(contents, list):
        for i in range(len(contents)):
            contents[i] = item_modifier(contents[i], version, object_id)
        return contents

    # Process different functions
    function_id: str = contents["function"]
    function_id = miscellaneous.namespace(function_id)
    contents["function"] = function_id



    if function_id == "minecraft:copy_nbt":
        source = contents["source"]
        if isinstance(source, dict):
            if source["type"] == "context":
                source = source["target"]
            else:
                source = "storage"
        for operation in contents["ops"]:
            id_array = {
                "block_entity": "block",
                "this": "entity",
                "killer": "entity",
                "direct_killer": "entity",
                "killer_player": "entity",
                "storage": "arbitrary"
            }
            if source in id_array:
                source = id_array[source]
            operation["source"] = nbt_paths.update(operation["source"], version, [], source)
            operation["target"] = nbt_paths.update(operation["target"], version, [], "item_tag")

    if function_id == "minecraft:set_contents":
        if "entries" in contents:
            for entry in contents["entries"]:
                loot_table.update_entry(entry, version)
        if "type" not in contents:
            if object_id:
                contents["type"] = object_id
            else:
                contents["type"] = "minecraft:shulker_box"
                if defaults.SEND_WARNINGS:
                    log('WARNING: Item modifier function "minecraft:set_contents" type specifier defaulted to "minecraft:shulker_box", check that this is correct')


    if function_id == "minecraft:set_lore":
        for i in range(len(contents["lore"])):
            contents["lore"][i] = json_text_component.update_component(contents["lore"][i], version, [])

    if function_id == "minecraft:set_name":
        contents["name"] = json_text_component.update_component(contents["name"], version, [])

    if function_id == "minecraft:set_nbt":
        contents["tag"] = nbt_tags.update(contents["tag"], version, [], "item_tag")



    if "conditions" in contents:
        for i in range(len(contents["conditions"])):
            contents["conditions"][i] = predicate.predicate(contents["conditions"][i], version)

    return contents