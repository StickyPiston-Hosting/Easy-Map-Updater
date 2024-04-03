# Import things

import shutil
from pathlib import Path
from lib import finalize
from lib.log import log



# Initialize variables

PROGRAM_PATH = Path(__file__).parent



# Define functions

def create_pack(world: Path):
    log("Creating admin kickback data pack")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    
    # Create data pack
    data_pack_folder = world / "datapacks"
    data_pack_folder.mkdir(exist_ok=True, parents=True)
    shutil.copytree(PROGRAM_PATH / "admin_kickback", data_pack_folder / "admin_kickback")
            
    log("Admin kickback data pack created")

    finalize.log_data_packs(world)