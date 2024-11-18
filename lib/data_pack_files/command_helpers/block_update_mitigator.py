# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from lib.data_pack_files import arguments
from lib.data_pack_files import command_helper



# Define functions

def handle_comparator_setblock(command: list[str]) -> str:
    # Extract blockstates from comparator
    states = {
        "facing": "north",
        "powered": "false"
    }
    if "[" in command[4]:
        block_states = arguments.parse(command[4].split("]")[0].split("[")[1], ",", False)
        for block_state in block_states:
            state_name = block_state.split("=")[0]
            if state_name in states:
                states[state_name] = block_state.split("=")[1]

    offset = "~ ~ ~"
    if states["facing"] == "east":
        offset = "~1 ~ ~"
    if states["facing"] == "west":
        offset = "~-1 ~ ~"
    if states["facing"] == "south":
        offset = "~ ~ ~1"
    if states["facing"] == "north":
        offset = "~ ~ ~-1"

    if states["powered"] == "false":
        return command_helper.create_function(
            f'execute positioned {command[1]} {command[2]} {command[3]} positioned {offset} if block ~ ~ ~ minecraft:command_block run data merge block ~ ~ ~ {{SuccessCount:0}}\n'
            f'execute positioned {command[1]} {command[2]} {command[3]} positioned {offset} if block ~ ~ ~ minecraft:chain_command_block run data merge block ~ ~ ~ {{SuccessCount:0}}\n'
            f'execute positioned {command[1]} {command[2]} {command[3]} positioned {offset} if block ~ ~ ~ minecraft:repeating_command_block run data merge block ~ ~ ~ {{SuccessCount:0}}\n'
            f'return run {" ".join(command)}'
        )
    else:
        return " ".join(command)
    


def handle_clean_clone(command: list[str]) -> str:
    return command_helper.create_function(
        f'execute store result score #do_tile_drops help.value run gamerule doTileDrops\n'
        f'gamerule doTileDrops false\n'
        f'execute store success score #success help.value run {" ".join(command)}\n'
        f'execute if score #do_tile_drops help.value matches 1 run gamerule doTileDrops true\n'
        f'execute if score #success help.value matches 0 run return 0\n'
        f'return 1'
    )