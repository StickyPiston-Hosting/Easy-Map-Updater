# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from lib.log import log
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import numeric_ids
from lib.data_pack_files import arguments
from lib.data_pack_files import items
from lib.data_pack_files import tables
from lib import defaults
from lib import utils



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def update_from_command(block: str | dict[str, str], version: int, issues: list[dict[str, str]]) -> str:
    global pack_version
    pack_version = version

    # Initialize parameters
    block_id = "minecraft:air"
    data_value = -1
    block_states = ""
    nbt = ""
    read = False

    # Extract arguments if a dict
    if isinstance(block, dict):
        if "id" in block:
            block_id: str = block["id"]
        if "nbt" in block:
            nbt: str = block["nbt"]
        if "data_value" in block:
            if block["data_value"] != "":
                data_value = block["data_value"]
                if "=" not in data_value:
                    data_value = int(data_value)
        if "read" in block:
            read: bool = block["read"]
    else:
        block_id = block

    # Assign NBT if present in ID
    if "{" in block_id:
        nbt = block_id[block_id.find("{"):]
        block_id = block_id[:block_id.find("{")]

    # Assign block states if present in ID
    if "[" in block_id:
        block_states = block_id[block_id.find("["):]
        block_id = block_id[:block_id.find("[")]

    # Remove blockcrack and blockdust
    for string in ["blockcrack_", "blockdust_"]:
        if string in block_id and block_id[:len(string)] == string:
            block_id = block_id[len(string):]

    # Update block
    new_block: dict[str, str | int | dict | bool | None] = update(
        {
            "id": block_id,
            "data_value": data_value,
            "block_states": unpack_block_states(block_states),
            "nbt": nbt_tags.unpack(nbt),
            "read": read
        },
        pack_version, issues
    )

    # Return block
    if new_block["nbt"]:
        return new_block["id"] + pack_block_states(new_block["block_states"]) + nbt_tags.pack(new_block["nbt"])
    return new_block["id"] + pack_block_states(new_block["block_states"])

def unpack_block_states(block_states: str) -> dict[str, str]:
    if not block_states:
        return {}
    output_block_states: dict[str, str] = {}
    for entry in arguments.parse_with_quotes(block_states[1:], ",", True):
        if "=" in entry:
            output_block_states[utils.unquote(entry.split("=")[0].strip())] = utils.unquote(entry.split("=")[1].strip())
    return output_block_states

def pack_block_states(block_states: dict[str, str]) -> str:
    if not block_states:
        return ""
    output_block_states: list[str] = []
    for entry in block_states:
        output_block_states.append(f"{entry}={block_states[entry]}")
    return f"[{','.join(output_block_states)}]"



def update_from_nbt(block: dict[str, str | dict | nbt_tags.TypeNumeric], version: int, issues: list[dict[str, str]]):
    global pack_version
    pack_version = version

    block_id = None
    data_value = -1
    block_states: dict[str, str] = {}
    nbt = None
    read = False

    # Extract arguments
    block_state_tag = "BlockState"
    if "Block" in block:
        block_id: str | nbt_tags.TypeNumeric = block["Block"]
    if "Data" in block:
        data_value = int(block["Data"].value)
    if "TileEntityData" in block:
        nbt: dict = block["TileEntityData"]
    if "BlockState" in block:
        if "Name" in block["BlockState"]:
            block_id: str | nbt_tags.TypeNumeric = block["BlockState"]["Name"]
        if "Properties" in block["BlockState"]:
            block_states = block["BlockState"]["Properties"]
    if "block_state" in block:
        block_state_tag = "block_state"
        if "Name" in block["block_state"]:
            block_id: str | nbt_tags.TypeNumeric = block["block_state"]["Name"]
        if "Properties" in block["block_state"]:
            block_states = block["block_state"]["Properties"]


    # Update block
    new_block: dict[str, str | int | dict] = update(
        {
            "id": block_id,
            "data_value": data_value,
            "block_states": block_states,
            "nbt": nbt,
            "read": read
        },
        pack_version, issues
    )

    # Return block
    if "Block" in block:
        del block["Block"]
    if "Data" in block:
        del block["Data"]
    block[block_state_tag] = {}
    if "id" in new_block and new_block["id"]:
        block[block_state_tag]["Name"] = new_block["id"]
    if "block_states" in new_block and new_block["block_states"]:
        block[block_state_tag]["Properties"] = new_block["block_states"]
    if "nbt" in new_block and new_block["nbt"]:
        block["TileEntityData"] = new_block["nbt"]
    return block[block_state_tag]



def update(block: dict[str, str | int | dict | bool | None], version: int, issues: list[dict[str, str]]) -> dict[str, str]:
    global pack_version
    pack_version = version

    # Extract arguments
    block_id: str | nbt_tags.TypeNumeric | None = block["id"]
    data_value: str | int = block["data_value"]
    block_states: dict[str, str] = block["block_states"]
    nbt: dict | None = block["nbt"]
    read: bool = block["read"]

    # Convert block ID
    if block_id != None:
        block_id, block_states, nbt = update_block_id(block_id, data_value, block_states, nbt, read, issues)

    # Update NBT
    nbt = nbt_tags.direct_update(nbt, pack_version, issues, "block", block_id)

    return {
        "id": block_id,
        "block_states": block_states,
        "nbt": nbt
    }

def update_block_id(block_id: str | nbt_tags.TypeNumeric, data_value: int | str, block_states: dict[str, str], nbt: dict, read: bool, issues: list[dict[str, str]]) -> tuple[str, dict[str, str]]:
    # Convert if a numeric
    if not isinstance(block_id, str):
        block_id, data_value = numeric_ids.update_block_item(int(block_id.value), data_value)
    elif block_id.isnumeric():
        block_id, data_value = numeric_ids.update_block_item(int(block_id), data_value)

    # Apply namespace to name
    block_id = miscellaneous.namespace(block_id)

    # Convert block ID
    if pack_version <= 809:
        # Handle command block edge case
        if block_id == "minecraft:command_block":
            if read and data_value == -1:
                pass
            elif data_value == -1:
                nbt["powered"] = nbt_tags.TypeByte(0)
            else:
                nbt["powered"] = nbt_tags.TypeByte(1 if data_value == 1 else 0)

    if pack_version <= 1202:
        # Exceptional cases:
        # - Banner (color is stored in NBT)
        # - Bed (color is stored in NBT)
        # - Flower pot (plant is derived from NBT)
        # - Skull (variant is stored in NBT)

        # Blocks that are read with no specifying data value
        if read and data_value == -1:
            id_array = tables.BLOCK_IDS_READ
            if block_id in id_array:
                if "Properties" in id_array[block_id]:
                    block_states = id_array[block_id]["Properties"]
                else:
                    block_states = {}
                block_id = id_array[block_id]["Name"]

            if "#tag_replacements" in block_id:
                log("Tag replacement data pack must be created!")

        # Default assignment values, not necessarily data value 0
        elif data_value == -1:
            id_array = tables.BLOCK_IDS_DEFAULT
            if block_id in id_array:
                if "Properties" in id_array[block_id]:
                    block_states = id_array[block_id]["Properties"]
                else:
                    block_states = {}
                block_id = id_array[block_id]["Name"]

        # Blocks specified with explicit block states
        elif type(data_value).__name__ == "str":
            block_states = unpack_block_states(f"[{data_value}]")

            id_array = {
                
            }

            if defaults.SEND_WARNINGS:
                log("WARNING: Data values specified as block states are not supported yet!")

        # Blocks specified with explicit data value
        else:
            id_array = tables.BLOCK_IDS_DATA

            if block_id in id_array:
                if "fallback" in id_array[block_id]:
                    fallback = id_array[block_id]["fallback"]
                else:
                    fallback = "default"

                data_array: dict[int, dict[str, str | dict[str, str]]] = id_array[block_id]
                if data_value in data_array:
                    block_id = data_array[data_value]["Name"]
                    if "Properties" in data_array[data_value]:
                        block_states = data_array[data_value]["Properties"]
                    else:
                        block_states = {}
                        
                elif fallback == "previous":
                    data_value_temp = data_value
                    while data_value_temp > 0:
                        data_value_temp -= 1
                        if data_value_temp in data_array:
                            block_id = data_array[data_value_temp]["Name"]
                            if "Properties" in data_array[data_value_temp]:
                                block_states = data_array[data_value_temp]["Properties"]
                            break
                    else:
                        id_array = tables.BLOCK_IDS_DEFAULT
                        if block_id in id_array:
                            if "Properties" in id_array[block_id]:
                                block_states = id_array[block_id]["Properties"]
                            else:
                                block_states = {}
                            block_id = id_array[block_id]["Name"]

                else:
                    id_array = tables.BLOCK_IDS_DEFAULT
                    if block_id in id_array:
                        if "Properties" in id_array[block_id]:
                            block_states = id_array[block_id]["Properties"]
                        else:
                            block_states = {}
                        block_id = id_array[block_id]["Name"]

            if block_id in ["minecraft:white_banner", "minecraft:white_wall_banner"] and nbt != None and "Base" in nbt:
                block_id = f'minecraft:{miscellaneous.color(15-nbt["Base"].value)}{block_id[15:]}'
                del nbt["Base"]

            if block_id == "minecraft:red_bed":
                if nbt != None and "color" in nbt:
                    block_id = f'minecraft:{miscellaneous.color(nbt["color"].value)}_bed'
                    del nbt["color"]
                if read:
                    block_id = "#tag_replacements:bed"
                    log("Tag replacement data pack must be created!")

            if block_id == "minecraft:flower_pot":
                if nbt != None and "Item" in nbt:
                    if "Data" in nbt:
                        flower = items.update_from_command({"id": nbt["Item"], "data_value": nbt["Data"].value}, pack_version, issues)
                        del nbt["Data"]
                    else:
                        flower = items.update_from_command(nbt["Item"], pack_version, issues)
                    del nbt["Item"]
                    if flower != "minecraft:air":
                        block_id = f'minecraft:potted_{flower[10:].split("[")[0]}'
                if read:
                    block_id = "#minecraft:flower_pots"
                    log("Tag replacement data pack must be created!")

            if block_id == "minecraft:skeleton_skull":
                if nbt != None and ("SkullType" in nbt or "Rot" in nbt):
                    if "SkullType" in nbt:
                        id_array = {
                            0: "minecraft:skeleton_skull",
                            1: "minecraft:wither_skeleton_skull",
                            2: "minecraft:zombie_head",
                            3: "minecraft:player_head",
                            4: "minecraft:creeper_head",
                            5: "minecraft:dragon_head"
                        }
                        if nbt["SkullType"].value in id_array:
                            block_id = id_array[nbt["SkullType"].value]
                        del nbt["SkullType"]
                    if "Rot" in nbt:
                        block_states["rotation"] = nbt["Rot"].value
                        del nbt["Rot"]
                if read:
                    block_id = "#tag_replacements:floor_skull"
                    log("Tag replacement data pack must be created!")

            if block_id == "minecraft:skeleton_wall_skull":
                if nbt != None and ("SkullType" in nbt or "Rot" in nbt):
                    if "SkullType" in nbt:
                        id_array = {
                            0: "minecraft:skeleton_wall_skull",
                            1: "minecraft:wither_skeleton_wall_skull",
                            2: "minecraft:zombie_wall_head",
                            3: "minecraft:player_wall_head",
                            4: "minecraft:creeper_wall_head",
                            5: "minecraft:ender_dragon_wall_head"
                        }
                        if nbt["SkullType"].value in id_array:
                            block_id = id_array[nbt["SkullType"].value]
                        del nbt["SkullType"]
                    if "Rot" in nbt:
                        del nbt["Rot"]
                if read:
                    block_id = "#tag_replacements:wall_skull"
                    log("Tag replacement data pack must be created!")

        # Blocks whose data values changed over time
        if pack_version <= 809:
            if block_id == "minecraft:command_block":
                block_states = {}

    if pack_version <= 1302:
        id_array = {
            "minecraft:sign":             "minecraft:oak_sign",
            "minecraft:wall_sign":        "minecraft:oak_wall_sign"
        }
        if block_id in id_array:
            block_id = id_array[block_id]

    if pack_version <= 1502:
        # Handle wall block states
        if block_id in [
            "minecraft:andesite_wall",
            "minecraft:brick_wall",
            "minecraft:cobblestone_wall",
            "minecraft:diorite_wall",
            "minecraft:end_stone_brick_wall",
            "minecraft:granite_wall",
            "minecraft:mossy_cobblestone_wall",
            "minecraft:mossy_stone_brick_wall",
            "minecraft:nether_brick_wall",
            "minecraft:prismarine_wall",
            "minecraft:red_nether_brick_wall",
            "minecraft:red_sandstone_wall",
            "minecraft:sandstone_wall",
            "minecraft:stone_brick_wall"
        ]:
            for block_state in ["north", "south", "east", "west"]:
                if block_state in block_states:
                    if block_states[block_state] == "false":
                        block_states[block_state] = "none"
                    if block_states[block_state] == "true":
                        block_states[block_state] = "low"

    if pack_version <= 1605:
        id_array = {
            "minecraft:grass_path": "minecraft:dirt_path"
        }
        if block_id in id_array:
            block_id = id_array[block_id]

    if pack_version <= 1802:
        id_array = {
            "#minecraft:carpets": "#minecraft:wool_carpets"
        }
        if block_id in id_array:
            block_id = id_array[block_id]

    if pack_version <= 2002:
        id_array = {
            "minecraft:grass": "minecraft:short_grass"
        }
        if block_id in id_array:
            block_id = id_array[block_id]

    return (block_id, block_states, nbt)