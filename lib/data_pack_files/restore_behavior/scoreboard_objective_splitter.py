# Import things

from pathlib import Path
import json
from lib.log import log
from lib import defaults
from lib import finalize



# Initialize variables

PROGRAM_PATH = Path(__file__).parent
EASY_MAP_UPDATER_PATH = PROGRAM_PATH.parent.parent.parent
MINECRAFT_PATH = EASY_MAP_UPDATER_PATH.parent
PACK_FORMAT = defaults.DATA_PACK_FORMAT



# Define functions

def insert_objective(name: str, criteria: str, id_list: list[str]):
    # Extract world name
    with (EASY_MAP_UPDATER_PATH / "options.json").open("r", encoding="utf-8") as file:
        options: dict[str, str] = json.load(file)
    world = MINECRAFT_PATH / "saves" / options["map_name"]

    if not world.exists():
        log("ERROR: World does not exist!")
        return

    # Create data pack if it doesn't exist
    data_pack_path = world / "datapacks" / "scoreboard_objective_splitter"
    if not data_pack_path.exists():
        create_data_pack(world, data_pack_path)

    # Insert commands into functions
    function_path = data_pack_path / "data" / "objective" / "functions"

    with (function_path / "load.mcfunction").open("r", encoding="utf-8") as file:
        contents = file.read().split("\n")
    for object_id in id_list:
        command = f'scoreboard objectives add OBJ.{criteria.split(":")[0][10:]}.{object_id[10:]} {criteria}{object_id[10:]}'
        if command not in contents:
            contents.append(command)
    with (function_path / "load.mcfunction").open("w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(contents))

    with (function_path / "push_scores.mcfunction").open("r", encoding="utf-8") as file:
        contents = file.read().split("\n")
    for object_id in id_list:
        command = f'execute as @a[scores={{OBJ.{criteria.split(":")[0][10:]}.{object_id[10:]}=1..}}] run scoreboard players operation @s {name} += @s OBJ.{criteria.split(":")[0][10:]}.{object_id[10:]}'
        if command not in contents:
            contents.append(command)
    with (function_path / "push_scores.mcfunction").open("w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(contents))

    with (function_path / "reset_scores.mcfunction").open("r", encoding="utf-8") as file:
        contents = file.read().split("\n")
    for object_id in id_list:
        command = f'scoreboard players set @a OBJ.{criteria.split(":")[0][10:]}.{object_id[10:]} 0'
        if command not in contents:
            contents.append(command)
    with (function_path / "reset_scores.mcfunction").open("w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(contents))



def create_data_pack(world: Path, data_pack_path: Path):
    data_pack_path.mkdir(exist_ok=True, parents=True)
    with (data_pack_path / "pack.mcmeta").open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            {
        	    "pack": {
        	    	"pack_format": PACK_FORMAT,
        	    	"description": "Adds scoreboard objectives to handle block and item IDs splitting."
        	    }
            },
            file,
            indent=4
        )
        
    function_tag_path = data_pack_path / "data" / "minecraft" / "tags" / "functions"
    function_tag_path.mkdir(exist_ok=True, parents=True)
    with (function_tag_path / "load.json").open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            {
                "values": [
                    "objective:load"
                ]
            },
            file,
            indent=4
        )
    with (function_tag_path / "tick.json").open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            {
                "values": [
                    "objective:tick"
                ]
            },
            file,
            indent=4
        )

    function_path = data_pack_path / "data" / "objective" / "functions"
    function_path.mkdir(exist_ok=True, parents=True)
    for function_name in ["load", "push_scores", "reset_scores"]:
        with (function_path / f"{function_name}.mcfunction").open("w", encoding="utf-8", newline="\n") as file:
            file.write("")
    with (function_path / "tick.mcfunction").open("w", encoding="utf-8", newline="\n") as file:
        file.write(
            "function objective:push_scores\n"
            "function objective:reset_scores"
        )

    finalize.log_data_packs(world)