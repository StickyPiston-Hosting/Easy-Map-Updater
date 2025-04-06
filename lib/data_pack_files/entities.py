# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from typing import cast
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import tables
from lib.data_pack_files.restore_behavior import tag_replacements
from lib import defaults
from lib import option_manager
import easy_map_updater



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def update(entity: str | dict[str, str | bool], version: int, issues: list[dict[str, str | int]]) -> str:
    # Assign version
    global pack_version
    pack_version = version

    # Initialize parameters
    entity_id = "minecraft:pig"
    nbt = ""
    read = False

    # Extract arguments if a dict
    if isinstance(entity, dict):
        if "id" in entity:
            entity_id = cast(str, entity["id"])
        if "nbt" in entity:
            nbt = cast(str, entity["nbt"])
        if "read" in entity:
            read = cast(bool, entity["read"])
    else:
        entity_id = entity

    boat_type: str | None = None
    item_type: str | None = None
    if nbt != "":
        unpacked_nbt: dict = cast(dict, nbt_tags.unpack(nbt))
        
        # Extract out true entity ID from NBT if "Riding" tag is present
        if "Riding" in unpacked_nbt:
            entity_id = extract_riding_id(unpacked_nbt["Riding"])

        # Extract boat type if it is defined
        if "Type" in unpacked_nbt:
            boat_type = cast(str, unpacked_nbt["Type"])

        # Extract item type if it is defined
        if "Item" in unpacked_nbt and "id" in unpacked_nbt["Item"]:
            item_type = miscellaneous.namespace(unpacked_nbt["Item"]["id"])

    entity_id = miscellaneous.namespace(entity_id)

    if pack_version <= 1202:
        entity_id = entity_id.lower()
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
        if read and boat_type is None:
            if entity_id == "minecraft:boat":
                entity_id = "#minecraft:boats"
            elif entity_id == "minecraft:chest_boat":
                entity_id = "#tag_replacements:chest_boat"
                tag_replacements.create_pack(
                    easy_map_updater.MINECRAFT_PATH / "saves" / option_manager.get_map_name()
                )

        else:
            boat_type = boat_type or "oak"

            if entity_id == "minecraft:boat":
                id_array = tables.BOAT_TYPES
                if boat_type in id_array:
                    entity_id = id_array[boat_type]

            elif entity_id == "minecraft:chest_boat":
                id_array = tables.CHEST_BOAT_TYPES
                if boat_type in id_array:
                    entity_id = id_array[boat_type]

    # In 1.21.5, potions were split into splash potions and lingering potions
    if pack_version <= 2104 and entity_id == "minecraft:potion":
        if read and item_type is None:
            entity_id = "#tag_replacements:potion"
            tag_replacements.create_pack(
                easy_map_updater.MINECRAFT_PATH / "saves" / option_manager.get_map_name()
            )

        else:
            entity_id = "minecraft:lingering_potion" if item_type == "minecraft:lingering_potion" else "minecraft:splash_potion"

    return entity_id.lower()

def extract_riding_id(nbt: dict) -> str:
    if "Riding" in nbt:
        return extract_riding_id(nbt["Riding"])
    elif "id" in nbt:
        return nbt["id"]
    else:
        return "minecraft:pig"