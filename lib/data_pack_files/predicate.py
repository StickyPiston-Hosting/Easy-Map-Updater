# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from typing import cast, Any
from lib import defaults
from lib import utils
from lib import json_manager
from lib.log import log
from lib.data_pack_files import blocks
from lib.data_pack_files import items
from lib.data_pack_files import entities
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import ids
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import nbt_to_json
from lib.data_pack_files import item_component
from lib.data_pack_files import tables



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
    utils.safe_file_write(file_path, json.dumps(predicate(contents, version), indent=4))



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

    if condition == "minecraft:alternative":
        contents["condition"] = "minecraft:any_of"
        for i in range(len(contents["terms"])):
            contents["terms"][i] = predicate(contents["terms"][i], version)

    if condition == "minecraft:any_of":
        for i in range(len(contents["terms"])):
            contents["terms"][i] = predicate(contents["terms"][i], version)

    if condition == "minecraft:block_state_property":
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

    if condition == "minecraft:damage_source_properties":
        contents["predicate"] = predicate_damage_type(contents["predicate"], version)

    if condition == "minecraft:entity_properties":
        contents["predicate"] = predicate_entity(contents["predicate"], version)

    if condition == "minecraft:entity_scores":
        contents["entity"] = miscellaneous.loot_context(contents["entity"])
        for score in contents["scores"]:
            score_provider = contents["scores"][score]
            if isinstance(score_provider, dict):
                if "min" in score_provider:
                    score_provider["min"] = miscellaneous.number_provider(score_provider["min"])
                if "max" in score_provider:
                    score_provider["max"] = miscellaneous.number_provider(score_provider["max"])

    if condition == "minecraft:inverted":
        contents["term"] = predicate(contents["term"], version)

    if condition == "minecraft:location_check":
        contents["predicate"] = predicate_location(contents["predicate"], version)

    if condition == "minecraft:match_tool":
        contents["predicate"] = predicate_item(contents["predicate"], version)

    if condition == "minecraft:random_chance":
        contents["chance"] = miscellaneous.number_provider(contents["chance"])

    if condition == "minecraft:random_chance_with_looting":
        contents["condition"] = "minecraft:random_chance_with_enchanted_bonus"
        contents["enchantment"] = "minecraft:looting"
        if "chance" in contents:
            contents["unenchanted_chance"] = contents["chance"]
            del contents["chance"]
        else:
            contents["unenchanted_chance"] = 0.0
        if "looting_multiplier" in contents:
            contents["enchanted_chance"] = {
                "type": "minecraft:linear",
                "base": contents["unenchanted_chance"] + contents["looting_multiplier"],
                "per_level_above_first": contents["looting_multiplier"],
            }
            del contents["looting_multiplier"]
        else:
            contents["enchanted_chance"] = contents["unenchanted_chance"]

    if condition == "minecraft:table_bonus":
        contents["enchantment"] = ids.enchantment(contents["enchantment"], version, [])

    if condition == "minecraft:time_check":
        value = contents["value"]
        if isinstance(value, dict):
            if "min" in value:
                value["min"] = miscellaneous.number_provider(value["min"])
            if "max" in value:
                value["max"] = miscellaneous.number_provider(value["max"])

    if condition == "minecraft:value_check":
        contents["value"] = miscellaneous.number_provider(contents["value"])
        value_range = contents["range"]
        if isinstance(value_range, dict):
            if "min" in value_range:
                value_range["min"] = miscellaneous.number_provider(value_range["min"])
            if "max" in value_range:
                value_range["max"] = miscellaneous.number_provider(value_range["max"])
        


    # Update entity context
    if "entity" in contents:
        contents["entity"] = miscellaneous.loot_context(contents["entity"])

    
    
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
        contents["type_specific"]["type"] = "minecraft:player"
        del contents["player"]

    if "equipment" in contents:
        for slot in contents["equipment"]:
            predicate_item(contents["equipment"][slot], version)

    if "location" in contents:
        contents["location"] = predicate_location(contents["location"], version)

    if "movement_affected_by" in contents:
        contents["movement_affected_by"] = predicate_location(contents["movement_affected_by"], version)

    if "nbt" in contents:
        contents["nbt"] = nbt_tags.update(contents["nbt"], version, [], "entity")

    if "stepping_on" in contents:
        contents["stepping_on"] = predicate_location(contents["stepping_on"], version)

    if "passenger" in contents:
        contents["passenger"] = predicate_entity(contents["passenger"], version)
    if "targeted_entity" in contents:
        contents["targeted_entity"] = predicate_entity(contents["targeted_entity"], version)
    if "vehicle" in contents:
        contents["vehicle"] = predicate_entity(contents["vehicle"], version)

    # Apply namespace to entity types
    if "type" in contents:
        if isinstance(contents["type"], str):
            contents["type"] = miscellaneous.namespace(contents["type"])
        else:
            for i in range(len(contents["type"])):
                contents["type"][i] = miscellaneous.namespace(contents["type"][i])

    if "type_specific" in contents:
        contents["type_specific"]["type"] = miscellaneous.namespace(contents["type_specific"]["type"])
        entity_type = contents["type_specific"]["type"]

        type_specific_conversion = {
            "minecraft:axolotl": "minecraft:axolotl/variant",
            "minecraft:cat": "minecraft:cat/variant",
            "minecraft:fox": "minecraft:fox/variant",
            "minecraft:frog": "minecraft:frog/variant",
            "minecraft:horse": "minecraft:horse/variant",
            "minecraft:llama": "minecraft:llama/variant",
            "minecraft:mooshroom": "minecraft:mooshroom/variant",
            "minecraft:painting": "minecraft:painting/variant",
            "minecraft:parrot": "minecraft:parrot/variant",
            "minecraft:pig": "minecraft:pig/variant",
            "minecraft:rabbit": "minecraft:rabbit/variant",
            "minecraft:salmon": "minecraft:salmon/size",
            "minecraft:tropical_fish": "minecraft:tropical_fish/pattern",
            "minecraft:villager": "minecraft:villager/variant",
            "minecraft:wolf": "minecraft:wolf/variant",
        }

        if entity_type == "minecraft:boat":
            variant = contents["type_specific"]["variant"]

            if "type" not in contents:
                contents["type"] = [
                    tables.BOAT_TYPES[variant],
                    tables.CHEST_BOAT_TYPES[variant]
                ]

            else:
                if isinstance(contents["type"], str):
                    if contents["type"] == "minecraft:boat":
                        contents["type"] = tables.BOAT_TYPES[variant]
                    elif contents["type"] == "minecraft:chest_boat":
                        contents["type"] = tables.CHEST_BOAT_TYPES[variant]
                    else:
                        if contents["type"].startswith("#"):
                            log(f"WARNING: Entity tag {contents["type"]} is being usurped by boat types in entity predicate")
                        contents["type"] = [
                            tables.BOAT_TYPES[variant],
                            tables.CHEST_BOAT_TYPES[variant]
                        ]

                else:
                    if "minecraft:boat" in contents["type"] and "minecraft:chest_boat" in contents["type"]:
                        contents["type"] = [
                            tables.BOAT_TYPES[variant],
                            tables.CHEST_BOAT_TYPES[variant]
                        ]
                    elif "minecraft:boat" in contents["type"]:
                        contents["type"] = tables.BOAT_TYPES[variant]
                    elif "minecraft:chest_boat" in contents["type"]:
                        contents["type"] = tables.CHEST_BOAT_TYPES[variant]
                    else:
                        contents["type"] = [
                            tables.BOAT_TYPES[variant],
                            tables.CHEST_BOAT_TYPES[variant]
                        ]

            del contents["type_specific"]

        elif entity_type == "minecraft:lightning":
            if "entity_struck" in contents["type_specific"]:
                contents["type_specific"]["entity_struck"] = predicate_entity(contents["type_specific"]["entity_struck"], version)

        elif entity_type == "minecraft:player":
            if "looking_at" in contents["type_specific"]:
                contents["type_specific"]["looking_at"] = predicate_entity(contents["type_specific"]["looking_at"], version)

        # Extract type specific check into an entity component
        elif entity_type in type_specific_conversion:            
            if "variant" in contents["type_specific"]:
                if "components" not in contents:
                    contents["components"] = {}

                if isinstance(contents["type_specific"]["variant"], list):
                    log(f"WARNING: type_specific: {entity_type} entity predicate variant is being condensed from a list to a single string")
                    variant = contents["type_specific"]["variant"][0] if len(contents["type_specific"]["variant"]) > 0 else None
                else:
                    variant = contents["type_specific"]["variant"]

                if variant is not None:
                    contents["components"][type_specific_conversion[entity_type]] = variant

            del contents["type_specific"]

        if entity_type == "minecraft:sheep":
            if "color" in contents["type_specific"]:
                if "components" not in contents:
                    contents["components"] = {}

                contents["components"]["minecraft:sheep/color"] = contents["type_specific"]["color"]
                del contents["type_specific"]["color"]

                if "sheared" not in contents["type_specific"]:
                    del contents["type_specific"]

    # Update entity types
    if "type" in contents:
        if isinstance(contents["type"], str):
            contents["type"] = entities.update({"id": contents["type"], "read": True}, version, [])
        else:
            for i in range(len(contents["type"])):
                contents["type"][i] = entities.update({"id": contents["type"][i], "read": True}, version, [])

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

    if "components" in contents:
        item_components = item_component.ItemComponents.unpack_from_dict(nbt_tags.convert_from_json(contents["components"]), False)
        updated_item_components = item_component.conform_components(item_components, version, []).pack_to_dict()
        contents["components"] = nbt_to_json.convert_item_components_to_json(updated_item_components)

    if "nbt" in contents:
        updated_data = cast(dict[str, Any], nbt_tags.direct_update(nbt_tags.unpack(contents["nbt"]), version, [], "item_tag", "", True))
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
                        "components": item_component.ItemComponents([]),
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
                    "components": item_component.ItemComponents([]),
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
            bundle_contents = predicates["minecraft:bundle_contents"]
            if "items" in bundle_contents:
                if "contains" in bundle_contents["items"]:
                    bundle_contents["items"]["contains"] = predicate_item(bundle_contents["items"]["contains"], version)

        if "minecraft:container" in predicates:
            container = predicates["minecraft:container"]
            if "items" in container:
                if "contains" in container["items"]:
                    container["items"]["contains"] = predicate_item(container["items"]["contains"], version)

        if "minecraft:enchantments" in predicates:
            for enchantment in predicates["minecraft:enchantments"]:
                if "enchantment" in enchantment:
                    enchantment["enchantments"] = enchantment["enchantment"]
                    del enchantment["enchantment"]
                if isinstance(enchantment["enchantments"], str):
                    enchantment["enchantments"] = ids.enchantment(enchantment["enchantments"], version, [])
                else:
                    for i in range(len(enchantment["enchantments"])):
                        enchantment["enchantments"][i] = ids.enchantment(enchantment["enchantments"][i], version, [])



    return contents



def predicate_location(contents: dict, version: int) -> dict:
    global pack_version
    pack_version = version

    if "biomes" in contents:
        if isinstance(contents["biomes"], list):
            for i in range(len(contents["biomes"])):
                contents["biomes"][i] = ids.biome(contents["biomes"][i], version, [])
        else:
            contents["biomes"] = ids.biome(contents["biomes"], version, [])

    if "biome" in contents:
        contents["biomes"] = [ids.biome(contents["biome"], version, [])]
        del contents["biome"]

    if "block" in contents:
        if "nbt" in contents["block"]:
            contents["block"]["nbt"] = nbt_tags.update(contents["block"]["nbt"], version, [], "block")

        if "tag" in contents["block"]:
            if "blocks" not in contents["block"]:
                contents["block"]["blocks"] = "#" + miscellaneous.namespace(contents["block"]["tag"])
            del contents["block"]["tag"]


    if "fluid" in contents:
        if "fluid" in contents["fluid"]:
            contents["fluid"]["fluids"] = miscellaneous.namespace(contents["fluid"]["fluid"])
            del contents["fluid"]["fluid"]

        if "tag" in contents["fluid"]:
            if "fluids" not in contents["fluid"]:
                contents["fluid"]["fluids"] = "#" + miscellaneous.namespace(contents["fluid"]["tag"])
            del contents["fluid"]["tag"]

    if "structure" in contents:
        contents["structures"] = contents["structure"]
        del contents["structure"]

    return contents