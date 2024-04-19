# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import shutil
from pathlib import Path
from lib import finalize
from lib.log import log



# Initialize variables

PROGRAM_PATH = Path(__file__).parent



# Define functions

def create_pack(world: Path):
    log("Creating area effect cloud killer data pack")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    
    # Create data pack
    data_pack_folder = world / "datapacks"
    data_pack_folder.mkdir(exist_ok=True, parents=True)
    shutil.copy(PROGRAM_PATH / "area_effect_cloud_killer.zip", data_pack_folder / "area_effect_cloud_killer.zip")
            
    log("Area effect cloud killer data pack created")

    finalize.log_data_packs(world)