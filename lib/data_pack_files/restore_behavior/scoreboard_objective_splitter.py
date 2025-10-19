# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from pathlib import Path
import json
from lib.log import log
from lib import defaults
from lib import utils
from lib import finalize
from lib import option_manager



# Initialize variables

PROGRAM_PATH = Path(__file__).parent
EASY_MAP_UPDATER_PATH = PROGRAM_PATH.parent.parent.parent
MINECRAFT_PATH = EASY_MAP_UPDATER_PATH.parent
PACK_FORMAT = defaults.DATA_PACK_FORMAT



# Define functions

def insert_objective(name: str, criteria: str, id_list: list[str]):
    # Get world path
    world = MINECRAFT_PATH / "saves" / option_manager.get_map_name()

    if not world.exists():
        log("ERROR: World does not exist!")
        return

    # Create data pack if it doesn't exist
    data_pack_path = world / "datapacks" / "scoreboard_objective_splitter"
    if not data_pack_path.exists():
        create_data_pack(world, data_pack_path)

    # Insert commands into functions
    function_path = data_pack_path / "data" / "objective" / "function"

    contents = utils.safe_file_read(function_path / "load.mcfunction").split("\n")
    for object_id in id_list:
        command = f'scoreboard objectives add OBJ.{criteria.split(":")[0][10:]}.{object_id[10:]} {criteria}{object_id[10:]}'
        if command not in contents:
            contents.append(command)
    utils.safe_file_write(function_path / "load.mcfunction", "\n".join(contents))

    contents = utils.safe_file_read(function_path / "push_scores.mcfunction").split("\n")
    for object_id in id_list:
        command = f'execute as @a[scores={{OBJ.{criteria.split(":")[0][10:]}.{object_id[10:]}=1..}}] run scoreboard players operation @s {name} += @s OBJ.{criteria.split(":")[0][10:]}.{object_id[10:]}'
        if command not in contents:
            contents.append(command)
    utils.safe_file_write(function_path / "push_scores.mcfunction", "\n".join(contents))

    contents = utils.safe_file_read(function_path / "reset_scores.mcfunction").split("\n")
    for object_id in id_list:
        command = f'scoreboard players set @a OBJ.{criteria.split(":")[0][10:]}.{object_id[10:]} 0'
        if command not in contents:
            contents.append(command)
    utils.safe_file_write(function_path / "reset_scores.mcfunction", "\n".join(contents))



def create_data_pack(world: Path, data_pack_path: Path):
    data_pack_path.mkdir(exist_ok=True, parents=True)
    utils.safe_file_write(data_pack_path / "pack.mcmeta",
        json.dumps(
            {
        	    "pack": {
        	    	"min_format": PACK_FORMAT,
        	    	"max_format": PACK_FORMAT,
        	    	"description": "Adds scoreboard objectives to handle block and item IDs splitting."
        	    }
            },
            indent=4
        )
    )
        
    function_tag_path = data_pack_path / "data" / "minecraft" / "tags" / "function"
    function_tag_path.mkdir(exist_ok=True, parents=True)
    utils.safe_file_write(function_tag_path / "load.json",
        json.dumps(
            {
                "values": [
                    "objective:load"
                ]
            },
            indent=4
        )
    )
    utils.safe_file_write(function_tag_path / "tick.json",
        json.dumps(
            {
                "values": [
                    "objective:tick"
                ]
            },
            indent=4
        )
    )

    function_path = data_pack_path / "data" / "objective" / "function"
    function_path.mkdir(exist_ok=True, parents=True)
    for function_name in ["load", "push_scores", "reset_scores"]:
        utils.safe_file_write(function_path / f"{function_name}.mcfunction", "")
    utils.safe_file_write(function_path / "tick.mcfunction",
        "function objective:push_scores\n"
        "function objective:reset_scores"
    )

    finalize.insert_data_pack(world, f"file/{data_pack_path.name}")
    finalize.log_data_packs(world)