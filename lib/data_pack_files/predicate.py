# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from typing import cast, Any
from lib import defaults
from lib import json_manager
from lib.data_pack_files import blocks
from lib.data_pack_files import items
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import nbt_to_json



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
        json.dump(predicate(contents, version), file, indent=4)



def predicate(contents: dict[str, Any] | list[dict], version: int) -> dict[str, Any] | list[dict]:
    global pack_version
    pack_version = version

    # If predicate is a list, feed it through a loop instead
    if isinstance(contents, list):
        for i in range(len(contents)):
            contents[i] = cast(dict, predicate(contents[i], version))
        return contents



    # Process different conditions
    condition: str = contents["condition"]
    condition = miscellaneous.namespace(condition)
    contents["condition"] = condition



    if condition == "minecraft:all_of":
        for i in range(len(contents["terms"])):
            contents["terms"][i] = predicate(contents["terms"][i], version)

    elif condition == "minecraft:alternative":
        contents["condition"] = "minecraft:any_of"
        for i in range(len(contents["terms"])):
            contents["terms"][i] = predicate(contents["terms"][i], version)

    elif condition == "minecraft:any_of":
        for i in range(len(contents["terms"])):
            contents["terms"][i] = predicate(contents["terms"][i], version)

    elif condition == "minecraft:block_state_property":
        block_data = cast(blocks.BlockInputFromNBT, {"BlockState": {"Name": contents["block"]}})
        if "properties" in contents["block"]:
            block_data["BlockState"]["Properties"] = {}
            for block_property in contents["block"]["properties"]:
                value = contents["block"]["properties"][block_property]
                if isinstance(value, str):
                    block_data["BlockState"]["Properties"][block_property] = value
        block_data = blocks.update_from_nbt(block_data, version, [])
        if "Name" in block_data:
            contents["block"] = block_data["Name"]
        if "Properties" in block_data:
            if "properties" not in contents["block"]:
                cast(dict, contents["block"])["properties"] = {}
            for block_property in block_data["Properties"]:
                cast(dict, contents["block"])["properties"] = block_data["Properties"][block_property]

    elif condition == "minecraft:damage_source_properties":
        contents["predicate"] = predicate_damage_type(contents["predicate"], version)

    elif condition == "minecraft:entity_properties":
        contents["predicate"] = predicate_entity(contents["predicate"], version)

    elif condition == "minecraft:inverted":
        contents["term"] = predicate(contents["term"], version)

    elif condition == "minecraft:location_check":
        contents["predicate"] = predicate_location(contents["predicate"], version)

    elif condition == "minecraft:match_tool":
        contents["predicate"] = predicate_item(contents["predicate"], version)

    
    
    return contents



def predicate_damage_type(contents: dict, version: int) -> dict:
    global pack_version
    pack_version = version

    for key in ["direct_entity", "source_entity"]:
        if key in contents:
            contents[key] = predicate_entity(contents[key], version)
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



def predicate_entity(contents: dict, version: int) -> dict:
    global pack_version
    pack_version = version

    # Player type-specific
    if "player" in contents:
        contents["type_specific"] = contents["player"]
        contents["type_specific"]["type"] = "player"
        del contents["player"]

    if "equipment" in contents:
        for slot in contents["equipment"]:
            predicate_item(contents["equipment"][slot], version)

    if "location" in contents:
        contents["location"] = predicate_location(contents["location"], version)

    if "nbt" in contents:
        contents["nbt"] = nbt_tags.update(contents["nbt"], version, [], "entity")

    if "passenger" in contents:
        contents["passenger"] = predicate_entity(contents["passenger"], version)
    if "targeted_entity" in contents:
        contents["targeted_entity"] = predicate_entity(contents["targeted_entity"], version)
    if "vehicle" in contents:
        contents["vehicle"] = predicate_entity(contents["vehicle"], version)

    if "type_specific" in contents:
        if contents["type_specific"]["type"] == "lightning":
            if "entity_struck" in contents["type_specific"]:
                contents["type_specific"]["entity_struck"] = predicate_entity(contents["type_specific"]["entity_struck"], version)

        if contents["type_specific"]["type"] == "player":
            if "looking_at" in contents["type_specific"]:
                contents["type_specific"]["looking_at"] = predicate_entity(contents["type_specific"]["looking_at"], version)

    return contents



def predicate_item(contents: dict, version: int) -> dict:
    global pack_version
    pack_version = version

    if "durability" in contents:
        if "predicates" not in contents:
            contents["predicates"] = {}
        contents["predicates"]["minecraft:damage"] = {
            "durability": contents["durability"]
        }
        del contents["durability"]

    if "enchantments" in contents:
        if "predicates" not in contents:
            contents["predicates"] = {}
        if "minecraft:enchantments" not in contents["predicates"]:
            contents["predicates"]["minecraft:enchantments"] = []
        for enchantment in contents["enchantments"]:
            contents["predicates"]["minecraft:enchantments"].append(enchantment)
        del contents["enchantments"]

    if "nbt" in contents:
        updated_data = cast(dict[str, Any], nbt_tags.direct_update(nbt_tags.unpack(contents["nbt"]), version, [], "item_tag", ""))
        if "minecraft:custom_data" in updated_data:
            if "predicates" not in contents:
                contents["predicates"] = {}
            contents["predicates"]["minecraft:custom_data"] = nbt_tags.pack(updated_data["minecraft:custom_data"])
            del updated_data["minecraft:custom_data"]
        if len(updated_data):
            contents["components"] = nbt_to_json.convert_item_components_to_json(updated_data)
        del contents["nbt"]

    if "potion" in contents:
        if "predicates" not in contents:
            contents["predicates"] = {}
        contents["predicates"]["minecraft:potion_contents"] = miscellaneous.namespace(contents["potion"])
        del contents["potion"]

    if "stored_enchantments" in contents:
        if "predicates" not in contents:
            contents["predicates"] = {}
        if "minecraft:stored_enchantments" not in contents["predicates"]:
            contents["predicates"]["minecraft:stored_enchantments"] = []
        for enchantment in contents["stored_enchantments"]:
            contents["predicates"]["minecraft:stored_enchantments"].append(enchantment)
        del contents["stored_enchantments"]



    if "items" in contents:
        if isinstance(contents["items"], list):
            for index in range(len(contents["items"])):
                contents["items"][index] = items.update(
                    {
                        "id": contents["items"][index],
                        "data_value": -1,
                        "components": {},
                        "nbt": {},
                        "read": True
                    },
                    version, []
                )["id"]
        if isinstance(contents["items"], str):
            contents["items"] = items.update(
                {
                    "id": contents["items"],
                    "data_value": -1,
                    "components": {},
                    "nbt": {},
                    "read": True
                },
                version, []
            )["id"]

    if "tag" in contents:
        if "items" not in contents:
            contents["items"] = "#" + miscellaneous.namespace(contents["tag"])
        del contents["tag"]



    if "predicates" in contents:
        predicates = contents["predicates"]
        
        if "minecraft:bundle_contents" in predicates:
            if "items" in predicates["minecraft:bundle_contents"]:
                if "contains" in predicates["minecraft:bundle_contents"]["items"]:
                    predicates["minecraft:bundle_contents"]["items"]["contains"] = predicate_item(predicates["minecraft:bundle_contents"]["items"]["contains"], version)

        if "minecraft:container" in predicates:
            if "items" in predicates["minecraft:container"]:
                if "contains" in predicates["minecraft:container"]["items"]:
                    predicates["minecraft:container"]["items"]["contains"] = predicate_item(predicates["minecraft:container"]["items"]["contains"], version)



    return contents



def predicate_location(contents: dict, version: int) -> dict:
    global pack_version
    pack_version = version

    if "biome" in contents:
        contents["biomes"] = contents["biome"]
        del contents["biome"]

    if "block" in contents:
        if "nbt" in contents["block"]:
            contents["block"]["nbt"] = nbt_tags.update(contents["block"]["nbt"], version, [], "block")

        if "tag" in contents["block"]:
            if "blocks" not in contents["block"]:
                contents["block"]["blocks"] = miscellaneous.namespace(contents["block"]["tag"])
            del contents["block"]["tag"]


    if "fluid" in contents:
        if "fluid" in contents["fluid"]:
            contents["fluid"]["fluids"] = miscellaneous.namespace(contents["fluid"])
            del contents["fluid"]

        if "tag" in contents["fluid"]:
            if "fluids" not in contents["fluid"]:
                contents["fluid"]["fluids"] = miscellaneous.namespace(contents["fluid"]["tag"])
            del contents["fluid"]["tag"]

    if "structure" in contents:
        contents["structures"] = contents["structure"]
        del contents["structure"]

    return contents