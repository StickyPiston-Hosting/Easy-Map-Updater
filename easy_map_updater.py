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
    (sys.version_info[0] == 3 and sys.version_info[1] >= 9)
    or
    (sys.version_info[0] > 3)
):
    print("\n\nERROR: Easy Map Updater requires Python 3.9 or newer!")
    input()
    exit()
    
    
    
# Import things

import shutil
import json
from enum import Enum
from pathlib import Path
from lib.log import log
from lib import finalize
from lib import data_pack
from lib import resource_pack
from lib import option_manager
from lib.data_pack_files import command
from lib.data_pack_files import json_text_component
from lib.data_pack_files import breakpoints
from lib.data_pack_files.restore_behavior import tag_replacements
from lib.data_pack_files.restore_behavior import spawner_bossbar
from lib.data_pack_files.restore_behavior import ore_fixer
from lib.data_pack_files.restore_behavior import area_effect_cloud_killer
from lib.data_pack_files.restore_behavior import firework_damage_canceler
from lib.data_pack_files.restore_behavior import unwaterloggable_leaves
from lib.data_pack_files.restore_behavior import old_adventure_mode
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

    DP_UNZIP = "dp.unzip"
    DP_ZIP = "dp.zip"
    DP_LOG = "dp.log"
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
    DP_BREAK = "dp.break"

    WORLD_ORIGINAL = "world.original"
    WORLD_ORIGINAL_PLAY = "world.original.play"
    WORLD_RELOAD = "world.reload"
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

    LICENSE = "license"
    EXIT = "exit"

    DEBUG_CMD = "debug.cmd"
    DEBUG_JSON = "debug.json"

actions: dict[str, dict[str, str]]



# Define functions

def program():
    # Show title
    log("")
    log("Easy Map Updater")
    log("- By Dominexis, and StickyPiston Hosting")

    # Extract input
    load_session()
    save_session()
    log("")
    list_actions()

    # Program loop
    while True:
        # Get action
        action = input("\nAction: ")
        if action not in actions:
            log("ERROR: Must be a valid action!")
            continue
        log("")

        # Run action
        actions[action]["show"] = True
        actions[action]["function"]()

        log("")
        save_session()
        list_actions()

def load_session():
    global actions
    session_path = PROGRAM_PATH / "session.json"
    action_reset()
    if not session_path.exists():
        return
    with session_path.open("r", encoding="utf-8") as file:
        session: dict[str, bool] = json.load(file)
    for action in session:
        if action in actions:
            actions[action]["show"] = session[action]

def save_session():
    session: dict[str, bool] = {}
    for action in actions:
        session[action] = actions[action]["show"]
    session_path = PROGRAM_PATH / "session.json"
    with session_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(session, file, indent=4)

def list_options():
    log("Options:")
    options = option_manager.get_options()
    for key in options:
        log(f"{key}: {options[key]}")

def list_actions():
    log("Actions:")
    for action in actions:
        if action == Action.LICENSE.value:
            log("")
        if actions[action]["show"]:
            log(f" {action}) {' '*max(21-len(action), 0)}{actions[action]['name']}")



# Define actions

def action_reset():
    global actions
    actions = {
        Action.RESET.value:                 { "show": True,  "function": action_reset, "name": "Reset actions" },
        Action.ALL.value:                   { "show": True,  "function": action_show_all_actions, "name": "Show all actions" },
        Action.UPDATE.value:                { "show": True,  "function": action_update, "name": "Update map" },
        Action.SCAN.value:                  { "show": True,  "function": action_scan_world, "name": "Scans your world to gather relevant information" },

        Action.RP_IMPORT.value:             { "show": False, "function": action_import_resource_pack, "name": "Import resource pack from world" },
        Action.RP_ORIGINAL.value:           { "show": False, "function": action_prepare_original_copy_resource_pack, "name": "Prepare original copy of resource pack" },
        Action.RP_RELOAD.value:             { "show": False, "function": action_reload_from_original_resource_pack, "name": "Reload resource pack from original copy" },
        Action.RP_PURGE.value:              { "show": False, "function": action_purge_vanilla_assets, "name": "Purge vanilla assets from resource pack" },
        Action.RP_UPDATE.value:             { "show": False, "function": action_update_resource_pack, "name": "Update resource pack" },
        Action.RP_FIX.value:                { "show": False, "function": action_fix_resource_pack, "name": "Fix resource pack" },

        Action.DP_UNZIP.value:              { "show": False, "function": action_unzip_data_packs, "name": "Unzip data packs" },
        Action.DP_LOG.value:                { "show": False, "function": action_log_data_packs, "name": "Log data packs" },
        Action.DP_VANILLA.value:            { "show": False, "function": action_fix_disabled_vanilla, "name": "Fix disabled vanilla data pack (must be done before merging)" },
        Action.DP_MERGE.value:              { "show": False, "function": action_merge_data_packs, "name": "Merge data packs" },
        Action.DP_STORED_FUNCTION.value:    { "show": False, "function": action_stored_functions, "name": "Extract stored functions" },
        Action.DP_STORED_ADVANCEMENT.value: { "show": False, "function": action_stored_advancements, "name": "Extract stored advancements" },
        Action.DP_ADVANCEMENT.value:        { "show": False, "function": action_disable_advancements, "name": "Disable advancements (if one of the data packs makes them all impossible)" },
        Action.DP_RECIPE.value:             { "show": False, "function": action_disable_recipes, "name": "Disable recipes (if one of the data packs makes them all impossible)" },

        Action.WORLD_ORIGINAL.value:        { "show": False, "function": action_prepare_original_copy_world, "name": "Prepare original copy of world (do this before opening the world)" },
        Action.WORLD_ORIGINAL_PLAY.value:   { "show": False, "function": action_prepare_original_play_copy, "name": "Prepare play version of original copy of world" },
        Action.WORLD_RELOAD.value:          { "show": False, "function": action_reload_from_original_world, "name": "Reload world from original copy" },
        
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

        Action.CMD_READ.value:              { "show": False, "function": action_read_commands, "name": "Read command block data" },
        Action.CMD_UPDATE.value:            { "show": False, "function": action_update_commands, "name": "Update command block data" },
        Action.CMD_WRITE.value:             { "show": False, "function": action_write_commands, "name": "Write command block data" },
        Action.CMD_CLEAR.value:             { "show": False, "function": action_clear_command_block_helper, "name": "Clear command block helper" },
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
        Action.CLEAN.value:                 { "show": False, "function": action_clean_up, "name": "Clean up files (remove worlds and resource pack)" },

        Action.LICENSE.value:               { "show": True,  "function": action_license, "name": "Show software license" },
        Action.EXIT.value:                  { "show": True,  "function": action_exit, "name": "Exit program" },

        Action.DEBUG_CMD.value:             { "show": True,  "function": action_update_single_command, "name": "Update single command (for testing)" },
        Action.DEBUG_JSON.value:            { "show": True,  "function": action_update_json_text_component, "name": "Update JSON text component (for testing)" }
    }
    log("")
    list_options()

def action_show_all_actions():
    global actions
    for action in actions:
        actions[action]["show"] = True



def action_update(): # Needs confirmation
    log("Updating map")

    # Make sure that world exists
    world: Path = MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    og_world: Path = MINECRAFT_PATH / "saves" / ( option_manager.get_map_name() + " - Original" )
    resource_pack: Path = MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack()
    if not world.exists():
        log("ERROR: World does not exist!")
        return

    # Get confirmation
    log(f'This action will update: {world.as_posix()}')
    confirm = input("Is this okay? (Y/N): ")
    if confirm not in ["Y", "y"]:
        log("Action canceled")
        return
    
    # Reload world if original world exists
    if og_world.exists():
        log("")
        confirm = input("Original copy of world found, do you wish to update from the original? (Y/N): ")
        if confirm in ["y", "Y"]:
            action_reload_from_original_world(False)

    # Scan world
    scan_world_booleans = finalize.scan_world(
        world,
        resource_pack
    )
    scan_again = False
    zipped_data_packs = False
    if scan_world_booleans["resource_pack"]:
        action_import_resource_pack()
        scan_again = True
    if scan_world_booleans ["zipped_data_packs"]:
        action_unzip_data_packs()
        scan_again = True
        zipped_data_packs = True
    if scan_world_booleans ["stored_functions"]:
        action_stored_functions()
        scan_again = True
    if scan_world_booleans ["stored_advancements"]:
        action_stored_advancements()
        scan_again = True
    if scan_again:
        scan_world_booleans = finalize.scan_world(
            world,
            resource_pack
        )

    version: int = option_manager.get_version()

    # Update resource pack
    if resource_pack.exists():
        action_prepare_original_copy_resource_pack(False)
        action_update_resource_pack()

    # Update data pack
    if scan_world_booleans["disabled_vanilla"]:
        action_fix_disabled_vanilla()
    if scan_world_booleans["advancements"]:
        log("")
        log("Advancements in the 'minecraft' namespace were found, which may be used to disable advancements in older maps")
        confirm = input("Do you wish to disable them via pack.mcmeta filters instead? (Y/N): ")
        if confirm in ["y", "Y"]:
            action_disable_advancements(False)
    if scan_world_booleans["recipes"]:
        log("")
        log("Recipes in the 'minecraft' namespace were found, which may be used to disable recipes in older maps")
        confirm = input("Do you wish to disable them via pack.mcmeta filters instead? (Y/N): ")
        if confirm in ["y", "Y"]:
            action_disable_recipes(False)
    action_prepare_original_copy_world(False)
    action_update_data_packs(False)

    # Optimize world
    log("")
    log("The world must now be optimized, boot up Minecraft and optimize the main copy of your world")
    while True:
        confirm = input("Confirm when it has been optimized (Y): ")
        if confirm in ["y", "Y"]:
            break

    # Fix world
    if version <= 1605:
        action_entity_extract(False)
    fix_world_booleans = action_fix_world(False)

    # Update command blocks
    action_read_commands(False)
    action_update_commands(False)
    action_write_commands(False)

    # Add various things to the world to restore old behavior
    if fix_world_booleans["spawner_bossbar"]:
        action_spawner_bossbar()
    if version <= 710:
        action_old_adventure_mode()
    if version <= 809:
        action_area_effect_cloud_killer()
    if version <= 1100:
        action_firework_damage_canceler()
    if version <= 1202:
        action_tag_replacements()
    if version <= 1502:
        action_illegal_chunk()
    if version <= 1605:
        action_ore_fixer()
    if version <= 1802:
        action_unwaterloggable_leaves()

    # Finalize map
    log("")
    confirm = input("Do you wish to remove player score data from your map? (Y/N): ")
    if confirm in ["y", "Y"]:
        action_get_player_names()
        log("")
        log("Player names have been logged in player_names.json")
        log("Go through the list and remove non-player names from the list (e.g. fakeplayer variable names)")
        while True:
            confirm = input("Confirm when the non-player names have been removed (Y): ")
            if confirm in ["y", "Y"]:
                break
    else:
        with (PROGRAM_PATH / "player_names.json").open("w", encoding="utf-8", newline="\n") as file:
            file.write("{}")
    action_finalize_map(False)
    if zipped_data_packs:
        action_zip_data_packs(False)
    if resource_pack.exists():
        action_export_resource_pack(False)
    action_prepare_play_copy(False)

    log("")
    log("Map updated")
    log("Join the play copy of the world and playtest it")

    global actions
    actions[Action.CLEAN.value]["show"] = True



def action_scan_world():
    booleans = finalize.scan_world(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack()
    )

    if not booleans["world"]:
        return

    global actions
    if booleans["resource_pack"]:
        actions[Action.RP_IMPORT.value]["show"] = True
    if booleans["disabled_vanilla"]:
        actions[Action.DP_VANILLA.value]["show"] = True
    if booleans["zipped_data_packs"]:
        actions[Action.DP_UNZIP.value]["show"] = True
    if booleans["stored_functions"]:
        actions[Action.DP_STORED_FUNCTION.value]["show"] = True
    if booleans["stored_advancements"]:
        actions[Action.DP_STORED_ADVANCEMENT.value]["show"] = True
    if booleans["advancements"]:
        actions[Action.DP_ADVANCEMENT.value]["show"] = True
    if booleans["recipes"]:
        actions[Action.DP_RECIPE.value]["show"] = True

    actions[Action.WORLD_ORIGINAL.value]["show"] = True



def action_import_resource_pack(manual: bool = True): # Needs confirmation
    resource_pack.import_pack(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack(),
        manual
    )

    global actions
    actions[Action.RP_IMPORT.value]["show"] = manual
    actions[Action.RP_ORIGINAL.value]["show"] = manual
    actions[Action.RP_PURGE.value]["show"] = manual

def action_export_resource_pack(manual: bool = True): # Needs confirmation
    resource_pack.export_pack(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack(),
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

    global actions
    actions[Action.DP_MERGE.value]["show"] = manual

def action_update_data_packs(manual: bool = True):
    data_pack.update(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        option_manager.get_version()
    )

    global actions
    if option_manager.get_version() <= 1202:
        actions[Action.DP_TAG.value]["show"] = manual

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

def action_stored_functions(manual: bool = True): # Needs confirmation
    data_pack.extract_stored_functions(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        MINECRAFT_PATH / "saves" / ( option_manager.get_map_name() + " - Original" ),
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

    global actions
    actions[Action.CMD_READ.value]["show"] = manual
    actions[Action.CMD_WRITE.value]["show"] = manual
    actions[Action.CMD_UPDATE.value]["show"] = manual
    actions[Action.CMD_CLEAR.value]["show"] = manual
    actions[Action.CMD_EXTRACT.value]["show"] = manual

def action_write_commands(manual: bool = True): # Needs confirmation
    command_blocks.write_commands(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        manual
    )

def action_update_commands(manual: bool = True):
    command_blocks.update_commands(
        option_manager.get_version()
    )

    global actions
    if option_manager.get_version() <= 1100:
        actions[Action.DP_FIREWORK.value]["show"] = manual
    if option_manager.get_version() <= 1202:
        actions[Action.DP_TAG.value]["show"] = manual

def action_clear_command_block_helper(): # Needs confirmation
    data_pack_path: Path = MINECRAFT_PATH / "saves" / option_manager.get_map_name() / "datapacks" / "command_block_helper"
    log(f'This action will delete: {data_pack_path.as_posix()}')
    confirm = input("Is this okay? (Y/N): ")
    if confirm not in ["Y", "y"]:
        log("Action canceled")
        return

    log("Clearing command block helper")

    if not data_pack_path.exists():
        log("ERROR: Command block helper does not exist!")
        return
    
    shutil.rmtree(data_pack_path)

    log("Command block helper cleared")

def action_extract_commands():
    command_blocks.extract_commands(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )



def action_get_player_names(manual: bool = True):
    finalize.get_player_names(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

    global actions
    actions[Action.FINAL.value]["show"] = manual

def action_finalize_map(manual: bool = True): # Needs confirmation
    finalize.finalize(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack(),
        manual
    )

    global actions
    actions[Action.WORLD_PLAY.value]["show"] = manual
    if actions[Action.DP_UNZIP.value]["show"]:
        actions[Action.DP_ZIP.value]["show"] = manual
    if actions[Action.RP_IMPORT.value]["show"]:
        actions[Action.RP_EXPORT.value]["show"] = manual
    actions[Action.CLEAN.value]["show"] = manual

def action_log_data_packs():
    finalize.log_data_packs(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )

    global actions
    actions[Action.DP_LOG.value]["show"] = True



def action_prepare_original_copy_world(manual: bool = True): # Needs confirmation
    log("Preparing original world copy")
    
    world: Path = MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    og_world: Path = MINECRAFT_PATH / "saves" / ( option_manager.get_map_name() + " - Original" )

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

    global actions
    actions[Action.WORLD_ORIGINAL_PLAY.value]["show"] = manual
    actions[Action.WORLD_RELOAD.value]["show"] = manual
    actions[Action.DP_UPDATE.value]["show"] = manual
    actions[Action.OPTIMIZE.value]["show"] = manual

def action_prepare_original_play_copy(): # Needs confirmation
    log("Preparing original play world copy")
    
    world: Path = MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()} - Original'
    play_world: Path = MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()} - Original - Play'

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
    og_world: Path = MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()} - Original'

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

    global actions
    actions[Action.WORLD_ORIGINAL_PLAY.value]["show"] = manual
    actions[Action.WORLD_RELOAD.value]["show"] = manual
    actions[Action.DP_UPDATE.value]["show"] = manual
    actions[Action.OPTIMIZE.value]["show"] = manual

def action_prepare_play_copy(manual: bool = True): # Needs confirmation
    log("Preparing play world copy")
    
    world: Path = MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    play_world: Path = MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()} - Play'

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

    global actions
    actions[Action.ADMIN_KICKBACK.value]["show"] = manual

def action_prepare_original_copy_resource_pack(manual: bool = True): # Needs confirmation
    log("Preparing original resource pack copy")
    
    resource_pack: Path = MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack()
    og_resource_pack: Path = MINECRAFT_PATH / "resourcepacks" / f'{option_manager.get_resource_pack()} - Original'

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

    global actions
    actions[Action.RP_UPDATE.value]["show"] = manual
    actions[Action.RP_RELOAD.value]["show"] = manual

def action_reload_from_original_resource_pack(): # Needs confirmation
    log("Reloading resource pack from original")
    
    resource_pack: Path = MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack()
    og_resource_pack: Path = MINECRAFT_PATH / "resourcepacks" / f'{option_manager.get_resource_pack()} - Original'

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
        MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()} - Original',
        option_manager.get_version(),
        manual
    )

    global actions
    if booleans["spawner_bossbar"]:
        actions[Action.DP_BOSSBAR.value]["show"] = manual
    if option_manager.get_version() <= 710:
        actions[Action.DP_ADVENTURE.value]["show"] = manual
    if option_manager.get_version() <= 809:
        actions[Action.DP_AEC_KILL.value]["show"] = manual
    if option_manager.get_version() <= 1605:
        actions[Action.DP_ORE_FIXER.value]["show"] = manual
    if option_manager.get_version() <= 1802:
        actions[Action.DP_WATER_LEAVES.value]["show"] = manual

    return booleans



def action_admin_kickback():
    admin_kickback.create_pack(
        MINECRAFT_PATH / "saves" / option_manager.get_map_name()
    )



def action_clean_up(): # Needs confirmation
    paths: list[Path] = [
        MINECRAFT_PATH / "saves" / option_manager.get_map_name(),
        MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()} - Original',
        MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()} - Play',
        MINECRAFT_PATH / "saves" / f'{option_manager.get_map_name()} - Original - Play',
        MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack(),
        MINECRAFT_PATH / "resourcepacks" / f'{option_manager.get_resource_pack()} - Original'
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

def action_debug_actions():
    log("Debug actions!")

def action_update_single_command():
    test_command = input("Command to update: ")
    log("")
    log(f'Old command: {test_command}')
    log(f'New command: {command.update(test_command, option_manager.get_version(), "test_command")}')

def action_update_json_text_component():
    test_component = input("JSON text component to update: ")
    log("")
    log(f'Old component: {test_component}')
    log(f'New component: {json_text_component.update(test_component, option_manager.get_version(), [], False)}')


    
program()