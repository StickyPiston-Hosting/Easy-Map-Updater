# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from typing import cast, Any
from pathlib import Path
from lib.log import log
from lib.data_pack_files import arguments
from lib.data_pack_files import target_selectors
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import nbt_paths
from lib.data_pack_files import nbt_tags_from_path
from lib.data_pack_files import nbt_types_from_path
from lib.data_pack_files import ids
from lib.data_pack_files import items
from lib.data_pack_files import blocks
from lib.data_pack_files import entities
from lib.data_pack_files import json_text_component
from lib.data_pack_files import particle
from lib.data_pack_files import miscellaneous
from lib.data_pack_files.command_helpers import block_nbt_modifier
from lib.data_pack_files.command_helpers import block_update_mitigator
from lib.data_pack_files.command_helpers import motion_canceler
from lib.data_pack_files.command_helpers import door_modifier
from lib.data_pack_files.command_helpers import falling_block_handler
from lib.data_pack_files.command_helpers import sign_merge_handler
from lib.data_pack_files.command_helpers import safe_nbt_interpret
from lib.data_pack_files.command_helpers import teleport_dismount
from lib.data_pack_files.restore_behavior import firework_damage_canceler
from lib.data_pack_files.restore_behavior import effect_overflow
from lib.region_files import illegal_chunk
from lib import defaults
from lib import utils



# Initialize variables

pack_version = defaults.PACK_VERSION
namespaced_id = ""

PROGRAM_PATH = Path(__file__).parent
with (PROGRAM_PATH / "command_tree.json").open("r", encoding="utf-8") as file:
    command_tree: dict[str, dict[str, str]] = json.load(file)



# Define functions

def update(line: str, version: int, function_id: str) -> str:
    # Assign version and function ID
    global pack_version
    pack_version = version
    global namespaced_id
    namespaced_id = function_id

    # Change version if ancient syntax is detected
    if pack_version >= 1300:
        for string in ["execute @", ",score_", "[score_", "scoreboard players tag", "scoreboard teams", ",r=", "[r=", ",rm=", "[rm=", ",c=", "[c="]:
            if string in line:
                log("Pack version changed to 1202 in:\n  " + namespaced_id + "\n  " + line)
                pack_version = 1202

    try:
        return command(line.strip()).strip()
    except Exception:
        log(f'A command from {namespaced_id} has thrown an error:\n\n{line.strip()}')
        utils.log_error()
        return line

def command(line: str) -> str:
    # Return if blank
    if len(line) == 0:
        return ""

    # Return commented version if the command begins with certain illegal characters
    if line[0] in [".", ","]:
        return "#" + line
    
    # Return command if a macro
    if line.startswith("$"):
        log(f'Macros are not yet handled: {line}')
        return line

    # Convert command
    command = parsed_command(arguments.parse(line, " ", pack_version >= 1400), True)
    if command.endswith("COMMAND_HELPER"):
        if namespaced_id == "commands.mcfunction":
            command = f'execute store result block ~ ~ ~ SuccessCount int 1 run {command[:-14]}'
        else:
            command = command[:-14]

    # Remove as @s
    segments = command.split(" as @s")
    for i in range(len(segments)-1):
        if segments[i].endswith("positioned") or segments[i].endswith("rotated"):
            segments[i] = segments[i] + " as @s"
            continue
        if segments[i+1].startswith("["):
            segments[i] = segments[i] + " if entity @s"

    return remove_run_execute("".join(segments).replace("positioned ~ ~ ~ ", "")).replace("at @s at @s ", "at @s ")

def remove_slash(line: str) -> str:
    if line == "":
        return line
    if line[0] == "/" and len(line) > 1:
        return line[1:]
    return line

def remove_run_execute(line: str) -> str:
    return line.replace("return run", "__RETURN_RUN__").replace(" run execute", "").replace("__RETURN_RUN__", "return run").replace("execute run ", "")

def parsed_command(argument_list: list[str], display_command: bool) -> str:
    # Skip if just whitespace
    if len(argument_list) == 0 or argument_list[0] == "":
        return ""

    # Print arguments if in debug mode
    if defaults.DEBUG_MODE and display_command:
        log(" ".join(argument_list))

    # Remove slash
    argument_list[0] = remove_slash(argument_list[0])

    # Flag stats command
    if argument_list[0] == "stats" and not defaults.FIXES["stats"]:
        log("WARNING: Stats fixer not enabled but stats have been found!")

    # Initialize issues list
    issues: list[dict[str, str | int]] = []

    return command_arguments(argument_list, command_tree, issues)


def command_arguments(argument_list: list[str], guide: list | dict[str, Any], issues: list[dict[str, str | int]]) -> str:
    # Get guide from array based on certain parameters
    if isinstance(guide, list):
        # Iterate through entries in the guide
        for entry in guide:
            boolean = True
            if "version" in entry:
                boolean = test_list_entry(entry["version"], pack_version, boolean)
            if "length" in entry:
                boolean = test_list_entry(entry["length"], len(argument_list), boolean)
            if "is_nbt" in entry:
                boolean = (
                    len(argument_list) > entry["is_nbt"] and
                    argument_list[entry["is_nbt"]] and
                    argument_list[entry["is_nbt"]][0] == "{"
                )
            if boolean:
                return command_arguments(argument_list, entry, issues)
        # Warn if no valid object was found
        if defaults.SEND_WARNINGS:
            log(f'WARNING: No branch found for: {" ".join(argument_list)}')
        return " ".join(argument_list)

    # Manage explicit branches
    if "index" in guide:
        return guide_branch(argument_list, guide, issues)

    # Return mapped arguments
    if "mapping" in guide:
        return guide_mapping(argument_list, guide, issues)

    # Sort through array if it is present
    if "array" in guide:
        return command_arguments(argument_list, guide["array"], issues)

    log(f'WARNING: Branch is undefined for: {" ".join(argument_list)}')
    if defaults.DEBUG_MODE:
        log(f'Current guide: {guide}')
    return " ".join(argument_list)

def test_list_entry(entry: dict[str, int] | int, value: int, boolean: bool) -> bool:
    if isinstance(entry, dict):
        if "max" in entry and value > entry["max"]:
            return False
        if "min" in entry and value < entry["min"]:
            return False
    if isinstance(entry, int) and value != entry:
        return False
    return boolean


def guide_branch(argument_list: list[str], guide: dict[str, Any], issues: list[dict[str, str | int]]) -> str:
    # Get index
    index: int = guide["index"]

    # Return if the branch is undefined
    lookup_guide: dict[str, Any]
    if len(argument_list) <= index or argument_list[index] not in guide["branches"]:
        # Check for wildcard branches first
        for branch in guide["branches"]:
            if "**" not in branch:
                continue
            if branch[-2:] == "**" and branch[:-2] in argument_list[index] and branch[:-2] == argument_list[index][:len(branch) - 2]:
                lookup_guide = guide["branches"][branch]
                break
            if branch[:2] == "**" and branch[2:] in argument_list[index] and branch[2:] == argument_list[index][2 - len(branch):]:
                lookup_guide = guide["branches"][branch]
                break
        else:
            if "else" not in guide:
                if defaults.SEND_WARNINGS:
                    log(f'WARNING: "{" ".join(argument_list)}" is not registered!')
                return " ".join(argument_list)
            # Use 'else' as the lookup guide
            lookup_guide = guide["else"]

    # Get lookup guide directly
    else:
        lookup_guide = guide["branches"][argument_list[index]]

    # Get reference from guide if lookup guide is a string
    if isinstance(lookup_guide, str):
        lookup_guide = guide["branches"][lookup_guide]

    # Explore the branch
    return command_arguments(argument_list, lookup_guide, issues)


def guide_mapping(argument_list: list[str], guide: dict[str, list | dict], issues: list[dict[str, str | int]]) -> str:
    # Get mapping
    mapping: list[str] = cast(list, guide["mapping"])

    # Get legend
    legend = get_legend(mapping, guide)

    # Get defaults
    defaults = {}
    if "defaults" in guide:
        defaults: dict[str, str] = cast(dict, guide["defaults"])

    # Compile new arguments list
    new_argument_list: list[str] = []
    for index in range(len(mapping)):
        # Get source
        source = get_source(argument_list, legend[index])

        # Insert default parameter
        if source == "":
            if str(index) in defaults:
                source = defaults[str(index)]
            else:
                break

        # Add argument to list
        new_argument_list.append(update_argument(source, mapping[index], issues))

    # Fix edge cases with helper functions
    return fix_helper_edge_case(new_argument_list, argument_list, issues)
    

def get_legend(mapping: list[str], guide: dict[str, Any]) -> list:
    # Get legend directly
    if "legend" in guide:
        return guide["legend"]

    # Get legend from legend array
    if "legend_array" in guide:
        for entry in guide["legend_array"]:
            bool = True
            if "max" in entry and pack_version > entry["max"]:
                bool = False
            if "min" in entry and pack_version < entry["min"]:
                bool = False
            if bool:
                return entry["legend"]

    # Set legend to direct mapping if all else fails
    return list(range(len(mapping)))


def get_source(argument_list: list[str], source: int | str | dict[str, Any]) -> str | dict[str, Any]:
    # Get source from arguments if a number
    if isinstance(source, int):
        return cast(str, get_argument(argument_list, source))

    # Convert sources into their arguments
    if isinstance(source, dict):
        out_source = source.copy()
        in_bounds = False
        for key in source:
            out_source[key] = get_argument(argument_list, source[key])
            if out_source[key] != "":
                in_bounds = True
        if not in_bounds:
            return ""
        return out_source
    
    # Return explicit string
    return source
    

def get_argument(argument_list: list[str], source: int | str | dict[str, Any]) -> str | list[str] | bool:
    # Get argument from list if source is a number
    if isinstance(source, int) and not isinstance(source, bool):
        # Get argument from list if source is in range
        if source < len(argument_list):
            return argument_list[source]
        # Return empty string otherwise
        return ""

    # Get range of arguments if source is a dict
    if isinstance(source, dict):
        if "min" in source and "max" in source:
            if len(argument_list) < source["max"]:
                return ""
            return argument_list[source["min"]: source["max"]+1]
        if "min" in source:
            if len(argument_list) < source["min"]:
                return ""
            return argument_list[source["min"]:]
        if "max" in source:
            if len(argument_list) < source["max"]:
                return ""
            return argument_list[:source["max"]+1]
        return ""

    # Return boolean
    return source



def update_argument(argument: str | dict[str, Any], argument_type: str, issues: list[dict[str, str | int]]) -> str:
    # Return carry arguments
    if argument_type == "carry":
        return cast(str, argument)

    # Return arguments based on type
    if argument_type in ARGUMENT_FUNCTIONS:
        argument_tuple = ARGUMENT_FUNCTIONS[argument_type]
        if argument_tuple[1] == None:
            return argument_tuple[0](argument, pack_version, issues)
        return argument_tuple[0](argument, pack_version, issues, argument_tuple[1])

    # Report that argument type was not found
    if defaults.SEND_WARNINGS:
        log(f'WARNING: Argument type "{argument_type}" is not defined!')
    return cast(str, argument)


def execute_command(argument: dict[str, list[str] | bool] | list[str], version: int, issues: list[dict[str, str | int]]):
    # Initialize parameters
    execute = False

    # Extract arguments if a dict
    if isinstance(argument, dict):
        if "execute" in argument:
            execute = cast(bool, argument["execute"])
        argument = cast(list, argument["argument"])

    # Prefix with "execute"
    if execute:
        argument.insert(0, "execute")

    # Return command
    if argument == ["execute"]:
        return "execute"
    return parsed_command(argument, False)

def command_string(command: str, version: int, issues: list[dict[str, str | int]]):
    return update(command, version, "NBT")



def fix_helper_edge_case(argument_list: list[str], old_argument_list: list[str], issues: list[dict[str, str | int]]) -> str:
    # Remove empty NBT from summon command
    if (
        len(argument_list) >= 6 and
        argument_list[0] == "summon" and
        argument_list[5] == "{}"
    ):
        argument_list.pop(5)

    # Fix comparator block updates (FIND VERSION WHERE IT IS NECESSARY)
    if (
        pack_version <= 1202 and
        argument_list[0] == "setblock" and
        len(argument_list) > 4 and
        argument_list[4].split("{")[0].split("[")[0] == "minecraft:comparator"
    ):
        return block_update_mitigator.handle_comparator_setblock(argument_list)
    
    # Fix pre-1.21.2 bugs
    if pack_version <= 2101:
        # Fix pre-1.21.2 teleports not dismounting riders
        if (
            len(argument_list) > 5 and
            argument_list[0] in ["tp", "teleport"]
        ):
            return teleport_dismount.handle_teleport(argument_list)
    
    # Fix pre-1.20.5 bugs
    if pack_version <= 2004:
        # Fix pre-1.20.5 handling of effects
        if argument_list[0] == "effect":
            if (
                len(argument_list) >= 4 and
                argument_list[1] == "give" and
                argument_list[3] in effect_overflow.SPECIAL_EFFECTS
            ):
                return effect_overflow.add_effect(argument_list)
            if (
                len(argument_list) >= 2 and
                argument_list[1] == "clear"
            ):
                if (
                    len(argument_list) >= 4 and
                    argument_list[3] in effect_overflow.SPECIAL_EFFECTS
                ):
                    return effect_overflow.remove_effect(argument_list)
                if len(argument_list) <= 3:
                    return effect_overflow.remove_all_effects(argument_list)
    
    # Fix pre-1.20 bugs
    if pack_version <= 1904:
        # Fix pre-1.20 handling of /data merge on signs
        if (
            len(argument_list) >= 7 and
            argument_list[0] == "data" and
            argument_list[1] == "merge" and
            argument_list[2] == "block"
        ):
            block_nbt: dict[str, Any] = nbt_tags.unpack(argument_list[6])
            old_block_nbt = nbt_tags.unpack(old_argument_list[6 if old_argument_list[0] == "data" else 4])
            if "front_text" in block_nbt and "front_text" not in old_block_nbt:
                return sign_merge_handler.handle_merge(argument_list, block_nbt, old_block_nbt)
    
    # Fix pre-1.18 bugs
    if pack_version <= 1702:
        # Fix pre-1.18 handling of falling blocks removing blocks and not spawning Time:0 versions
        if (
            len(argument_list) >= 6 and
            argument_list[0] == "summon" and
            argument_list[1] == "minecraft:falling_block"
        ):
            entity_nbt: dict[str, nbt_tags.TypeInt] = nbt_tags.unpack(argument_list[5])
            falling_block_time: int = 0
            if "Time" in entity_nbt:
                falling_block_time = entity_nbt["Time"].value
            if falling_block_time == 0:
                return falling_block_handler.handle_time_0(argument_list, entity_nbt)
            return falling_block_handler.handle_non_time_0(argument_list, entity_nbt)
        
    # Fix pre-1.16 bugs
    if pack_version <= 1502:
        if len(argument_list) >= 5 and argument_list[0] == "setblock":
            block = argument_list[4].split("{")[0].split("[")
            # Fix pre-1.16 handling of illegal block states
            if (
                (
                    len(block) > 1 and
                    block[0].endswith("_stairs") and
                    (
                        "outer_right" in block[1] or
                        "outer_left"  in block[1] or
                        "inner_right" in block[1] or
                        "inner_left"  in block[1]
                    )
                ) or
                (
                    block[0] == "minecraft:cactus"
                )
            ):
                return illegal_chunk.replace_command(argument_list)
            
            # Fix pre-1.16 doors being modified by setblock
            if block[0].endswith("_door"):
                return door_modifier.handle_doors(argument_list)
    
    # Fix pre-1.13 testfor handling of SuccessCount
    if (
        pack_version <= 1202 and
        len(argument_list) == 4 and
        argument_list[0] == "execute" and
        argument_list[1] == "if" and
        argument_list[2] == "entity"
    ):
        return f'execute store result block ~ ~ ~ SuccessCount int 1 if entity {argument_list[3]}'

    # Fix pre-1.12 block NBT modifications
    if pack_version <= 1102:
        if argument_list[0] == "setblock":
            if len(argument_list) > 4 and "{" in argument_list[4]:
                return block_nbt_modifier.handle_setblock(argument_list)

        if argument_list[0] == "fill":
            if len(argument_list) > 7 and "{" in argument_list[7]:
                return block_nbt_modifier.handle_fill(argument_list)
            
    # Fix pre-1.11 bugs
    if pack_version <= 1002:
        # Fix pre-1.11 fireworks damaging players
        if (
            argument_list[0] == "summon" and
            argument_list[1] == "minecraft:firework_rocket"
        ):
            return firework_damage_canceler.cancel_damage(argument_list)

        # Fix pre-1.11 NBTless item spawning
        if (
            argument_list[0] == "summon" and
            argument_list[1] == "minecraft:item"
        ):
            if len(argument_list) < 5:
                argument_list = ["summon", "minecraft:item", "~", "~", "~", '{Item:{id:"minecraft:stone",Count:1b}}']
            elif len(argument_list) < 6:
                argument_list.append('{Item:{id:"minecraft:stone",Count:1b}}')
            elif argument_list[5] == "":
                argument_list[5] = '{Item:{id:"minecraft:stone",Count:1b}}'
    
    # Fix pre-1.10 teleport canceling motion
    if pack_version <= 904:
        if (
            len(argument_list) >= 9 and
            argument_list[0] == "execute" and
            argument_list[4] == "data" and
            argument_list[5] == "merge" and
            argument_list[6] == "entity" and
            "Motion" in nbt_tags.unpack_compound(argument_list[8])
        ):
            return motion_canceler.handle_motion_modification(argument_list)
        if (
            (argument_list[0] == "execute" and "teleport" in argument_list) or
            argument_list[0] == "teleport"
        ):
            return motion_canceler.handle_teleport(argument_list)
    
    # Fix pre-1.9 clone breaking blocks
    if (
        pack_version <= 809 and
        defaults.FIXES["clean_clone"] and
        argument_list[0] == "clone"
    ):
        return block_update_mitigator.handle_clean_clone(argument_list)
    
    # Remove illegal particles
    if (
        len(argument_list) > 1 and
        argument_list[0] == "particle" and
        argument_list[1] in ["minecraft:depthsuspend", "minecraft:depthSuspend", "minecraft:footstep"]
    ):
        return "#" + " ".join(argument_list)
    
    # Move comment hash back through an execute chain
    if (
        len(argument_list) > 2 and
        argument_list[0] == "execute" and
        argument_list[-1].startswith("#")
    ):
        argument_list[-1] = argument_list[-1][1:]
        return "#" + " ".join(argument_list)
    


    # Process issues list
    safe_nbt_interpret_issues: list[dict[str, str | int]] = []
    for issue in issues:
        if issue["type"] == "safe_nbt_interpret":
            safe_nbt_interpret_issues.append(issue)

    if len(safe_nbt_interpret_issues) > 0:
        return safe_nbt_interpret.handle_interpret(argument_list, safe_nbt_interpret_issues)



    # Return list of arguments
    return " ".join(argument_list)



ARGUMENT_FUNCTIONS: dict[str, tuple] = {
    "advancement": ( miscellaneous.advancement, None ),
    "attribute": ( miscellaneous.attribute, None ),
    "attribute_id": ( miscellaneous.attribute_id, None ),
    "attribute_modifier_operation": ( miscellaneous.attribute_modifier_operation, None ),
    "banner_color": ( miscellaneous.banner_color, None ),
    "banner_pattern": ( miscellaneous.banner_pattern, None ),
    "biome": ( ids.biome, None ),
    "block": ( blocks.update_from_command, None),
    "block_nbt": ( nbt_tags.update, "block" ),
    "block_nbt_from_path": ( nbt_tags_from_path.update, "block" ),
    "block_nbt_path": ( nbt_paths.update, "block" ),
    "command": ( execute_command, None),
    "command_string": ( command_string, None ),
    "coordinate": ( miscellaneous.coordinate, None),
    "coord_map_to_array": ( miscellaneous.coord_map_to_array, None ),
    "difficulty": ( miscellaneous.difficulty, None ),
    "dimension": ( miscellaneous.dimension, None ),
    "effect": ( ids.effect, None),
    "effect_duration": ( miscellaneous.effect_duration, None),
    "effect_time": ( miscellaneous.effect_time, None),
    "enchantment": ( ids.enchantment, None ),
    "entity": ( entities.update, None),
    "entity_nbt": ( nbt_tags.update, "entity" ),
    "entity_nbt_from_path": ( nbt_tags_from_path.update, "entity" ),
    "entity_nbt_path": ( nbt_paths.update, "entity" ),
    "experience_type": ( miscellaneous.experience_type, None ),
    "experience_value": ( miscellaneous.experience_value, None ),
    "fill_mode": ( miscellaneous.fill_mode, None ),
    "function": ( miscellaneous.function_call, None ),
    "gamemode": ( miscellaneous.gamemode, None ),
    "gamerule": ( miscellaneous.gamerule, None ),
    "hangable_facing": ( miscellaneous.hangable_facing, None ),
    "int_coordinate": ( miscellaneous.int_coordinate, None ),
    "item": ( items.update_from_command, None ),
    "item_read": ( items.update_from_command_read, None ),
    "join_text": ( miscellaneous.join_text, None ),
    "json_text_component": ( json_text_component.update, False ),
    "json_text_component_merge": ( json_text_component.update_merge, False ),
    "json_text_component_mangled": ( json_text_component.update, True ),
    "loot_table": ( miscellaneous.loot_table, None ),
    "nbt": ( nbt_tags.update, "arbitrary" ),
    "nbt_path": ( nbt_paths.update, "arbitrary" ),
    "nbt_type": ( nbt_types_from_path.update, None ),
    "particle": ( particle.update_from_command, None ),
    "particle_mode": ( miscellaneous.particle_mode, None ),
    "particle_nbt": ( particle.update_from_nbt, None ),
    "pitch": ( miscellaneous.pitch, None ),
    "poi": ( ids.structure, None ),
    "predicate": ( miscellaneous.predicate, None ),
    "recipe": ( miscellaneous.recipe, None ),
    "say_text": ( miscellaneous.say_text, None ),
    "scoreboard_objective_criteria": ( ids.scoreboard_objective_criteria, None),
    "scoreboard_objective_display_slot": ( miscellaneous.scoreboard_objective_display_slot, None ),
    "scoreboard_range": ( miscellaneous.scoreboard_range, None ),
    "setblock_mode": ( miscellaneous.setblock_mode, None ),
    "slot": ( miscellaneous.slot, None),
    "sound_event": ( ids.sound_event, None ),
    "structure": ( ids.structure, None ),
    "target_selector": ( target_selectors.update, False ),
    "target_selector_list": ( target_selectors.update, False ),
    "target_selector_single": ( target_selectors.update, True ),
    "team_setting": ( miscellaneous.team_setting, None ),
    "uuid_from_string": ( miscellaneous.uuid_from_string, None ),
    "world_border_coordinate": ( miscellaneous.world_border_coordinate, None ),
    "world_border_diameter": ( miscellaneous.world_border_diameter, None ),
    "yaw": ( miscellaneous.yaw, None )
}