# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from lib import defaults
from lib import json_manager
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import predicate
from lib.data_pack_files import item_modifier



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
        json.dump(loot_table(contents), file, indent=4)



def loot_table(contents: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    # Update item modifiers
    if "functions" in contents:
        for item_function in contents["functions"]:
            item_modifier.item_modifier(item_function)

    # Update pools
    if "pools" in contents:
        for pool in contents["pools"]:
            update_pool(pool)

    return contents



def update_pool(pool: dict[str, list]) -> dict[str, list]:
    # Update conditions
    if "conditions" in pool:
        for condition in pool["conditions"]:
            predicate.predicate(condition)

    # Update item modifiers
    if "functions" in pool:
        for item_function in pool["functions"]:
            item_modifier.item_modifier(item_function)

    # Update entries
    if "entries" in pool:
        for entry in pool["entries"]:
            update_entry(entry)

    return pool



def update_entry(entry: dict[str, str | list]) -> dict[str, str | list]:
    # Update conditions
    if "conditions" in entry:
        for condition in entry["conditions"]:
            predicate.predicate(condition)

    # Update item modifiers
    if "functions" in entry:
        object_id = miscellaneous.namespace(entry["name"]) if miscellaneous.namespace(entry["type"]) == "minecraft:item" and "name" in entry else ""
        for item_function in entry["functions"]:
            item_modifier.item_modifier(item_function, object_id)

    # Update children
    if "children" in entry:
        for children in entry["children"]:
            update_entry(children)

    return entry