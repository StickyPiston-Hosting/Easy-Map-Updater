# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import shutil
from pathlib import Path
from lib.log import log
from lib import finalize



# Initialize variables

PROGRAM_PATH = Path(__file__).parent



# Define functions

def create_pack(world: Path):
    log("Creating attribute reset data pack")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    
    # Create data pack
    data_pack_folder = world / "datapacks"
    data_pack_folder.mkdir(exist_ok=True, parents=True)
    shutil.copy(PROGRAM_PATH / "attribute_reset.zip", data_pack_folder / "attribute_reset.zip")
            
    log("Attribute reset data pack created")

    finalize.insert_data_pack(world, "file/attribute_reset.zip")
    finalize.log_data_packs(world)