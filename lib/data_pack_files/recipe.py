# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from typing import Any
from lib import defaults
from lib import json_manager
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import items



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def update(file_path: Path, source_file_path: Path, version: int):
    global pack_version
    pack_version = version

    # Read file
    contents, load_bool = json_manager.safe_load(source_file_path)
    if not load_bool:
        return

    # Write to new location
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(recipe(contents, version), file, indent=4)


def recipe(contents: dict[str, Any], version: int) -> dict[str, Any]:
    global pack_version
    pack_version = version

    if "type" in contents:
        contents["type"] = miscellaneous.namespace(contents["type"])

    if "ingredient" in contents:
        if isinstance(contents["ingredient"], dict):
            contents["ingredient"] = update_ingredient(contents["ingredient"])
        elif isinstance(contents["ingredient"], list):
            for i in range(len(contents["ingredient"])):
                contents["ingredient"][i] = update_ingredient(contents["ingredient"][i])

    if "key" in contents:
        for key in contents["key"]:
            if isinstance(contents[key], dict):
                contents[key] = update_ingredient(contents[key])
            elif isinstance(contents[key], list):
                for i in range(len(contents[key])):
                    contents[key][i] = update_ingredient(contents[key][i])

    for tag in ["template", "base", "addition"]:
        if tag in contents:
            contents[tag] = update_ingredient(contents[tag])

    if "result" in contents:
        contents["result"] = update_result(contents["result"])

    return contents


def update_ingredient(ingredient: dict[str, Any]) -> dict[str, Any]:
    if "item" in ingredient:
        ingredient["item"] = items.update_from_command(ingredient["item"], pack_version, [])

    if "tag" in ingredient:
        ingredient["tag"] = items.update_from_command(ingredient["tag"], pack_version, [])

    return ingredient


def update_result(result: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(result, str):
        result = {"id": result}

    if "id" in result:
        updated_item = items.update_from_json(
            {
                "id": result["id"],
                "components": result["components"] if "components" in result else None,
            },
            pack_version,
            []
        )
        result["id"] = updated_item["id"]
        if updated_item["components"]:
            result["components"] = updated_item["components"]

    return result