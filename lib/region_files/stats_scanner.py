# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import math
from enum import Enum
from pathlib import Path
from typing import cast, TypedDict
from nbt import nbt as NBT
from nbt import region
from lib.log import log
from lib import utils
from lib.data_pack_files import command
from lib.data_pack_files import arguments
from lib.data_pack_files import target_selectors
from lib.data_pack_files import nbt_tags



# Initialize variables

EXPECTED_STATS = { # GO OVER THESE AND MAKE SURE THAT THEY ARE ACCURATE
    "advancement":     "AffectedEntities",
    "blockdata":       "AffectedBlocks",
    "clear":           "AffectedItems",
    "clone":           "AffectedBlocks",
    "debug":           "SuccessCount",
    "defaultgamemode": "SuccessCount",
    "difficulty":      "SuccessCount",
    "effect":          "AffectedEntities",
    "enchant":         "AffectedEntities",
    "entitydata":      "AffectedEntities",
    "execute":         "SuccessCount",
    "fill":            "AffectedBlocks",
    "function":        "SuccessCount",
    "gamemode":        "AffectedEntities",
    "gamerule":        "SuccessCount",
    "give":            "AffectedEntities",
    "help":            "SuccessCount",
    "kill":            "AffectedEntities",
    "locate":          "SuccessCount",
    "me":              "SuccessCount",
    "msg":             "SuccessCount",
    "particle":        "SuccessCount",
    "playsound":       "SuccessCount",
    "publish":         "SuccessCount",
    "recipe":          "SuccessCount",
    "reload":          "SuccessCount",
    "replaceitem":     "AffectedItems",
    "say":             "SuccessCount",
    "scoreboard":      "SuccessCount",
    "seed":            "QueryResult",
    "setblock":        "AffectedBlocks",
    "setworldspawn":   "SuccessCount",
    "spawnpoint":      "SuccessCount",
    "spreadplayers":   "AffectedEntities",
    "stats":           "SuccessCount",
    "stopsound":       "SuccessCount",
    "summon":          "AffectedEntities",
    "teleport":        "AffectedEntities",
    "tell":            "SuccessCount",
    "tellraw":         "SuccessCount",
    "testfor":         "SuccessCount",
    "testforblock":    "SuccessCount",
    "testforblocks":   "SuccessCount",
    "time":            "QueryResult",
    "title":           "SuccessCount",
    "toggledownfall":  "SuccessCount",
    "tp":              "SuccessCount",
    "trigger":         "SuccessCount",
    "w":               "SuccessCount",
    "weather":         "QueryResult",
    "worldborder":     "SuccessCount",
    "xp":              "SuccessCount"
}

class Discoveries(Enum):
    # Means that there exist blocks which use stats or there are commands to apply stat usage to blocks
    block_stats_used = 1

    # Means that the locations of blocks that use stats are unpredictable
    block_positions_dynamic = 2
    
    # Means that commands are written to command blocks at locations that gather stats
    commands_written_to_sensitive_position = 3
    
    # Means that commands are written to unpredictable locations (guarantees the previous one)
    commands_written_to_arbitrary_position = 4
    
    # Means that there exist entities which use stats or there are commands to apply stat usage to entities
    entity_stats_used = 5
    
    # Means that the types of entities that use stats are unpredictable
    entity_types_dynamic = 6
    
    # Means that either multiple stats are used or the stat which is used is not the natural output of the modern version
    complex_stat_usage = 7



# Define functions

class StatCoordinates(TypedDict):
    stats: dict[tuple[int, int, int], list[str]]
    command_contents: dict[tuple[int, int, int], str]
    command_modified: list[tuple[int, int, int]]

def scan(world: Path):
    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return

    discoveries = {
        Discoveries.block_stats_used: False,
        Discoveries.block_positions_dynamic: False,
        Discoveries.commands_written_to_sensitive_position: False,
        Discoveries.commands_written_to_arbitrary_position: False,
        Discoveries.entity_stats_used: False,
        Discoveries.entity_types_dynamic: False,
        Discoveries.complex_stat_usage: False
    }
    coordinates: StatCoordinates = {
        "stats": {}, # This stores the list of stats associated with each registered coordinate
        "command_contents": {}, # This stores the command name associated with each registered coordinate
        "command_modified": [] # This stores the list of coordinates which have their commands modified
    }
    entity_types: list[str] = []

    log("Scanning world for usage of stats")
    scan_region_folder(discoveries, coordinates, entity_types, world / "region")
    scan_entity_folder(discoveries, coordinates, entity_types, world / "entities")
    scan_region_folder(discoveries, coordinates, entity_types, world / "DIM-1" / "region")
    scan_entity_folder(discoveries, coordinates, entity_types, world / "DIM-1" / "entities")
    scan_region_folder(discoveries, coordinates, entity_types, world / "DIM1" / "region")
    scan_entity_folder(discoveries, coordinates, entity_types, world / "DIM1" / "entities")

    for coordinate in cast(dict[tuple[int, int, int], list[str]], coordinates["stats"]):
        used_stats = utils.deduplicate_list(coordinates["stats"][coordinate])
        if len(used_stats) > 1:
            log(f'Multiple stats on one block found: {coordinate} {used_stats}')
            discoveries[Discoveries.complex_stat_usage] = True
        if coordinate in coordinates["command_contents"] and used_stats[0] != EXPECTED_STATS[coordinates["command_contents"][coordinate]]:
            log(f'Unexpected stat found: {coordinates["command_contents"][coordinate]} => {used_stats[0]}, {coordinate} {used_stats[0]}')
            discoveries[Discoveries.complex_stat_usage] = True
        if coordinate in coordinates["command_modified"]:
            log(f'Modification of a stat-manipulating block found: {coordinate}')
            discoveries[Discoveries.commands_written_to_sensitive_position] = True

    log(
        f'\nResults:\n'
        f'block_stats_used: {discoveries[Discoveries.block_stats_used]}\n'
        f'block_positions_dynamic: {discoveries[Discoveries.block_positions_dynamic]}\n'
        f'commands_written_to_sensitive_position: {discoveries[Discoveries.commands_written_to_sensitive_position]}\n'
        f'commands_written_to_arbitrary_position: {discoveries[Discoveries.commands_written_to_arbitrary_position]}\n'
        f'entity_stats_used: {discoveries[Discoveries.entity_stats_used]}\n'
        f'entity_types_dynamic: {discoveries[Discoveries.entity_types_dynamic]}\n'
        f'complex_stat_usage: {discoveries[Discoveries.complex_stat_usage]}'
    )



def scan_region_folder(discoveries: dict[Discoveries, bool], coordinates: StatCoordinates, entity_types: list[str], folder_path: Path):
    if not folder_path.exists():
        return

    for file_path in folder_path.iterdir():
        scan_region_file(discoveries, coordinates, entity_types, file_path)

def scan_region_file(discoveries: dict[Discoveries, bool], coordinates: StatCoordinates, entity_types: list[str], file_path: Path):
    log(f" Scanning region/{file_path.name}")

    region_file = region.RegionFile(file_path)
    chunk_metadata: region.ChunkMetadata
    for chunk_metadata in region_file.get_metadata():
        try:
            chunk = region_file.get_nbt(chunk_metadata.x, chunk_metadata.z)
        except:
            continue
        if not chunk:
            continue
        if "block_entities" not in chunk:
            continue
        block_entities: NBT.TAG_List = chunk["block_entities"]
        if block_entities == None or len(block_entities) == 0:
            continue

        # Iterate through block entities
        block_entity: NBT.TAG_Compound
        for block_entity in block_entities:
            x: int = block_entity["x"].value
            y: int = block_entity["y"].value
            z: int = block_entity["z"].value

            used_stats: list[str] = []
            if "CommandStats" in block_entity:
                discoveries[Discoveries.block_stats_used] = True
                key: str
                for key in block_entity["CommandStats"]:
                    if key.endswith("Name"):
                        used_stats.append(key[:-4])
                log(f'Block using command stats found: {(x,y,z)} {used_stats}')
                
                if (x,y,z) not in coordinates["stats"]:
                    coordinates["stats"][(x,y,z)] = used_stats
                else:
                    coordinates["stats"][(x,y,z)].extend(used_stats)

            if "Command" in block_entity:
                scan_command(discoveries, coordinates, entity_types, x, y, z, block_entity["Command"].value)



def scan_entity_folder(discoveries: dict[Discoveries, bool], coordinates: StatCoordinates, entity_types: list[str], folder_path: Path):
    if not folder_path.exists():
        return

    for file_path in folder_path.iterdir():
        scan_entity_file(discoveries, coordinates, entity_types, file_path)

def scan_entity_file(discoveries: dict[Discoveries, bool], coordinates: StatCoordinates, entity_types: list[str], file_path: Path):
    log(f" Scanning entities/{file_path.name}")

    region_file = region.RegionFile(file_path)
    chunk_metadata: region.ChunkMetadata
    for chunk_metadata in region_file.get_metadata():
        try:
            chunk = region_file.get_nbt(chunk_metadata.x, chunk_metadata.z)
        except:
            continue
        if not chunk:
            continue
        if "Entities" not in chunk:
            continue
        entities: NBT.TAG_List = chunk["Entities"]
        if entities == None or len(entities) == 0:
            continue

        # Iterate through block entities
        entity: NBT.TAG_Compound
        for entity in entities:
            entity_id: str = entity["id"].value

            used_stats: list[str] = []
            if "CommandStats" in entity:
                discoveries[Discoveries.entity_stats_used] = True
                entity_types.append(entity_id)
                key: str
                for key in entity["CommandStats"]:
                    if key.endswith("Name"):
                        used_stats.append(key[:-4])
                log(f'Entity using command stats found: {entity_id} {used_stats}')



def scan_command(discoveries: dict[Discoveries, bool], coordinates: StatCoordinates, entity_types: list[str], x: int, y: int, z: int, command_string: str):
    # Types of commands to manipulate stats:
    # /stats: directly modifying the stats of a block or entity.
    # /blockdata, /entitydata: indirectly modifying the stats of a block or entity via NBT, requires checking the data.
    # /setblock, /summon: spawning a block or entity with the stats data built-in. (WILL NOT COVER UNTIL A CASE COMES UP)
    # /fill, /clone: manipulating blocks which may copy stats blocks. (WILL NOT COVER UNTIL A CASE COMES UP)

    # Types of commands to manipulate commands:
    # /setblock: placing a command block with a command directly, overwrites the existing command, won't be counted.
    # /blockdata: inserts a command into a command block, doesn't interfere with stats data.

    # Extract command
    argument_list: list[str] = arguments.parse(command.remove_slash(command_string), " ", True)
    if len(argument_list) == 0:
        return
    inside_execute = False
    coordinates["command_contents"][(x,y,z)] = argument_list[0]
    if argument_list[0] == "execute":
        inside_execute = True
        argument_list = extract_command_from_execute(argument_list)
    if len(argument_list) == 0:
        return
    
    # Determine if command manipulates stats
    block_stats_used = False
    entity_stats_used = False
    entity_selector = ""
    block_coords: list[str] = []
    used_stats: list[str] = []
    command_modified = False
    if argument_list[0] == "stats":
        if len(argument_list) >= 7 and argument_list[1] == "block" and argument_list[5] == "set":
            block_stats_used = True
            block_coords = argument_list[2:5]
            used_stats = [argument_list[6]]
        if len(argument_list) >= 5 and argument_list[1] == "entity" and argument_list[3] == "set":
            entity_stats_used = True
            entity_selector = argument_list[2]
            used_stats = [argument_list[4]]
    if argument_list[0] == "blockdata":
        if len(argument_list) >= 5:
            nbt_compound = nbt_tags.unpack(argument_list[4])
            if "CommandStats" in nbt_compound:
                block_stats_used = True
                block_coords = argument_list[1:4]
                for key in nbt_compound["CommandStats"]:
                    if key.endswith("Name"):
                        used_stats.append(key[:-4])
            if "Command" in nbt_compound:
                command_modified = True
                block_coords = argument_list[1:4]
    if argument_list[0] == "entitydata":
        if len(argument_list) >= 3:
            nbt_compound = nbt_tags.unpack(argument_list[2])
            if "CommandStats" in nbt_compound:
                entity_stats_used = True
                entity_selector = argument_list[1]
                for key in nbt_compound["CommandStats"]:
                    if key.endswith("Name"):
                        used_stats.append(key[:-4])


    # Compute coordinates of command
    execution_coords: list[int] = [x, y, z]
    if block_coords:
        for i in range(len(block_coords)):
            coordinate = block_coords[i]
            if coordinate[0] == "~":
                if len(coordinate) > 1:
                    execution_coords[i] += int(math.floor(float(coordinate[1:])))
            else:
                execution_coords[i] = int(math.floor(float(coordinate)))
    coords_tuple = (
        execution_coords[0],
        execution_coords[1],
        execution_coords[2]
    )


    # Apply data from commands to discoveries
    if block_stats_used:
        log(f'Block applying command stats found: {(x,y,z)} => {coords_tuple} {used_stats}')
        discoveries[Discoveries.block_stats_used] = True
        if coords_tuple not in coordinates["stats"]:
            coordinates["stats"][coords_tuple] = used_stats
        else:
            coordinates["stats"][coords_tuple].extend(used_stats)
        if inside_execute:
            log(f'Blocks of arbitrary positions may use stats: {(x,y,z)}')
            discoveries[Discoveries.block_positions_dynamic] = True

    if entity_stats_used:
        log(f'Entity applying command stats found: {(x,y,z)} => {entity_selector} {used_stats}')
        discoveries[Discoveries.entity_stats_used] = True
        if entity_selector[0] == "@":
            # Get types from target selector
            types_used: list[str] = []
            if len(entity_selector) > 2:
                selector_arguments = target_selectors.unpack_arguments(entity_selector[3:-1])
                if "type" in selector_arguments:
                    types_used = cast(list, selector_arguments["type"])

            if entity_selector[1] in ["a", "p"]:
                types_used.append("minecraft:player")
            if entity_selector[1] == "r" and not types_used:
                types_used.append("minecraft:player")

            if not types_used and entity_selector[1] != "s":
                log(f'Entities of arbitrary types may use stats: {(x,y,z)}')
                discoveries[Discoveries.entity_types_dynamic] = True
            if types_used:
                entity_types.extend(types_used)

    if command_modified:
        coordinates["command_modified"].append((execution_coords[0], execution_coords[1], execution_coords[2]))
        if inside_execute:
            log(f'Commands of arbitrary positions may be modified: {(x,y,z)}')
            discoveries[Discoveries.commands_written_to_arbitrary_position] = True


def extract_command_from_execute(argument_list: list[str]) -> list[str]:
    if argument_list[0] != "execute":
        return argument_list
    if len(argument_list) < 6:
        return []
    if argument_list[5] == "detect":
        if len(argument_list) < 12:
            return []
        return extract_command_from_execute(argument_list[11:])
    return extract_command_from_execute(argument_list[5:])