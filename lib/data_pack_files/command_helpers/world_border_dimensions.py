# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from lib.data_pack_files import command_helper



# Define functions

def handle_world_border_commands(command: list[str], is_macro: bool) -> str:
    return command_helper.create_function(
        f'execute in minecraft:the_nether run {" ".join(command)}\n'
        f'execute in minecraft:the_end run {" ".join(command)}\n'
        f'return run execute in minecraft:overworld run {" ".join(command)}',
        is_macro
    )