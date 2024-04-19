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

def update(argument: dict[str, str], version: int, issues: list[dict[str, str]], source: str) -> str:
    global pack_version
    pack_version = version

    nbt = argument["nbt"]
    path = argument["path"]
    mode = argument["mode"]

    if path.startswith("{"):
        return nbt_tags.update(nbt, pack_version, issues, source)
    
    path_parts = arguments.parse_with_quotes("ROOT." + path + ("[0]" if mode in ["insert", "append", "prepend"] else ""), ".", True, "[")
    return get_source(path_parts, source, nbt, issues)

def get_source(path_parts: list[str], source, nbt: str, issues: list[dict[str, str]]) -> str:
    # Get guide
    if source not in NBT_TREE["sources"]:
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Source "{source}" is not registered!')
        return nbt_tags.update(nbt, pack_version, issues, source)
    return branch(path_parts, NBT_TREE["sources"][source], source, nbt, issues)

def branch(path_parts: list[str], guide: dict, source: str, nbt: str, issues: list[dict[str, str]]) -> str:
    # Return function based on contents of guide
    if "edge_case" in guide:
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Edge case {guide["edge_case"]["case"] if "case" in guide["edge_case"] else guide["edge_case"]} found in NBT tags from path conversion')
        return nbt
    if "source" in guide:
        return get_source(path_parts, guide["source"], nbt, issues)
    if "tags" in guide:
        return search_tags(path_parts, guide["tags"], source, nbt, issues)
    if "list" in guide:
        return search_list(path_parts, guide["list"], source, nbt, issues)
    if "path" in guide:
        return branch(path_parts, guide["path"], source, nbt, issues)
    return nbt_tags.update_with_guide(nbt, pack_version, issues, source, guide, "branch")

def search_tags(path_parts: list[str], guide: dict, source: str, nbt: str, issues: list[dict[str, str]]) -> str:
    if len(path_parts) < 2:
        return nbt_tags.update_with_guide(nbt, pack_version, issues, source, guide, "tags")
    if path_parts[1] in guide:
        return branch(path_parts[1:], guide[path_parts[1]], source, nbt, issues)
    return nbt

def search_list(path_parts: list[str], guide: dict, source: str, nbt: str, issues: list[dict[str, str]]) -> str:
    if len(path_parts) < 2:
        return nbt_tags.update_with_guide(nbt, pack_version, issues, source, guide, "list")
    return branch(path_parts[1:], guide, source, nbt, issues)