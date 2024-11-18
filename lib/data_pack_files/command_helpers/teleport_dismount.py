# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from lib.data_pack_files import command_helper



# Define functions

def handle_teleport(command: list[str]) -> str:
    function_call = command_helper.create_function(
        f'scoreboard players set #rotate help.value 0\n'
        f'execute if entity @s[type=!minecraft:player] on vehicle run scoreboard players set #rotate help.value 1\n'
        f'execute if score #rotate help.value matches 0 store success score #success help.value run teleport @s {" ".join(command[2:])}\n'
        f'execute if score #rotate help.value matches 1 store success score #success help.value run rotate @s {" ".join(command[5:])}\n'
        f'execute if score #success help.value matches 0 run return 0\n'
        f'return 1'
    )
    return f'execute as {command[1]} run {function_call}'