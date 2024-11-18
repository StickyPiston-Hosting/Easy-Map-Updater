# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from lib.data_pack_files import command_helper
from lib.data_pack_files import blocks



# Define functions

def handle_doors(command: list[str]) -> str:
    # Extract block states
    block = command[4].split("{")[0]
    if "[" in block:
        block_id = block[:block.find("[")]
        block_states = blocks.unpack_block_states(block[block.find("["):])
    else:
        block_id = block
        block_states: dict[str, str] = {}
    half = block_states["half"] if "half" in block_states else "lower"
    offset = "1" if half == "lower" else "-1"
    block_states["half"] = "upper" if half == "lower" else "lower"

    return command_helper.create_function(
        f'execute store result score #boolean help.value if block {command[1]} {command[2]} {command[3]} {block_id}[half={half}]\n'

        f'execute if score #boolean help.value matches 1 positioned {command[1]} {command[2]} {command[3]} run fill ~ ~ ~ ~ ~{offset} ~ minecraft:air\n'
        f'execute if score #boolean help.value matches 1 positioned {command[1]} {command[2]} {command[3]} run setblock ~ ~{offset} ~ {block_id}{blocks.pack_block_states(block_states)}\n'

        f'return run {" ".join(command)}'
    )