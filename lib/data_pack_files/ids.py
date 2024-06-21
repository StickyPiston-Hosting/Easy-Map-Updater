# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from typing import cast
from lib.log import log
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import items
from lib.data_pack_files import blocks
from lib.data_pack_files import entities
from lib.data_pack_files import tables
from lib.data_pack_files.restore_behavior import scoreboard_objective_splitter
from lib import defaults



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def effect(name: int | str | nbt_tags.TypeNumeric, version: int, issues: list[dict[str, str | int]]) -> str:
    global pack_version
    pack_version = version

    if isinstance(name, nbt_tags.TypeNumeric):
        name = int(name.value)

    if isinstance(name, str) and name.isnumeric():
        name = int(name)
        
    if isinstance(name, int):
        id_array = tables.EFFECT_IDS
        if name in id_array:
            name = id_array[name]
        else:
            name = "minecraft:speed"
    
    return miscellaneous.namespace(name)

def enchantment(name: str | int | nbt_tags.TypeNumeric, version: int, issues: list[dict[str, str | int]]) -> str:
    global pack_version
    pack_version = version

    # Convert if a numeric
    if isinstance(name, nbt_tags.TypeNumeric):
        name = int(name.value)

    # Convert if a number
    if isinstance(name, int):
        id_array = tables.ENCHANTMENT_IDS
        if name in id_array:
            name = id_array[name]
        else:
            name = "minecraft:protection"

    # Update enchantment names for 1.20.5
    id_array = {
        "minecraft:sweeping": "minecraft:sweeping_edge"
    }
    if name in id_array:
        name = id_array[name]

    return miscellaneous.namespace(name)

def particle(particle: str, version: int, issues: list[dict[str, str | int]]) -> str:
    global pack_version
    pack_version = version

    particle = miscellaneous.namespace(particle)

    # Convert ID based on version
    if pack_version <= 1202:
        for substring in ["minecraft:blockcrack_", "minecraft:blockdust_", "minecraft:iconcrack_"]:
            if substring in particle:
                particle = substring[:len(substring) - 1]

        id_array = tables.PARTICLE_IDS
        if particle in id_array:
            particle = id_array[particle]

    return particle

def scoreboard_objective_criteria(objective: dict[str, str], version: int, issues: list[dict[str, str | int]]) -> str:
    global pack_version
    pack_version = version

    name = objective["name"]
    criteria = objective["criteria"]

    if pack_version <= 1202:
        if criteria.split(".")[0] == "stat":
            block_stats = {
                "mineBlock": "minecraft.mined:minecraft."
            }
            item_stats = {
                "breakItem": "minecraft.broken:minecraft.",
                "craftItem": "minecraft.crafted:minecraft.",
                "drop": "minecraft.dropped:minecraft.",
                "useItem": "minecraft.used:minecraft."
            }
            entity_stats = {
                "entityKilledBy": "minecraft.killed_by:minecraft.",
                "killEntity": "minecraft.killed:minecraft."
            }

            stat = criteria.split(".")[1]
            object_id = ":".join(criteria.split(".")[2:])

            if stat in block_stats:
                block_id = cast(str, blocks.update({"id": object_id, "data_value": -1, "block_states": {}, "nbt": {}, "read": True}, pack_version, issues)["id"])
                if block_id in tables.BLOCK_TAG_REPLACEMENTS:
                    scoreboard_objective_splitter.insert_objective(name, block_stats[stat], tables.BLOCK_TAG_REPLACEMENTS[block_id])
                    return "dummy"
                return block_stats[stat] + block_id[10:]
            
            elif stat in item_stats:
                item_id = cast(str, items.update({"id": object_id, "data_value": -1, "components": {}, "nbt": {}, "read": True}, pack_version, issues)["id"])
                if item_id in tables.ITEM_TAG_REPLACEMENTS:
                    scoreboard_objective_splitter.insert_objective(name, item_stats[stat], tables.ITEM_TAG_REPLACEMENTS[item_id])
                    return "dummy"
                return item_stats[stat] + item_id[10:]

            elif stat in entity_stats:
                return entity_stats[stat] + entities.update(object_id, pack_version, issues)[10:]
            
            else:
                id_array = tables.SCOREBOARD_STATISTIC_IDS
                if stat in id_array:
                    return "minecraft.custom:minecraft." + id_array[stat]

            

            if stat == "mineBlock":
                return "minecraft.mined:minecraft."     + blocks.update_from_command(object_id, pack_version, issues)[10:]
            elif stat == "breakItem":
                return "minecraft.broken:minecraft."    + items.update_from_command( object_id, pack_version, issues)[10:]
            elif stat == "craftItem":
                return "minecraft.crafted:minecraft."   + items.update_from_command( object_id, pack_version, issues)[10:]
            elif stat == "drop":
                return "minecraft.dropped:minecraft."   + items.update_from_command( object_id, pack_version, issues)[10:]
            elif stat == "useItem":
                return "minecraft.used:minecraft."      + items.update_from_command( object_id, pack_version, issues)[10:]
            elif stat == "entityKilledBy":
                return "minecraft.killed_by:minecraft." + entities.update(           object_id, pack_version, issues)[10:]
            elif stat == "killEntity":
                return "minecraft.killed:minecraft."    + entities.update(           object_id, pack_version, issues)[10:]
            else:
                id_array = tables.SCOREBOARD_STATISTIC_IDS
                if stat in id_array:
                    return "minecraft.custom:minecraft." + id_array[stat]
        else:
            return criteria

    return criteria

def sound_event(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    global pack_version
    pack_version = version

    # Apply namespace
    name = miscellaneous.namespace(name)

    # Convert ID based on version
    if pack_version <= 809:
        id_array = tables.SOUND_EVENTS_1_8
        if name in id_array:
            name = id_array[name]
    if pack_version <= 1202:
        id_array = tables.SOUND_EVENTS_1_12
        if name in id_array:
            name = id_array[name]

    return name