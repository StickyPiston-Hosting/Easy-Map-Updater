# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from pathlib import Path
from typing import cast
from nbt import nbt as NBT
from lib.log import log
from lib import defaults
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import blocks



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def update(file_path: Path, source_file_path: Path, version: int):
    global pack_version
    pack_version = version

    if version <= 1202:
        log(f"WARNING: Structures are not handled for pre-1.13 yet!")
        return

    try:
        structure_file = NBT.NBTFile(source_file_path)
    except Exception:
        log(f"ERROR: Could not parse structure: {source_file_path.as_posix()}")
        return
    
    structure_file["DataVersion"] = NBT.TAG_Int(defaults.DATA_VERSION)


    if "palette" in structure_file:
        for block in cast(list[NBT.TAG_Compound], structure_file["palette"]):
            update_palette_block(block)

    if "palettes" in structure_file:
        for palette in cast(list[NBT.TAG_List], structure_file["palettes"]):
            for block in cast(list[NBT.TAG_Compound], palette):
                update_palette_block(block)


    if "blocks" in structure_file:
        for block in cast(list[NBT.TAG_Compound], structure_file["blocks"]):
            if "nbt" not in block:
                continue

            state = cast(int, block["state"].value) if "state" in block else 0
            palette = None
            if "palette" in structure_file:
                palette = cast(NBT.TAG_Compound, structure_file["palette"])
            elif "palettes" in structure_file and len(structure_file["palettes"]) > 0:
                palette = cast(NBT.TAG_Compound, structure_file["palettes"][0])
            block_state = None
            if palette is not None and len(palette) > state:
                block_state = cast(NBT.TAG_Compound, palette[state])
            block_id = None
            if block_state is not None and "Name" in block_state:
                block_id = cast(str, block_state["Name"].value)

            block_entity = cast(NBT.TAG_Compound, block["nbt"])
            block_nbt = nbt_tags.convert_from_lib_format_compound(block_entity)
            block_nbt = cast(dict, nbt_tags.direct_update(block_nbt, pack_version, [], "block", block_id or "minecraft:stone"))
            block["nbt"] = nbt_tags.convert_to_lib_format_compound(block_nbt)


    if "entities" in structure_file:
        for entity in cast(list[NBT.TAG_Compound], structure_file["entities"]):
            if "nbt" not in entity:
                continue

            entity_data = cast(NBT.TAG_Compound, entity["nbt"])
            entity_nbt = nbt_tags.convert_from_lib_format_compound(entity_data)
            entity_nbt = cast(dict, nbt_tags.direct_update(entity_nbt, pack_version, [], "entity", entity_nbt["id"] if "id" in entity_nbt else "minecraft:pig"))
            entity["nbt"] = nbt_tags.convert_to_lib_format_compound(entity_nbt)


    file_path.parent.mkdir(parents=True, exist_ok=True)
    structure_file.write_file(file_path)



def update_palette_block(block: NBT.TAG_Compound):
    block_id = cast(str, block["Name"].value) if "Name" in block else "minecraft:air"
    block_states: dict[str, str] = {}
    if "Properties" in block:
        for key in cast(dict[str, NBT.TAG_String], block["Properties"]):
            block_states[key] = block["Properties"][key].value

    updated_block = blocks.update({
        "id": block_id,
        "data_value": 0,
        "block_states": block_states,
        "nbt": None,
        "read": False,
    }, pack_version, [])

    block["Name"] = NBT.TAG_String(updated_block["id"])
    if updated_block["block_states"]:
        block["Properties"] = NBT.TAG_Compound()
        for key in updated_block["block_states"]:
            block["Properties"][key] = NBT.TAG_String(updated_block["block_states"][key])
    elif "Properties" in block:
        del block["Properties"]