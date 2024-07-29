# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Modifications and additions to world saves made by this program are
# not covered by this license and instead fall under the MIT license.



# Check that correct Python version is running

import sys
if not (
    (sys.version_info[0] == 3 and sys.version_info[1] >= 12)
    or
    (sys.version_info[0] > 3)
):
    print("\nERROR: Easy Map Updater requires Python 3.12 or newer!")
    input()
    exit()
    
    
    
# Import things

import shutil
import json
import traceback
from typing import cast, TypedDict, Callable, Any
from enum import Enum
from pathlib import Path
from lib.log import log
from lib import defaults
from lib import utils
from lib import finalize
from lib import data_pack
from lib import resource_pack
from lib import option_manager
from lib import json_manager
from lib.data_pack_files import command
from lib.data_pack_files import json_text_component
from lib.data_pack_files import breakpoints
from lib.data_pack_files import advancement
from lib.data_pack_files import item_modifier
from lib.data_pack_files import loot_table
from lib.data_pack_files import predicate
from lib.data_pack_files import recipe
from lib.data_pack_files.restore_behavior import tag_replacements
from lib.data_pack_files.restore_behavior import spawner_bossbar
from lib.data_pack_files.restore_behavior import ore_fixer
from lib.data_pack_files.restore_behavior import area_effect_cloud_killer
from lib.data_pack_files.restore_behavior import firework_damage_canceler
from lib.data_pack_files.restore_behavior import unwaterloggable_leaves
from lib.data_pack_files.restore_behavior import old_adventure_mode
from lib.data_pack_files.restore_behavior import effect_overflow
from lib.data_pack_files.admin_controls import admin_kickback
from lib.region_files import command_blocks
from lib.region_files import entity_extractor
from lib.region_files import fix_world
from lib.region_files import stats_scanner
from lib.region_files import illegal_chunk



# Initialize variables

PROGRAM_PATH = Path(__file__).parent
MINECRAFT_PATH = PROGRAM_PATH.parent

class Action(Enum):
    RESET = "reset"
    ALL = "all"
    UPDATE = "update"
    SCAN = "scan"

    RP_IMPORT = "rp.import"
    RP_ORIGINAL = "rp.original"
    RP_RELOAD = "rp.reload"
    RP_PURGE = "rp.purge"
    RP_UPDATE = "rp.update"
    RP_FIX = "rp.fix"
    RP_EXPORT = "rp.export"
    RP_EXPORT_ORIGINAL = "rp.export_original"

    DP_UNZIP = "dp.unzip"
    DP_ZIP = "dp.zip"
    DP_LOG = "dp.log"
    DP_DIRECTORY = "dp.directory"
    DP_VANILLA = "dp.vanilla"
    DP_MERGE = "dp.merge"
    DP_STORED_FUNCTION = "dp.stored_function"
    DP_STORED_ADVANCEMENT = "dp.stored_advancement"
    DP_ADVANCEMENT = "dp.advancement"
    DP_RECIPE = "dp.recipe"
    DP_UPDATE = "dp.update"
    DP_TAG = "dp.tag"
    DP_BOSSBAR = "dp.bossbar"
    DP_AEC_KILL = "dp.aec_kill"
    DP_FIREWORK = "dp.firework"
    DP_ORE_FIXER = "dp.ore"
    DP_WATER_LEAVES = "dp.water_leaves"
    DP_ADVENTURE = "dp.adventure"
    DP_EFFECT = "dp.effect"
    DP_BREAK = "dp.break"

    WORLD_ORIGINAL = "world.original"
    WORLD_ORIGINAL_PLAY = "world.original.play"
    WORLD_RELOAD = "world.reload"
    WORLD_SOURCE = "world.source"
    WORLD_PLAY = "world.play"
    WORLD_FIX = "world.fix"

    OPTIMIZE = "optimize"
    ENTITY_EXTRACT = "entity.extract"
    STATS_SCAN = "stats.scan"
    ILLEGAL_CHUNK = "illegal.chunk"

    CMD_READ = "cmd.read"
    CMD_UPDATE = "cmd.update"
    CMD_WRITE = "cmd.write"
    CMD_CLEAR = "cmd.clear"
    CMD_EXTRACT = "cmd.extract"

    FINAL_SCORE = "final.score"
    FINAL = "final"

    ADMIN_KICKBACK = "admin.kickback"

    CLEAN = "clean"

    VERSION = "version"
    LICENSE = "license"
    EXIT = "exit"

    DEBUG = "debug"
    DEBUG_CMD = "debug.cmd"
    DEBUG_JSON = "debug.json"
    DEBUG_ADVANCEMENT = "debug.advancement"
    DEBUG_LOOT_TABLE = "debug.loot_table"
    DEBUG_ITEM_MODIFIER = "debug.item_modifier"
    DEBUG_PREDICATE = "debug.predicate"
    DEBUG_RECIPE = "debug.recipe"



class ActionDefinition(TypedDict):
    show: bool
    function: Callable
    name: str

actions: dict[str, ActionDefinition]



class UpdateProgressDefinition(TypedDict):
    stage: int
    world_scan: finalize.WorldScan
    fix_world_flags: fix_world.FixWorldFlags

def default_update_progress() -> UpdateProgressDefinition:
    return {
        "stage": 0,
        "world_scan": {
            "world": False,
            "resource_pack": False,
            "disabled_vanilla": False,
            "zipped_data_packs": False,
            "stored_functions": False,
            "stored_advancements": False,
            "advancements": False,
            "recipes": False,
        },
        "fix_world_flags": {
            "spawner_bossbar": False,
        },
    }
update_progress: UpdateProgressDefinition = default_update_progress()



# Define functions

def program():
    # Show title
    print("")
    log("Easy Map Updater")
    log("- By Dominexis, and StickyPiston Hosting")

    # Initialize variables
    option_manager.get_options()
    action_reset()
    load_session()
    save_session()
    print("")
    print_version()
    print("")
    list_actions()

    # Program loop
    while True:
        # Get action
        action = input("\nAction: ")
        if action not in actions:
            log("ERROR: Must be a valid action!")
            continue
        print("")

        # Run action
        actions[action]["show"] = True
        try:
            actions[action]["function"]()
        except Exception:
            save_session()
            print("")
            log(f'ERROR:\n{traceback.format_exc()}', True)

        print("")
        save_session()
        list_actions()

class SessionDefinition(TypedDict):
    actions: dict[str, bool]
    update_progress: UpdateProgressDefinition

def load_session():
    session_path = PROGRAM_PATH / "session.json"
    if not session_path.exists():
        return
    with session_path.open("r", encoding="utf-8") as file:
        session = cast(SessionDefinition, json.load(file))
    if "debug.cmd" in session:
        session = cast(SessionDefinition, {"actions": session})

    if "actions" not in session:
        session["actions"] = cast(dict[str, bool], {})
    for action in session["actions"]:
        if action in actions:
            actions[action]["show"] = session["actions"][action]

    if "update_progress" in session:
        session_update_progress = session["update_progress"]
        for key in ["stage", "world_scan", "fix_world_flags"]:
            if key in session_update_progress:
                update_progress[key] = session_update_progress[key]

def save_session():
    session: SessionDefinition = {
        "actions": {},
        "update_progress": update_progress
    }
    for action in actions:
        session["actions"][action] = actions[action]["show"]
    session_path = PROGRAM_PATH / "session.json"
    with session_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(session, file, indent=4)

def list_options():
    log("Options:")
    options = option_manager.get_options()
    for key in options:
        log(f"{key}: {options[key]}")

def list_actions():
    print("Actions:")
    for action in actions:
        if action == Action.VERSION.value:
            print("")
        if actions[action]["show"]:
            print(f" {action}) {' '*max(21-len(action), 0)}{actions[action]['name']}")



# Define actions

def action_reset():
    global actions
    actions = {
        Action.RESET.value:                 { "show": True,  "function": action_reset, "name": "Reset actions" },
        Action.ALL.value:                   { "show": True,  "function": action_show_all_actions, "name": "Show all actions" },
        Action.UPDATE.value:                { "show": True,  "function": action_update, "name": "Update map" },
        Action.SCAN.value:                  { "show": True,  "function": action_scan_world, "name": "Scans your world to gather relevant information" },

        Action.WORLD_ORIGINAL.value:        { "show": False, "function": action_prepare_original_copy_world, "name": "Prepare original copy of world (do this before updating)" },
        Action.WORLD_ORIGINAL_PLAY.value:   { "show": False, "function": action_prepare_original_play_copy, "name": "Prepare play version of original copy of world" },
        Action.WORLD_RELOAD.value:          { "show": False, "function": action_reload_from_original_world, "name": "Reload world from original copy" },

        Action.RP_IMPORT.value:             { "show": False, "function": action_import_resource_pack, "name": "Import resource pack from world" },
        Action.RP_ORIGINAL.value:           { "show": False, "function": action_prepare_original_copy_resource_pack, "name": "Prepare original copy of resource pack" },
        Action.RP_RELOAD.value:             { "show": False, "function": action_reload_from_original_resource_pack, "name": "Reload resource pack from original copy" },
        Action.RP_PURGE.value:              { "show": False, "function": action_purge_vanilla_assets, "name": "Purge vanilla assets from resource pack" },
        Action.RP_UPDATE.value:             { "show": False, "function": action_update_resource_pack, "name": "Update resource pack" },
        Action.RP_FIX.value:                { "show": False, "function": action_fix_resource_pack, "name": "Fix resource pack" },

        Action.DP_UNZIP.value:              { "show": False, "function": action_unzip_data_packs, "name": "Unzip data packs" },
        Action.DP_LOG.value:                { "show": False, "function": action_log_data_packs, "name": "Log data packs" },
        Action.DP_DIRECTORY.value:          { "show": False, "function": action_rename_data_pack_directories, "name": "Rename data pack directories" },
        Action.DP_VANILLA.value:            { "show": False, "function": action_fix_disabled_vanilla, "name": "Fix disabled vanilla data pack (must be done before merging)" },
        Action.DP_MERGE.value:              { "show": False, "function": action_merge_data_packs, "name": "Merge data packs" },
        Action.DP_STORED_FUNCTION.value:    { "show": False, "function": action_stored_functions, "name": "Extract stored functions" },
        Action.DP_STORED_ADVANCEMENT.value: { "show": False, "function": action_stored_advancements, "name": "Extract stored advancements" },
        Action.DP_ADVANCEMENT.value:        { "show": False, "function": action_disable_advancements, "name": "Disable advancements (if one of the data packs makes them all impossible)" },
        Action.DP_RECIPE.value:             { "show": False, "function": action_disable_recipes, "name": "Disable recipes (if one of the data packs makes them all impossible)" },

        Action.WORLD_SOURCE.value:          { "show": False, "function": action_prepare_source_copy, "name": "Prepare source copy of world (do this before opening world)" },
        
        Action.DP_UPDATE.value:             { "show": False, "function": action_update_data_packs, "name": "Update data packs" },

        Action.OPTIMIZE.value:              { "show": False, "function": action_optimize_world, "name": "Mark world as optimized" },
        Action.ENTITY_EXTRACT.value:        { "show": False, "function": action_entity_extract, "name": "Extract entities from regions" },
        Action.STATS_SCAN.value:            { "show": False, "function": action_stats_scan, "name": "Scan world for stats usage" },
        Action.WORLD_FIX.value:             { "show": False, "function": action_fix_world, "name": "Fix broken data in world" },

        Action.DP_BOSSBAR.value:            { "show": False, "function": action_spawner_bossbar, "name": "Create spawner bossbar data pack" },
        Action.DP_AEC_KILL.value:           { "show": False, "function": action_area_effect_cloud_killer, "name": "Create area effect cloud killer data pack" },
        Action.DP_ORE_FIXER.value:          { "show": False, "function": action_ore_fixer, "name": "Create ore fixer data pack" },
        Action.DP_WATER_LEAVES.value:       { "show": False, "function": action_unwaterloggable_leaves, "name": "Create unwaterloggable leaves data pack" },
        Action.DP_ADVENTURE.value:          { "show": False, "function": action_old_adventure_mode, "name": "Create old adventure mode data pack" },
        Action.DP_EFFECT.value:             { "show": False, "function": action_effect_overflow, "name": "Create effect overflow data pack" },

        Action.CMD_READ.value:              { "show": False, "function": action_read_commands, "name": "Read command block data" },
        Action.CMD_UPDATE.value:            { "show": False, "function": action_update_commands, "name": "Update command block data" },
        Action.CMD_WRITE.value:             { "show": False, "function": action_write_commands, "name": "Write command block data" },
        Action.CMD_CLEAR.value:             { "show": False, "function": action_clear_command_helper, "name": "Clear command helper" },
        Action.CMD_EXTRACT.value:           { "show": False, "function": action_extract_commands, "name": "Extract commands from a command block chain" },

        Action.DP_TAG.value:                { "show": False, "function": action_tag_replacements, "name": "Create tag replacements data pack" },
        Action.DP_FIREWORK.value:           { "show": False, "function": action_firework_damage_canceler, "name": "Create firework damage canceler data pack" },
        Action.ILLEGAL_CHUNK.value:         { "show": False, "function": action_illegal_chunk, "name": "Insert illegal block state chunk into world" },

        Action.DP_BREAK.value:              { "show": False, "function": action_breakpoint, "name": "Apply breakpoints to data pack" },

        Action.FINAL_SCORE.value:           { "show": False, "function": action_get_player_names, "name": "Get player names from scoreboard" },
        Action.FINAL.value:                 { "show": False, "function": action_finalize_map, "name": "Finalize map" },

        Action.WORLD_PLAY.value:            { "show": False, "function": action_prepare_play_copy, "name": "Prepare play version of world (use for testing map)" },
        
        Action.ADMIN_KICKBACK.value:        { "show": False, "function": action_admin_kickback, "name": "Create admin control (kickback) data pack" },

        Action.DP_ZIP.value:                { "show": False, "function": action_zip_data_packs, "name": "Zip data packs" },
        Action.RP_EXPORT.value:             { "show": False, "function": action_export_resource_pack, "name": "Export resource pack to world" },
        Action.RP_EXPORT_ORIGINAL.value:    { "show": False, "function": action_export_original_resource_pack, "name": "Export original resource pack to source world" },
        Action.CLEAN.value:                 { "show": False, "function": action_clean_up, "name": "Clean up files (remove worlds and resource pack)" },

        Action.VERSION.value:               { "show": True,  "function": action_set_version, "name": "Edit source version" },
        Action.LICENSE.value:               { "show": True,  "function": action_license, "name": "Show software license" },
        Action.EXIT.value:                  { "show": True,  "function": action_exit, "name": "Exit program" },

        Action.DEBUG.value:                 { "show": False, "function": action_toggle_debug_mode, "name": "Toggle debug mode" },
        Action.DEBUG_CMD.value:             { "show": False,  "function": action_update_single_command, "name": "Update single command (for testing)" },
        Action.DEBUG_JSON.value:            { "show": False,  "function": action_update_json_text_component, "name": "Update JSON text component (for testing)" },
        Action.DEBUG_ADVANCEMENT.value:     { "show": False,  "function": action_update_advancement, "name": "Update advancement from file (for testing)" },
        Action.DEBUG_LOOT_TABLE.value:      { "show": False,  "function": action_update_loot_table, "name": "Update loot table from file (for testing)" },
        Action.DEBUG_ITEM_MODIFIER.value:   { "show": False,  "function": action_update_item_modifier, "name": "Update item modifier from file (for testing)" },
        Action.DEBUG_PREDICATE.value:       { "show": False,  "function": action_update_predicate, "name": "Update predicate from file (for testing)" },
        Action.DEBUG_RECIPE.value:          { "show": False,  "function": action_update_recipe, "name": "Update recipe from file (for testing)" },
    }

def action_show_all_actions():
    global actions
    for action in actions:
        actions[action]["show"] = True



def action_update(): # Needs confirmation
    log("Updating map")

    # Make sure that world exists
    world: Path = MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    og_world: Path = MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()}_original'
    source_world: Path = MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()}_source'
    resource_pack: Path = MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack()
    if not world.exists():
        log("ERROR: World does not exist!")
        return

    # Get confirmation
    log(f'This action will update: {world.as_posix()}')
    confirm = input("Is this okay? (Y/N): ")
    if confirm not in ["y", "Y"]:
        log("Action canceled")
        return
    
    # Get confirmation for starting in the middle
    if update_progress["stage"] > 0:
        confirm = input("The map was partially updated. Do you wish to resume where it last stopped? (Y/N): ")
        if confirm not in ["y" ,"Y"]:
            log("Starting update from beginning")
            reset_update_progress()
        else:
            log("Resuming update")
    
    # Reload world if original world exists
    if update_progress["stage"] == 0:
        if og_world.exists():
            print("")
            confirm = input("Original copy of world found, do you wish to update from the original? (Y/N): ")
            if confirm in ["y", "Y"]:
                action_reload_from_original_world(False)
        else:
            action_prepare_original_copy_world(False)
        next_update_progress_section()

    # Scan world
    progress_scan = update_progress["world_scan"]
    progress_flags = update_progress["fix_world_flags"]
    if update_progress["stage"] == 100:
        world_scan = finalize.scan_world(
            world,
            resource_pack
        )
        scan_again = False
        for key in world_scan:
            progress_scan[key] = world_scan[key]
        if world_scan["resource_pack"]:
            action_import_resource_pack(False)
            scan_again = True
        if world_scan["zipped_data_packs"]:
            action_unzip_data_packs(False)
            scan_again = True
        if world_scan["stored_functions"]:
            action_stored_functions(False)
            scan_again = True
        if world_scan["stored_advancements"]:
            action_stored_advancements(False)
            scan_again = True
        if scan_again:
            world_scan = finalize.scan_world(
                world,
                resource_pack
            )
            for key in world_scan:
                progress_scan[key] = world_scan[key]
        next_update_progress_section()

    version: int = option_manager.get_version()

    # Update resource pack
    if update_progress["stage"] == 200:
        if resource_pack.exists():
            action_prepare_original_copy_resource_pack(False)
            action_update_resource_pack()
        next_update_progress_section()

    # Update data pack
    if update_progress["stage"] == 300:
        if version <= 2006:
            action_rename_data_pack_directories(False)
        next_update_progress()
    if update_progress["stage"] == 301:
        if progress_scan["disabled_vanilla"]:
            action_fix_disabled_vanilla()
        next_update_progress()
    if update_progress["stage"] == 302:
        if progress_scan["advancements"]:
            print("")
            log("Advancements in the 'minecraft' namespace were found, which may be used to disable advancements in older maps")
            confirm = input("Do you wish to disable them via pack.mcmeta filters instead? (Y/N): ")
            if confirm in ["y", "Y"]:
                action_disable_advancements(False)
        if progress_scan["recipes"]:
            print("")
            log("Recipes in the 'minecraft' namespace were found, which may be used to disable recipes in older maps")
            confirm = input("Do you wish to disable them via pack.mcmeta filters instead? (Y/N): ")
            if confirm in ["y", "Y"]:
                action_disable_recipes(False)
        next_update_progress()
    if update_progress["stage"] == 303:
        action_prepare_source_copy(False)
        next_update_progress()
    if update_progress["stage"] == 304:
        action_update_data_packs(False)
        next_update_progress_section()

    # Optimize world
    if update_progress["stage"] == 400:
        print("")
        log(f'The world must now be optimized, boot up Minecraft {utils.get_version_string(defaults.PACK_VERSION)} and optimize the main copy of your world')
        confirm = input("Confirm when it has been optimized, decline to cancel (Y/N): ")
        if confirm not in ["y", "Y"]:
            log("Updated canceled")
            return
        next_update_progress_section()

    # Fix world
    if update_progress["stage"] == 500:
        if version <= 1605:
            action_entity_extract(False)
        next_update_progress()
    if update_progress["stage"] == 501:
        fix_world_flags = action_fix_world(False)
        for key in fix_world_flags:
            progress_flags[key] = fix_world_flags[key]
        next_update_progress_section()

    # Update command blocks
    if update_progress["stage"] == 600:
        action_read_commands(False)
        next_update_progress()
    if update_progress["stage"] == 601:
        action_update_commands(False)
        next_update_progress()
    if update_progress["stage"] == 602:
        action_write_commands(False)
        next_update_progress_section()

    # Add various things to the world to restore old behavior
    if update_progress["stage"] == 700:
        if progress_flags["spawner_bossbar"]:
            action_spawner_bossbar()
        next_update_progress()
    if update_progress["stage"] == 701:
        if version <= 710:
            action_old_adventure_mode()
        next_update_progress()
    if update_progress["stage"] == 702:
        if version <= 809:
            action_area_effect_cloud_killer()
        next_update_progress()
    if update_progress["stage"] == 703:
        if version <= 1100:
            action_firework_damage_canceler()
        next_update_progress()
    if update_progress["stage"] == 704:
        if version <= 1202:
            action_tag_replacements()
        next_update_progress()
    if update_progress["stage"] == 705:
        if version <= 1502:
            action_illegal_chunk()
        next_update_progress()
    if update_progress["stage"] == 706:
        if version <= 1605:
            action_ore_fixer()
        next_update_progress()
    if update_progress["stage"] == 707:
        if version <= 1802:
            action_unwaterloggable_leaves()
        next_update_progress_section()

    # Finalize map
    if update_progress["stage"] == 800:
        print("")
        if (world / "data" / "scoreboard.dat").exists():
            confirm = input("Do you wish to remove player score data from your map? (Y/N): ")
        else:
            confirm = "n"
        if confirm in ["y", "Y"]:
            action_get_player_names(False)
            print("")
            log("Player names have been logged in player_names.json")
            log("Go through the list and remove non-player names from the list (e.g. fakeplayer variable names)")
            confirm = input("Confirm when the non-player names have been removed, declined to cancel (Y/N): ")
            if confirm not in ["y", "Y"]:
                with (PROGRAM_PATH / "player_names.json").open("w", encoding="utf-8", newline="\n") as file:
                    file.write("{}")
        else:
            with (PROGRAM_PATH / "player_names.json").open("w", encoding="utf-8", newline="\n") as file:
                file.write("{}")
        next_update_progress()
    if update_progress["stage"] == 801:
        action_finalize_map(False)
        next_update_progress()
    if update_progress["stage"] == 802:
        if progress_scan["zipped_data_packs"]:
            action_zip_data_packs(False)
        next_update_progress()
    if update_progress["stage"] == 803:
        if resource_pack.exists():
            action_export_resource_pack(False)
            action_export_original_resource_pack(False)
        next_update_progress()
    if update_progress["stage"] == 804:
        action_prepare_play_copy(False)
        next_update_progress_section()

    print("")
    log("Map updated")
    log("Join the play copy of the world and playtest it", True)

    global actions
    actions[Action.CLEAN.value]["show"] = True

    reset_update_progress()

def reset_update_progress():
    global update_progress
    update_progress = default_update_progress()
    save_session()

def next_update_progress():
    update_progress["stage"] += 1
    save_session()

def next_update_progress_section():
    update_progress["stage"] = (update_progress["stage"] + 100)//100*100
    save_session()



def action_scan_world():
    world_scan = finalize.scan_world(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack()
    )

    if not world_scan["world"]:
        return

    global actions
    if world_scan["resource_pack"]:
        actions[Action.RP_IMPORT.value]["show"] = True
    if world_scan["disabled_vanilla"]:
        actions[Action.DP_VANILLA.value]["show"] = True
    if world_scan["zipped_data_packs"]:
        actions[Action.DP_UNZIP.value]["show"] = True
    if world_scan["stored_functions"]:
        actions[Action.DP_STORED_FUNCTION.value]["show"] = True
    if world_scan["stored_advancements"]:
        actions[Action.DP_STORED_ADVANCEMENT.value]["show"] = True
    if world_scan["advancements"]:
        actions[Action.DP_ADVANCEMENT.value]["show"] = True
    if world_scan["recipes"]:
        actions[Action.DP_RECIPE.value]["show"] = True

    actions[Action.WORLD_ORIGINAL.value]["show"] = True



def action_import_resource_pack(manual: bool = True): # Needs confirmation
    resource_pack.import_pack(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack(),
        manual
    )

    if manual:
        global actions
        actions[Action.RP_IMPORT.value]["show"] = True
        actions[Action.RP_ORIGINAL.value]["show"] = True
        actions[Action.RP_PURGE.value]["show"] = True

def action_export_resource_pack(manual: bool = True): # Needs confirmation
    resource_pack.export_pack(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack(),
        manual
    )

def action_export_original_resource_pack(manual: bool = True): # Needs confirmation
    resource_pack.export_pack(
        MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()}_source',
        MINECRAFT_PATH / "resourcepacks" / f'{option_manager.get_resource_pack()}_original',
        manual
    )

def action_update_resource_pack():
    resource_pack.update(
        MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack(),
        option_manager.get_version()
    )

def action_fix_resource_pack():
    resource_pack.fix(
        MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack()
    )

def action_purge_vanilla_assets(): # Needs confirmation
    resource_pack.purge_vanilla_assets(
        MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack()
    )



def action_unzip_data_packs(manual: bool = True): # Needs confirmation
    data_pack.unzip_packs(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        manual
    )

def action_zip_data_packs(manual: bool = True): # Needs confirmation
    data_pack.zip_packs(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        manual
    )

def action_merge_data_packs(manual: bool = True): # Needs confirmation
    data_pack.merge_packs(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        option_manager.get_fancy_name()
    )

    if manual:
        global actions
        actions[Action.DP_MERGE.value]["show"] = True

def action_rename_data_pack_directories(manual: bool = True):
    data_pack.rename_directories(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        manual
    )

def action_update_data_packs(manual: bool = True):
    data_pack.update(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        option_manager.get_version()
    )

    if manual:
        global actions
        if option_manager.get_version() <= 1202:
            actions[Action.DP_TAG.value]["show"] = True

def action_tag_replacements():
    tag_replacements.create_pack(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

def action_spawner_bossbar():
    spawner_bossbar.create_pack(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

def action_area_effect_cloud_killer():
    area_effect_cloud_killer.create_pack(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

def action_ore_fixer():
    ore_fixer.create_pack(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

def action_unwaterloggable_leaves():
    unwaterloggable_leaves.create_pack(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

def action_old_adventure_mode():
    old_adventure_mode.create_pack(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

def action_firework_damage_canceler():
    firework_damage_canceler.create_pack(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

def action_effect_overflow():
    effect_overflow.create_pack(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

def action_stored_functions(manual: bool = True): # Needs confirmation
    data_pack.extract_stored_functions(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        manual
    )

def action_stored_advancements(manual: bool = True): # Needs confirmation
    data_pack.extract_stored_advancements(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        manual
    )

def action_disable_advancements(manual: bool = True): # Needs confirmation
    data_pack.disable_advancements(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        manual
    )

def action_disable_recipes(manual: bool = True): # Needs confirmation
    data_pack.disable_recipes(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        manual
    )

def action_fix_disabled_vanilla():
    data_pack.fix_disabled_vanilla(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

def action_breakpoint(): # Needs confirmation
    breakpoints.apply_breakpoints(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )



def action_read_commands(manual: bool = True):
    command_blocks.read_commands(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

    if manual:
        global actions
        actions[Action.CMD_READ.value]["show"] = True
        actions[Action.CMD_WRITE.value]["show"] = True
        actions[Action.CMD_UPDATE.value]["show"] = True
        actions[Action.CMD_CLEAR.value]["show"] = True
        actions[Action.CMD_EXTRACT.value]["show"] = True

def action_write_commands(manual: bool = True): # Needs confirmation
    command_blocks.write_commands(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        manual
    )

def action_update_commands(manual: bool = True):
    command_blocks.update_commands(
        option_manager.get_version()
    )

    if manual:
        global actions
        if option_manager.get_version() <= 1100:
            actions[Action.DP_FIREWORK.value]["show"] = True
        if option_manager.get_version() <= 1202:
            actions[Action.DP_TAG.value]["show"] = True

def action_clear_command_helper(): # Needs confirmation
    data_pack_path: Path = MINECRAFT_PATH / "saves" / option_manager.get_map_name() / "datapacks" / "command_helper"
    log(f'This action will delete: {data_pack_path.as_posix()}')
    confirm = input("Is this okay? (Y/N): ")
    if confirm not in ["Y", "y"]:
        log("Action canceled")
        return

    log("Clearing command helper")

    if not data_pack_path.exists():
        log("ERROR: Command helper does not exist!")
        return
    
    shutil.rmtree(data_pack_path)

    log("Command helper cleared")

def action_extract_commands():
    command_blocks.extract_commands(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )



def action_get_player_names(manual: bool = True):
    finalize.get_player_names(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

    if manual:
        global actions
        actions[Action.FINAL.value]["show"] = True

def action_finalize_map(manual: bool = True): # Needs confirmation
    finalize.finalize(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack(),
        manual
    )

    if manual:
        global actions
        actions[Action.WORLD_PLAY.value]["show"] = True
        if actions[Action.DP_UNZIP.value]["show"]:
            actions[Action.DP_ZIP.value]["show"] = True
        if actions[Action.RP_IMPORT.value]["show"]:
            actions[Action.RP_EXPORT.value]["show"] = True
        actions[Action.CLEAN.value]["show"] = True

def action_log_data_packs():
    finalize.log_data_packs(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

    global actions
    actions[Action.DP_LOG.value]["show"] = True



def action_prepare_original_copy_world(manual: bool = True): # Needs confirmation
    log("Preparing original world copy")
    
    world: Path = MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    og_world: Path = MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()}_original'

    if og_world.exists() and manual:
        log(f'This action will overwrite: {og_world.as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return

    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if og_world.exists():
        shutil.rmtree(og_world)
    shutil.copytree(world, og_world)
    log("Original world copy prepared")

    if manual:
        global actions
        actions[Action.WORLD_ORIGINAL_PLAY.value]["show"] = True
        actions[Action.WORLD_RELOAD.value]["show"] = True
        actions[Action.WORLD_SOURCE.value]["show"] = True

def action_prepare_original_play_copy(): # Needs confirmation
    log("Preparing original play world copy")
    
    world: Path = MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()}_original'
    play_world: Path = MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()}_original_play'

    if play_world.exists():
        log(f'This action will overwrite: {play_world.as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return

    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if play_world.exists():
        shutil.rmtree(play_world)
    shutil.copytree(world, play_world)
    log("Play world copy prepared")

def action_reload_from_original_world(manual: bool = True): # Needs confirmation
    log("Reloading world from original")
    
    world: Path = MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    og_world: Path = MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()}_original'

    if world.exists() and manual:
        log(f'This action will overwrite: {world.as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return

    if not og_world.exists():
        log("ERROR: World does not exist!")
        return
    if world.exists():
        shutil.rmtree(world)
    shutil.copytree(og_world, world)
    log("World reloaded from original")

    if manual:
        global actions
        actions[Action.WORLD_ORIGINAL_PLAY.value]["show"] = True
        actions[Action.WORLD_RELOAD.value]["show"] = True
        actions[Action.WORLD_SOURCE.value]["show"] = True

def action_prepare_source_copy(manual: bool = True): # Needs confirmation
    log("Preparing source world copy")
    
    world: Path = MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    source_world: Path = MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()}_source'

    if source_world.exists() and manual:
        log(f'This action will overwrite: {source_world.as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return

    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if source_world.exists():
        shutil.rmtree(source_world)
    shutil.copytree(world, source_world)
    log("Source world copy prepared")

    if manual:
        global actions
        actions[Action.DP_UPDATE.value]["show"] = True
        actions[Action.OPTIMIZE.value]["show"] = True

def action_prepare_play_copy(manual: bool = True): # Needs confirmation
    log("Preparing play world copy")
    
    world: Path = MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    play_world: Path = MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()}_play'

    if play_world.exists() and manual:
        log(f'This action will overwrite: {play_world.as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return

    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if play_world.exists():
        shutil.rmtree(play_world)
    shutil.copytree(world, play_world)
    log("Play world copy prepared")

    if manual:
        global actions
        actions[Action.ADMIN_KICKBACK.value]["show"] = True

def action_prepare_original_copy_resource_pack(manual: bool = True): # Needs confirmation
    log("Preparing original resource pack copy")
    
    resource_pack: Path = MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack()
    og_resource_pack: Path = MINECRAFT_PATH / "resourcepacks" / f'{option_manager.get_resource_pack()}_original'

    if og_resource_pack.exists() and manual:
        log(f'This action will overwrite: {og_resource_pack.as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return

    if not resource_pack.exists():
        log("ERROR: Resource pack does not exist!")
        return
    if og_resource_pack.exists():
        shutil.rmtree(og_resource_pack)
    shutil.copytree(resource_pack, og_resource_pack)
    log("Original resource pack copy prepared")

    if manual:
        global actions
        actions[Action.RP_UPDATE.value]["show"] = True
        actions[Action.RP_RELOAD.value]["show"] = True

def action_reload_from_original_resource_pack(): # Needs confirmation
    log("Reloading resource pack from original")
    
    resource_pack: Path = MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack()
    og_resource_pack: Path = MINECRAFT_PATH / "resourcepacks" / f'{option_manager.get_resource_pack()}_original'

    if resource_pack.exists():
        log(f'This action will overwrite: {resource_pack.as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return

    if not og_resource_pack.exists():
        log("ERROR: Resource pack does not exist!")
        return
    if resource_pack.exists():
        shutil.rmtree(resource_pack)
    shutil.copytree(og_resource_pack, resource_pack)
    log("Resource pack reloaded from original")



def action_optimize_world():
    log("World marked as optimized")

    global actions
    actions[Action.CMD_READ.value]["show"] = True
    actions[Action.FINAL_SCORE.value]["show"] = True
    if option_manager.get_version() <= 1605:
        actions[Action.ENTITY_EXTRACT.value]["show"] = True
    if option_manager.get_version() <= 1502:
        actions[Action.ILLEGAL_CHUNK.value]["show"] = True
    if option_manager.get_version() <= 1202 and option_manager.get_version() >= 800:
        actions[Action.STATS_SCAN.value]["show"] = True
    actions[Action.WORLD_FIX.value]["show"] = True

def action_entity_extract(manual: bool = True): # Needs confirmation
    entity_extractor.extract(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        manual
    )

def action_stats_scan():
    stats_scanner.scan(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

def action_illegal_chunk():
    illegal_chunk.insert_chunk(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

def action_fix_world(manual: bool = True): # Needs confirmation
    booleans = fix_world.fix(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()}_source',
        option_manager.get_version(),
        manual
    )

    if manual:
        global actions
        if booleans["spawner_bossbar"]:
            actions[Action.DP_BOSSBAR.value]["show"] = True
        if option_manager.get_version() <= 710:
            actions[Action.DP_ADVENTURE.value]["show"] = True
        if option_manager.get_version() <= 809:
            actions[Action.DP_AEC_KILL.value]["show"] = True
        if option_manager.get_version() <= 1605:
            actions[Action.DP_ORE_FIXER.value]["show"] = True
        if option_manager.get_version() <= 1802:
            actions[Action.DP_WATER_LEAVES.value]["show"] = True
        if option_manager.get_version() <= 2004:
            actions[Action.DP_EFFECT.value]["show"] = True

    return booleans



def action_admin_kickback():
    admin_kickback.create_pack(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )



def action_clean_up(): # Needs confirmation
    paths: list[Path] = [
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()}_original',
        MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()}_source',
        MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()}_play',
        MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()}_original_play',
        MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack(),
        MINECRAFT_PATH / "resourcepacks" / f'{option_manager.get_resource_pack()}_original'
    ]

    log("This action will delete the following:")
    for path in paths:
        log(path.as_posix())
    confirm = input("Is this okay? (Y/N): ")
    if confirm not in ["Y", "y"]:
        log("Action canceled")
        return

    log("Cleaning up")
    for path in paths:
        if path.exists():
            shutil.rmtree(path)
    log("All clean!")

    action_reset()



def action_set_version():
    print_version()
    version_name, version = utils.get_version_from_user("Enter source version (leave blank to cancel): ", True)
    if not version_name:
        return
    option_manager.set_version(version)
    print_version()

def print_version():
    log(f'Source: {utils.get_version_string(option_manager.get_version())}, Target: {utils.get_version_string(defaults.PACK_VERSION)}')



def action_license():
    log("""
Easy Map Updater  Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under the GNU GPLv3 license.
        
Modifications and additions to world saves made by this program are
not covered by this license and instead fall under the MIT license.
""")

def action_exit():
    log("Exiting...")
    exit()



def action_toggle_debug_mode():
    if defaults.DEBUG_MODE:
        defaults.DEBUG_MODE = False
        log("Disabled debug mode")
    else:
        defaults.DEBUG_MODE = True
        log("Enabled debug mode")

def action_update_single_command():
    while True:
        test_command = input("Command to update (leave blank to cancel): ")
        if not test_command:
            break
        print("")
        log(f'Old command: {test_command}')
        log(f'New command: {command.update(test_command, option_manager.get_version(), "test_command")}')
        print("")

def action_update_json_text_component():
    while True:
        test_component = input("JSON text component to update (leave blank to cancel): ")
        if not test_component:
            break
        print("")
        log(f'Old component: {test_component}')
        log(f'New component: {json_text_component.update(test_component, option_manager.get_version(), [], False)}')
        print("")

def retrieve_json_file_contents(message: str) -> Any:
    while True:
        path_input = input(message)
        if not path_input:
            return
        if path_input.startswith("&"):
            path_input = path_input[1:].strip()
        path_input = utils.unpack_string_check(path_input)
        file_path = Path(path_input)
        if not file_path.exists():
            print("ERROR: File does not exist!")
            continue
        contents, load_bool = json_manager.safe_load(file_path)
        if not load_bool:
            print("ERROR: File could not be loaded!")
            continue
        return contents

def action_update_advancement():
    while True:
        contents = retrieve_json_file_contents("Advancement file path to update (leave blank to exit): ")
        if not contents:
            break
        contents = advancement.advancement(contents, option_manager.get_version())
        print("")
        log("Updated advancement:")
        print("")
        log(json.dumps(contents, indent=4))
        print("")

def action_update_loot_table():
    while True:
        contents = retrieve_json_file_contents("Loot table file path to update (leave blank to exit): ")
        if not contents:
            break
        contents = loot_table.loot_table(contents, option_manager.get_version())
        print("")
        log("Updated loot table:")
        print("")
        log(json.dumps(contents, indent=4))
        print("")

def action_update_item_modifier():
    while True:
        contents = retrieve_json_file_contents("Item modifier file path to update (leave blank to exit): ")
        if not contents:
            break
        contents = item_modifier.item_modifier(contents, option_manager.get_version())
        print("")
        log("Updated item modifier:")
        print("")
        log(json.dumps(contents, indent=4))
        print("")

def action_update_predicate():
    while True:
        contents = retrieve_json_file_contents("Predicate file path to update (leave blank to exit): ")
        if not contents:
            break
        contents = predicate.predicate(contents, option_manager.get_version())
        print("")
        log("Updated predicate:")
        print("")
        log(json.dumps(contents, indent=4))
        print("")

def action_update_recipe():
    while True:
        contents = retrieve_json_file_contents("Recipe file path to update (leave blank to exit): ")
        if not contents:
            break
        contents = recipe.recipe(contents, option_manager.get_version())
        print("")
        log("Updated recipe:")
        print("")
        log(json.dumps(contents, indent=4))
        print("")




if __name__ == "__main__":
    program()