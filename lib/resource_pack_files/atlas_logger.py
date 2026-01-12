# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from lib import json_manager
from lib import utils
from lib.log import log
from lib.resource_pack_files import miscellaneous



# Initialize variables

LEGAL_CHARS = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","0","1","2","3","4","5","6","7","8","9","/",".","_","-",":"]



# Define functions

def log_atlas(og_pack: Path, pack: Path, version: int):
    log("Gathering model IDs")
    block_models = get_block_model_list(pack)
    item_models = get_item_model_list(pack)

    log("Gathering texture IDs")
    block_textures, item_textures = get_texture_list(pack, block_models, item_models)

    log("Creating atlas file")
    if len(block_textures) > 0 or len(item_textures) > 0:
        create_atlas_file(og_pack, pack, block_textures, item_textures, version)

    log("Textures logged into atlas")



def insert_model_entry(model_list: list[str], model: str):
    model = miscellaneous.namespace(model)
    if model not in model_list:
        model_list.append(model)



def get_block_model_list(pack: Path) -> list[str]:
    block_models: list[str] = []

    block_states_folder = pack / "assets" / "minecraft" / "blockstates"
    if not block_states_folder.exists() or not block_states_folder.is_dir():
        return block_models
    
    for file_path in block_states_folder.glob("**/*.json"):
        if not file_path.is_file():
            continue
        block_state_json, load_bool = json_manager.safe_load(file_path)
        if not load_bool:
            continue

        if "variants" in block_state_json:
            for key in block_state_json["variants"]:
                variant = block_state_json["variants"][key]
                if isinstance(variant, dict):
                    if "model" in variant:
                        insert_model_entry(block_models, variant["model"])
                else:
                    for entry in variant:
                        if "model" in entry:
                            insert_model_entry(block_models, entry["model"])

        if "multipart" in block_state_json:
            for case in block_state_json["multipart"]:
                if "apply" in case:
                    if isinstance(case["apply"], dict):
                        if "model" in case["apply"]:
                            insert_model_entry(block_models, case["apply"]["model"])
                    else:
                        for entry in case["apply"]:
                            if "model" in entry:
                                insert_model_entry(block_models, entry["model"])

    return block_models



def get_item_model_list(pack: Path) -> list[str]:
    item_models: list[str] = []

    items_folder = pack / "assets" / "minecraft" / "items"
    if not items_folder.exists() or not items_folder.is_dir():
        return item_models
    
    for file_path in items_folder.glob("**/*.json"):
        if not file_path.is_file():
            continue
        item_json, load_bool = json_manager.safe_load(file_path)
        if not load_bool:
            continue

        if "model" in item_json:
            get_item_models_from_item_definition(item_json["model"], item_models)

    return item_models

def get_item_models_from_item_definition(model: dict, item_models: list[str]):
    if "model" in model and isinstance(model["model"], str):
        insert_model_entry(item_models, model["model"])

    for key in ["on_true", "on_false", "fallback"]:
        if key in model:
            get_item_models_from_item_definition(model[key], item_models)

    if "models" in model:
        for entry in model["models"]:
            get_item_models_from_item_definition(entry, item_models)

    for key in ["cases", "entries"]:
        if key in model:
            for entry in model[key]:
                if "model" in entry:
                    get_item_models_from_item_definition(entry["model"], item_models)




def get_texture_list(pack: Path, block_model_list: list[str], item_model_list: list[str]) -> tuple[list[str], list[str]]:
    block_textures: list[str] = []
    item_textures: list[str] = []
    model_array = {}

    # Iterate through namespaces
    for namespace in (pack / "assets").iterdir():
        if not namespace.is_dir():
            continue

        models_path = namespace / "models"
        if not models_path.exists():
            continue

        for file_path in models_path.glob("**/*.json"):
            model_id = f"{namespace.name}:{file_path.as_posix()[len(models_path.as_posix()) + 1:-5]}"

            # Get model contents from file or from stored array
            model_json, load_bool = get_model_contents(pack, model_id, model_array, block_model_list, item_model_list)
            if not load_bool:
                continue

            if not "textures" in model_json:
                continue

            if not isinstance(model_json["textures"], dict):
                log(f" Warning: {file_path} has incorrectly listed textures!")
                continue

            # Log any textures that exist
            for key, texture in model_json["textures"].items():
                if not (isinstance(key, str) and isinstance(texture, str)):
                    log(f" Warning: {file_path} has an incorrect texture listed!")
                    continue

                # Skip if the texture is a reference
                if texture.startswith("#"):
                    continue

                texture = miscellaneous.namespace(texture)
                subfolder = texture.split(":")[1].split("/")[0] if "/" in texture else ""

                if not miscellaneous.resource_exists(pack, texture, "textures", ".png"):
                    continue

                if subfolder != "block" and model_array[model_id]["is_block"] and texture not in block_textures:
                    block_textures.append(texture)
                if subfolder != "item" and model_array[model_id]["is_item"] and texture not in item_textures:
                    item_textures.append(texture)

    return block_textures, item_textures


def get_model_contents(pack: Path, model_id: str, model_array: dict, block_model_list: list[str], item_model_list: list[str]) -> tuple[dict, bool]:
    file_path = pack / "assets" / model_id.split(":")[0] / "models" / (model_id.split(":")[1] + ".json")
    model_subfolder = model_id.split(":")[1].split("/")[0] if "/" in model_id else ""

    if model_id not in model_array:
        if not file_path.is_file():
            return {}, False
        model_json, load_bool = json_manager.safe_load(file_path)
        if not load_bool:
            return {}, False
        model_array[model_id] = {
            "model": model_json,
            "is_block": model_id in block_model_list or model_subfolder == "block",
            "is_item": model_id in item_model_list or model_subfolder == "item",
        }

        if (not model_array[model_id]["is_block"] or not model_array[model_id]["is_item"]) and "parent" in model_json:
            parent = miscellaneous.namespace(model_json["parent"])
            if parent not in model_array:
                get_model_contents(pack, parent, model_array, block_model_list, item_model_list)
            if parent in model_array:
                model_array[model_id]["is_block"] = model_array[parent]["is_block"]
                model_array[model_id]["is_item"] = model_array[parent]["is_item"]
        
        return model_json, True

    else:
        model_json = model_array[model_id]["model"]
        return model_json, True



def create_atlas_file(og_pack: Path, pack: Path, block_textures: list[str], item_textures: list[str], version: int):
    # Read existing atlas files
    og_blocks_atlas_path = og_pack / "assets" / "minecraft" / "atlases" / "blocks.json"
    if og_blocks_atlas_path.exists():
        blocks_atlas, load_bool = json_manager.safe_load(og_blocks_atlas_path)
        if not load_bool:
            blocks_atlas = {"sources": []}
        if "sources" not in blocks_atlas:
            blocks_atlas["sources"] = []
    else:
        blocks_atlas = {"sources": []}
    block_sources: list[dict] = blocks_atlas["sources"]

    og_items_atlas_path = og_pack / "assets" / "minecraft" / "atlases" / "items.json"
    if og_items_atlas_path.exists():
        items_atlas, load_bool = json_manager.safe_load(og_items_atlas_path)
        if not load_bool:
            items_atlas = {"sources": []}
        if "sources" not in items_atlas:
            items_atlas["sources"] = []
    else:
        items_atlas = {"sources": []}
    item_sources: list[dict] = items_atlas["sources"]

    # Update sources
    for source_list in [block_sources, item_sources]:
        for source in source_list:
            if "type" not in source:
                continue

            if source["type"] == "single" or source["type"] == "unstitch":
                source["resource"] = miscellaneous.update_texture_path(source["resource"] + ".png", version)[:-4]

            if source["type"] == "paletted_permutations":
                for permutation in source["permutations"]:
                    source["permutations"][permutation] = miscellaneous.update_texture_path(source["permutations"][permutation] + ".png", version)[:-4]

    for texture in block_textures:
        if not is_texture_in_atlas(block_sources, texture):
            block_sources.append(
                {
                    "type": "single",
                    "resource": texture
                }
            )
    for texture in item_textures:
        if not is_texture_in_atlas(item_sources, texture):
            item_sources.append(
                {
                    "type": "single",
                    "resource": texture
                }
            )


    folder = pack / "assets" / "minecraft" / "atlases"
    folder.mkdir(parents=True, exist_ok=True)
    if len(block_sources) > 0:
        utils.safe_file_write(folder / "blocks.json", json.dumps(blocks_atlas, indent=4))
    if len(item_sources) > 0:
        utils.safe_file_write(folder / "items.json", json.dumps(items_atlas, indent=4))

def is_texture_in_atlas(sources: list[dict], texture: str) -> bool:
    texture = miscellaneous.namespace(texture)

    for source in sources:
        if "type" not in source:
            continue

        if source["type"] == "single" and miscellaneous.namespace(source["resource"]) == texture:
            return True
        
        if source["type"] == "directory" and texture.split(":")[1].startswith(source["prefix"]):
            return True
        
        if source["type"] == "paletted_permutations":
            for base_texture in source["textures"]:
                base_texture = miscellaneous.namespace(base_texture)
                separator = source["separator"] if "separator" in source else "_"
                for permutation in source["permutations"]:
                    if base_texture + separator + permutation == texture:
                        return True
                    
        if source["type"] == "unstitch":
            for region in source["regions"]:
                if miscellaneous.namespace(region["sprite"]) == texture:
                    return True
        
    return False