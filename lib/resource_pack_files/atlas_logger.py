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
    log("Gathering texture IDs")
    textures = get_texture_list(pack)

    log("Creating atlas file")
    if len(textures) > 0:
        create_atlas_file(og_pack, pack, textures, version)

    log("Textures logged into atlas")

def get_texture_list(pack: Path) -> list[str]:
    textures: list[str] = []

    # Iterate through namespaces
    for namespace in (pack / "assets").iterdir():
        if not namespace.is_dir():
            continue

        if not (namespace / "models").exists():
            continue

        for file_path in (namespace / "models").glob("**/*.json"):
            if not file_path.is_file():
                continue
            model_json, load_bool = json_manager.safe_load(file_path)
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

                if ":" not in texture:
                    texture = miscellaneous.namespace(texture)

                if (
                    (
                        "/" not in texture or
                        texture.split(":")[1].split("/")[0] not in ["block", "item"]
                    ) and
                    texture not in textures and
                    miscellaneous.resource_exists(pack, texture, "textures", ".png")
                ):
                    textures.append(texture)
    return textures

def create_atlas_file(og_pack: Path, pack: Path, textures: list[str], version: int):
    # Read existing atlas file
    og_atlas_path = og_pack / "assets" / "minecraft" / "atlases" / "blocks.json"
    if og_atlas_path.exists():
        atlas, load_bool = json_manager.safe_load(og_atlas_path)
        if not load_bool:
            atlas = {"sources": []}
        if "sources" not in atlas:
            atlas["sources"] = []
    else:
        atlas = {"sources": []}
    sources: list[dict] = atlas["sources"]

    # Update sources
    for source in sources:
        if "type" not in source:
            continue

        if source["type"] == "single" or source["type"] == "unstitch":
            source["resource"] = miscellaneous.update_texture_path(source["resource"] + ".png", version)[:-4]

        if source["type"] == "paletted_permutations":
            for permutation in source["permutations"]:
                source["permutations"][permutation] = miscellaneous.update_texture_path(source["permutations"][permutation] + ".png", version)[:-4]

    for texture in textures:
        if is_texture_in_atlas(sources, texture):
            continue

        sources.append(
            {
                "type": "single",
                "resource": texture
            }
        )

    folder = pack / "assets" / "minecraft" / "atlases"
    folder.mkdir(parents=True, exist_ok=True)
    utils.safe_file_write(folder / "blocks.json", json.dumps(atlas, indent=4))

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