# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from typing import Any, cast
from pathlib import Path
from lib.data_pack_files import miscellaneous
from lib.resource_pack_files import model_tables
from lib import json_manager
from lib import utils
from lib.log import log
from lib import defaults



# Initialize variables

pack_version = defaults.PACK_VERSION
PROGRAM_PATH = Path(__file__).parent

pack_path: Path

with (PROGRAM_PATH / "file_legend.json").open("r", encoding="utf-8") as file:
    FILE_LEGEND: dict[str, Any] = json.load(file)

overrides_array: dict[str, list[dict]] = {}
builtin_models: list[str] = []



# Define functions

def update(pack: Path, version: int):
    log("Updating models")

    global pack_version
    pack_version = version

    global pack_path
    pack_path = pack

    # Reset globals
    global overrides_array
    overrides_array = {}
    global builtin_models
    builtin_models = []

    process_models(pack)
    if pack_version <= 2103:
        create_item_definitions(pack)



def process_models(pack: Path):
    assets_folder = pack / "assets"
    if not assets_folder.exists():
        return
    for namespace_folder in assets_folder.iterdir():
        if not namespace_folder.is_dir():
            continue
        models_folder = namespace_folder / "models"
        if not models_folder.exists():
            continue

        for model_type_folder in models_folder.iterdir():
            if not model_type_folder.is_dir():
                continue
            for model_path in model_type_folder.glob("**/*.json"):
                if not model_path.is_file():
                    continue
                process_model(model_path, namespace_folder.name, model_type_folder)



def process_model(model_path: Path, namespace: str, model_type_folder: Path):
    modified = False
    model_json, load_bool = json_manager.safe_load(model_path)
    if not load_bool:
        return
    model_type = model_type_folder.name
    namespaced_id = f"{namespace}:{model_type}/{utils.remove_extension(model_path.as_posix()[len(model_type_folder.as_posix()) + 1:])}"

    # Create item definition if the model has no overrides and is a block reference model
    if (
        pack_version <= 2103 and
        "overrides" not in model_json and
        "parent" in model_json and
        model_json["parent"] in model_tables.BLOCK_MODEL_REPLACEMENTS.values()
    ):
        create_item_definition_for_block_reference(namespaced_id)

    modified = update_texture_names(model_json, modified)
    if model_type == "item":
        modified = extract_overrides(model_json, namespaced_id, modified)
        if pack_version <= 2103 and "parent" in model_json:
            updated_parent = change_block_model_reference(model_json["parent"])
            if model_json["parent"] != updated_parent:
                model_json["parent"] = updated_parent
                modified = True

    if "parent" in model_json and miscellaneous.namespace(model_json["parent"]).startswith("minecraft:builtin"):
        builtin_models.append(namespaced_id)

    if modified:
        utils.safe_file_write(model_path, json.dumps(model_json))



def update_texture_names(model_json: dict, modified: bool) -> bool:
    if "textures" not in model_json:
        return modified
    if not isinstance(model_json["textures"], dict):
        return modified

    for key in model_json["textures"]:
        texture = model_json["textures"][key]
        if not isinstance(texture, str):
            continue
        if texture.startswith("#"):
            continue
        texture = miscellaneous.namespace(texture)
        texture += ".png"
        if texture.split(":")[0] != "minecraft":
            continue
        path = ["minecraft", "textures"] + texture.split(":")[1].split("/")

        for file_version in FILE_LEGEND:
            if pack_version > int(file_version):
                continue
            legend = FILE_LEGEND[file_version]
            for folder in path[:-1]:
                if folder in legend:
                    legend = legend[folder]
                else:
                    break
            else:
                if path[-1] in legend:
                    target = legend[path[-1]]
                elif "*" in legend:
                    target = legend["*"]
                else:
                    continue

                if isinstance(target, list):
                    target = target[0]
                elif isinstance(target, dict):
                    continue
                new_texture = "minecraft:" + "/".join(update_texture_name("/".join(path), target).split("/")[2:])
                
                if texture != new_texture:
                    model_json["textures"][key] = new_texture[:-4]
                    modified = True

                break

    # Insert particle texture if it doesn't exist
    if "particle" not in model_json["textures"] and len(model_json["textures"].keys()):
        model_json["textures"]["particle"] = list(model_json["textures"].values())[0]
        modified = True

    return modified

def update_texture_name(subdir: str, target: str) -> str:
    path = Path(subdir)
    target_path = target.replace("*", path.name).split("/")
    path = path.parent
    for target_folder in target_path:
        if target_folder == ".":
            path = path.parent
        else:
            path = path / target_folder
    return path.as_posix()



def extract_overrides(model_json: dict, namespaced_id: str, modified: bool) -> bool:
    if "overrides" not in model_json:
        return modified
    
    overrides_array[namespaced_id] = model_json["overrides"]
    del model_json["overrides"]

    return True



def change_block_model_reference(namespaced_id: str) -> str:
    namespaced_id = miscellaneous.namespace(namespaced_id)
    model_path = pack_path / "assets" / "minecraft" / "models" / f"{namespaced_id.split(":")[1]}.json"
    if namespaced_id in model_tables.BLOCK_MODEL_REPLACEMENTS and not model_path.exists():
        return model_tables.BLOCK_MODEL_REPLACEMENTS[namespaced_id]
    return namespaced_id




def create_item_definition_for_block_reference(namespaced_id: str):
    file_path = pack_path / "assets" / namespaced_id.split(":")[0] / "items" / f"{"/".join(namespaced_id.split(":")[1].split("/")[1:])}.json"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            {"model": get_base_model_definition(namespaced_id, namespaced_id)},
            file,
            indent=4
        )

def create_item_definitions(pack: Path):
    for namespaced_id in overrides_array:
        if defaults.DEBUG_MODE:
            log(f"Converting: {namespaced_id}")
        item_definition = convert_overrides(overrides_array[namespaced_id], namespaced_id)
        file_path = pack / "assets" / namespaced_id.split(":")[0] / "items" / f"{"/".join(namespaced_id.split(":")[1].split("/")[1:])}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8", newline="\n") as file:
            json.dump(
                {"model": item_definition},
                file,
                indent=4
            )

predicates_array = [
    "angle",
    "blocking",
    "broken",
    "brushing",
    "cast",
    "charged",
    "cooldown",
    "custom_model_data",
    "damage",
    "damaged",
    "filled",
    # "firework", Not used on its own, but only with charged
    "honey_level",
    "lefthanded",
    "level",
    "pull",
    "pulling",
    "throwing",
    "time",
    "tooting",
    "trim_type",
]

def convert_overrides(overrides: list[dict], namespaced_id: str, predicate_index: int = 0) -> dict:

    # Return default model if overrides list is empty
    if len(overrides) == 0:
        return get_base_model_definition(namespaced_id, namespaced_id)
    
    # Get list of predicates used in overrides
    predicates: list[str] = []
    for override in overrides:
        if "predicate" not in override:
            continue
        for predicate in override["predicate"]:
            if predicate not in predicates:
                predicates.append(predicate)
    
    # Iterate through predicate list and process overrides based on that predicate
    while predicate_index < len(predicates_array):
        if predicates_array[predicate_index] in predicates:
            return filter_overrides_by_predicate(overrides, namespaced_id, predicate_index)

        predicate_index += 1

    # Return first override if the predicate checks fail
    if "model" in overrides[0]:
        model_id = miscellaneous.namespace(cast(str, overrides[0]["model"]))
        if namespaced_id == model_id:
            return get_base_model_definition(namespaced_id, namespaced_id)
        if model_id in overrides_array:
            return convert_overrides(overrides_array[model_id], model_id)
        return get_base_model_definition(namespaced_id, model_id)
    else:
        return get_base_model_definition(namespaced_id, namespaced_id)
    


def filter_overrides_by_predicate(overrides: list[dict], namespaced_id: str, predicate_index: int) -> dict:
    predicate = predicates_array[predicate_index]

    # Condition predicates
    if predicate in ["blocking", "broken", "cast", "damaged", "pulling", "throwing", "tooting"]:
        on_false: list[dict] = []
        on_true: list[dict] = []

        for override in overrides:
            if "predicate" not in override or predicate not in override["predicate"]:
                on_false.append(override)
                continue
            value = cast(int, override["predicate"][predicate])
            if value == 0:
                on_false.append(override)
            else:
                on_true.append(override)

        item = {
            "type": "minecraft:condition",
            "property": {
                "blocking": "minecraft:using_item",
                "broken": "minecraft:broken",
                "cast": "minecraft:fishing_rod/cast",
                "damaged": "minecraft:damaged",
                "pulling": "minecraft:using_item",
                "throwing": "minecraft:using_item",
                "tooting": "minecraft:using_item",
            }[predicate],
            "on_false": convert_overrides(on_false, namespaced_id, predicate_index + 1),
            "on_true": convert_overrides(on_true, namespaced_id, predicate_index + 1),
        }

        return item


    # Range dispatch predicates
    if predicate in ["angle", "brushing", "cooldown", "custom_model_data", "damage", "filled", "pull", "time"]:
        entries: dict[float, list[dict]] = {}
        fallback: list[dict] = []

        for override in overrides:
            if "predicate" not in override or predicate not in override["predicate"]:
                fallback.append(override)
                continue
            value = float(override["predicate"][predicate])
            if value not in entries:
                entries[value] = []
            entries[value].append(override)

        item = {
            "type": "minecraft:range_dispatch",
            "property": {
                "angle": "minecraft:compass",
                "brushing": "minecraft:use_cycle",
                "cooldown": "minecraft:cooldown",
                "custom_model_data": "minecraft:custom_model_data",
                "damage": "minecraft:damage",
                "filled": "minecraft:bundle/fullness",
                "pull": "minecraft:crossbow/pull" if namespaced_id == "minecraft:item/crossbow" else "minecraft:use_duration",
                "time": "minecraft:time",
            }[predicate],
            "entries": [],
            "fallback": convert_overrides(fallback, namespaced_id, predicate_index + 1),
        }
        for entry in entries:
            item["entries"].append({
                "model": convert_overrides(entries[entry], namespaced_id, predicate_index + 1),
                "threshold": entry
            })

        # Edge cases
        if predicate == "angle":
            if namespaced_id == "minecraft:item/recovery_compass":
                item["target"] = "recovery"
            else:
                item = {
                    "type": "minecraft:condition",
                    "property": "minecraft:has_component",
                    "component": "minecraft:lodestone_tracker",
                    "on_false": {
                        "type": "minecraft:select",
                        "property": "minecraft:context_dimension",
                        "cases": [{
                            "model": item.copy(),
                            "when": "minecraft:overworld",
                        }],
                        "fallback": item.copy(),
                    },
                    "on_true": item.copy(),
                }
                item["on_false"]["cases"][0]["model"]["target"] = "spawn"
                item["on_false"]["fallback"]["target"] = "none"
                item["on_true"]["target"] = "lodestone"

        if predicate == "brushing":
            item["period"] = 10.0
            item["scale"] = 0.1

        if predicate == "pull":
            if item["property"] == "minecraft:use_duration":
                item["scale"] = 0.05

        if predicate == "time":
            item = {
                "type": "minecraft:select",
                "property": "minecraft:context_dimension",
                "cases": [{
                    "model": item.copy(),
                    "when": "minecraft:overworld",
                }],
                "fallback": item.copy(),
            }
            item["cases"][0]["model"]["target"] = "daytime"
            item["fallback"]["target"] = "random"

        return item


    # Select predicates edge cases
    if predicate == "honey_level":
        full: list[dict] = []
        fallback: list[dict] = []

        for override in overrides:
            if "predicate" not in override or predicate not in override["predicate"]:
                fallback.append(override)
                continue
            value = float(override["predicate"][predicate])
            if value == 1:
                full.append(override)
            else:
                fallback.append(override)

        item = {
            "type": "minecraft:select",
            "property": "minecraft:block_state",
            "block_state_property": "honey_level",
            "cases": [{
                "model": convert_overrides(full, namespaced_id, predicate_index + 1),
                "when": "5",
            }],
            "fallback": convert_overrides(fallback, namespaced_id, predicate_index + 1),
        }

        return item

    if predicate == "lefthanded":
        left_handed: list[dict] = []
        fallback: list[dict] = []

        for override in overrides:
            if "predicate" not in override or predicate not in override["predicate"]:
                fallback.append(override)
                continue
            value = cast(int, override["predicate"][predicate])
            if value == 1:
                left_handed.append(override)
            else:
                fallback.append(override)

        item = {
            "type": "minecraft:select",
            "property": "minecraft:main_hand",
            "cases": [{
                "model": convert_overrides(left_handed, namespaced_id, predicate_index + 1),
                "when": "left",
            }],
            "fallback": convert_overrides(fallback, namespaced_id, predicate_index + 1),
        }

        return item

    if predicate == "level":
        entries: dict[float, list[dict]] = {}
        fallback: list[dict] = []

        for override in overrides:
            if "predicate" not in override or predicate not in override["predicate"]:
                fallback.append(override)
                continue
            value = float(override["predicate"][predicate])
            if value not in entries:
                entries[value] = []
            entries[value].append(override)

        item = {
            "type": "minecraft:select",
            "property": "minecraft:block_state",
            "block_state_property": "level",
            "cases": [],
            "fallback": convert_overrides(fallback, namespaced_id, predicate_index + 1),
        }
        for entry in entries:
            item["cases"].append({
                "model": convert_overrides(entries[entry], namespaced_id, predicate_index + 1),
                "when": str(int(entry*16))
            })

        return item

    if predicate == "trim_type":
        entries: dict[float, list[dict]] = {}
        fallback: list[dict] = []

        for override in overrides:
            if "predicate" not in override or predicate not in override["predicate"]:
                fallback.append(override)
                continue
            value = float(override["predicate"][predicate])
            if value not in entries:
                entries[value] = []
            entries[value].append(override)

        item = {
            "type": "minecraft:select",
            "property": "minecraft:trim_material",
            "cases": [],
            "fallback": convert_overrides(fallback, namespaced_id, predicate_index + 1),
        }
        for entry in entries:
            materials = {
                0.1: "minecraft:quartz",
                0.2: "minecraft:iron",
                0.3: "minecraft:netherite",
                0.4: "minecraft:redstone",
                0.5: "minecraft:copper",
                0.6: "minecraft:gold",
                0.7: "minecraft:emerald",
                0.8: "minecraft:diamond",
                0.9: "minecraft:lapis",
                1.0: "minecraft:amethyst",
            }
            for key in materials:
                if entry <= key:
                    item["cases"].append({
                        "model": convert_overrides(entries[entry], namespaced_id, predicate_index + 1),
                        "when": materials[key],
                    })
                    break

        return item


    # Special crossbow charged predicate
    if predicate == "charged":
        arrow: list[dict] = []
        rocket: list[dict] = []
        fallback: list[dict] = []

        for override in overrides:
            if "predicate" not in override or predicate not in override["predicate"]:
                fallback.append(override)
                continue
            value = cast(int, override["predicate"][predicate])
            if value == 1:
                if "firework" in override["predicate"] and override["predicate"]["firework"] == 1:
                    rocket.append(override)
                else:
                    arrow.append(override)
            else:
                fallback.append(override)

        item = {
            "type": "minecraft:select",
            "property": "minecraft:charge_type",
            "cases": [
                {
                    "model": convert_overrides(arrow, namespaced_id, predicate_index + 1),
                    "when": "arrow",
                },
                {
                    "model": convert_overrides(rocket, namespaced_id, predicate_index + 1),
                    "when": "rocket",
                }
            ],
            "fallback": convert_overrides(fallback, namespaced_id, predicate_index + 1),
        }

        return item


    # Return default model if predicate is not found
    return get_base_model_definition(namespaced_id, namespaced_id)



def get_base_model_definition(namespaced_id: str, model_id: str) -> dict:
    model_id = change_block_model_reference(model_id)

    # Handle special model cases
    if namespaced_id in model_tables.SPECIAL_MODELS:
        model_type = model_tables.SPECIAL_MODELS[namespaced_id]

        if model_type in ["minecraft:conduit", "minecraft:decorated_pot", "minecraft:shield", "minecraft:trident"]:
            if model_id not in builtin_models:
                return {
                    "type": "minecraft:model",
                    "model": model_id
                }
            return {
                "type": "minecraft:special",
                "base": model_id,
                "model": {
                    "type": model_type,
                }
            }
        
        if model_type == "minecraft:chest":
            return {
                "type": "minecraft:special",
                "base": model_id,
                "model": {
                    "type": "minecraft:chest",
                    "texture": {
                        "minecraft:item/chest": "minecraft:normal",
                        "minecraft:item/ender_chest": "minecraft:ender",
                        "minecraft:item/trapped_chest": "minecraft:trapped",
                    }[namespaced_id]
                }
            }
        
        if model_type == "minecraft:head":
            return {
                "type": "minecraft:special",
                "base": "minecraft:item/template_skull",
                "model": {
                    "type": "minecraft:head",
                    "kind": "_".join(namespaced_id.split("_")[:-1])
                }
            }
        
        if model_type == "minecraft:banner":
            return {
                "type": "minecraft:special",
                "base": "minecraft:item/template_banner",
                "model": {
                    "type": "minecraft:banner",
                    "color": namespaced_id.split("/")[-1][:-7]
                }
            }
        
        if model_type == "minecraft:bed":
            return {
                "type": "minecraft:special",
                "base": model_id,
                "model": {
                    "type": "minecraft:bed",
                    "texture": f"minecraft:{namespaced_id.split("/")[-1][:-4]}"
                }
            }
        
        if model_type == "minecraft:shulker_box":
            return {
                "type": "minecraft:special",
                "base": model_id,
                "model": {
                    "type": "minecraft:shulker_box",
                    "texture": "minecraft:shulker" if namespaced_id == "minecraft:item/shulker_box" else f"minecraft:shulker_{namespaced_id.split("/")[-1][:-12]}"
                }
            }
        

    # Handle items with tints
    if namespaced_id in [
        "minecraft:item/leather_helmet",
        "minecraft:item/leather_chestplate",
        "minecraft:item/leather_leggings",
        "minecraft:item/leather_boots",
    ]:
        return {
            "type": "minecraft:model",
            "model": model_id,
            "tints": [
                {
                    "type": "minecraft:dye",
                    "default": -6265536
                }
            ]
        }
    
    if namespaced_id in model_tables.TINT_DATA:
        return {
            "type": "minecraft:model",
            "model": "minecraft:item/template_spawn_egg" if namespaced_id.endswith("_spawn_egg") else model_id,
            "tints": model_tables.TINT_DATA[namespaced_id]
        }


    return {
        "type": "minecraft:model",
        "model": model_id
    }