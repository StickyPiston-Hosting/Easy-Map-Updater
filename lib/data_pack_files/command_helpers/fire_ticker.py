# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from lib.data_pack_files import command_helper



# Define functions

def handle_do_fire_tick_set(command: list[str], is_macro: bool) -> str:
    if command[2] == "true":
        return command_helper.create_function(
            "execute if score #allow_fire_ticks_away_from_player help.value matches 0 run gamerule minecraft:fire_spread_radius_around_player 8\n"
            "execute if score #allow_fire_ticks_away_from_player help.value matches 1 run gamerule minecraft:fire_spread_radius_around_player -1\n"
            "return 1",
            is_macro
        )
    else:
        return "gamerule minecraft:fire_spread_radius_around_player 0"
    
def handle_allow_fire_ticks_set(command: list[str], is_macro: bool) -> str:
    if command[2] == "true":
        return command_helper.create_function(
            "execute store result score #fire_spread_radius_around_player help.value run gamerule minecraft:fire_spread_radius_around_player\n"
            "execute if score #fire_spread_radius_around_player help.value matches 1.. run gamerule minecraft:fire_spread_radius_around_player -1\n"
            "scoreboard players set #allow_fire_ticks_away_from_player help.value 1\n"
            "return 1",
            is_macro
        )
    else:
        return command_helper.create_function(
            "execute store result score #fire_spread_radius_around_player help.value run gamerule minecraft:fire_spread_radius_around_player\n"
            "execute if score #fire_spread_radius_around_player help.value matches -1 run gamerule minecraft:fire_spread_radius_around_player 8\n"
            "scoreboard players set #allow_fire_ticks_away_from_player help.value 0\n"
            "return 0",
            is_macro
        )

def handle_do_fire_tick_get(command: list[str], is_macro: bool) -> str:
    return command_helper.create_function(
        "execute store result score #fire_spread_radius_around_player help.value run gamerule minecraft:fire_spread_radius_around_player\n"
        "execute if score #fire_spread_radius_around_player help.value matches 0 run return 0\n"
        "return 1",
        is_macro
    )

def handle_allow_fire_ticks_get(command: list[str], is_macro: bool) -> str:
    return "scoreboard players get #allow_fire_ticks_away_from_player help.value"