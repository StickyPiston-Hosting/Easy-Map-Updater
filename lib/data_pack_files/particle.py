# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from typing import Any
from lib.data_pack_files import blocks
from lib.data_pack_files import items
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import tables
from lib.data_pack_files import arguments



def update_from_command(particle: str | dict[str, str], version: int, issues: list[dict[str, str | int]]) -> str:
    global pack_version
    pack_version = version

    return pack(update(particle, version, issues))

def update_from_nbt(particle: str | dict[str, Any], version: int, issues: list[dict[str, str | int]]) -> dict[str, Any]:
    global pack_version
    pack_version = version

    # Return if input type is a dict
    if isinstance(particle, dict):
        return particle

    particle_array = arguments.parse_with_quotes(particle, " ", True)
    particle_id = miscellaneous.namespace(particle_array[0])
    length = len(particle_array)
    particle_data = {
        "particle": particle_id
    }

    if particle_id in ["minecraft:block", "minecraft:block_marker", "minecraft:falling_dust"]:
        if length >= 2:
            particle_data["block"] = particle_array[1]

    if particle_id == "minecraft:dust":
        if length >= 5:
            particle_data["color_r"] = particle_array[1]
            particle_data["color_g"] = particle_array[2]
            particle_data["color_b"] = particle_array[3]
            particle_data["scale"] = particle_array[4]

    if particle_id == "minecraft:dust_color_transition":
        if length >= 8:
            particle_data["from_color_r"] = particle_array[1]
            particle_data["from_color_g"] = particle_array[2]
            particle_data["from_color_b"] = particle_array[3]
            particle_data["scale"] = particle_array[4]
            particle_data["to_color_r"] = particle_array[5]
            particle_data["to_color_g"] = particle_array[6]
            particle_data["to_color_b"] = particle_array[7]

    if particle_id == "minecraft:item":
        if length >= 2:
            particle_data["item"] = particle_array[1]

    if particle_id == "minecraft:sculk_charge":
        if length >= 2:
            particle_data["roll"] = particle_array[1]

    if particle_id == "minecraft:shriek":
        if length >= 2:
            particle_data["delay"] = particle_array[1]

    if particle_id == "minecraft:vibration":
        if length >= 5:
            particle_data["pos_x"] = particle_array[1]
            particle_data["pos_y"] = particle_array[2]
            particle_data["pos_z"] = particle_array[3]
            particle_data["arrival_in_ticks"] = particle_array[4]

    return update(particle_data, version, issues)



def update(particle: str | dict[str, str], version: int, issues: list[dict[str, str | int]]) -> dict[str, Any]:
    global pack_version
    pack_version = version

    # Initialize variables
    particle_id = "minecraft:cloud"
    block = ""
    item = ""
    color_r = ""
    color_g = ""
    color_b = ""
    from_color_r = ""
    from_color_g = ""
    from_color_b = ""
    to_color_r = ""
    to_color_g = ""
    to_color_b = ""
    scale = ""
    roll = ""
    delay = ""
    arrival_in_ticks = ""
    pos_x = ""
    pos_y = ""
    pos_z = ""

    # Extract arguments if a dict
    if isinstance(particle, dict):
        if "particle" in particle:
            particle_id = miscellaneous.namespace(particle["particle"])
        if "block" in particle:
            block = particle["block"]
        if "item" in particle:
            item = particle["item"]

        if "color_r" in particle:
            color_r = particle["color_r"]
        if "color_g" in particle:
            color_g = particle["color_g"]
        if "color_b" in particle:
            color_b = particle["color_b"]
        if "from_color_r" in particle:
            from_color_r = particle["from_color_r"]
        if "from_color_g" in particle:
            from_color_g = particle["from_color_g"]
        if "from_color_b" in particle:
            from_color_b = particle["from_color_b"]
        if "to_color_r" in particle:
            to_color_r = particle["to_color_r"]
        if "to_color_g" in particle:
            to_color_g = particle["to_color_g"]
        if "to_color_b" in particle:
            to_color_b = particle["to_color_b"]

        if "scale" in particle:
            scale = particle["scale"]

        if "roll" in particle:
            roll = particle["roll"]
        if "delay" in particle:
            delay = particle["delay"]
        if "arrival_in_ticks" in particle:
            arrival_in_ticks = particle["arrival_in_ticks"]

        if "pos_x" in particle:
            pos_x = particle["pos_x"]
        if "pos_y" in particle:
            pos_y = particle["pos_y"]
        if "pos_z" in particle:
            pos_z = particle["pos_z"]
    else:
        particle_id = miscellaneous.namespace(particle)



    # Convert ID based on version
    if pack_version <= 1202:
        for substring in ["minecraft:blockcrack_", "minecraft:blockdust_", "minecraft:iconcrack_"]:
            if substring in particle_id:
                particle_id = substring[:len(substring) - 1]

        id_array = tables.PARTICLE_IDS
        if particle_id in id_array:
            particle_id = id_array[particle_id]



    # Update block and item if they are set
    if block:
        block = blocks.update_from_command(block, version, issues)
    if item:
        item = items.update_from_command(item, version, issues)



    # Pack particle
    particle_data: dict[str, Any] = {
        "type": particle_id
    }

    if block:
        if "[" in block:
            block_states = block[block.find("["):]
            block_id = block[:block.find("[")]
        else:
            block_id = block
            block_states = ""
        particle_data["block_state"] = {}
        particle_data["block_state"]["Name"] = block_id
        if block_states:
            particle_data["block_state"]["Properties"] = blocks.unpack_block_states(block_states)

    if item:
        if "[" in item:
            item_id = item[:item.find("[")]
        else:
            item_id = item
        particle_data["item"] = item_id

    if color_r:
        particle_data["color"] = nbt_tags.TypeList([
            nbt_tags.TypeFloat(color_r),
            nbt_tags.TypeFloat(color_g),
            nbt_tags.TypeFloat(color_b),
        ])

    if from_color_r:
        particle_data["from_color"] = nbt_tags.TypeList([
            nbt_tags.TypeFloat(from_color_r),
            nbt_tags.TypeFloat(from_color_g),
            nbt_tags.TypeFloat(from_color_b),
        ])

    if to_color_r:
        particle_data["to_color"] = nbt_tags.TypeList([
            nbt_tags.TypeFloat(to_color_r),
            nbt_tags.TypeFloat(to_color_g),
            nbt_tags.TypeFloat(to_color_b),
        ])

    if scale:
        particle_data["scale"] = nbt_tags.TypeFloat(scale)
    if roll:
        particle_data["roll"] = nbt_tags.TypeFloat(roll)
    if delay:
        particle_data["delay"] = nbt_tags.TypeInt(delay)
    if arrival_in_ticks:
        particle_data["arrival_in_ticks"] = nbt_tags.TypeInt(arrival_in_ticks)

    if pos_x:
        particle_data["pos"] = nbt_tags.TypeList([
            nbt_tags.TypeFloat(pos_x),
            nbt_tags.TypeFloat(pos_y),
            nbt_tags.TypeFloat(pos_z),
        ])

    

    # Handle entity effects
    if pack_version <= 2004:
        if particle_id == "minecraft:entity_effect":
            particle_data["color"] = nbt_tags.TypeList([
                nbt_tags.TypeFloat(0),
                nbt_tags.TypeFloat(0),
                nbt_tags.TypeFloat(0),
                nbt_tags.TypeFloat(1),
            ])
        elif particle_id == "minecraft:ambient_entity_effect":
            particle_id = "minecraft:entity_effect"
            particle_data["type"] = particle_id
            particle_data["color"] = nbt_tags.TypeList([
                nbt_tags.TypeFloat(0),
                nbt_tags.TypeFloat(0),
                nbt_tags.TypeFloat(0),
                nbt_tags.TypeFloat(0.5),
            ])



    return particle_data



def pack(particle: dict[str, Any]) -> str:
    particle_id = "minecraft:cloud"

    if "type" in particle:
        particle_id = miscellaneous.namespace(particle["type"])
        del particle["type"]

    if particle:
        return particle_id + nbt_tags.pack(particle)
    else:
        return particle_id