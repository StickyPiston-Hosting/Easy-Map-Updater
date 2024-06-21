# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from typing import Any
from pathlib import Path
from lib.log import log
from lib import defaults
from lib.data_pack_files import arguments
from lib.data_pack_files import nbt_tags



# Initialize variables

pack_version = defaults.PACK_VERSION

PROGRAM_PATH = Path(__file__).parent
with (PROGRAM_PATH / "nbt_tree.json").open("r", encoding="utf-8") as file:
    NBT_TREE: dict[str, Any] = json.load(file)



# Define functions

def update(path: str, version: int, issues: list[dict[str, str | int]], source: str) -> str:
    global pack_version
    pack_version = version

    # Update NBT string if the first character is a curly brace, otherwise return it
    if not path:
        return path
    if path.startswith("{"):
        return nbt_tags.update(path, pack_version, issues, source)

    path_parts = unpack(f'ROOT.{path}')
    if defaults.DEBUG_MODE:
        log(str(path_parts))
    path_parts = get_source(path_parts, source, issues)
    if defaults.DEBUG_MODE:
        log(str(path_parts))
    return pack(path_parts[1:])

def direct_update(path_parts: list[str], version: int, issues: list[dict[str, str]], source: str) -> list[str]:
    global pack_version
    pack_version = version

    path_parts = ["ROOT"] + path_parts
    path_parts = get_source(path_parts, source, issues)
    return path_parts[1:]

def get_source(path_parts: list[str], source, issues: list[dict[str, str | int]]) -> list[str]:
    # Get guide
    if source not in NBT_TREE["sources"]:
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Source "{source}" is not registered!')
        return path_parts
    return branch(path_parts, NBT_TREE["sources"][source], source, issues)

def branch(path_parts: list[str], guide: dict, source: str, issues: list[dict[str, str | int]]) -> list[str]:
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
    
def modify_path(path_parts: list[str], guide: dict, source: str, issues: list[dict[str, str | int]]) -> list[str]:
    if "rename" in guide:
        return guide["rename"]
    if "source" in guide:
        return get_source(path_parts, guide["source"], issues)
    if "tags" in guide:
        return search_tags(path_parts, guide["tags"], source, issues)
    return path_parts

def search_tags(path_parts: list[str], guide: dict, source: str, issues: list[dict[str, str | int]]) -> list[str]:
    if len(path_parts) < 2:
        return path_parts
    if path_parts[1] in guide:
        return path_parts[:1] + branch(path_parts[1:], guide[path_parts[1]], source, issues)
    return path_parts

def search_list(path_parts: list[str], guide: dict, source: str, issues: list[dict[str, str | int]]) -> list[str]:
    if len(path_parts) < 2:
        return path_parts
    if path_parts[1].startswith("[") and path_parts[1][1:-1].strip().startswith("{"):
        path_parts[1] = "[" + nbt_tags.update_with_guide(path_parts[1][1:-1].strip(), pack_version, issues, source, guide, "branch") + "]"
    return path_parts[:1] + branch(path_parts[1:], guide, source, issues)



def unpack(path: str) -> list[str]:
    return arguments.parse_with_quotes(path, ".", True, "[")

def pack(path_parts: list[str]) -> str:
    path = ""
    for part in path_parts:
        if not path or part.startswith("["):
            path += part
        else:
            path += "." + part
    return path



def build_nbt_from_path(nbt, path_parts: list[str]) -> tuple[dict[str], list[str]]:
    if len(path_parts) == 0:
        return nbt, path_parts
    
    if path_parts[-1].startswith("["):
        part_contents = path_parts[-1][1:-1].strip()
        if part_contents.startswith("{"):
            nested_nbt = nbt_tags.TypeList([nbt_tags.unpack(part_contents), nbt])
            index = "[1]"
        else:
            nested_nbt = nbt_tags.TypeList([nbt])
            index = "[0]"
        nested_nbt, new_path_parts = build_nbt_from_path(nested_nbt, path_parts[:-1])
        return nested_nbt, new_path_parts + [index]
    
    nested_nbt = {path_parts[-1]: nbt}
    nested_nbt, new_path_parts = build_nbt_from_path(nested_nbt, path_parts[:-1])
    return nested_nbt, new_path_parts + [path_parts[-1]]



def extract_nbt_from_path(nbt, path_parts: list[str]):
    if len(path_parts) == 0:
        return nbt

    if path_parts[0].startswith("["):
        part_contents = path_parts[0][1:-1].strip()
        if part_contents.startswith("{") and defaults.SEND_WARNINGS:
            log(f'WARNING: NBT list index used in NBT extraction by path is not yet supported!')
            return
        index = int(part_contents)
        if index < len(nbt):
            return extract_nbt_from_path(nbt[index], path_parts[1:])
        return
    
    if path_parts[0] in nbt:
        return extract_nbt_from_path(nbt[path_parts[0]], path_parts[1:])