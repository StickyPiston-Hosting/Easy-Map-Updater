# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from lib.data_pack_files import command_helper



# Define functions

def handle_store(command: list[str], is_macro: bool, source: str, path: str, type_index: int | None) -> str:
    if type_index is not None:
        command[type_index] = "float"
    return command_helper.create_function(
        f'execute unless data {source} {path} run data modify {source} {path[:-3]} append value 0.0f\n'
        f'return run {" ".join(command).replace(".__CUSTOM_MODEL_PATH__", "")}',
        is_macro
    )