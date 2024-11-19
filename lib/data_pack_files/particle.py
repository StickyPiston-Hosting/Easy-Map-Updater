# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from typing import Any, cast
from lib.data_pack_files import blocks
from lib.data_pack_files import items
from lib.data_pack_files import item_component
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

    # Prepare particle data
    particle_data: dict[str, Any] = {
        "type": "minecraft:cloud"
    }

    # Extract arguments if a dict
    if isinstance(particle, dict):
        if "particle" in particle:
            particle_data["type"] = miscellaneous.namespace(particle["particle"])
        if "block" in particle:
            block = particle["block"]
            if "[" in block:
                block_id = block[:block.find("[")]
                block_states = block[block.find("["):]
            else:
                block_id = block
                block_states = ""
            particle_data["block_state"] = {}
            particle_data["block_state"]["Name"] = block_id
            if block_states:
                particle_data["block_state"]["Properties"] = blocks.unpack_block_states(block_states)
        if "item" in particle:
            item = particle["item"]
            if "[" in item:
                item_id = item[:item.find("[")]
                components = item[item.find("["):]
            else:
                item_id = item
                components = ""
            particle_data["item"] = {}
            particle_data["item"]["id"] = item_id
            if components:
                particle_data["item"]["components"] = item_component.ItemComponents.unpack(components).pack_to_dict()

        if "color_r" in particle:
            particle_data["color"] = nbt_tags.TypeList([
                nbt_tags.TypeFloat(particle["color_r"]),
                nbt_tags.TypeFloat(particle["color_g"]),
                nbt_tags.TypeFloat(particle["color_b"]),
            ])

        if "from_color_r" in particle:
            particle_data["from_color"] = nbt_tags.TypeList([
                nbt_tags.TypeFloat(particle["from_color_r"]),
                nbt_tags.TypeFloat(particle["from_color_g"]),
                nbt_tags.TypeFloat(particle["from_color_b"]),
            ])

        if "to_color_r" in particle:
            particle_data["to_color"] = nbt_tags.TypeList([
                nbt_tags.TypeFloat(particle["to_color_r"]),
                nbt_tags.TypeFloat(particle["to_color_g"]),
                nbt_tags.TypeFloat(particle["to_color_b"]),
            ])

        if "scale" in particle:
            particle_data["scale"] = nbt_tags.TypeFloat(particle["scale"])
        if "roll" in particle:
            particle_data["roll"] = nbt_tags.TypeFloat(particle["roll"])
        if "delay" in particle:
            particle_data["delay"] = nbt_tags.TypeInt(particle["delay"])
        if "arrival_in_ticks" in particle:
            particle_data["arrival_in_ticks"] = nbt_tags.TypeInt(particle["arrival_in_ticks"])

        if "pos_x" in particle:
            if "destination" not in particle_data:
                particle_data["destination"] = {}
            particle_data["destination"]["type"] = "block"
            particle_data["destination"]["pos"] = nbt_tags.TypeList([
                nbt_tags.TypeInt(particle["pos_x"]),
                nbt_tags.TypeInt(particle["pos_y"]),
                nbt_tags.TypeInt(particle["pos_z"]),
            ])

    else:
        # Extract particle data if in string form
        if "{" in particle:
            particle_data = nbt_tags.unpack(particle[particle.index("{"):])
            particle_data["type"] = miscellaneous.namespace(particle[:particle.index("{")])
        else:
            particle_data["type"] = miscellaneous.namespace(particle)



    # Convert ID based on version
    if pack_version <= 1202:
        for substring in ["minecraft:blockcrack_", "minecraft:blockdust_", "minecraft:iconcrack_"]:
            if substring in particle_data["type"]:
                particle_data["type"] = substring[:len(substring) - 1]

        id_array = tables.PARTICLE_IDS
        if particle_data["type"] in id_array:
            particle_data["type"] = id_array[particle_data["type"]]



    # Update block and item if they are set
    if "block_state" in particle_data:
        block_state = particle_data["block_state"]
        block = blocks.update({
            "id": block_state["Name"],
            "data_value": 0,
            "block_states": block_state["Properties"] if "Properties" in block_state else {},
            "nbt": None,
            "read": False,
        }, pack_version, [])
        block_state["Name"] = block["id"]
        if block["block_states"]:
            block_state["Properties"] = block["block_states"]
        elif "Properties" in block_state:
            del block_state["Properties"]

    if "item" in particle_data:
        item = items.update_from_nbt(cast(items.ItemInputFromNBT, particle_data["item"]), version, issues)

    

    # Handle entity effects
    if pack_version <= 2004:
        if particle_data["type"] == "minecraft:entity_effect":
            particle_data["color"] = nbt_tags.TypeList([
                nbt_tags.TypeFloat(0),
                nbt_tags.TypeFloat(0),
                nbt_tags.TypeFloat(0),
                nbt_tags.TypeFloat(1),
            ])
        elif particle_data["type"] == "minecraft:ambient_entity_effect":
            particle_id = "minecraft:entity_effect"
            particle_data["type"] = particle_id
            particle_data["color"] = nbt_tags.TypeList([
                nbt_tags.TypeFloat(0),
                nbt_tags.TypeFloat(0),
                nbt_tags.TypeFloat(0),
                nbt_tags.TypeFloat(0.5),
            ])



    # Clamp values
    if "scale" in particle_data:
        particle_data["scale"] = nbt_tags.TypeFloat(min(max(particle_data["scale"].value, 0.01), 4.0))



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