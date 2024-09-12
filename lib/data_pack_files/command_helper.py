# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
import hashlib
from pathlib import Path
from lib.log import log
from lib import defaults
from lib import utils
from lib import option_manager



# Initialize variables

PACK_FORMAT = defaults.DATA_PACK_FORMAT
PROGRAM_PATH = Path(__file__).parent
EASY_MAP_UPDATER_PATH = PROGRAM_PATH.parent.parent
MINECRAFT_PATH = EASY_MAP_UPDATER_PATH.parent



# Define functions

def create_function(commands: str) -> str:
    if defaults.DEBUG_MODE:
        log("Command helper data pack was modified")

    # Prepare data pack path
    data_pack_path = MINECRAFT_PATH / "saves" / option_manager.get_map_name() / "datapacks" / "command_helper"
    data_pack_path.mkdir(exist_ok=True, parents=True)

    # Prepare pack.mcmeta
    utils.safe_file_write(data_pack_path / "pack.mcmeta",
        json.dumps(
            {
            	"pack": {
            		"pack_format": PACK_FORMAT,
            		"description": "Adds functions which are useful for emulating old command behavior."
            	}
            },
            indent=4
        )
    )

    # Prepare load function
    file_path = data_pack_path / "data" / "minecraft" / "tags" / "function" / "load.json"
    file_path.parent.mkdir(exist_ok=True, parents=True)
    utils.safe_file_write(file_path,
        json.dumps(
            {
                "values": [
                    "help:load"
                ]
            },
            indent=4
        )
    )
    file_path = data_pack_path / "data" / "help" / "function" / "load.mcfunction"
    file_path.parent.mkdir(exist_ok=True, parents=True)
    utils.safe_file_write(file_path,
        "# Create scoreboard objectives\n\n"
        "scoreboard objectives add help.value dummy"
    )

    # Prepare tick function
    file_path = data_pack_path / "data" / "minecraft" / "tags" / "function" / "tick.json"
    file_path.parent.mkdir(exist_ok=True, parents=True)
    utils.safe_file_write(file_path,
        json.dumps(
            {
                "values": [
                    "help:tick"
                ]
            },
            indent=4
        )
    )
    file_path = data_pack_path / "data" / "help" / "function" / "tick.mcfunction"
    file_path.parent.mkdir(exist_ok=True, parents=True)
    utils.safe_file_write(file_path,
        "# Remove motion modified tag\n\n"
        "tag @e remove help.motion_modified"
    )

    # Create function
    function_name = hashlib.sha256(commands.encode("utf-8")).hexdigest()
    function_path = data_pack_path / "data" / "help" / "function" / f"{function_name}.mcfunction"
    function_path.parent.mkdir(exist_ok=True, parents=True)
    utils.safe_file_write(function_path, commands)

    return f"function help:{function_name}COMMAND_HELPER"