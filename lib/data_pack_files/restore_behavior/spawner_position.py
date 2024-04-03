# Import things

import json
from pathlib import Path
from lib.log import log
from lib import defaults
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

    with (data_pack_path / "pack.mcmeta").open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            {
            	"pack": {
            		"pack_format": PACK_FORMAT,
            		"description": "Teleports freshly-spawned mobs to their encoded positions."
            	}
            },
            file,
            indent=4
        )

    tag_path = data_pack_path / "data" / "minecraft" / "tags" / "functions"
    tag_path.mkdir(exist_ok=True, parents=True)

    with (tag_path / "tick.json").open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            {
                "values": [
                    "spawner_position:tick"
                ]
            },
            file,
            indent=4
        )

    function_path = data_pack_path / "data" / "spawner_position" / "functions" / "tick.mcfunction"
    function_path.parent.mkdir(exist_ok=True, parents=True)

    contents: list[str] = []
    if function_path.exists():
        with function_path.open("r", encoding="utf-8") as file:
            contents = file.read().split("\n")
    
    for command in spawner_position_list:
        if command not in contents:
            contents.append(command)

    with function_path.open("w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(contents))

    log("Spawner position data pack created")

    finalize.log_data_packs(world)