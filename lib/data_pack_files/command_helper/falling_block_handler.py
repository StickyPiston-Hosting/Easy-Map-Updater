# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from lib.data_pack_files import command_helper



# Define functions

def handle_time_0(command: list[str], entity_nbt: dict) -> str:
    block_id = get_block_id(entity_nbt)
    return command_helper.create_function(
        f'execute store success score #success help.value if block ~ ~ ~ {block_id} run {" ".join(command)}\n'
        f'execute if block ~ ~ ~ {block_id} run setblock ~ ~ ~ minecraft:air\n'
        f'execute if score #success help.value matches 0 run return 0\n'
        f'return 1'
    )

def handle_non_time_0(command: list[str], entity_nbt: dict) -> str:
    block_id = get_block_id(entity_nbt)
    return command_helper.create_function(
        f'execute store success score #success help.value run {" ".join(command)}\n'
        f'execute if block ~ ~ ~ {block_id} run setblock ~ ~ ~ minecraft:air\n'
        f'execute if score #success help.value matches 0 run return 0\n'
        f'return 1'
    )

def get_block_id(entity_nbt: dict) -> str:
    block_id = "minecraft:sand"
    if "BlockState" in entity_nbt and "Name" in entity_nbt["BlockState"]:
        block_id = entity_nbt["BlockState"]["Name"]
    return block_id