# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from typing import Any
from pathlib import Path
from lib import utils
from lib.log import log
from lib.data_pack_files import arguments



# Initialize variables

PROGRAM_PATH = Path(__file__).parent.parent
MINECRAFT_PATH = PROGRAM_PATH.parent



# Define functions

def merge(a, b):
    # Merge if a dict
    if isinstance(a, dict) and isinstance(b, dict):
        return merge_compound(a, b)
    # Merge if a list
    if isinstance(a, list) and isinstance(b, list):
        return merge_list(a, b)
    # Assign otherwise
    return b



def merge_compound(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    # Iterate through keys
    for key in b:
        # If the key does not exist in a, write it
        if key not in a:
            a[key] = b[key]
        # Merge them otherwise
        else:
            a[key] = merge(a[key], b[key])
    return a



def merge_list(a: list, b: list) -> list:
    # Iterate through items on the list, append them if they aren't in it already
    for element in b:
        if element not in a:
            a.append(element)
    return a



def safe_load(file_path: Path) -> tuple[dict, bool]:
    try:
        contents = utils.safe_file_read(file_path)
        return json.loads(contents.encode(encoding="utf-8", errors="backslashreplace")), True
    except (json.JSONDecodeError, FileNotFoundError):
        log(f'ERROR: Invalid JSON file at: {file_path.as_posix()[len(MINECRAFT_PATH.as_posix()):]}')
        return {}, False
    


def unpack(string: str) -> Any:
    # Return if blank
    string = string.strip()
    if string == "":
        return string
    
    if string[0] == "{":
        return unpack_compound(string)
    if string[0] == "[":
        return unpack_list(string)
    if string[0] in ['"', "'"]:
        return utils.unpack_string(string)
    
    # Return if something else
    if string in ["true", "True"]:
        return True
    if string in ["false", "False"]:
        return False
    if string in ["null", "None"]:
        return None
    
    try:
        int(string)
    except:
        pass
    else:
        return int(string)
    try:
        float(string)
    except:
        pass
    else:
        return float(string)
    
    return string

def unpack_compound(string: str) -> dict:
    # Prepare compound
    compound = {}

    # Stop if compound is empty
    if string.strip() == "" or string.strip()[1:-1].strip() == "":
        return compound

    # Add tags to compound
    for tag in arguments.parse_with_quotes(string.strip()[1:], ",", False):
        if ":" not in tag:
            continue
        parts = arguments.parse_with_quotes(tag, ":", False)
        name = utils.unpack_string(parts[0].strip())
        value = ":".join(parts[1:]).strip()
        compound[name] = unpack(value)

    return compound

def unpack_list(string: str) -> list:
    # Prepare list
    out_list = []

    # Stop if list is empty
    if string.strip() == "" or string.strip()[1:-1].strip() == "":
        return out_list

    # Add tags to list
    for tag in arguments.parse_with_quotes(string.strip()[1:], ",", False):
        out_list.append(unpack(tag.strip()))

    return out_list



def pack(json_object) -> str:
    # Pack based on type
    if isinstance(json_object, dict):
        return pack_compound(json_object)
    if isinstance(json_object, list):
        return pack_list(json_object)
    if isinstance(json_object, str):
        return utils.pack_string(json_object, force_double=True)
    if type(json_object).__name__ == "bool":
        if json_object:
            return "true"
        return "false"
    if json_object == None:
        return "null"
    return str(json_object)

def pack_list(json_object: list) -> str:
    # Prepare list
    out_list = []
    for entry in json_object:
        out_list.append(pack(entry))

    return f'[{",".join(out_list)}]'

def pack_compound(json_object: dict[str, Any]) -> str:
    # Prepare tag list
    tags: list[str] = []

    # Iterate through keys
    for key in json_object:
        tags.append(f'"{key}":{pack(json_object[key])}')
    
    # Return stringified version of compound
    return f'{{{",".join(tags)}}}'