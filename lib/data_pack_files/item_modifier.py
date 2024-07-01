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

def update(file_path: Path, source_file_path: Path, version: int):
    global pack_version
    pack_version = version

    # Read file
    contents, load_bool = json_manager.safe_load(source_file_path)
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
        output = []
        for entry in contents:
            entry = item_modifier(entry, version, object_id)
            if isinstance(entry, list):
                output.extend(entry)
            else:
                output.append(entry)
        return output



    if "conditions" in contents:
        for i in range(len(contents["conditions"])):
            contents["conditions"][i] = predicate.predicate(contents["conditions"][i], version)



    # Process different functions
    function_id: str = contents["function"]
    function_id = miscellaneous.namespace(function_id)
    contents["function"] = function_id



    if function_id == "minecraft:copy_nbt":
        contents["function"] = "minecraft:copy_custom_data"
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
            target_path = nbt_paths.direct_update(nbt_paths.unpack(operation["target"]), version, [], "item_tag")
            if target_path[0] == "minecraft:custom_data":
                operation["target"] = nbt_paths.pack(target_path[1:])
            else:
                operation["target"] = nbt_paths.pack(target_path)
                if defaults.SEND_WARNINGS:
                    log(f'WARNING: Item modifier function "minecraft:copy_nbt" could not be converted to "minecraft:copy_components", target path changed to: {operation["target"]}')

    if function_id == "minecraft:set_attributes":
        if "modifiers" in contents:
            for modifier in contents["modifiers"]:
                if "operation" in modifier:
                    id_array = {
                        "addition": "add_value",
                        "multiply_base": "add_multiplied_base",
                        "multiply_total": "add_multiplied_total",
                    }
                    if modifier["operation"] in id_array:
                        modifier["operation"] = id_array[modifier["operation"]]

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
        updated_data = cast(dict[str, Any], nbt_tags.direct_update(nbt_tags.unpack(contents["tag"]), version, [], "item_tag", ""))
        if "minecraft:custom_data" in updated_data:
            set_custom_data = {
                "function": "minecraft:set_custom_data",
                "tag": nbt_tags.pack(updated_data["minecraft:custom_data"])
            }
            if "conditions" in contents:
                set_custom_data["conditions"] = contents["conditions"]
            del updated_data["minecraft:custom_data"]
        else:
            set_custom_data = None
        if len(updated_data):
            set_components = {
                "function": "minecraft:set_components",
                "components": nbt_tags.convert_to_json(updated_data)
            }
            if "conditions" in contents:
                set_components["conditions"] = contents["conditions"]
        else:
            set_components = None
        if set_custom_data and set_components:
            return [set_custom_data, set_components]
        if set_custom_data:
            return set_custom_data
        if set_components:
            return set_components
        return []


    return contents