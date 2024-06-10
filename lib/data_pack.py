# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import os
import shutil
import json
from nbt import nbt as NBT
from pathlib import Path
from lib.log import log
from lib.data_pack_files import command
from lib.data_pack_files import advancement
from lib.data_pack_files import predicate
from lib.data_pack_files import loot_table
from lib.data_pack_files import item_modifier
from lib.data_pack_files import mcfunction
from lib.data_pack_files import tags
from lib import finalize
from lib import json_manager
from lib import defaults
from lib import utils



# Initialize variables

pack_version = defaults.PACK_VERSION
PACK_FORMAT = defaults.DATA_PACK_FORMAT



# Define functions

def update(world: Path, version: int):
    log("Updating data packs")

    # Set original path
    og_world = world.parent / f'{world.name}_original'

    # Set pack version
    global pack_version
    pack_version = version

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if not og_world.exists():
        log("ERROR: Original copy of world doesn't exist, prepare it!")
        return
    if not (world / "datapacks").exists():
        log("ERROR: World has no data packs!")
        return
    if not (og_world / "datapacks").exists():
        log("ERROR: Original copy of world has no data packs!")
        return

    # Update data packs
    for data_pack in (og_world / "datapacks").iterdir():
        if data_pack.is_file():
            continue
        update_data_pack(
            world / "datapacks" / data_pack.name,
            og_world / "datapacks" / data_pack.name,
            data_pack.name
        )

    # Log completion
    log("Data packs updated")



def update_data_pack(pack: Path, og_pack: Path, data_pack: str):
    log(f"Updating {data_pack}")

    pack.mkdir(exist_ok=True, parents=True)
    update_pack_mcmeta(pack, og_pack)
    update_namespaces(pack, og_pack)



def update_pack_mcmeta(pack: Path, og_pack: Path):
    # Skip if the original pack.mcmeta does not exist
    if not (og_pack / "pack.mcmeta").exists():
        return

    # Modify contents of pack.mcmeta
    contents, load_bool = json_manager.safe_load(og_pack / "pack.mcmeta")
    if not load_bool:
        return
    if contents["pack"]["pack_format"] < PACK_FORMAT:
        contents["pack"]["pack_format"] = PACK_FORMAT
    with (pack / "pack.mcmeta").open("w", encoding="utf-8", newline="\n") as file:
        json.dump(contents, file, indent=4)



def update_namespaces(pack: Path, og_pack: Path):
    # Skip if the data folder does not exist
    if not (og_pack / "data").exists():
        return

    # Iterate through namespaces
    for namespace in (og_pack / "data").iterdir():
        # Skip if not a folder
        if not namespace.is_dir():
            continue

        # Update functions
        folder = pack / "data" / namespace.name / "functions"
        og_folder = namespace / "functions"
        if og_folder.exists():
            update_functions(folder, og_folder, namespace.name)

        # Update advancements
        folder = pack / "data" / namespace.name / "advancements"
        og_folder = namespace / "advancements"
        if og_folder.exists():
            update_advancements(folder, og_folder)

        # Update predicates
        folder = pack / "data" / namespace.name / "predicates"
        og_folder = namespace / "predicates"
        if og_folder.exists():
            update_predicates(folder, og_folder)

        # Update loot tables
        folder = pack / "data" / namespace.name / "loot_tables"
        og_folder = namespace / "loot_tables"
        if og_folder.exists():
            update_loot_tables(folder, og_folder)

        # Update item modifiers
        folder = pack / "data" / namespace.name / "item_modifiers"
        og_folder = namespace / "item_modifiers"
        if og_folder.exists():
            update_item_modifiers(folder, og_folder)

        # Update block tags
        folder = pack / "data" / namespace.name / "tags" / "blocks"
        og_folder = namespace / "tags" / "blocks"
        if og_folder.exists():
            update_tags(folder, og_folder, "blocks")

        # Update item tags
        folder = pack / "data" / namespace.name / "tags" / "items"
        og_folder = namespace / "tags" / "items"
        if og_folder.exists():
            update_tags(folder, og_folder, "items")



def update_functions(folder: Path, og_folder: Path, namespace: str):
    for og_file_path in og_folder.glob("**/*.mcfunction"):
        pack_subdir = og_file_path.as_posix()[len(og_folder.as_posix()) + 1:]
        file_path = folder / pack_subdir
        mcfunction.update(file_path, og_file_path, pack_version, namespace + ":" + pack_subdir.split(".")[0].replace("\\", "/"))



def update_advancements(folder: Path, og_folder: Path):
    for og_file_path in og_folder.glob("**/*.json"):
        pack_subdir = og_file_path.as_posix()[len(og_folder.as_posix()) + 1:]
        file_path = folder / pack_subdir
        advancement.update(file_path, og_file_path, pack_version)



def update_predicates(folder: Path, og_folder: Path):
    for og_file_path in og_folder.glob("**/*.json"):
        pack_subdir = og_file_path.as_posix()[len(og_folder.as_posix()) + 1:]
        file_path = folder / pack_subdir
        predicate.update(file_path, og_file_path, pack_version)



def update_loot_tables(folder: Path, og_folder: Path):
    for og_file_path in og_folder.glob("**/*.json"):
        pack_subdir = og_file_path.as_posix()[len(og_folder.as_posix()) + 1:]
        file_path = folder / pack_subdir
        loot_table.update(file_path, og_file_path, pack_version)



def update_item_modifiers(folder: Path, og_folder: Path):
    for og_file_path in og_folder.glob("**/*.json"):
        pack_subdir = og_file_path.as_posix()[len(og_folder.as_posix()) + 1:]
        file_path = folder / pack_subdir
        item_modifier.update(file_path, og_file_path, pack_version)



def update_tags(folder: Path, og_folder: Path, tag_type: str):
    for og_file_path in og_folder.glob("**/*.json"):
        pack_subdir = og_file_path.as_posix()[len(og_folder.as_posix()) + 1:]
        file_path = folder / pack_subdir
        tags.update(file_path, og_file_path, pack_version, tag_type)



def extract_stored_functions(world: Path, og_world: Path, get_confirmation: bool):
    log("Extracting stored functions")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if not og_world.exists():
        log("ERROR: Original copy of world does not exist!")
        return
    if not (world / "data" / "functions"):
        log("ERROR: World has no stored functions!")
        return
    
    # Get confirmation
    if get_confirmation:
        log(f'This action will move: {(world / "data" / "functions").as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return
    
    data_pack = world / "datapacks" / "stored_functions"
    (data_pack / "data").mkdir(exist_ok=True, parents=True)
    with (data_pack / "pack.mcmeta").open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            {
            	"pack": {
            		"pack_format": PACK_FORMAT,
            		"description": "Stores functions which were originally stored in 1.12 worlds."
            	}
            },
            file,
            indent=4
        )

    for namespace in (world / "data" / "functions").iterdir():
        if not namespace.is_dir():
            continue
        path_length = len(namespace.as_posix()) + 1
        for file_path in namespace.glob("**/*.mcfunction"):
            destination = data_pack / "data" / namespace.name.lower() / "functions" / file_path.as_posix()[path_length:].lower()
            destination.parent.mkdir(exist_ok=True, parents=True)
            shutil.move(file_path, data_pack / "data" / namespace.name.lower() / "functions" / file_path.as_posix()[path_length:].lower())

    # Get gameLoopFunction value
    if (og_world / "level.dat").exists():
        file = NBT.NBTFile(og_world / "level.dat")
        if (
            "Data" in file and
            "GameRules" in file["Data"] and
            "gameLoopFunction" in file["Data"]["GameRules"]
        ):
            ticking_function: str = file["Data"]["GameRules"]["gameLoopFunction"].value.lower()
            if ticking_function:
                tick_json = data_pack / "data" / "minecraft" / "tags" / "functions" / "tick.json"
                tick_json.parent.mkdir(exist_ok=True, parents=True)
                with tick_json.open("w", encoding="utf-8", newline="\n") as file:
                    json.dump(
                        {
                        	"values": [
                                ticking_function
                            ]
                        },
                        file,
                        indent=4
                    )

    log("Stored functions extracted")



def extract_stored_advancements(world: Path, get_confirmation: bool):
    log("Extracting stored advancements")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if not (world / "data" / "advancements"):
        log("ERROR: World has no stored advancements!")
        return
    
    # Get confirmation
    if get_confirmation:
        log(f'This action will move: {(world / "data" / "advancements").as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return
    
    data_pack = world / "datapacks" / "stored_advancements"
    (data_pack / "data").mkdir(exist_ok=True, parents=True)
    with (data_pack / "pack.mcmeta").open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            {
            	"pack": {
            		"pack_format": PACK_FORMAT,
            		"description": "Stores advancements which were originally stored in 1.12 worlds."
            	}
            },
            file,
            indent=4
        )

    for namespace in (world / "data" / "advancements").iterdir():
        if not namespace.is_dir():
            continue
        path_length = len(namespace.as_posix()) + 1
        for file_path in namespace.glob("**/*.json"):
            destination = data_pack / "data" / namespace.name.lower() / "advancements" / file_path.as_posix()[path_length:].lower()
            destination.parent.mkdir(exist_ok=True, parents=True)
            shutil.move(file_path, data_pack / "data" / namespace.name.lower() / "advancements" / file_path.as_posix()[path_length:].lower())

    log("Stored advancements extracted")



def disable_advancements(world: Path, get_confirmation: bool):
    disable_folder(world, "advancements", get_confirmation)

def disable_recipes(world: Path, get_confirmation: bool):
    disable_folder(world, "recipes", get_confirmation)

def disable_folder(world: Path, folder: str, get_confirmation: bool):
    log(f"Disabling {folder}")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if not (world / "datapacks").exists():
        log("ERROR: World has no data packs!")
        return

    # Get confirmation
    if get_confirmation:
        log(f'This action will delete certain folders in: {(world / "datapacks").as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return

    # Disable folder in the data packs
    for data_pack in (world / "datapacks").iterdir():
        # Skip if not a folder
        if not data_pack.is_dir():
            continue

        # Skip if the folder doesn't exist
        if not (data_pack / "data" / "minecraft" / folder).exists():
            continue

        # Remove the folder
        shutil.rmtree(data_pack / "data" / "minecraft" / folder)

        # Add the filter to pack.mcmeta
        file_path = data_pack / "pack.mcmeta"
        if not file_path.exists():
            continue

        # Open file
        contents, load_bool = json_manager.safe_load(file_path)
        if not load_bool:
            return

        # Add filter to contents
        if "filter" not in contents:
            contents["filter"] = {}
        if "block" not in contents["filter"]:
            contents["filter"]["block"] = []
         
        # Check if there is already an entry which disables the folder
        found_bool = False
        for element in contents["filter"]["block"]:
            if "namespace" in element and element["namespace"] == "minecraft" and "path" in element and folder in element["path"]:
                found_bool = True

        # Add block
        if not found_bool and {
	            "namespace": "minecraft",
	            "path": folder + "/.*"
	        } not in contents["filter"]["block"]:
            contents["filter"]["block"].append(
                {
	                "namespace": "minecraft",
	                "path": folder + "/.*"
	            }
            )

        # Save file
        with file_path.open("w", encoding="utf-8", newline="\n") as file:
            json.dump(contents, file, indent=4)

    # Log
    log(f"{folder.capitalize()} disabled")

def fix_disabled_vanilla(world: Path):
    log("Fixing disabled vanilla data pack")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if not (world / "datapacks").exists():
        log("ERROR: World has no data packs!")
        return

    # Create vanilla disabler
    if (world / "datapacks" / "vanilla_disabler").exists():
        log("ERROR: Vanilla disabler already exists!")
        return
    (world / "datapacks" / "vanilla_disabler").mkdir(parents=True, exist_ok=True)
    with (world / "datapacks" / "vanilla_disabler" / "pack.mcmeta").open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            {
            	"pack": {
            		"pack_format": PACK_FORMAT,
            		"description": "Disables various vanilla features so that the critical ones can be enabled."
            	},
            	"filter": {
            	    "block": [
                        {
            	            "namespace": "minecraft",
            	            "path": "advancements/.*"
            	        },
            	        {
            	            "namespace": "minecraft",
            	            "path": "loot_tables/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "recipes/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/banner_pattern/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/blocks/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/cat_variant/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/entity_types/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/fluids/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/game_events/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/instrument/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/items/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/painting_variant/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/point_of_interest_type/.*"
            	        }
            	    ]
            	}
            },
            file,
            indent=4
        )

    # Open level.dat
    file = NBT.NBTFile(world / "level.dat")

    # Enable vanilla data pack and vanilla disabler
    utils.nbt_list_remove(file["Data"]["DataPacks"]["Disabled"], "vanilla")
    utils.nbt_list_remove(file["Data"]["DataPacks"]["Enabled"], "vanilla")
    if not utils.nbt_list_contains(file["Data"]["DataPacks"]["Enabled"], "file/vanilla_disabler"):
        file["Data"]["DataPacks"]["Enabled"].insert(0, NBT.TAG_String("file/vanilla_disabler"))
    file["Data"]["DataPacks"]["Enabled"].insert(0, NBT.TAG_String("vanilla"))

    # Close file
    file.write_file()

    log("Disabled vanilla data pack fixed")

    finalize.log_data_packs(world)



def unzip_packs(world: Path, get_confirmation: bool):
    log("Unzipping data packs")

    # Cancel if the world doesn't exist
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if not (world / "datapacks").exists():
        log("ERROR: World has no data packs!")
        return

    # Get confirmation
    if get_confirmation:
        log(f'This action will remove all zipped files and unzip them in: {(world / "datapacks").as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return

    # Unzip the zipped data packs
    has_packs = False
    for file_path in (world / "datapacks").iterdir():
        # Skip if not a zip
        if not file_path.is_file() or file_path.suffix != ".zip":
            continue

        # Skip if the folder already exists
        folder = file_path.with_suffix("")
        if folder.exists() and folder.is_dir():
            log(f"ERROR: {folder.name} is already unzipped!")
            continue

        # Unzip data pack
        log(f"Unzipping {folder.name}")
        shutil.unpack_archive(file_path, folder, "zip")
        os.remove(file_path)
        has_packs = True

    # Report if there are no zipped packs
    if not has_packs:
        log("ERROR: There are no zipped data packs!")
        return

    log("Data packs unzipped")

    finalize.log_data_packs(world)

def zip_packs(world: Path, get_confirmation: bool):
    log("Zipping data packs")

    # Cancel if the world doesn't exist
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if not (world / "datapacks").exists():
        log("ERROR: World has no data packs!")
        return

    # Get confirmation
    if get_confirmation:
        log(f'This action will remove all folders and zip them up in: {(world / "datapacks").as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return

    # Zip the unzipped data packs
    has_packs = False
    for folder in (world / "datapacks").iterdir():
        # Skip if not a folder
        if not folder.is_dir():
            continue

        # Zip folder
        log(f"Zipping {folder.name}")
        shutil.make_archive(folder, "zip", folder)
        shutil.rmtree(folder)
        has_packs = True

    # Report if there are no unzipped packs
    if not has_packs:
        log("ERROR: There are no unzipped data packs!")
        return

    log("Data packs zipped")

    finalize.log_data_packs(world)



def merge_packs(world: Path, name: str):
    log("Merging data packs")

    # Cancel if the world doesn't exist
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if not (world / "datapacks").exists():
        log("ERROR: World has no data packs!")
        return

    # Cancel if the output pack already exists
    if (world / "datapacks" / (name + " Data Pack")).exists():
        log("ERROR: Output data pack already exists!")
        return

    # Get confirmation
    log(f'This action will remove all data packs and merge them together in: {(world / "datapacks").as_posix()}')
    confirm = input("Is this okay? (Y/N): ")
    if confirm not in ["Y", "y"]:
        log("Action canceled")
        return

    # Merge data packs in order listed in level.dat
    has_packs = False
    file = NBT.NBTFile(world / "level.dat")
    data_pack_entry: NBT.TAG_String
    for data_pack_entry in file["Data"]["DataPacks"]["Enabled"]:
        data_pack_name = str(data_pack_entry)
        # Skip if vanilla
        if data_pack_name == "vanilla":
            continue
        
        # Remove file/ prefix
        if len(data_pack_name) > 5 and data_pack_name[:5] == "file/":
            data_pack_name = data_pack_name[5:]

        # Define data pack path
        data_pack = world / "datapacks" / data_pack_name

        # Skip if doesn't exist or not a folder
        if not data_pack.exists() or not data_pack.is_dir():
            continue

        merge_pack(
            world / "datapacks" / (name + " Data Pack"),
            data_pack,
            data_pack.name
        )
        has_packs = True

    # Report if there are no packs
    if not has_packs:
        log("ERROR: World has no data packs!")
        return

    log("Data packs merged")

    finalize.log_data_packs(world)

    # Tell if there are minecraft advancements or recipes
    if (world / "datapacks" / (name + " Data Pack") / "data" / "minecraft" / "advancements").exists():
        log("Advancements in the 'minecraft' namespace were found, consider disabling them")
    if (world / "datapacks" / (name + " Data Pack") / "data" / "minecraft" / "recipes").exists():
        log("Recipes in the 'minecraft' namespace were found, consider disabling them")

def merge_pack(pack_a: Path, pack_b: Path, data_pack: str):
    log(f"Merging {data_pack}")

    # Iterate through files
    for file_path_b in pack_b.glob("**/*"):
        # Skip if not a file
        if not file_path_b.is_file():
            continue

        # Get pack subdirectory
        pack_subdir = file_path_b.as_posix()[len(pack_b.as_posix()) + 1:]
        file_path_a = pack_a / pack_subdir
        folders = pack_subdir.split("/")

        merge_file(folders, file_path_a, file_path_b)

    # Remove data pack
    shutil.rmtree(pack_b)

def merge_file(folders: list[str], file_path_a: Path, file_path_b: Path):
    # Create folder path if it doesn't exist
    file_path_a.parent.mkdir(parents=True, exist_ok=True)

    # Copy file directly if it doesn't exist
    if not file_path_a.exists():
        shutil.copy(file_path_b, file_path_a)
        return

    # Determine if files should be JSON merged
    merge_json = False
    if folders[0] == "pack.mcmeta":
        merge_json = True
    if len(folders) >= 4 and folders[0] == "data" and folders[2] == "tags":
        merge_json = True

    # Merge JSON
    if merge_json:
        # Open files
        contents_b, load_bool = json_manager.safe_load(file_path_b)
        if not load_bool:
            # If the source file is broken, skip it
            return

        contents_a, load_bool = json_manager.safe_load(file_path_a)
        if not load_bool:
            # If the destination file is broken, overwrite it
            shutil.copy(file_path_b, file_path_a)
            return

        # Write to file
        with file_path_a.open("w", encoding="utf-8", newline="\n") as file:
            json.dump(json_manager.merge(contents_a, contents_b), file, indent=4)
        return

    # Overwrite file
    shutil.copy(file_path_b, file_path_a)