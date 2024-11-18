# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from lib.data_pack_files import command_helper
from lib.data_pack_files.command_helpers import teleport_dismount



# Define functions

def handle_motion_modification(command: list[str]) -> str:
    function_call = command_helper.create_function(
        f'execute store success score #success help.value run {" ".join(command[4:])}\n'
        f'tag @s add help.motion_modified\n'
        f'execute if score #success help.value matches 0 run return 0\n'
        f'return 1'
    )
    return f'{" ".join(command[:4])} {function_call}'

def handle_teleport(command: list[str]) -> str:
    # Compute selector and index
    length = len(command)
    selector_index = -1
    if command[0] == "execute":
        if command[1] == "as":
            selector_index = 2
        else:
            selector_index = -1
    elif length == 2:
        selector_index = -1
    elif length == 4:
        selector_index = -1
    
    if selector_index == -1:
        selector = "@s"
    else:
        selector = command[selector_index]
        command[selector_index] = "@s"

    # Modify command using teleport dismount fix
    index = command.index("teleport")
    command_string = " ".join(command[:index]) + teleport_dismount.handle_teleport(command[index:])

    function_call = command_helper.create_function(
        f'execute if entity @s[type=!minecraft:player,tag=help.motion_modified] run data modify storage help:data Motion set from entity @s Motion\n' +
        f'execute store success score #success help.value run {command_string}\n'.replace("as @s ", "").replace(" run execute", "") +
        f'execute if entity @s[type=!minecraft:player,tag=help.motion_modified] run data modify entity @s Motion set from storage help:data Motion\n' +
        f'execute if score #success help.value matches 0 run return 0\n' +
        f'return 1'
    )
    return f'execute as {selector} run {function_call}'