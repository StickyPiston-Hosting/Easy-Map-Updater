# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
import hashlib
from pathlib import Path
from lib.log import log
from lib import defaults



# Initialize variables

PACK_FORMAT = defaults.DATA_PACK_FORMAT
PROGRAM_PATH = Path(__file__).parent
EASY_MAP_UPDATER_PATH = PROGRAM_PATH.parent.parent
MINECRAFT_PATH = EASY_MAP_UPDATER_PATH.parent



# Define functions

def create_function(commands: str) -> str:
    if defaults.DEBUG_MODE:
        log("Command block helper data pack was modified")

    # Prepare data pack path
    file_path = EASY_MAP_UPDATER_PATH / "options.json"
    with file_path.open("r", encoding="utf-8") as file:
        contents: dict[str, str] = json.load(file)
    data_pack_path = MINECRAFT_PATH / "saves" / contents["map_name"] / "datapacks" / "command_block_helper"
    data_pack_path.mkdir(exist_ok=True, parents=True)

    # Prepare pack.mcmeta
    with (data_pack_path / "pack.mcmeta").open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            {
            	"pack": {
            		"pack_format": PACK_FORMAT,
            		"description": "Adds functions which are useful for emulating old command block behavior."
            	}
            },
            file,
            indent=4
        )

    # Prepare load function
    file_path = data_pack_path / "data" / "minecraft" / "tags" / "functions" / "load.json"
    file_path.parent.mkdir(exist_ok=True, parents=True)
    with file_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            {
                "values": [
                    "help:load"
                ]
            },
            file,
            indent=4
        )
    file_path = data_pack_path / "data" / "help" / "functions" / "load.mcfunction"
    file_path.parent.mkdir(exist_ok=True, parents=True)
    with file_path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(
            "# Create scoreboard objectives\n\n"
            "scoreboard objectives add help.value dummy"
        )

    # Prepare tick function
    file_path = data_pack_path / "data" / "minecraft" / "tags" / "functions" / "tick.json"
    file_path.parent.mkdir(exist_ok=True, parents=True)
    with file_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            {
                "values": [
                    "help:tick"
                ]
            },
            file,
            indent=4
        )
    file_path = data_pack_path / "data" / "help" / "functions" / "tick.mcfunction"
    file_path.parent.mkdir(exist_ok=True, parents=True)
    with file_path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(
            "# Remove motion modified tag\n\n"
            "tag @e remove help.motion_modified"
        )

    # Create function
    function_name = hashlib.sha256(commands.encode("utf-8")).hexdigest()
    function_path = data_pack_path / "data" / "help" / "functions" / f"{function_name}.mcfunction"
    function_path.parent.mkdir(exist_ok=True, parents=True)
    with function_path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(commands)

    return f"function help:{function_name}COMMAND_BLOCK_HELPER"