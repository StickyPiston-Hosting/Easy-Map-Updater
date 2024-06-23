# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from typing import cast, TypedDict, Any
from lib import defaults
from lib import json_manager
from lib.data_pack_files import items
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import predicate
from lib.data_pack_files import item_modifier



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
        json.dump(loot_table(contents, version), file, indent=4)



def loot_table(contents: dict[str, Any], version: int) -> dict[str, dict[str, str]]:
    global pack_version
    pack_version = version

    # Update item modifiers
    if "functions" in contents:
        for item_function in contents["functions"]:
            item_modifier.item_modifier(item_function, version)

    # Update pools
    if "pools" in contents:
        for pool in contents["pools"]:
            update_pool(pool, version)

    return contents



def update_pool(pool: dict[str, list], version: int) -> dict[str, list]:
    global pack_version
    pack_version = version

    # Update conditions
    if "conditions" in pool:
        for condition in pool["conditions"]:
            predicate.predicate(condition, version)

    # Update item modifiers
    if "functions" in pool:
        for item_function in pool["functions"]:
            item_modifier.item_modifier(item_function, version)

    # Update entries
    if "entries" in pool:
        for entry in pool["entries"]:
            update_entry(entry, version)

    return pool



class LootTableEntry(TypedDict):
    conditions: list
    functions: list
    type: str
    children: list

def update_entry(entry: LootTableEntry, version: int) -> LootTableEntry:
    global pack_version
    pack_version = version

    # Update conditions
    if "conditions" in entry:
        for condition in cast(list, entry["conditions"]):
            predicate.predicate(condition, version)

    # Update item modifiers
    if "functions" in entry:
        object_id = miscellaneous.namespace(entry["name"]) if miscellaneous.namespace(entry["type"]) == "minecraft:item" and "name" in entry else ""
        for item_function in entry["functions"]:
            item_modifier.item_modifier(item_function, version, object_id)

    # Update children
    if "children" in entry:
        for children in entry["children"]:
            update_entry(children, version)

    # Update keys based on type
    if "type" in entry:
        entry["type"] = miscellaneous.namespace(entry["type"])

        if entry["type"] == "minecraft:item":
            if "name" in entry:
                entry["name"] = items.update(
                    {
                        "id": entry["name"],
                        "data_value": -1,
                        "nbt": {},
                        "read": True
                    },
                    version, []
                )["id"]
                
        if entry["type"] in ["minecraft:loot_table", "minecraft:tag"]:
            if "name" in entry:
                entry["name"] = miscellaneous.namespace(entry["name"])

    return entry