# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from lib.data_pack_files import command_helper
from lib.data_pack_files import nbt_tags



# Define functions

def handle_merge(command: list[str], is_macro: bool, block_nbt: dict, old_block_nbt: dict) -> str:
    new_commands: list[str] = []
    for key, i in {"Text1": 0, "Text2": 1, "Text3": 2, "Text4": 3}.items():
        if key not in old_block_nbt:
            continue
        new_commands.append(f'data modify block {" ".join(command[3:6])} front_text.messages[{i}] set value {block_nbt["front_text"]["messages"][i]}')
    del block_nbt["front_text"]
    if block_nbt:
        new_commands.append(f'{" ".join(command[:6])} {nbt_tags.pack(block_nbt)}')
    if not new_commands:
        return " ".join(command)
    if len(new_commands) == 1:
        return new_commands[0]
    return command_helper.create_function(
        "\n".join(new_commands) +
        "\nreturn 1",
        is_macro
    )