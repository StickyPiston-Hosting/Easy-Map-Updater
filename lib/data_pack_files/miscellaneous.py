# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import math
import json
from lib.log import log
from lib import defaults
from lib import utils
from lib.data_pack_files import arguments
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import target_selectors
from lib.data_pack_files import tables
from lib.data_pack_files import predicate as predicate_lib
from lib.data_pack_files.restore_behavior import loot_table_replacements
from lib import option_manager
from lib import json_manager
import easy_map_updater



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def advancement(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    # Assign version
    global pack_version
    pack_version = version

    if pack_version <= 1202 and defaults.SEND_WARNINGS:
        log("WARNING: Advancements are not handled for 1.12!")

    return namespace(name)

def attribute(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    # Assign version
    global pack_version
    pack_version = version

    # Return if a macro token
    if isinstance(name, str) and is_macro_token(name):
        return name

    name = namespace(name)

    # Attribute IDs changed in 1.16
    id_array = tables.ATTRIBUTE_IDS
    if name in id_array:
        name = id_array[name]

    # Attribute IDs changed again in 1.20.5
    id_array = {
        "minecraft:horse.jump_strength": "minecraft:generic.jump_strength"
    }
    if name in id_array:
        name = id_array[name]

    # Attribute IDs had their prefixes removed in 1.21.2
    for prefix in ["generic.", "player.", "zombie."]:
        if name.split(":")[-1].startswith(prefix):
            name = f"{name.split(":")[0]}:{name.split(":")[-1][len(prefix):]}"
            break

    return name

def attribute_id(value: str, version: int, issues: list[dict[str, str | int]]) -> str:
    # Return if a macro token
    if isinstance(value, str) and is_macro_token(value):
        return value

    if version <= 2006:
        return namespace(utils.uuid_from_int_array(utils.uuid_from_string(value)))
    return namespace(value)

def attribute_modifier_operation(operation: str | int | nbt_tags.TypeInt, version: int, issues: list[dict[str, str | int]]) -> str:
    # Assign version
    global pack_version
    pack_version = version

    if isinstance(operation, nbt_tags.TypeInt):
        operation = operation.value

    # Attribute modifier operations were changed in 1.20.5
    id_array = {
        "add": "add_value",
        "multiply_base": "add_multiplied_base",
        "multiply": "add_multiplied_total",
        0: "add_value",
        1: "add_multiplied_base",
        2: "add_multiplied_total"
    }
    if operation in id_array:
        operation = id_array[operation]

    return str(operation)

def banner_color(name: nbt_tags.TypeInt, version: int, issues: list[dict[str, str | int]]) -> str:
    if version <= 1202:
        return color(15 - name.value)
    return color(name.value)

def banner_color_numeric(name: nbt_tags.TypeInt, version: int) -> nbt_tags.TypeInt:
    if version <= 1202:
        return nbt_tags.TypeInt(15 - name.value)
    return name

def banner_pattern(pattern: str, version: int, issues: list[dict[str, str | int]]) -> str:
    if version <= 2004:
        id_array = {
            "b":    "minecraft:base",
            "bs":   "minecraft:stripe_bottom",
            "ts":   "minecraft:stripe_top",
            "ls":   "minecraft:stripe_left",
            "rs":   "minecraft:stripe_right",
            "cs":   "minecraft:stripe_center",
            "ms":   "minecraft:stripe_middle",
            "drs":  "minecraft:stripe_downright",
            "dls":  "minecraft:stripe_downleft",
            "ss":   "minecraft:small_stripes",
            "cr":   "minecraft:cross",
            "sc":   "minecraft:straight_cross",
            "ld":   "minecraft:diagonal_left",
            "rud":  "minecraft:diagonal_right",
            "lud":  "minecraft:diagonal_up_left",
            "rd":   "minecraft:diagonal_up_right",
            "vh":   "minecraft:half_vertical",
            "vhr":  "minecraft:half_vertical_right",
            "hh":   "minecraft:half_horizontal",
            "hhb":  "minecraft:half_horizontal_bottom",
            "bl":   "minecraft:square_bottom_left",
            "br":   "minecraft:square_bottom_right",
            "tl":   "minecraft:square_top_left",
            "tr":   "minecraft:square_top_right",
            "bt":   "minecraft:triangle_bottom",
            "tt":   "minecraft:triangle_top",
            "bts":  "minecraft:triangles_bottom",
            "tts":  "minecraft:triangles_top",
            "mc":   "minecraft:circle",
            "mr":   "minecraft:rhombus",
            "bo":   "minecraft:border",
            "cbo":  "minecraft:curly_border",
            "bri":  "minecraft:bricks",
            "gra":  "minecraft:gradient",
            "gru":  "minecraft:gradient_up",
            "cre":  "minecraft:creeper",
            "sku":  "minecraft:skull",
            "flo":  "minecraft:flower",
            "moj":  "minecraft:mojang",
            "glb":  "minecraft:globe",
            "pig":  "minecraft:piglin",
        }
        if pattern in id_array:
            return id_array[pattern]
    return pattern

def color(index: int) -> str:
    return [
        "white",
        "orange",
        "magenta",
        "light_blue",
        "yellow",
        "lime",
        "pink",
        "gray",
        "light_gray",
        "cyan",
        "purple",
        "blue",
        "brown",
        "green",
        "red",
        "black"
    ][min(max(index, 0), 15)]

def coordinate(coord: str, version: int, issues: list[dict[str, str | int]]) -> str:
    return coord.replace("+", "")

def coord_map_to_array(coordinates: dict[str, nbt_tags.TypeInt], version: int, issues: list[dict[str, str | int]]) -> nbt_tags.TypeIntArray:
    new_coordinates = {
        "X": nbt_tags.TypeInt(0),
        "Y": nbt_tags.TypeInt(0),
        "Z": nbt_tags.TypeInt(0),
    }
    for axis in ["X", "Y", "Z"]:
        if axis in coordinates:
            new_coordinates[axis] = coordinates[axis]
    return nbt_tags.TypeIntArray([
        nbt_tags.TypeInt(new_coordinates["X"].value),
        nbt_tags.TypeInt(new_coordinates["Y"].value),
        nbt_tags.TypeInt(new_coordinates["Z"].value),
    ])

def coord_map_to_array_double(coordinates: dict[str, nbt_tags.TypeDouble], version: int, issues: list[dict[str, str | int]]) -> nbt_tags.TypeList:
    new_coordinates = {
        "x": nbt_tags.TypeDouble(0),
        "y": nbt_tags.TypeDouble(0),
        "z": nbt_tags.TypeDouble(0),
    }
    for axis in ["x", "y", "z"]:
        if axis in coordinates:
            new_coordinates[axis] = coordinates[axis]
    return nbt_tags.TypeList([
        nbt_tags.TypeDouble(new_coordinates["x"].value),
        nbt_tags.TypeDouble(new_coordinates["y"].value),
        nbt_tags.TypeDouble(new_coordinates["z"].value),
    ])

def difficulty(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    id_array = {
        "0": "peaceful",
        "1": "easy",
        "2": "normal",
        "3": "hard",
        "p": "peaceful",
        "e": "easy",
        "n": "normal",
        "h": "hard"
    }
    if name in id_array:
        name = id_array[name]
    return name

def dimension(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    return name.lower()

def effect_duration(duration: nbt_tags.TypeInt | str, version: int, issues: list[dict[str, str | int]]) -> nbt_tags.TypeInt:
    if isinstance(duration, str):
        return nbt_tags.TypeInt(-1)
    return duration

def effect_time(argument: str, version: int, issues: list[dict[str, str | int]]) -> str:
    if argument == "infinite":
        return argument
    if not argument.isnumeric():
        return "1"
    if int(argument) == 0:
        return "1"
    return argument

def entity_id_from_item(item_id: str) -> str:
    if item_id.endswith("_spawn_egg"):
        return namespace(item_id[:-10])
    if item_id.endswith("_bucket"):
        return namespace(item_id[:-7])
    elif namespace(item_id) in [
        "minecraft:armor_stand",
    ]:
       return namespace(item_id)
    return "minecraft:pig"

def experience_type(value: str, version: int, issues: list[dict[str, str | int]]) -> str:
    if value[-1] in ["l", "L"]:
        return "levels"
    return "points"

def experience_value(value: str, version: int, issues: list[dict[str, str | int]]) -> str:
    if value == "":
        return ""
    if value[-1] in ["l", "L"]:
        value = value[:-1]
    if len(value) <= 1:
        return value
    if value[0] == "+":
        value = value[1:]
    return value

def fill_mode(argument: str, version: int, issues: list[dict[str, str | int]]) -> str:
    if argument not in ["destroy", "hollow", "keep", "outline", "replace", "strict"]:
        return "replace"
    return argument

def function_call(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    return name.lower()

def gamemode(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    id_array = {
        "0":   "survival",
        "1":   "creative",
        "2":   "adventure",
        "3":   "spectator",
        "!0":  "!survival",
        "!1":  "!creative",
        "!2":  "!adventure",
        "!3":  "!spectator",
        "s":   "survival",
        "c":   "creative",
        "a":   "adventure",
        "sp":  "spectator",
        "!s":  "!survival",
        "!c":  "!creative",
        "!a":  "!adventure",
        "!sp": "!spectator"
    }
    if name in id_array:
        name = id_array[name]
    return name

def gamerule(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    return name

def hangable_facing(direction: nbt_tags.TypeInt, version: int, issues: list[dict[str, str | int]]) -> nbt_tags.TypeInt:
    if version <= 1202:
        table = {
            0: 3,
            1: 4,
            2: 2,
            3: 5
        }
        return nbt_tags.TypeInt(table[direction.value%4])
    return direction

def int_coordinate(coord: str, version: int, issues: list[dict[str, str | int]]) -> str:
    coord = coord.replace("+", "")
    if "~" not in coord and "^" not in coord:
        coord = str(math.floor(float(coord)))
    return coord

def is_macro_token(token: str) -> bool:
    if not token.startswith("$(") or not token.endswith(")"):
        return False
    tokens = arguments.parse(token[1:], "", True)
    return len(tokens) == 1

def join_text(text: dict[str, list[str]], version: int, issues: list[dict[str, str | int]]) -> str:
    return " ".join(text["join_text"])

def loot_context(context: str) -> str:
    id_array = {
        "killer": "attacker",
        "direct_killer": "direct_attacker",
        "killer_player": "attacking_player",
    }
    if context in id_array:
        context = id_array[context]
    return context

def loot_context_alt(context: str) -> str:
    id_array = {
        "killer": "attacking_entity",
        "killer_player": "last_damage_player",
    }
    if context in id_array:
        context = id_array[context]
    return context

def loot_table(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    # Assign version
    global pack_version
    pack_version = version

    # Return if a macro token
    if isinstance(name, str) and is_macro_token(name):
        return name

    if pack_version <= 1202 and defaults.SEND_WARNINGS:
        log("WARNING: Loot tables are not handled for 1.12!")

    if name == "minecraft:empty":
        name = "loot_table_replacements:empty"
        loot_table_replacements.create_pack(
            easy_map_updater.MINECRAFT_PATH / "saves" / option_manager.get_map_name()
        )

    return namespace(name)

def namespace(argument: str) -> str:
    if argument == "":
        return argument
    if ":" in argument:
        return argument
    if argument[0] == "#":
        return "#minecraft:" + argument[1:]
    if argument[0] == "!":
        return "!minecraft:" + argument[1:]
    return "minecraft:" + argument

def number_provider(provider: int | float | dict) -> int | float | dict:
    if not isinstance(provider, dict):
        return provider
    if "type" not in provider:
        provider["type"] = "minecraft:uniform"
    provider["type"] = namespace(provider["type"])
    provider_type = provider["type"]

    if provider_type == "minecraft:binomial":
        provider["n"] = number_provider(provider["n"])
        provider["p"] = number_provider(provider["p"])

    if provider_type == "minecraft:score":
        target = provider["target"]
        if isinstance(target, dict):
            target["type"] = namespace(target["type"])
            target_type = target["type"]
            if target_type == "minecraft:context":
                target["target"] = loot_context(target["target"])
        else:
            provider["target"] = loot_context(target)

    if provider_type == "minecraft:uniform":
        provider["min"] = number_provider(provider["min"])
        provider["max"] = number_provider(provider["max"])

    return provider

def particle_mode(argument: str, version: int, issues: list[dict[str, str | int]]) -> str:
    if argument not in ["normal", "force"]:
        return "normal"
    return argument

def pitch(argument: str, version: int, issues: list[dict[str, str | int]]) -> str:
    if version >= 900:
        return argument
    if "~" not in argument:
        value = float(argument)
        return str(abs((value - 90) % 360 - 180) - 90)
    elif len(argument) > 1:
        value = float(argument[1:])
        return "~" + str(abs((value - 90) % 360 - 180) - 90)
    else:
        return argument

def predicate(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    if name.startswith("{") or name.startswith("["):
        contents = json_manager.unpack(name)
        return json.dumps(predicate_lib.predicate(contents, version))

    return namespace(name.lower())

def recipe(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    return name.lower()

def say_text(text: dict[str, list[str]], version: int, issues: list[dict[str, str | int]]) -> str:
    # Convert any target selecors that are present
    output_list: list[str] = []
    for string in text["say_text"]:
        if string[0] == "@":
            string = target_selectors.update(string, version, issues, False)
        output_list.append(string)
    return " ".join(output_list)

def scoreboard_objective_display_slot(slot: str, version: int, issues: list[dict[str, str | int]]) -> str:
    id_array = {
        "belowName": "below_name"
    }
    if slot in id_array:
        slot = id_array[slot]
    return slot

def scoreboard_range(argument: dict[str, str], version: int, issues: list[dict[str, str | int]]) -> str:
    if argument["lower"] == argument["upper"]:
        return argument["lower"]
    return f'{argument["lower"]}..{argument["upper"]}'

def setblock_mode(argument: str, version: int, issues: list[dict[str, str | int]]) -> str:
    if argument not in ["destroy", "keep", "replace", "strict"]:
        return "replace"
    return argument

def slot(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    # Assign version
    global pack_version
    pack_version = version

    # Remove slot. prefix
    if pack_version <= 1202 and len(name) > 5 and name[:5] == "slot.":
        name = name[5:]

    # Change slot names for 1.20.5
    id_array = {
        "horse.armor": "armor.body"
    }
    if name in id_array:
        name = id_array[name]

    # Change slot names for 1.21.5
    id_array = {
        "horse.saddle": "saddle"
    }
    if name in id_array:
        name = id_array[name]

    return name

def team_setting(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    id_array = {
        "friendlyfire": "friendlyFire"
    }
    if name in id_array:
        name = id_array[name]
    return name

def uuid_from_string(uuid: str | nbt_tags.TypeIntArray, version: int, issues: list[dict[str, str | int]]) -> nbt_tags.TypeIntArray:
    if not isinstance(uuid, str):
        return nbt_tags.TypeIntArray(uuid)
    new_uuid = utils.uuid_from_string(uuid)
    return nbt_tags.TypeIntArray([
        nbt_tags.TypeInt(new_uuid[0]),
        nbt_tags.TypeInt(new_uuid[1]),
        nbt_tags.TypeInt(new_uuid[2]),
        nbt_tags.TypeInt(new_uuid[3])
    ])

def new_uuid_int_array() -> nbt_tags.TypeIntArray:
    new_uuid = utils.new_uuid()
    return nbt_tags.TypeIntArray([
        nbt_tags.TypeInt(new_uuid[0]),
        nbt_tags.TypeInt(new_uuid[1]),
        nbt_tags.TypeInt(new_uuid[2]),
        nbt_tags.TypeInt(new_uuid[3])
    ])

def world_border_coordinate(coordinate: str, version: int, issues: list[dict[str, str | int]]) -> str:
    if coordinate.startswith("~") or coordinate.startswith("^"):
        return coordinate
    if "." in coordinate:
        numeric_coordinate = float(coordinate)
    else:
        numeric_coordinate = int(coordinate)
    return str(min(max(numeric_coordinate, -29999984), 29999984))

def world_border_diameter(diameter: str, version: int, issues: list[dict[str, str | int]]) -> str:
    if "." in diameter:
        numeric_diameter = float(diameter)
    else:
        numeric_diameter = int(diameter)
    new_diameter = min(numeric_diameter, 59999968)
    if new_diameter != numeric_diameter:
        log("WARNING: World border diameter clamped, check if it is used in a time manager")
    return str(new_diameter)

def yaw(argument: dict[str, str], version: int, issues: list[dict[str, str | int]]) -> str:
    yaw_str = argument["yaw"]
    if "pitch" in argument:
        pitch_str = argument["pitch"]
    else:
        pitch_str = "~"
    if version >= 900:
        return yaw_str
    
    flip_yaw = False
    if "~" not in pitch_str:
        pitch_value = float(pitch_str)%360
        if 90 < pitch_value and pitch_value < 270:
            flip_yaw = True
        else:
            return yaw_str
    elif len(pitch_str) > 1:
        pitch_value = float(pitch_str[1:])
        if pitch_value < -90 or 90 < pitch_value:
            flip_yaw = True
        else:
            return yaw_str
    else:
        return yaw_str
    
    if flip_yaw:
        if "~" not in yaw_str:
            return str(float(yaw_str)%360 - 180)
        elif len(yaw_str) > 1:
            return "~" + str(float(yaw_str[1:])%360 - 180)
        else:
            return "~180"
    else:
        return yaw_str