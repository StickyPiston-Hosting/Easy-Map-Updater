# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import shutil
from pathlib import Path
from lib.log import log
from lib import finalize
from lib import option_manager



# Initialize variables

# Initialize variables

PROGRAM_PATH = Path(__file__).parent
EASY_MAP_UPDATER_PATH = PROGRAM_PATH.parent.parent.parent
MINECRAFT_PATH = EASY_MAP_UPDATER_PATH.parent



# Define functions

def fix_locks():
    world = MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    data_pack_path = world / "datapacks" / "lock_fixer.zip"
    if world.exists() and not data_pack_path.exists():
        create_pack(world)

def create_pack(world: Path):
    log("Creating lock fixer data pack")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    
    # Create data pack
    data_pack_folder = world / "datapacks"
    data_pack_folder.mkdir(exist_ok=True, parents=True)
    shutil.copy(PROGRAM_PATH / "lock_fixer.zip", data_pack_folder / "lock_fixer.zip")
            
    log("Lock fixer data pack created")

    finalize.insert_data_pack(world, "file/lock_fixer.zip")
    finalize.log_data_packs(world)