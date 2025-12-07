# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from lib import option_manager
from lib.data_pack_files import command_helper
from lib.data_pack_files import miscellaneous



# Define functions

def handle_world_border_add(command: list[str], is_macro: bool, version: int) -> str:
    diameter = command[2] if len(command) >= 3 else "0"
    duration = command[3] if len(command) >= 4 else "0"
    duration_multiplier = 1000 if version <= 2108 and miscellaneous.is_macro_token(duration) else 50

    if version <= 2108 and option_manager.FIXES["command_helper"]["world_border_dimensions"]:
        return command_helper.create_function(
            f"execute store result score #overworld_border_time help.value run stopwatch query help:overworld_border 1000\n"
            f"scoreboard players operation #overworld_border_time < #overworld_border_duration help.value\n"
            f"scoreboard players operation #overworld_border_current help.value = #overworld_border_after help.value\n"
            f"scoreboard players operation #overworld_border_current help.value -= #overworld_border_before help.value\n"
            f"scoreboard players operation #overworld_border_current help.value *= #overworld_border_time help.value\n"
            f"scoreboard players operation #overworld_border_current help.value /= #overworld_border_duration help.value\n"
            f"scoreboard players operation #overworld_border_current help.value += #overworld_border_before help.value\n"
            f"scoreboard players operation #overworld_border_before help.value = #overworld_border_current help.value\n"
            f"scoreboard players operation #overworld_border_after help.value = #overworld_border_current help.value\n"
            f"scoreboard players set #overworld_border_increment help.value {diameter}\n"
            f"scoreboard players operation #overworld_border_after help.value += #overworld_border_increment help.value\n"
            f"scoreboard players set #overworld_border_after help.value {diameter}\n"
            f"scoreboard players set #overworld_border_duration help.value {duration}\n"
            f"scoreboard players operation #overworld_border_duration help.value *= #{duration_multiplier} help.value\n"
            f"stopwatch reset help:overworld_border\n"
            f"execute in minecraft:the_nether run {" ".join(command)}\n"
            f"execute in minecraft:the_end run {" ".join(command)}\n"
            f"return run execute in minecraft:overworld run {" ".join(command)}",
            is_macro
        )

    else:
        return command_helper.create_function(
            "".join([
                f"execute if dimension minecraft:{dimension} store result score #{dimension}_border_time help.value run stopwatch query help:{dimension}_border 1000\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_time < #{dimension}_border_duration help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_current help.value = #{dimension}_border_after help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_current help.value -= #{dimension}_border_before help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_current help.value *= #{dimension}_border_time help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_current help.value /= #{dimension}_border_duration help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_current help.value += #{dimension}_border_before help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_before help.value = #{dimension}_border_current help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_after help.value = #{dimension}_border_current help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players set #{dimension}_border_increment help.value {diameter}\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_after help.value += #{dimension}_border_increment help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players set #{dimension}_border_duration help.value {duration}\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_duration help.value *= #{duration_multiplier} help.value\n"
                f"execute if dimension minecraft:{dimension} run stopwatch reset help:{dimension}_border\n"
                f"execute if dimension minecraft:{dimension} run return run {" ".join(command)}\n"
                for dimension in [
                    "overworld",
                    "the_nether",
                    "the_end"
                ]
            ]),
            is_macro
        )
    


def handle_world_border_set(command: list[str], is_macro: bool, version: int) -> str:
    diameter = command[2] if len(command) >= 3 else "0"
    duration = command[3] if len(command) >= 4 else "0"
    duration_multiplier = 1000 if version <= 2108 and miscellaneous.is_macro_token(duration) else 50

    if version <= 2108 and option_manager.FIXES["command_helper"]["world_border_dimensions"]:
        return command_helper.create_function(
            f"execute store result score #overworld_border_time help.value run stopwatch query help:overworld_border 1000\n"
            f"scoreboard players operation #overworld_border_time < #overworld_border_duration help.value\n"
            f"scoreboard players operation #overworld_border_current help.value = #overworld_border_after help.value\n"
            f"scoreboard players operation #overworld_border_current help.value -= #overworld_border_before help.value\n"
            f"scoreboard players operation #overworld_border_current help.value *= #overworld_border_time help.value\n"
            f"scoreboard players operation #overworld_border_current help.value /= #overworld_border_duration help.value\n"
            f"scoreboard players operation #overworld_border_current help.value += #overworld_border_before help.value\n"
            f"scoreboard players operation #overworld_border_before help.value = #overworld_border_current help.value\n"
            f"scoreboard players set #overworld_border_after help.value {diameter}\n"
            f"scoreboard players set #overworld_border_duration help.value {duration}\n"
            f"scoreboard players operation #overworld_border_duration help.value *= #{duration_multiplier} help.value\n"
            f"stopwatch reset help:overworld_border\n"
            f"execute in minecraft:the_nether run {" ".join(command)}\n"
            f"execute in minecraft:the_end run {" ".join(command)}\n"
            f"return run execute in minecraft:overworld run {" ".join(command)}",
            is_macro
        )

    else:
        return command_helper.create_function(
            "".join([
                f"execute if dimension minecraft:{dimension} store result score #{dimension}_border_time help.value run stopwatch query help:{dimension}_border 1000\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_time < #{dimension}_border_duration help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_current help.value = #{dimension}_border_after help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_current help.value -= #{dimension}_border_before help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_current help.value *= #{dimension}_border_time help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_current help.value /= #{dimension}_border_duration help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_current help.value += #{dimension}_border_before help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_before help.value = #{dimension}_border_current help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players set #{dimension}_border_after help.value {diameter}\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players set #{dimension}_border_duration help.value {duration}\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_duration help.value *= #{duration_multiplier} help.value\n"
                f"execute if dimension minecraft:{dimension} run stopwatch reset help:{dimension}_border\n"
                f"execute if dimension minecraft:{dimension} run return run {" ".join(command)}\n"
                for dimension in [
                    "overworld",
                    "the_nether",
                    "the_end"
                ]
            ]),
            is_macro
        )
    


def handle_world_border_get(command: list[str], is_macro: bool, version: int) -> str:
    if version <= 2108 and option_manager.FIXES["command_helper"]["world_border_dimensions"]:
        return command_helper.create_function(
            f"execute store result score #overworld_border_time help.value run stopwatch query help:overworld_border 1000\n"
            f"scoreboard players operation #overworld_border_time < #overworld_border_duration help.value\n"
            f"scoreboard players operation #overworld_border_current help.value = #overworld_border_after help.value\n"
            f"scoreboard players operation #overworld_border_current help.value -= #overworld_border_before help.value\n"
            f"scoreboard players operation #overworld_border_current help.value *= #overworld_border_time help.value\n"
            f"scoreboard players operation #overworld_border_current help.value /= #overworld_border_duration help.value\n"
            f"scoreboard players operation #overworld_border_current help.value += #overworld_border_before help.value\n"
            f"return run scoreboard players get #overworld_border_current help.value\n",
            is_macro
        )

    else:
        return command_helper.create_function(
            "".join([
                f"execute if dimension minecraft:{dimension} store result score #{dimension}_border_time help.value run stopwatch query help:{dimension}_border 1000\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_time < #{dimension}_border_duration help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_current help.value = #{dimension}_border_after help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_current help.value -= #{dimension}_border_before help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_current help.value *= #{dimension}_border_time help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_current help.value /= #{dimension}_border_duration help.value\n"
                f"execute if dimension minecraft:{dimension} run scoreboard players operation #{dimension}_border_current help.value += #{dimension}_border_before help.value\n"
                f"execute if dimension minecraft:{dimension} run return run scoreboard players get #{dimension}_border_current help.value\n"
                for dimension in [
                    "overworld",
                    "the_nether",
                    "the_end"
                ]
            ]),
            is_macro
        )