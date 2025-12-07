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

def create_function(commands: str, is_macro: bool) -> str:
    data_pack_path = prepare_helper_data_pack()
    if data_pack_path is None:
        return f"function help:helper_function_requires_world"

    # Handle macros
    macro_provider = ""
    if is_macro:
        new_commands: list[str] = []
        macro_tokens: list[str] = []

        for command in commands.split("\n"):
            if command.strip().startswith("#"):
                new_commands.append(command)
                continue

            tokens = command.split("$(")
            for token in tokens[1:]:
                if ")" not in token:
                    continue
                macro_tokens.append(token[:token.index(")")])
            if len(tokens) > 1:
                command = "$" + command
            new_commands.append(command)

        if len(macro_tokens) > 0:
            for i in range(len(macro_tokens)):
                macro_tokens[i] = f'{macro_tokens[i]}:$({macro_tokens[i]})'
            macro_provider = " {" + ",".join(macro_tokens) + "}"

        commands = "\n".join(new_commands)

    # Create function
    function_name = hashlib.sha256(commands.encode("utf-8")).hexdigest()
    function_path = data_pack_path / "data" / "help" / "function" / f"{function_name}.mcfunction"
    function_path.parent.mkdir(exist_ok=True, parents=True)
    utils.safe_file_write(function_path, commands)

    return f"function help:{function_name}{macro_provider}COMMAND_HELPER"



def create_predicate(contents: str) -> str:
    data_pack_path = prepare_helper_data_pack()
    if data_pack_path is None:
        return f"help:helper_predicate_requires_world"
    
    # Create predicate
    predicate_name = hashlib.sha256(contents.encode("utf-8")).hexdigest()
    predicate_path = data_pack_path / "data" / "help" / "predicate" / f"{predicate_name}.json"
    predicate_path.parent.mkdir(exist_ok=True, parents=True)
    utils.safe_file_write(predicate_path, contents)

    return f"help:{predicate_name}"



def create_painting_variant(contents: str) -> str:
    data_pack_path = prepare_helper_data_pack()
    if data_pack_path is None:
        return f"help:helper_painting_variant_requires_world"
    
    # Create painting variant
    painting_variant_name = hashlib.sha256(contents.encode("utf-8")).hexdigest()
    painting_variant_path = data_pack_path / "data" / "help" / "painting_variant" / f"{painting_variant_name}.json"
    painting_variant_path.parent.mkdir(exist_ok=True, parents=True)
    utils.safe_file_write(painting_variant_path, contents)

    return f"help:{painting_variant_name}"



def prepare_helper_data_pack() -> Path | None:
    # Prepare data pack path
    world = data_pack_path = MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    if not world.exists():
        return None
    data_pack_path = world / "datapacks" / "command_helper"
    data_pack_path.mkdir(exist_ok=True, parents=True)

    if defaults.DEBUG_MODE:
        log("Command helper data pack was modified")

    # Prepare pack.mcmeta
    utils.safe_file_write(data_pack_path / "pack.mcmeta",
        json.dumps(
            {
            	"pack": {
            		"min_format": PACK_FORMAT,
            		"max_format": PACK_FORMAT,
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
        "scoreboard objectives add help.value dummy\n\n\n\n"
        "# Set constants\n\n"
        "scoreboard players set #50 help.value 50\n"
        "scoreboard players set #1000 help.value 1000\n\n\n\n"
        "# Initialize world border stopwatch\n\n"
        "stopwatch create help:overworld_border\n"
        "stopwatch create help:the_nether_border\n"
        "stopwatch create help:the_end_border\n"
        "execute unless score #overworld_border_before help.value = #overworld_border_before help.value in minecraft:overworld store result score #overworld_border_before help.value run worldborder get\n"
        "execute unless score #overworld_border_after help.value = #overworld_border_after help.value in minecraft:overworld store result score #overworld_border_after help.value run worldborder get\n"
        "execute unless score #overworld_border_duration help.value = #overworld_border_duration help.value run scoreboard players set #overworld_border_duration help.value 0\n"
        "execute unless score #the_nether_border_before help.value = #the_nether_border_before help.value in minecraft:the_nether store result score #the_nether_border_before help.value run worldborder get\n"
        "execute unless score #the_nether_border_after help.value = #the_nether_border_after help.value in minecraft:the_nether store result score #the_nether_border_after help.value run worldborder get\n"
        "execute unless score #the_nether_border_duration help.value = #the_nether_border_duration help.value run scoreboard players set #the_nether_border_duration help.value 0\n"
        "execute unless score #the_end_border_before help.value = #the_end_border_before help.value in minecraft:the_end store result score #the_end_border_before help.value run worldborder get\n"
        "execute unless score #the_end_border_after help.value = #the_end_border_after help.value in minecraft:the_end store result score #the_end_border_after help.value run worldborder get\n"
        "execute unless score #the_end_border_duration help.value = #the_end_border_duration help.value run scoreboard players set #the_end_border_duration help.value 0\n"
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

    return data_pack_path