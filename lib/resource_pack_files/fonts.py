# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from lib.log import log
from lib import json_manager
from lib import utils
from lib.resource_pack_files import miscellaneous



# Define functions

def update(pack: Path, version: int):
    log("Updating fonts")

    # Iterate through namespaces
    for namespace in (pack / "assets").iterdir():
        if not namespace.is_dir():
            continue

        folder = namespace / "font"
        if not folder.exists():
            continue

        for file_path in folder.glob("**/*.json"):
            if not file_path.is_file():
                continue
            update_font(pack, file_path, version)

def update_font(pack: Path, file_path: Path, version: int):
    contents, load_bool = json_manager.safe_load(file_path)
    if not load_bool:
        return

    if "providers" not in contents:
        return

    # Remove entries from the list that don't have a texture file
    new_providers: list[dict] = []
    space_bool = False
    provider: dict
    for provider in contents["providers"]:
        # Check if it is a space provider
        if provider["type"] == "space":
            space_bool = True

        # Append to list if not a bitmap
        if provider["type"] != "bitmap":
            new_providers.append(provider)
            continue

        # Get texture ID
        provider["file"] = miscellaneous.update_texture_path(provider["file"], version)

        # Add provider to the list if the texture exists
        if miscellaneous.resource_exists(pack, provider["file"], "textures"):
            new_providers.append(provider)

    # Add a space provider if one doesn't exist
    if not space_bool:
        new_providers.insert(
            0,
            {
                "type": "space",
                "advances": {
                    " ": 4,
                    "\u200c": 0
                }
            }
        )

    contents["providers"] = new_providers

    utils.safe_file_write(file_path, json.dumps(contents, indent=4))