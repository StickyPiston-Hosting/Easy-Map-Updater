# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from lib import json_manager
from lib.log import log
from lib import defaults



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def update(pack: Path, version: int):
    log("Updating shaders")

    global pack_version
    pack_version = version

    # Update shader references
    if pack_version <= 2101:
        update_shader_references(pack)



def update_shader_references(pack: Path):
    shaders_folder = pack / "assets" / "minecraft" / "shaders"
    if not shaders_folder.exists():
        return
    for shader_type_folder in shaders_folder.iterdir():
        if not shader_type_folder.is_dir():
            continue
        for file_path in shader_type_folder.glob("**/*.json"):
            if not file_path.is_file():
                continue

            file_json, load_bool = json_manager.safe_load(file_path)
            if not load_bool:
                return
            
            for key in ["fragment", "vertex"]:
                if key not in file_json or "/" in file_json[key] or ":" in file_json[key]:
                    continue
                file_json[key] = f"minecraft:{shader_type_folder.name}/{file_json[key]}"

            with file_path.open("w", encoding="utf-8", newline="\n") as file:
                json.dump(file_json, file, indent=4)