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

SPECIAL_EFFECTS = [
    "minecraft:levitation",
    "minecraft:jump_boost",
    "minecraft:mining_fatigue",
]



# Define functions

def add_effect(command: list[str]) -> str:
    check_pack_creation()

    effect = command[3].split(":")[1]

    return command_helper.create_function(
        f'{" ".join(command)}\n'
        f'execute as {command[2]} if entity @s[type=minecraft:player,predicate=effect:{effect}] run function effect:{effect}/check\n'
        f'return 1'
    )

def remove_effect(command: list[str]) -> str:
    check_pack_creation()

    effect = command[3].split(":")[1]

    return command_helper.create_function(
        f'{" ".join(command)}\n'
        f'execute as {command[2]} if entity @s[type=minecraft:player] unless score @s effect.{effect}_duration matches 0 run function effect:{effect}/remove\n'
        f'return 1'
    )

def remove_all_effects(command: list[str]) -> str:
    check_pack_creation()

    return command_helper.create_function(
        f'{" ".join(command)}\n'
        f'execute as {command[2] if len(command) >= 3 else "@s"} if entity @s[type=minecraft:player] run function effect:remove_all\n'
        f'return 1'
    )

def check_pack_creation():
    world = MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    data_pack_path = world / "datapacks" / "effect_overflow.zip"
    data_pack_path.parent.mkdir(exist_ok=True, parents=True)
    if not data_pack_path.exists():
        create_pack(world)

def create_pack(world: Path):
    log("Creating effect overflow data pack")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    
    # Create data pack
    data_pack_folder = world / "datapacks"
    data_pack_folder.mkdir(exist_ok=True, parents=True)
    shutil.copy(PROGRAM_PATH / "effect_overflow.zip", data_pack_folder / "effect_overflow.zip")
            
    log("Effect overflow data pack created")

    finalize.insert_data_pack(world, "file/effect_overflow.zip")
    finalize.log_data_packs(world)