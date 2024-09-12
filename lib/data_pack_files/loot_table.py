# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from typing import cast, TypedDict, NotRequired
from lib import defaults
from lib import utils
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
    utils.safe_file_write(file_path, json.dumps(loot_table(cast(LootTable, contents), version), indent=4))



class LootTable(TypedDict):
    functions: list
    pools: "list[LootTablePool]"

def loot_table(contents: LootTable, version: int) -> LootTable:
    global pack_version
    pack_version = version

    # Update item modifiers
    if "functions" in contents:
        contents["functions"] = cast(list, item_modifier.item_modifier(contents["functions"], version))

    # Update pools
    if "pools" in contents:
        for pool in contents["pools"]:
            update_pool(pool, version)

    return contents



class LootTablePool(TypedDict):
    conditions: list
    functions: list
    entries: "list[LootTableEntry]"
    rolls: int | float | dict
    bonus_rolls: int | float | dict

def update_pool(pool: LootTablePool, version: int) -> LootTablePool:
    global pack_version
    pack_version = version

    # Update conditions
    if "conditions" in pool:
        for condition in pool["conditions"]:
            predicate.predicate(condition, version)

    # Update item modifiers
    if "functions" in pool:
        pool["functions"] = cast(list, item_modifier.item_modifier(pool["functions"], version))

    # Update entries
    if "entries" in pool:
        for entry in pool["entries"]:
            update_entry(entry, version)

    # Update rolls
    if "rolls" in pool:
        pool["rolls"] = miscellaneous.number_provider(pool["rolls"])
    if "bonus_rolls" in pool:
        pool["bonus_rolls"] = miscellaneous.number_provider(pool["bonus_rolls"])

    return pool



class LootTableEntry(TypedDict):
    conditions: list
    functions: list
    type: str
    name: NotRequired[str]
    value: str | LootTable
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
        entry["functions"] = cast(list, item_modifier.item_modifier(entry["functions"], version, object_id))

    # Update children
    if "children" in entry:
        for children in entry["children"]:
            update_entry(children, version)

    # Update keys based on type
    if "type" in entry:
        entry["type"] = miscellaneous.namespace(entry["type"])

        if entry["type"] == "minecraft:item":
            if "name" in entry:
                entry["name"] = cast(str, items.update(
                    {
                        "id": entry["name"],
                        "data_value": -1,
                        "components": {},
                        "nbt": {},
                        "read": True
                    },
                    version, []
                )["id"])
                
        if entry["type"] == "minecraft:loot_table":
            if "name" in entry:
                entry["value"] = miscellaneous.namespace(entry["name"])
                del entry["name"]

            elif "value" in entry:
                if isinstance(entry["value"], dict):
                    entry["value"] = loot_table(entry["value"], pack_version)
                else:
                    entry["value"] = miscellaneous.namespace(entry["value"])

        if entry["type"] == "minecraft:tag":
            if "name" in entry:
                entry["name"] = miscellaneous.namespace(entry["name"])

    return entry