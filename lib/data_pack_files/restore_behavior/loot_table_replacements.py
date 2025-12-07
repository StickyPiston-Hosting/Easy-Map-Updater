# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from typing import cast
from pathlib import Path
from lib.log import log
from lib import defaults
from lib import utils
from lib import finalize



# Initialize variables

pack_version = defaults.PACK_VERSION
PACK_FORMAT = defaults.DATA_PACK_FORMAT



# Define functions

def create_pack(world: Path):
    log("Creating loot table replacements data pack")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return

    # Create data pack
    data_pack_path = world / "datapacks" / "loot_table_replacements"
    if data_pack_path.exists():
        log("Loot table replacements data pack already exists")
        return
    data_pack_path.mkdir(exist_ok=True, parents=True)

    utils.safe_file_write(data_pack_path / "pack.mcmeta",
        json.dumps(
            {
            	"pack": {
            		"min_format": PACK_FORMAT,
            		"max_format": PACK_FORMAT,
            		"description": "Adds loot tables which were removed from the game."
            	}
            },
            indent=4
        )
    )

    # Create loot tables
    folder_path = data_pack_path / "data" / "loot_table_replacements" / "loot_table"
    folder_path.mkdir(exist_ok=True, parents=True)

    with (folder_path / "empty.json").open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            { "type": "minecraft:empty" },
            file
        )


    log("Loot table replacements data pack created")

    finalize.insert_data_pack(world, "file/loot_table_replacements")
    finalize.log_data_packs(world)