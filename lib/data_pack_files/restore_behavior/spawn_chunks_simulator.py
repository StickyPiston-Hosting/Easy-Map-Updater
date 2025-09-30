# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import shutil
from pathlib import Path
from lib import finalize
from lib import option_manager
from lib.log import log
from lib.data_pack_files import command_helper



# Initialize variables

PROGRAM_PATH = Path(__file__).parent
EASY_MAP_UPDATER_PATH = PROGRAM_PATH.parent.parent.parent
MINECRAFT_PATH = EASY_MAP_UPDATER_PATH.parent



# Define functions

def change_world_spawn(command: list[str], is_macro: bool) -> str:
    check_pack_creation()

    coordinates = f"{
        command[1] if len(command) >= 2 else "~"
    } {
        command[2] if len(command) >= 3 else "~"
    } {
        command[3] if len(command) >= 4 else "~"
    }"

    return command_helper.create_function(
        f"execute positioned {coordinates} summon minecraft:marker run function spawn_chunks:get_chunk_coords\n"
        f"scoreboard players operation #new_spawn_x spawn_chunks.value = #x spawn_chunks.value\n"
        f"scoreboard players operation #new_spawn_z spawn_chunks.value = #z spawn_chunks.value\n"
        f"execute store result score #new_radius spawn_chunks.value run data get storage spawn_chunks:data spawn.radius\n"
        f"execute if score #in_overworld spawn_chunks.value matches 1 run function spawn_chunks:spawn/update\n"
        f"return run {" ".join(command)}",
        is_macro
    )

def change_spawn_chunks_radius(command: list[str], is_macro: bool) -> str:
    check_pack_creation()

    radius = command[2] if len(command) >= 3 else "2"

    return command_helper.create_function(
        f"scoreboard players set #new_radius spawn_chunks.value {radius}\n"
        f"execute store result score #new_spawn_x spawn_chunks.value run data get storage spawn_chunks:data spawn.x\n"
        f"execute store result score #new_spawn_z spawn_chunks.value run data get storage spawn_chunks:data spawn.z\n"
        f"execute if score #in_overworld spawn_chunks.value matches 1 run function spawn_chunks:spawn/update\n"
        f"return 1",
        is_macro
    )

def add_forceloaded_chunks(command: list[str], is_macro: bool) -> str:
    check_pack_creation()

    first_coordinates = [
        command[2] if len(command) >= 3 else "~",
        command[3] if len(command) >= 4 else "~"
    ]
    second_coordinates = [
        command[4] if len(command) >= 5 else "~",
        command[5] if len(command) >= 6 else "~"
    ]

    return command_helper.create_function(
        f"execute positioned {first_coordinates[0]} ~ {first_coordinates[1]} summon minecraft:marker run function spawn_chunks:get_chunk_coords\n"
        f"scoreboard players operation #start_x spawn_chunks.value = #x spawn_chunks.value\n"
        f"scoreboard players operation #start_z spawn_chunks.value = #z spawn_chunks.value\n"
        f"execute positioned {second_coordinates[0]} ~ {second_coordinates[1]} summon minecraft:marker run function spawn_chunks:get_chunk_coords\n"
        f"scoreboard players operation #end_x spawn_chunks.value = #x spawn_chunks.value\n"
        f"scoreboard players operation #end_z spawn_chunks.value = #z spawn_chunks.value\n"
        f"execute if score #start_x spawn_chunks.value > #end_x spawn_chunks.value run scoreboard players operation #start_x spawn_chunks.value >< #end_x spawn_chunks.value\n"
        f"execute if score #start_z spawn_chunks.value > #end_z spawn_chunks.value run scoreboard players operation #start_z spawn_chunks.value >< #end_z spawn_chunks.value\n"
        f"execute if score #in_overworld spawn_chunks.value matches 1 run function spawn_chunks:forceload/add\n"
        f"return run {" ".join(command)}",
        is_macro
    )

def remove_forceloaded_chunks(command: list[str], is_macro: bool) -> str:
    check_pack_creation()

    first_coordinates = [
        command[2] if len(command) >= 3 else "~",
        command[3] if len(command) >= 4 else "~"
    ]
    second_coordinates = [
        command[4] if len(command) >= 5 else "~",
        command[5] if len(command) >= 6 else "~"
    ]

    return command_helper.create_function(
        f"execute positioned {first_coordinates[0]} ~ {first_coordinates[1]} summon minecraft:marker run function spawn_chunks:get_chunk_coords\n"
        f"scoreboard players operation #start_x spawn_chunks.value = #x spawn_chunks.value\n"
        f"scoreboard players operation #start_z spawn_chunks.value = #z spawn_chunks.value\n"
        f"execute positioned {second_coordinates[0]} ~ {second_coordinates[1]} summon minecraft:marker run function spawn_chunks:get_chunk_coords\n"
        f"scoreboard players operation #end_x spawn_chunks.value = #x spawn_chunks.value\n"
        f"scoreboard players operation #end_z spawn_chunks.value = #z spawn_chunks.value\n"
        f"execute if score #start_x spawn_chunks.value > #end_x spawn_chunks.value run scoreboard players operation #start_x spawn_chunks.value >< #end_x spawn_chunks.value\n"
        f"execute if score #start_z spawn_chunks.value > #end_z spawn_chunks.value run scoreboard players operation #start_z spawn_chunks.value >< #end_z spawn_chunks.value\n"
        f"execute if score #in_overworld spawn_chunks.value matches 1 run function spawn_chunks:forceload/remove\n"
        f"return run {" ".join(command)}",
        is_macro
    )

def remove_all_forceloaded_chunks(command: list[str], is_macro: bool) -> str:
    check_pack_creation()

    return command_helper.create_function(
        f"execute summon minecraft:marker run function spawn_chunks:get_chunk_coords\n"
        f"execute if score #in_overworld spawn_chunks.value matches 1 run function spawn_chunks:forceload/remove_all\n"
        f"return run {" ".join(command)}",
        is_macro
    )

def check_pack_creation():
    world = MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    data_pack_path = world / "datapacks" / "spawn_chunks_simulator.zip"
    data_pack_path.parent.mkdir(exist_ok=True, parents=True)
    if not data_pack_path.exists():
        create_pack(world)

def create_pack(world: Path):
    log("Creating spawn chunks simulator data pack")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    
    # Create data pack
    data_pack_folder = world / "datapacks"
    data_pack_folder.mkdir(exist_ok=True, parents=True)
    shutil.copy(PROGRAM_PATH / "spawn_chunks_simulator.zip", data_pack_folder / "spawn_chunks_simulator.zip")
            
    log("Spawn chunks simulator data pack created")

    finalize.insert_data_pack(world, "file/spawn_chunks_simulator.zip")
    finalize.log_data_packs(world)