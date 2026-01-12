# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from typing import TypedDict
from enum import Enum
from pathlib import Path
from lib import defaults
from typing import Any



# Initialize variables

PROGRAM_PATH = Path(__file__).parent.parent
OPTIONS_PATH = PROGRAM_PATH / "options.json"

class Option(Enum):
    MAP_NAME = "map_name"
    RESOURCE_PACK = "resource_pack"
    FANCY_NAME = "fancy_name"
    VERSION = "version"
    FIXES = "fixes"

class Options(TypedDict):
    map_name: str
    resource_pack: str
    fancy_name: str
    version: int
    fixes: dict[str, Any]



# Define functions

def get_default_options() -> Options:
    return {
        Option.MAP_NAME.value: "world",
        Option.RESOURCE_PACK.value: "resources",
        Option.FANCY_NAME.value: "Map",
        Option.VERSION.value: defaults.PACK_VERSION,
        Option.FIXES.value: {
            "command_helper": {
                "teleport_dismount": True,
                "effect_overflow": True,
                "safe_nbt_interpret": True,
                "sign_nbt_merge": True,
                "time_0_falling_block": True,
                "illegal_block_states": True,
                "command_block_testfor": True,
                "block_nbt_modifier": True,
                "cancel_firework_damage": True,
                "teleport_motion_cancel": True,
                "mitigate_block_update": True,
                "custom_model_data_store": True,
                "removed_default_nbt": True,
                "restore_spawn_chunks": True,
                "handle_forceload_with_spawn_chunks": True,
                "world_border_dimensions": True,
                "world_border_stopwatch": True,
                "fire_tick_game_rules": True,
            },
            "no_ai_horse_movement": True,
            "broken_score_references": True,
            "stats": True,
            "old_adventure_mode_items": True,
            "post_fixes": True,
            "lock_fixer": True,
            "empty_equipment_override": False,
            "macros": True,
            "json_text_components_in_storage": True,
            "oversized_in_gui": False,
            "stats_options": {
                "block_stats_used": True,
                "block_positions_dynamic": False,
                "commands_written_to_sensitive_position": False,
                "commands_written_to_arbitrary_position": False,
                "entity_stats_used": False,
                "entity_types_dynamic": False,
                "complex_stat_usage": False
            },
        },
    }

def set_options(options: Options):
    with OPTIONS_PATH.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(options, file, indent=4)

def get_options():
    options = get_default_options()
    if OPTIONS_PATH.exists():
        with OPTIONS_PATH.open("r", encoding="utf-8") as file:
            merge_options(options, json.load(file))
    set_options(options)

    return options

def merge_options(target: Options, source: Options):
    for key in source:
        if key not in target:
            target[key] = source[key]
        elif isinstance(source[key], dict) and isinstance(target[key], dict):
            merge_options(target[key], source[key])
        else:
            target[key] = source[key]



def get_map_name() -> str:
    options = get_options()
    return options[Option.MAP_NAME.value]

def get_resource_pack() -> str:
    options = get_options()
    return options[Option.RESOURCE_PACK.value]

def get_fancy_name() -> str:
    options = get_options()
    return options[Option.FANCY_NAME.value]

def get_version() -> int:
    options = get_options()
    return options[Option.VERSION.value]

def get_fixes() -> dict[str, Any]:
    options = get_options()
    return options[Option.FIXES.value]



def set_map_name(map_name: str):
    options = get_options()
    options[Option.MAP_NAME.value] = map_name
    set_options(options)

def set_resource_pack(resource_pack: str):
    options = get_options()
    options[Option.RESOURCE_PACK.value] = resource_pack
    set_options(options)

def set_fancy_name(fancy_name: str):
    options = get_options()
    options[Option.FANCY_NAME.value] = fancy_name
    set_options(options)

def set_version(version: int):
    options = get_options()
    options[Option.VERSION.value] = version
    set_options(options)



FIXES = get_fixes()