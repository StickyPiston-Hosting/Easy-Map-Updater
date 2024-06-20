# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from typing import cast
from pathlib import Path
from lib.log import log
from lib import defaults
from lib import finalize
from lib.data_pack_files import tables



# Initialize variables

pack_version = defaults.PACK_VERSION
PACK_FORMAT = defaults.DATA_PACK_FORMAT
SEND_PYTHON = False



# Define functions

def create_pack(world: Path):
    log("Creating tag replacements data pack")

    SEND_PYTHON = False

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return

    # Create data pack
    data_pack_path = world / "datapacks" / "tag_replacements"
    data_pack_path.mkdir(exist_ok=True, parents=True)

    with (data_pack_path / "pack.mcmeta").open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            {
            	"pack": {
            		"pack_format": PACK_FORMAT,
            		"description": "Adds block and item tags to account for the flattening of 1.13."
            	}
            },
            file,
            indent=4
        )

    # Create item tags
    folder_path = data_pack_path / "data" / "tag_replacements" / "tags" / "items"
    folder_path.mkdir(exist_ok=True, parents=True)
    item_id_array = tables.ITEM_IDS_DATA

    for item in item_id_array:
        # Handle special cases
        if item == "minecraft:spawn_egg":
            create_item_tag(folder_path, item, tables.SPAWN_EGGS)
        # Handle normal cases
        elif len(item_id_array[item]) == 1:
            if SEND_PYTHON:
                log(f'"{item}": "{item_id_array[item][0]}",')
        else:
            create_item_tag(folder_path, item, item_id_array[item])

    # Create block tags
    folder_path = data_pack_path / "data" / "tag_replacements" / "tags" / "blocks"
    folder_path.mkdir(exist_ok=True, parents=True)
    block_id_array = tables.BLOCK_IDS_DATA

    for block in block_id_array:
        block_data: dict[int, dict[str, str | dict[str, str]]] = block_id_array[block]
        block_ids: list[str] = []
        first_block = block_data[list(block_data.keys())[0]]
        # Initialize stored properties list for comparison, only properties which are the same for all blocks will be kept
        if "Properties" in first_block:
            block_properties: dict[str, str] = cast(dict[str, str], first_block["Properties"]).copy()
        else:
            block_properties = {}
        # Iterate through data values
        for data_value in block_data:
            if not isinstance(data_value, int):
                continue
            block_variant = block_data[data_value]
            # Get block ID and add it to the list
            block_id: str = cast(str, block_variant["Name"])
            if block_id not in block_ids:
                block_ids.append(block_id)
            # Remove properties which do not appear in the current variant
            if "Properties" in block_variant:
                for block_property in list(block_properties.keys()):
                    if block_property not in block_variant["Properties"] or block_properties[block_property] != cast(dict[str, str], block_variant["Properties"])[block_property]:
                        del block_properties[block_property]
            else:
                block_properties = {}

        # Handle special cases
        if block == "minecraft:standing_banner":
            create_block_tag(folder_path, block, [
                "minecraft:white_banner",
                "minecraft:orange_banner",
                "minecraft:magenta_banner",
                "minecraft:light_blue_banner",
                "minecraft:yellow_banner",
                "minecraft:lime_banner",
                "minecraft:pink_banner",
                "minecraft:gray_banner",
                "minecraft:light_gray_banner",
                "minecraft:cyan_banner",
                "minecraft:purple_banner",
                "minecraft:blue_banner",
                "minecraft:brown_banner",
                "minecraft:green_banner",
                "minecraft:red_banner",
                "minecraft:black_banner" 
            ])
        elif block == "minecraft:wall_banner":
            create_block_tag(folder_path, block, [
                "minecraft:white_wall_banner",
                "minecraft:orange_wall_banner",
                "minecraft:magenta_wall_banner",
                "minecraft:light_blue_wall_banner",
                "minecraft:yellow_wall_banner",
                "minecraft:lime_wall_banner",
                "minecraft:pink_wall_banner",
                "minecraft:gray_wall_banner",
                "minecraft:light_gray_wall_banner",
                "minecraft:cyan_wall_banner",
                "minecraft:purple_wall_banner",
                "minecraft:blue_wall_banner",
                "minecraft:brown_wall_banner",
                "minecraft:green_wall_banner",
                "minecraft:red_wall_banner",
                "minecraft:black_wall_banner" 
            ])
        elif block == "minecraft:bed":
            create_block_tag(folder_path, block, [
                "minecraft:white_bed",
                "minecraft:orange_bed",
                "minecraft:magenta_bed",
                "minecraft:light_blue_bed",
                "minecraft:yellow_bed",
                "minecraft:lime_bed",
                "minecraft:pink_bed",
                "minecraft:gray_bed",
                "minecraft:light_gray_bed",
                "minecraft:cyan_bed",
                "minecraft:purple_bed",
                "minecraft:blue_bed",
                "minecraft:brown_bed",
                "minecraft:green_bed",
                "minecraft:red_bed",
                "minecraft:black_bed"
            ])
        elif block == "minecraft:flower_pot":
            if SEND_PYTHON:
                log(f'"{block}": {{"Name": "#minecraft:flower_pots"}},')
        elif block == "minecraft:skull":
            create_block_tag(folder_path, block, [
                "minecraft:skeleton_skull",
                "minecraft:wither_skeleton_skull",
                "minecraft:zombie_head",
                "minecraft:player_head",
                "minecraft:creeper_head",
                "minecraft:dragon_head",
                "minecraft:skeleton_wall_skull",
                "minecraft:wither_skeleton_wall_skull",
                "minecraft:zombie_wall_head",
                "minecraft:player_wall_head",
                "minecraft:creeper_wall_head",
                "minecraft:ender_dragon_wall_head"
            ])
            create_block_tag(folder_path, "minecraft:floor_skull", [
                "minecraft:skeleton_skull",
                "minecraft:wither_skeleton_skull",
                "minecraft:zombie_head",
                "minecraft:player_head",
                "minecraft:creeper_head",
                "minecraft:dragon_head"
            ])
            create_block_tag(folder_path, "minecraft:wall_skull", [
                "minecraft:skeleton_wall_skull",
                "minecraft:wither_skeleton_wall_skull",
                "minecraft:zombie_wall_head",
                "minecraft:player_wall_head",
                "minecraft:creeper_wall_head",
                "minecraft:ender_dragon_wall_head"
            ])
        elif len(block_ids) == 1:
            if SEND_PYTHON:
                properties_string = ', "Properties": ' + str(block_properties).replace("'", '"')
                log(f'"{block}": {{"Name": "{block_ids[0]}"{properties_string if block_properties else ""}}},')
        else:
            # Create block tag if multiple block IDs were found (also ignoring all block properties)
            create_block_tag(folder_path, block, block_ids)


            
    log("Tag replacements data pack created")

    finalize.log_data_packs(world)



def create_item_tag(folder_path: Path, object_id: str, object_list: list[str]):
    if SEND_PYTHON:
        log(f'"{object_id}": "#tag_replacements:{object_id[10:]}",')
        #log(f'"#tag_replacements:{object_id[10:]}": {object_list}'.replace("'", '"'))
        log(f'"{object_list[0]}": "#tag_replacements:{object_id[10:]}"')
    file_path = folder_path / (object_id[10:] + ".json")
    with file_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            {
                "values": object_list
            },
            file,
            indent=4
        )

def create_block_tag(folder_path: Path, object_id: str, object_list: list[str]):
    if SEND_PYTHON:
        log(f'"{object_id}": {{"Name": "#tag_replacements:{object_id[10:]}"}},')
    #log(f'"#tag_replacements:{object_id[10:]}": {object_list}'.replace("'", '"'))
    #log(f'"{object_list[0]}": "#tag_replacements:{object_id[10:]}"')
    file_path = folder_path / (object_id[10:] + ".json")
    with file_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            {
                "values": object_list
            },
            file,
            indent=4
        )