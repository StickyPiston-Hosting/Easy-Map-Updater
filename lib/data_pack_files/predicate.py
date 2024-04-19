# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from lib import defaults
from lib import json_manager
from lib.data_pack_files import blocks
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import nbt_tags



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
        json.dump(predicate(contents), file, indent=4)



def predicate(contents: dict[str, dict[str, str]] | list[dict]) -> dict[str, dict[str, str]]:
    # If predicate is a list, feed it through a loop instead
    if isinstance(contents, list):
        for i in range(len(contents)):
            contents[i] = predicate(contents[i])
        return contents



    # Process different conditions
    condition: str = contents["condition"]
    condition = miscellaneous.namespace(condition)
    contents["condition"] = condition



    if condition == "minecraft:all_of":
        for i in range(len(contents["terms"])):
            contents["terms"][i] = predicate(contents["terms"][i])

    elif condition == "minecraft:alternative":
        contents["condition"] = "minecraft:any_of"
        for i in range(len(contents["terms"])):
            contents["terms"][i] = predicate(contents["terms"][i])

    elif condition == "minecraft:any_of":
        for i in range(len(contents["terms"])):
            contents["terms"][i] = predicate(contents["terms"][i])

    elif condition == "minecraft:block_state_property":
        block_data = {"BlockState": {"Name": contents["block"]}}
        if "properties" in contents["block"]:
            block_data["BlockState"]["Properties"] = {}
            for block_property in contents["block"]["properties"]:
                value = contents["block"]["properties"][block_property]
                if isinstance(value, str):
                    block_data["BlockState"]["Properties"][block_property] = value
        block_data = blocks.update_from_nbt(block_data, pack_version)
        if "Name" in block_data:
            contents["block"] = block_data["Name"]
        if "Properties" in block_data:
            if "properties" not in contents["block"]:
                contents["block"]["properties"] = {}
            for block_property in block_data["Properties"]:
                contents["block"]["properties"] = block_data["Properties"][block_property]

    elif condition == "minecraft:damage_source_properties":
        contents["predicate"] = predicate_damage_type(contents["predicate"])

    elif condition == "minecraft:entity_properties":
        contents["predicate"] = predicate_entity(contents["predicate"])

    elif condition == "minecraft:inverted":
        contents["term"] = predicate(contents["term"])

    elif condition == "minecraft:location_check":
        contents["predicate"] = predicate_location(contents["predicate"])

    elif condition == "minecraft:match_tool":
        contents["predicate"] = predicate_item(contents["predicate"])

    
    
    return contents



def predicate_damage_type(contents: dict) -> dict:
    for key in ["direct_entity", "source_entity"]:
        if key in contents:
            contents[key] = predicate_entity(contents[key])
    if "tags" not in contents:
        contents["tags"] = []
    for key in ["is_projectile", "is_explosion", "bypasses_armor", "bypasses_invulnerability", "bypasses_magic", "is_fire", "is_magic", "is_lightning"]:
        if key in contents:
            contents["tags"].append({
                "id": miscellaneous.namespace(key),
                "expected": contents[key]
            })
            del contents[key]
    return contents



def predicate_entity(contents: dict) -> dict:
    # Player type-specific
    if "player" in contents:
        contents["type_specific"] = contents["player"]
        contents["type_specific"]["type"] = "player"
        del contents["player"]

    if "equipment" in contents:
        for slot in contents["equipment"]:
            predicate_item(contents["equipment"][slot])

    if "location" in contents:
        contents["location"] = predicate_location(contents["location"])

    if "nbt" in contents:
        contents["nbt"] = nbt_tags.update(contents["nbt"], pack_version, [], "entity")

    if "passenger" in contents:
        contents["passenger"] = predicate_entity(contents["passenger"])
    if "targeted_entity" in contents:
        contents["targeted_entity"] = predicate_entity(contents["targeted_entity"])
    if "vehicle" in contents:
        contents["vehicle"] = predicate_entity(contents["vehicle"])

    if "type_specific" in contents:
        if contents["type_specific"]["type"] == "lightning":
            if "entity_struck" in contents["type_specific"]:
                contents["type_specific"]["entity_struck"] = predicate_entity(contents["type_specific"]["entity_struck"])

        if contents["type_specific"]["type"] == "player":
            if "looking_at" in contents["type_specific"]:
                contents["type_specific"]["looking_at"] = predicate_entity(contents["type_specific"]["looking_at"])

    return contents



def predicate_item(contents: dict) -> dict:
    if "nbt" in contents:
        contents["nbt"] = nbt_tags.update(contents["nbt"], pack_version, [], "item_tag")

    return contents



def predicate_location(contents: dict) -> dict:
    if "block" in contents:
        if "nbt" in contents["block"]:
            contents["block"]["nbt"] = nbt_tags.update(contents["block"]["nbt"], pack_version, [], "block")

    return contents