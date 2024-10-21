# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from typing import Any
from lib import defaults
from lib import utils
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
    utils.safe_file_write(file_path, json.dumps(recipe(contents, version), indent=4))


def recipe(contents: dict[str, Any], version: int) -> dict[str, Any]:
    global pack_version
    pack_version = version

    if "type" in contents:
        contents["type"] = miscellaneous.namespace(contents["type"])

    for key in ["addition", "base", "ingredient", "template"]:
        if key in contents:
            if isinstance(contents[key], dict | str):
                contents[key] = update_ingredient(contents[key])
            elif isinstance(contents[key], list):
                for i in range(len(contents[key])):
                    contents[key][i] = update_ingredient(contents[key][i])

    if "ingredients" in contents and isinstance(contents["ingredients"], list):
        for i in range(len(contents["ingredients"])):
            if isinstance(contents["ingredients"][i], dict | str):
                contents["ingredients"][i] = update_ingredient(contents["ingredients"][i])
            elif isinstance(contents["ingredients"][i], list):
                for j in range(len(contents["ingredients"][i])):
                    contents["ingredients"][i][j] = update_ingredient(contents["ingredients"][i][j])

    if "key" in contents:
        for key in contents["key"]:
            if isinstance(contents["key"][key], dict | str):
                contents["key"][key] = update_ingredient(contents["key"][key])
            elif isinstance(contents["key"][key], list):
                for i in range(len(contents["key"][key])):
                    contents["key"][key][i] = update_ingredient(contents["key"][key][i])

    if "result" in contents:
        contents["result"] = update_result(contents["result"])

    return contents


def update_ingredient(ingredient: dict[str, Any] | str) -> str:
    if isinstance(ingredient, dict):
        if "item" in ingredient:
            return items.update_from_command("minecraft:barrier" if ingredient["item"] == "minecraft:air" else ingredient["item"], pack_version, [])

        if "tag" in ingredient:
            return items.update_from_command(f"#{ingredient["tag"]}", pack_version, [])
        
        return "minecraft:stone"
        
    else:
        return items.update_from_command("minecraft:barrier" if ingredient == "minecraft:air" else ingredient, pack_version, [])


def update_result(result: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(result, str):
        result = {"id": result}

    if "item" in result:
        result["id"] = result["item"]
        del result["item"]

    if "id" in result:
        updated_item = items.update_from_json(
            {
                "id": result["id"],
                "components": result["components"] if "components" in result else None,
            },
            pack_version,
            []
        )
        result["id"] = "minecraft:barrier" if updated_item["id"] == "minecraft:air" else updated_item["id"]
        if updated_item["components"]:
            result["components"] = updated_item["components"]

    return result