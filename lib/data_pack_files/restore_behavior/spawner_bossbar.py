# Import things

import shutil
from pathlib import Path
from lib.log import log
from lib import finalize



# Initialize variables

PROGRAM_PATH = Path(__file__).parent



# Define functions

def create_pack(world: Path):
    log("Creating spawner bossbar data pack")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    
    # Create data pack
    data_pack_folder = world / "datapacks"
    data_pack_folder.mkdir(exist_ok=True, parents=True)
    shutil.copy(PROGRAM_PATH / "spawner_bossbar.zip", data_pack_folder / "spawner_bossbar.zip")


            
    log("Spawner bossbar data pack created")

    finalize.log_data_packs(world)