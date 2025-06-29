# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from pathlib import Path
from typing import Any
import json



# Initialize variables

PROGRAM_PATH = Path(__file__).parent

LEGAL_CHARS = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","0","1","2","3","4","5","6","7","8","9","/",".","_","-",":"]



# Define functions

def is_resource_legal(resource: str) -> bool:
    for char in resource:
        if char not in LEGAL_CHARS:
            return False
    return True

def namespace(resource: str) -> str:
    if resource == "":
        return resource
    if ":" in resource:
        return resource
    return "minecraft:" + resource

def resource_exists(pack: Path, resource: str, resource_type: str, file_type: str = "") -> bool:
    if not is_resource_legal(resource):
        return False

    resource_path = pack / "assets" / resource.split(":")[0] / resource_type / (resource.split(":")[1] + file_type)
    if resource_path.exists():
        return True
    
    vanilla_pack = pack.parent / "vanilla_resources"
    if not vanilla_pack.exists():
        return True
    
    resource_path = vanilla_pack / "assets" / resource.split(":")[0] / resource_type / resource.split(":")[1]
    if resource_path.exists():
        return True
    
    return False



with (PROGRAM_PATH / "file_legend.json").open("r", encoding="utf-8") as file:
    FILE_LEGEND: dict[str, Any] = json.load(file)

def update_texture_path(texture: str, version: int) -> str:
    texture = namespace(texture)
    if texture.split(":")[0] != "minecraft":
        return texture
    path = ["minecraft", "textures"] + texture.split(":")[1].split("/")

    for file_version in FILE_LEGEND:
        if version > int(file_version):
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

            return "minecraft:" + "/".join(collapse_path("/".join(path), target).split("/")[2:])

    return texture


def collapse_path(subdir: str, target: str) -> str:
    path = Path(subdir)
    target_path = target.replace("*", path.name).split("/")
    path = path.parent
    for target_folder in target_path:
        if target_folder == ".":
            path = path.parent
        else:
            path = path / target_folder
    return path.as_posix()