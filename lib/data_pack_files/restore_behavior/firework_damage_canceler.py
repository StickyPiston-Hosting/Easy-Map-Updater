# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import shutil
from pathlib import Path
from lib import finalize
from lib import option_manager
from lib.log import log
from lib.data_pack_files import command_helper
from lib.data_pack_files import nbt_tags



# Initialize variables

PROGRAM_PATH = Path(__file__).parent
EASY_MAP_UPDATER_PATH = PROGRAM_PATH.parent.parent.parent
MINECRAFT_PATH = EASY_MAP_UPDATER_PATH.parent



# Define functions

def cancel_damage(command: list[str]) -> str:
    world = MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    data_pack_path = world / "datapacks" / "firework_damage_canceler.zip"
    if world.exists() and not data_pack_path.exists():
        create_pack(world)

    # Get wait time
    wait_time = 0
    if len(command) >= 6 and command[5] and command[5][0] == "{" and "LifeTime" in command[5]:
        firework_nbt = nbt_tags.unpack(command[5])
        if "LifeTime" in firework_nbt:
            wait_time: int = firework_nbt["LifeTime"].value

    # Get position
    position = "~ ~ ~"
    if len(command) >= 5:
        position = " ".join(command[2:5])

    return command_helper.create_function(
        f'scoreboard players set #wait_time firework.value {min(wait_time, 60)}\n'
        f'execute positioned {position} run function firework:spawn/pre\n'
        f'execute store success score #success help.value run {" ".join(command)}\n'
        f'execute positioned {position} run function firework:spawn/post\n'
        f'execute if score #success help.value matches 0 run return 0\n'
        f'return 1'
    )

def create_pack(world: Path):
    log("Creating firework damage canceler data pack")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    
    # Create data pack
    data_pack_folder = world / "datapacks"
    data_pack_folder.mkdir(exist_ok=True, parents=True)
    shutil.copy(PROGRAM_PATH / "firework_damage_canceler.zip", data_pack_folder / "firework_damage_canceler.zip")
            
    log("Firework damage canceler data pack created")

    finalize.insert_data_pack(world, "file/firework_damage_canceler.zip")
    finalize.log_data_packs(world)