# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from lib.log import log
from lib import defaults
from lib.data_pack_files import arguments
from lib.data_pack_files import nbt_tags



# Initialize variables

pack_version = defaults.PACK_VERSION

PROGRAM_PATH = Path(__file__).parent
with (PROGRAM_PATH / "nbt_tree.json").open("r", encoding="utf-8") as file:
    NBT_TREE: dict[str, dict[str, str]] = json.load(file)



# Define functions

def update(path: str, version: int, issues: list[dict[str, str]], source: str) -> str:
    global pack_version
    pack_version = version

    # Update NBT string if the first character is a curly brace, otherwise return it
    if not path:
        return path
    if path.startswith("{"):
        return nbt_tags.update(path, pack_version, issues, source)

    path_parts = arguments.parse_with_quotes("ROOT." + path, ".", True, "[")
    path_parts = get_source(path_parts, source, issues)
    output = ""
    for part in path_parts[1:]:
        if not output or part[0] == "[":
            output += part
        else:
            output += "." + part
    return output

def get_source(path_parts: list[str], source, issues: list[dict[str, str]]) -> list[str]:
    # Get guide
    if source not in NBT_TREE["sources"]:
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Source "{source}" is not registered!')
        return path_parts
    return branch(path_parts, NBT_TREE["sources"][source], source, issues)

def branch(path_parts: list[str], guide: dict, source: str, issues: list[dict[str, str]]) -> list[str]:
    # Return function based on contents of guide
    if "rename" in guide:
        path_parts = [guide["rename"]] + path_parts[1:]
    if "path" in guide:
        return modify_path(path_parts, guide["path"], source, issues)
    if "source" in guide:
        return get_source(path_parts, guide["source"], issues)
    if "tags" in guide:
        return search_tags(path_parts, guide["tags"], source, issues)
    if "list" in guide:
        return search_list(path_parts, guide["list"], source, issues)
    return path_parts
    
def modify_path(path_parts: list[str], guide: dict, source: str, issues: list[dict[str, str]]) -> list[str]:
    if "rename" in guide:
        return guide["rename"]
    if "source" in guide:
        return get_source(path_parts, guide["source"], issues)
    if "tags" in guide:
        return search_tags(path_parts, guide["tags"], source, issues)
    return path_parts

def search_tags(path_parts: list[str], guide: dict, source: str, issues: list[dict[str, str]]) -> list[str]:
    if len(path_parts) < 2:
        return path_parts
    if path_parts[1] in guide:
        return path_parts[:1] + branch(path_parts[1:], guide[path_parts[1]], source, issues)
    return path_parts

def search_list(path_parts: list[str], guide: dict, source: str, issues: list[dict[str, str]]) -> list[str]:
    if len(path_parts) < 2:
        return path_parts
    if path_parts[1].startswith("[") and path_parts[1][1:-1].strip().startswith("{"):
        path_parts[1] = "[" + nbt_tags.update_with_guide(path_parts[1][1:-1].strip(), pack_version, issues, source, guide, "branch") + "]"
    return path_parts[:1] + branch(path_parts[1:], guide, source, issues)