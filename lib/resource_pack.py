# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import os
import json
import shutil
from pathlib import Path
from typing import cast, Any
from PIL import Image, ImageDraw, ImageChops
from lib.log import log
from lib.resource_pack_files import atlas_logger
from lib.resource_pack_files import fonts
from lib.resource_pack_files import models
from lib.resource_pack_files import remove_translucency
from lib import json_manager
from lib import finalize
from lib import defaults
from lib import utils



# Initialize variables

pack_version = defaults.PACK_VERSION
PACK_FORMAT = defaults.RESOURCE_PACK_FORMAT
PROGRAM_PATH = Path(__file__).parent

with (PROGRAM_PATH / "resource_pack_files" / "file_legend.json").open("r", encoding="utf-8") as file:
    FILE_LEGEND: dict[str, Any] = json.load(file)



# Define functions

def update(pack: Path, version: int):
    log("Updating resource pack")

    global pack_version
    pack_version = version

    og_pack = pack.parent / f'{pack.name}_original'

    # Check for errors
    if not og_pack.exists():
        log("ERROR: Original copy of resource pack does not exist!")
        return
    if not (og_pack / "pack.mcmeta").exists():
        log("ERROR: Resource pack does not have pack.mcmeta!")
        return
    if not (og_pack / "assets").exists():
        log("ERROR: Resource pack does not have assets!")
        return

    dirpath, dirnames, filenames = next(os.walk(og_pack / "assets"))
    if len(dirnames) == 0:
        log("ERROR: Resource pack has no namespaces!")
        return
    
    pack.mkdir(exist_ok=True, parents=True)
    if (pack / "assets").exists():
        shutil.rmtree(pack / "assets")

    try:
        update_pack_mcmeta(og_pack, pack)
        update_file_names(og_pack, pack)
        atlas_logger.log_atlas(pack)
        fonts.update(pack)
        models.update(pack, pack_version)
        finalize.delete_ds_store(pack)
        log("Resource pack updated")
    except Exception:
        log(f"An error occurred while updating the resource pack: {pack.as_posix()}")
        utils.log_error()



def update_pack_mcmeta(og_pack: Path, pack: Path):
    contents, load_bool = json_manager.safe_load(og_pack / "pack.mcmeta")
    if not load_bool:
        return
    if contents["pack"]["pack_format"] < PACK_FORMAT:
        contents["pack"]["pack_format"] = PACK_FORMAT
    utils.safe_file_write(pack / "pack.mcmeta", json.dumps(contents, indent=4))



def update_file_names(og_pack: Path, pack: Path):
    log("Updating file names")
    og_namespace = og_pack / "assets"
    namespace = pack / "assets"
    if not og_namespace.exists():
        return
    for og_file_path in og_namespace.glob("**/*"):
        if og_file_path.is_dir():
            continue
        subdir = og_file_path.as_posix()[len(og_namespace.as_posix())+1:]
        if subdir.endswith(".mcmeta"):
            continue
        path = subdir.split("/")
        # Search for the file in the legend to rename it
        for version in FILE_LEGEND:
            if pack_version > int(version):
                continue
            legend = FILE_LEGEND[version]
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
                    for entry in target:
                        update_file_name(og_namespace, namespace, subdir, entry)
                elif isinstance(target, str) or isinstance(target, dict):
                    update_file_name(og_namespace, namespace, subdir, target)
                break
        # If the file is not renamed, carry it over directly
        else:
            (namespace / subdir).parent.mkdir(exist_ok=True, parents=True)
            shutil.copyfile(
                og_namespace / subdir,
                namespace / subdir
            )
            og_path = (og_namespace / subdir).parent / ((og_namespace / subdir).name + ".mcmeta")
            path = (namespace / subdir).parent / ((namespace / subdir).name + ".mcmeta")
            if og_path.exists():
                shutil.copyfile(
                    og_path,
                    path
                )

def update_file_name(og_namespace: Path, namespace: Path, subdir: str, target: str | dict[str, Any]):
    path = Path(subdir)

    if defaults.DEBUG_MODE:
        log(f"Updating {(og_namespace / subdir).as_posix()}")

    try:

        if subdir in [
            "realms/textures/gui/realms/expires_soon_icon.png"
        ]:
            log(f'WARNING: Edge case file found: {subdir}')

        slice_data = None
        clip_data = None
        metadata = None
        if isinstance(target, str):
            target_path = target.replace("*", path.name).split("/")
        elif isinstance(target, dict):
            target_path = target["path"].replace("*", path.name).split("/")
            if "slice" in target:
                slice_data = cast(list[int], target["slice"])
            if "clip" in target:
                clip_data = cast(list[int], target["clip"])
            if "metadata" in target:
                metadata = cast(dict[str, Any], target["metadata"])

        path = path.parent
        for target_folder in target_path:
            if target_folder == ".":
                path = path.parent
            else:
                path = path / target_folder
        (namespace / path).parent.mkdir(exist_ok=True, parents=True)

        if slice_data:
            image = Image.open(og_namespace / subdir, "r", ["png"])
            ax = min(int( (slice_data[0]                )*image.size[0]//slice_data[4] ), image.size[0] - 1)
            ay = min(int( (slice_data[1]                )*image.size[1]//slice_data[5] ), image.size[1] - 1)
            bx = max(int( (slice_data[0] + slice_data[2])*image.size[0]//slice_data[4] ), ax + 1)
            by = max(int( (slice_data[1] + slice_data[3])*image.size[1]//slice_data[5] ), ay + 1)
            cropped_image = image.crop((ax, ay, bx, by))
            if defaults.DEBUG_MODE:
                log(f"Original dimensions: {image.size[0]}, {image.size[1]} - Cropped dimensions: {cropped_image.size[0]}, {cropped_image.size[1]}")
            cropped_image.save(namespace / path, "png")
        elif clip_data:
            image = Image.open(og_namespace / subdir, "r", ["png"])
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            alpha = image.split()[-1]

            mask = Image.new("L", image.size, color = 255)
            draw = ImageDraw.Draw(mask)
            ax = min(int( (clip_data[0]               )*image.size[0]//clip_data[4] ), image.size[0] - 1)
            ay = min(int( (clip_data[1]               )*image.size[1]//clip_data[5] ), image.size[1] - 1)
            bx = max(int( (clip_data[0] + clip_data[2])*image.size[0]//clip_data[4] ) - 1, ax + 1)
            by = max(int( (clip_data[1] + clip_data[3])*image.size[1]//clip_data[5] ) - 1, ay + 1) 
            draw.rectangle((ax, ay, bx, by), fill = 0)
            alpha = ImageChops.subtract(alpha, mask)

            image.putalpha(alpha)
            image.save(namespace / path, "png")
        else:
            shutil.copyfile(
                og_namespace / subdir,
                namespace / path
            )

        og_metadata_path = (og_namespace / subdir).parent / f'{(og_namespace / subdir).name}.mcmeta'
        metadata_path = (namespace / path).parent / f'{path.name}.mcmeta'
        if og_metadata_path.exists():
            shutil.copyfile(
                og_metadata_path,
                metadata_path
            )

        if metadata:
            utils.safe_file_write(metadata_path, json.dumps(metadata, indent=4))

    except:
        log(f"An error occurred when updating {(og_namespace / subdir).as_posix()}")



def fix(pack: Path):
    log("Fixing resource pack")

    if not pack.exists():
        log("ERROR: Resource pack does not exist!")
        return

    remove_translucency.remove_translucency(pack)

    log("Resource pack fixed")



def import_pack(world: Path, pack: Path, get_confirmation: bool):
    log("Importing resource pack")

    # Cancel if the pack doesn't exist or if the destination folder already exists
    file = world / "resources.zip"
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if not file.exists():
        log("ERROR: resources.zip does not exist!")
        return

    # Get confirmation
    if get_confirmation:
        log(f'This action will delete: {(world / "resources.zip").as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return
        
        if pack.exists():
            log(f'This action will overwrite: {pack.as_posix()}')
            confirm = input("Is this okay? (Y/N): ")
            if confirm not in ["Y", "y"]:
                log("Action canceled")
                return

    # Unpack archive
    try:
        if pack.exists():
            if pack.is_dir():
                shutil.rmtree(pack)
            else:
                os.remove(pack)
        shutil.unpack_archive(file, pack, "zip")
        os.remove(file)
        log("Resource pack imported")
    except Exception:
        log(f"An error occurred when importing the resource pack")
        utils.log_error()

def export_pack(world: Path, pack: Path, get_confirmation: bool):
    log("Exporting resource pack")

    # Cancel if the pack doesn't exist
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if not pack.exists():
        log("ERROR: Resource pack doesn't exist!")
        return

    # Get confirmation
    if (world / "resources.zip").exists() and get_confirmation:
        log(f'This action will overwrite: {(world / "resources.zip").as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return

    # Make archive
    try:
        shutil.make_archive((world / "resources").as_posix(), "zip", pack)
        log("Resource pack exported")
    except Exception:
        log(f"An error occurred when exporting the resource pack: {pack.as_posix()}")
        utils.log_error()



def purge_vanilla_assets(pack: Path):
    log("Purging vanilla assets from resource pack")

    if not pack.exists():
        log("ERROR: Resource pack doesn't exist!")
        return

    # Get confirmation
    log(f'This action will remove various files in: {pack.as_posix()}')
    confirm = input("Is this okay? (Y/N): ")
    if confirm not in ["Y", "y"]:
        log("Action canceled")
        return

    vanilla_pack = pack.parent / input("Name of vanilla pack to reference: ")
    if not vanilla_pack.exists():
        log("ERROR: Vanilla resource pack does not exist!")
        return

    # Iterate through all files in the resource pack
    duplicate_files = 0
    for dirpath, dirnames, filenames in os.walk(pack / "assets"):
        # Iterate through files in folder
        for filename in filenames:
            file_path = Path(dirpath) / filename
            vanilla_file_path = vanilla_pack / file_path.as_posix()[len(pack.as_posix())+1:]

            # Skip file if the vanilla pack doesn't have it
            if not vanilla_file_path.exists():
                continue

            # Compare files
            if file_path.suffix in defaults.TEXT_FILE_FORMATS:
                contents = utils.safe_file_read(file_path)
                vanilla_contents = utils.safe_file_read(vanilla_file_path)
                if contents == vanilla_contents:
                    duplicate_files += 1
                    os.remove(file_path)
                    if defaults.DEBUG_MODE:
                        log(f'Removing {file_path.as_posix()}')
            else:
                with file_path.open("rb") as file:
                    contents = file.read()
                with vanilla_file_path.open("rb") as file:
                    vanilla_contents = file.read()
                if contents == vanilla_contents:
                    duplicate_files += 1
                    os.remove(file_path)
                    if defaults.DEBUG_MODE:
                        log(f'Removing {file_path.as_posix()}')

        # Delete folder if it is empty
        if len(os.listdir(dirpath)) == 0:
            shutil.rmtree(dirpath)

    log(f'{duplicate_files} duplicate file{"" if duplicate_files == 1 else "s"} were removed')
            