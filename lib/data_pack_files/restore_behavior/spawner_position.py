# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from lib.log import log
from lib import defaults
from lib import utils
from lib import finalize



# Initialize variables

pack_version = defaults.PACK_VERSION
PACK_FORMAT = defaults.DATA_PACK_FORMAT



# Define functions

def create_pack(world: Path, spawner_position_list: list[str]):
    log("Creating spawner position data pack")

    if not world.exists():
        log("ERROR: World does not exist!")
        return

    # Create data pack
    data_pack_path = world / "datapacks" / "spawner_position"
    data_pack_path.mkdir(exist_ok=True, parents=True)

    utils.safe_file_write(data_pack_path / "pack.mcmeta",
        json.dumps(
            {
            	"pack": {
            		"min_format": PACK_FORMAT,
            		"max_format": PACK_FORMAT,
            		"description": "Teleports freshly-spawned mobs to their encoded positions."
            	}
            },
            indent=4
        )
    )

    tag_path = data_pack_path / "data" / "minecraft" / "tags" / "function"
    tag_path.mkdir(exist_ok=True, parents=True)

    utils.safe_file_write(tag_path / "tick.json",
        json.dumps(
            {
                "values": [
                    "spawner_position:tick"
                ]
            },
            indent=4
        )
    )

    function_path = data_pack_path / "data" / "spawner_position" / "function" / "tick.mcfunction"
    function_path.parent.mkdir(exist_ok=True, parents=True)

    contents: list[str] = []
    if function_path.exists():
        contents = utils.safe_file_read(function_path).split("\n")
    
    for command in spawner_position_list:
        if command not in contents:
            contents.append(command)

    utils.safe_file_write(function_path, "\n".join(contents))

    log("Spawner position data pack created")

    finalize.insert_data_pack(world, "file/spawner_position.zip")
    finalize.log_data_packs(world)