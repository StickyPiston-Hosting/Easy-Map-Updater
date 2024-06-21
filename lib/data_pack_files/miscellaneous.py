# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import math
from typing import cast, Any
from lib.log import log
from lib import defaults
from lib import utils
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import target_selectors
from lib.data_pack_files import tables



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

    name = namespace(name)

    id_array = tables.ATTRIBUTE_IDS
    if name in id_array:
        name = id_array[name]

    return name

def banner_color(color: nbt_tags.TypeInt, version: int, issues: list[dict[str, str | int]]) -> nbt_tags.TypeInt:
    if version <= 1202:
        return nbt_tags.TypeInt(15 - color.value)
    return color

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

def effect_time(argument: str, version: int, issues: list[dict[str, str | int]]) -> str:
    if argument == "infinite":
        return argument
    if not argument.isnumeric():
        return "1"
    if int(argument) == 0:
        return "1"
    return argument

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
    if argument not in ["destroy", "hollow", "keep", "outline", "replace"]:
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

def join_text(text: dict[str, list[str]], version: int, issues: list[dict[str, str | int]]) -> str:
    return " ".join(text["join_text"])

def loot_table(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    # Assign version
    global pack_version
    pack_version = version

    if pack_version <= 1202 and defaults.SEND_WARNINGS:
        log("WARNING: Loot tables are not handled for 1.12!")

    return namespace(name)

def namespace(argument: str) -> str:
    if argument == "":
        return argument
    if ":" in argument:
        return argument
    if argument[0] == "#":
        return "#minecraft:" + argument[1:]
    return "minecraft:" + argument

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
    return name.lower()

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
    if argument not in ["destroy", "keep", "replace"]:
        return "replace"
    return argument

def slot(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    # Assign version
    global pack_version
    pack_version = version

    # Remove slot. prefix
    if pack_version <= 1202 and len(name) > 5 and name[:5] == "slot.":
        name = name[5:]
    return name

def team_setting(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    id_array = {
        "friendlyfire": "friendlyFire"
    }
    if name in id_array:
        name = id_array[name]
    return name

def uuid_from_string(uuid: str, version: int, issues: list[dict[str, str | int]]) -> nbt_tags.TypeIntArray:
    if isinstance(uuid, nbt_tags.TypeIntArray):
        return uuid
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