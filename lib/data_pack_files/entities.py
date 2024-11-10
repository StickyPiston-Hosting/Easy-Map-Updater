# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from typing import cast
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import tables
from lib import defaults



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def update(entity: str | dict[str, str], version: int, issues: list[dict[str, str | int]]) -> str:
    # Assign version
    global pack_version
    pack_version = version

    # Initialize parameters
    entity_id = "minecraft:pig"
    nbt = ""

    # Extract arguments if a dict
    if isinstance(entity, dict):
        if "id" in entity:
            entity_id: str = entity["id"]
        if "nbt" in entity:
            nbt: str = entity["nbt"]
    else:
        entity_id = entity

    boat_type = "oak"
    if nbt != "":
        unpacked_nbt: dict = cast(dict, nbt_tags.unpack(nbt))
        
        # Extract out true entity ID from NBT if "Riding" tag is present
        if "Riding" in unpacked_nbt:
            entity_id = extract_riding_id(unpacked_nbt["Riding"])

        # Extract boat type if it is defined
        if "Type" in unpacked_nbt:
            boat_type = cast(str, unpacked_nbt["Type"])

    entity_id = miscellaneous.namespace(entity_id)

    if pack_version <= 1202:
        id_array = tables.ENTITY_IDS
        if entity_id in id_array:
            entity_id = id_array[entity_id]

    if pack_version <= 1502:
        id_array = {
            "minecraft:zombie_pigman": "minecraft:zombified_piglin"
        }
        if entity_id in id_array:
            entity_id = id_array[entity_id]
        
    # In 1.21.2, boat IDs were split up
    if pack_version <= 2101:
        if entity_id == "minecraft:boat":
            id_array = tables.BOAT_TYPES
            if boat_type in id_array:
                entity_id = id_array[boat_type]

        if entity_id == "minecraft:chest_boat":
            id_array = tables.CHEST_BOAT_TYPES
            if boat_type in id_array:
                entity_id = id_array[boat_type]

    return entity_id.lower()

def extract_riding_id(nbt: dict) -> str:
    if "Riding" in nbt:
        return extract_riding_id(nbt["Riding"])
    elif "id" in nbt:
        return nbt["id"]
    else:
        return "minecraft:pig"