# Import things

from lib.data_pack_files import command_block_helper
from lib.data_pack_files import nbt_tags



# Define functions

def handle_fill(command: list[str]) -> str:
    if len(command) <= 8:
        return command_block_helper.create_function(
            f'execute store success score #success help.value run fill {command[1]} {command[2]} {command[3]} {command[4]} {command[5]} {command[6]} minecraft:netherite_block\n'
            f'fill {command[1]} {command[2]} {command[3]} {command[4]} {command[5]} {command[6]} {command[7]}\n'
            f'execute if score #success help.value matches 0 run return 0\n'
            f'return 1'
        )
    if command[8] == "destroy":
        return command_block_helper.create_function(
            f'execute store success score #success help.value run fill {command[1]} {command[2]} {command[3]} {command[4]} {command[5]} {command[6]} minecraft:netherite_block destroy\n'
            f'fill {command[1]} {command[2]} {command[3]} {command[4]} {command[5]} {command[6]} {command[7]}\n'
            f'execute if score #success help.value matches 0 run return 0\n'
            f'return 1'
        )
    if command[8] == "replace" and len(command) >= 10:
        return command_block_helper.create_function(
            f'execute store success score #success help.value run fill {command[1]} {command[2]} {command[3]} {command[4]} {command[5]} {command[6]} minecraft:netherite_block replace {command[9]}\n'
            f'fill {command[1]} {command[2]} {command[3]} {command[4]} {command[5]} {command[6]} {command[7]} replace minecraft:netherite_block\n'
            f'execute if score #success help.value matches 0 run return 0\n'
            f'return 1'
        )
    return command_block_helper.create_function(
        f'execute store success score #success help.value run fill {command[1]} {command[2]} {command[3]} {command[4]} {command[5]} {command[6]} minecraft:netherite_block {command[8]}\n'
        f'fill {command[1]} {command[2]} {command[3]} {command[4]} {command[5]} {command[6]} {command[7]} {command[8]}\n'
        f'execute if score #success help.value matches 0 run return 0\n'
        f'return 1'
    )

def handle_setblock(command: list[str]) -> str:
    if command[4].split("[")[0].split("{")[0] in ["minecraft:command_block", "minecraft:chain_command_block", "minecraft:repeating_command_block"]:
        nbt = nbt_tags.unpack_compound(command[4][command[4].find("{"):])
        default_values = {
            "auto": nbt_tags.TypeByte(0),
            "Command": "",
            "conditionMet": nbt_tags.TypeByte(0),
            "CustomName": '{"text":"@"}',
            "LastExecution": nbt_tags.TypeLong(0),
            "LastOutput": '{"text":""}',
            "powered": nbt_tags.TypeByte(0),
            "SuccessCount": nbt_tags.TypeInt(0),
            "TrackOutput": nbt_tags.TypeByte(1),
            "UpdateLastExecution": nbt_tags.TypeByte(1)
        }
        for key in default_values:
            if key not in nbt:
                nbt[key] = default_values[key]
        return command_block_helper.create_function(
            f'execute if block {command[1]} {command[2]} {command[3]} {command[4][:command[4].find("{")]} run data merge block {command[1]} {command[2]} {command[3]} {nbt_tags.pack_compound(nbt)}\n'
            f'execute unless block {command[1]} {command[2]} {command[3]} {command[4][:command[4].find("{")]} run {" ".join(command)}\n'
            f'execute store success score #success help.value if loaded {command[1]} {command[2]} {command[3]}\n'
            f'execute if score #success help.value matches 0 run return 0\n'
            f'return 1'
        )
    return command_block_helper.create_function(
        f'setblock {command[1]} {command[2]} {command[3]} minecraft:netherite_block\n'
        f'{" ".join(command)}\n'
        f'execute store success score #success help.value if loaded {command[1]} {command[2]} {command[3]}\n'
        f'execute if score #success help.value matches 0 run return 0\n'
        f'return 1'
    )