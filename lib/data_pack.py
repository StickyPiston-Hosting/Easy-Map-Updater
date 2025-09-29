# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import os
import shutil
import json
from typing import cast
from nbt import nbt as NBT
from pathlib import Path
from lib.log import log
from lib.data_pack_files import command # This import is necessary to prevent circular loading
from lib.data_pack_files import advancement
from lib.data_pack_files import predicate
from lib.data_pack_files import loot_table
from lib.data_pack_files import recipe
from lib.data_pack_files import item_modifier
from lib.data_pack_files import mcfunction
from lib.data_pack_files import tags
from lib.data_pack_files.restore_behavior import lock_fixer
from lib.region_files import structure
from lib import finalize
from lib import json_manager
from lib import defaults
from lib import utils



# Initialize variables

pack_version = defaults.PACK_VERSION
PACK_FORMAT = defaults.DATA_PACK_FORMAT

DIRECTORY_RENAMES = [
    ("advancements", "advancement"),
    ("functions", "function"),
    ("item_modifiers", "item_modifier"),
    ("loot_tables", "loot_table"),
    ("predicates", "predicate"),
    ("recipes", "recipe"),
    ("structures", "structure"),
    ("tags/blocks", "tags/block"),
    ("tags/entity_types", "tags/entity_type"),
    ("tags/fluids", "tags/fluid"),
    ("tags/functions", "tags/function"),
    ("tags/game_events", "tags/game_event"),
    ("tags/items", "tags/item"),
]



# Define functions

def update(world: Path, version: int):
    log("Updating data packs")

    # Set source path
    source_world = world.parent / f'{world.name}_source'

    # Set pack version
    global pack_version
    pack_version = version

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if not source_world.exists():
        log("ERROR: Source copy of world doesn't exist, prepare it!")
        return
    if not (world / "datapacks").exists():
        log("ERROR: World has no data packs!")
        return
    if not (source_world / "datapacks").exists():
        log("ERROR: Source copy of world has no data packs!")
        return

    # Update data packs
    for data_pack in (source_world / "datapacks").iterdir():
        if data_pack.is_file():
            continue
        try:
            update_data_pack(
                world / "datapacks" / data_pack.name,
                source_world / "datapacks" / data_pack.name,
                data_pack.name
            )
        except Exception:
            log(f"An error was thrown while updating the data pack: {data_pack.name}")
            utils.log_error()

    # Replace behavior restoring data packs if they have been updated
    if version <= 2104:
        for name in ["lock_fixer", "lock_fixer.zip"]:
            lock_fixer_path = world / "datapacks" / name
            if lock_fixer_path.exists():
                log("Replacing lock fixer data pack with updated version")
                if lock_fixer_path.is_file():
                    os.remove(lock_fixer_path)
                else:
                    shutil.rmtree(lock_fixer_path)
                lock_fixer.create_pack(world)
                break

    # Log completion
    log("Data packs updated")



def update_data_pack(pack: Path, source_pack: Path, data_pack: str):
    log(f"Updating {data_pack}")

    pack.mkdir(exist_ok=True, parents=True)
    update_pack_mcmeta(pack, source_pack)
    update_namespaces(pack, source_pack)



def update_pack_mcmeta(pack: Path, source_pack: Path):
    # Skip if the source pack.mcmeta does not exist
    if not (source_pack / "pack.mcmeta").exists():
        return

    # Modify contents of pack.mcmeta
    contents, load_bool = json_manager.safe_load(source_pack / "pack.mcmeta")
    if not load_bool:
        return
    
    # Update pack format
    min_format = PACK_FORMAT
    max_format = PACK_FORMAT
    if "pack_format" in contents["pack"]:
        if isinstance(contents["pack"]["pack_format"], list):
            max_format = max(max_format, contents["pack"]["pack_format"][0])
        else:
            max_format = max(max_format, contents["pack"]["pack_format"])
    if "max_format" in contents["pack"]:
        if isinstance(contents["pack"]["max_format"], list):
            max_format = max(max_format, contents["pack"]["max_format"][0])
        else:
            max_format = max(max_format, contents["pack"]["max_format"])
    if "supported_formats" in contents["pack"]:
        if isinstance(contents["pack"]["supported_formats"], dict):
            if "max_inclusive" in contents["pack"]["supported_formats"]:
                max_format = max(max_format, contents["pack"]["supported_formats"]["max_inclusive"])
        elif isinstance(contents["pack"]["supported_formats"], list):
            max_format = max(max_format, contents["pack"]["supported_formats"][0])
        else:
            max_format = max(max_format, contents["pack"]["supported_formats"])
        del contents["pack"]["supported_formats"]

    if max_format == min_format:
        contents["pack"]["pack_format"] = max_format
        if "min_format" in contents["pack"]:
            del contents["pack"]["min_format"]
        if "max_format" in contents["pack"]:
            del contents["pack"]["max_format"]
    else:
        contents["pack"]["min_format"] = min_format
        contents["pack"]["max_format"] = max_format
        if "pack_format" in contents["pack"]:
            del contents["pack"]["pack_format"]

    # Update filters
    if "filter" in contents:
        if "block" in contents["filter"]:
            for path_filter in contents["filter"]["block"]:
                for folder_pair in DIRECTORY_RENAMES:
                    if cast(str, path_filter["path"]).startswith(folder_pair[0]):
                        path_filter["path"] = folder_pair[1] + path_filter["path"][len(folder_pair[0]):]

    utils.safe_file_write(pack / "pack.mcmeta", json.dumps(contents, indent=4))



def update_namespaces(pack: Path, source_pack: Path):
    # Skip if the data folder does not exist
    if not (source_pack / "data").exists():
        return

    # Iterate through namespaces
    for namespace in (source_pack / "data").iterdir():
        # Skip if not a folder
        if not namespace.is_dir():
            continue

        # Update functions
        folder = pack / "data" / namespace.name / "function"
        source_folder = namespace / "function"
        if source_folder.exists():
            update_functions(folder, source_folder, namespace.name)

        # Update advancements
        folder = pack / "data" / namespace.name / "advancement"
        source_folder = namespace / "advancement"
        if source_folder.exists():
            update_advancements(folder, source_folder)

        # Update predicates
        folder = pack / "data" / namespace.name / "predicate"
        source_folder = namespace / "predicate"
        if source_folder.exists():
            update_predicates(folder, source_folder)

        # Update loot tables
        folder = pack / "data" / namespace.name / "loot_table"
        source_folder = namespace / "loot_table"
        if source_folder.exists():
            update_loot_tables(folder, source_folder)

        # Update recipes
        folder = pack / "data" / namespace.name / "recipe"
        source_folder = namespace / "recipe"
        if source_folder.exists():
            update_recipes(folder, source_folder)

        # Update item modifiers
        folder = pack / "data" / namespace.name / "item_modifier"
        source_folder = namespace / "item_modifier"
        if source_folder.exists():
            update_item_modifiers(folder, source_folder)

        # Update block tags
        folder = pack / "data" / namespace.name / "tags" / "block"
        source_folder = namespace / "tags" / "block"
        if source_folder.exists():
            update_tags(folder, source_folder, "block")

        # Update item tags
        folder = pack / "data" / namespace.name / "tags" / "item"
        source_folder = namespace / "tags" / "item"
        if source_folder.exists():
            update_tags(folder, source_folder, "item")

        # Update structures
        folder = pack / "data" / namespace.name / "structure"
        source_folder = namespace / "structure"
        if source_folder.exists():
            update_structures(folder, source_folder, namespace.name)



def update_functions(folder: Path, source_folder: Path, namespace: str):
    for source_file_path in source_folder.glob("**/*.mcfunction"):
        if not source_file_path.is_file():
            continue
        pack_subdir = source_file_path.as_posix()[len(source_folder.as_posix()) + 1:]
        file_path = folder / pack_subdir
        try:
            mcfunction.update(file_path, source_file_path, pack_version, namespace + ":" + pack_subdir.split(".")[0].replace("\\", "/"))
        except Exception:
            log(f"ERROR: An error occurred while updating the function: {source_file_path.as_posix()}")
            utils.log_error()



def update_advancements(folder: Path, source_folder: Path):
    for source_file_path in source_folder.glob("**/*.json"):
        if not source_file_path.is_file():
            continue
        pack_subdir = source_file_path.as_posix()[len(source_folder.as_posix()) + 1:]
        file_path = folder / pack_subdir
        try:
            advancement.update(file_path, source_file_path, pack_version)
        except Exception:
            log(f"ERROR: An error occurred when updating advancement: {source_file_path.as_posix()}")
            utils.log_error()



def update_predicates(folder: Path, source_folder: Path):
    for source_file_path in source_folder.glob("**/*.json"):
        if not source_file_path.is_file():
            continue
        pack_subdir = source_file_path.as_posix()[len(source_folder.as_posix()) + 1:]
        file_path = folder / pack_subdir
        try:
            predicate.update(file_path, source_file_path, pack_version)
        except Exception:
            log(f"ERROR: An error occurred when updating predicate: {source_file_path.as_posix()}")
            utils.log_error()



def update_loot_tables(folder: Path, source_folder: Path):
    for source_file_path in source_folder.glob("**/*.json"):
        if not source_file_path.is_file():
            continue
        pack_subdir = source_file_path.as_posix()[len(source_folder.as_posix()) + 1:]
        file_path = folder / pack_subdir
        try:
            loot_table.update(file_path, source_file_path, pack_version)
        except Exception:
            log(f"ERROR: An error occurred when updating loot table: {source_file_path.as_posix()}")
            utils.log_error()



def update_recipes(folder: Path, source_folder: Path):
    for source_file_path in source_folder.glob("**/*.json"):
        if not source_file_path.is_file():
            continue
        pack_subdir = source_file_path.as_posix()[len(source_folder.as_posix()) + 1:]
        file_path = folder / pack_subdir
        try:
            recipe.update(file_path, source_file_path, pack_version)
        except Exception:
            log(f"ERROR: An error occurred when updating recipe: {source_file_path.as_posix()}")
            utils.log_error()



def update_item_modifiers(folder: Path, source_folder: Path):
    for source_file_path in source_folder.glob("**/*.json"):
        if not source_file_path.is_file():
            continue
        pack_subdir = source_file_path.as_posix()[len(source_folder.as_posix()) + 1:]
        file_path = folder / pack_subdir
        try:
            item_modifier.update(file_path, source_file_path, pack_version)
        except Exception:
            log(f"ERROR: An error occurred when updating item modifier: {source_file_path.as_posix()}")
            utils.log_error()



def update_tags(folder: Path, source_folder: Path, tag_type: str):
    for source_file_path in source_folder.glob("**/*.json"):
        if not source_file_path.is_file():
            continue
        pack_subdir = source_file_path.as_posix()[len(source_folder.as_posix()) + 1:]
        file_path = folder / pack_subdir
        try:
            tags.update(file_path, source_file_path, pack_version, tag_type)
        except Exception:
            log(f"ERROR: An error occurred when updating tag: {source_file_path.as_posix()}")
            utils.log_error()



def update_structures(folder: Path, source_folder: Path, namespace: str):
    for source_file_path in source_folder.glob("**/*.nbt"):
        if not source_file_path.is_file():
            continue
        pack_subdir = source_file_path.as_posix()[len(source_folder.as_posix()) + 1:]
        file_path = folder / pack_subdir
        log(f" Fixing structure {namespace}:{pack_subdir[:-4]}")
        try:
            structure.update(file_path, source_file_path, pack_version)
        except Exception:
            log(f"ERROR: An error occurred when updating structure: {source_file_path.as_posix()}")
            utils.log_error()
        


def rename_directories(world: Path, get_conformation: bool):
    log("Renaming data pack directories")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    
    # Get confirmation
    if get_conformation:
        log(f'This action will rename several directories in: {(world / "datapacks").as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return
        
    # Iterate through folders
    data_pack_path = world / "datapacks"
    if data_pack_path.exists() and data_pack_path.is_dir():
        for data_pack in (world / "datapacks").iterdir():
            data_path = data_pack / "data"
            if data_path.exists() and data_path.is_dir():
                for namespace in data_path.iterdir():
                    for folder_pair in DIRECTORY_RENAMES:
                        source_path = namespace / folder_pair[0]
                        target_path = namespace / folder_pair[1]
                        if source_path.exists() and source_path.is_dir():
                            if target_path.exists():
                                log(f'ERROR: Cannot rename directory {source_path}, target path already exists')
                            else:
                                os.rename(source_path, target_path)
    
    log("Data pack directories renamed")



def extract_stored_functions(world: Path, get_confirmation: bool):
    log("Extracting stored functions")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
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
    utils.safe_file_write(data_pack / "pack.mcmeta",
        json.dumps(
            {
            	"pack": {
            		"pack_format": PACK_FORMAT,
            		"description": "Stores functions which were originally stored in 1.12 worlds."
            	}
            },
            indent=4
        )
    )

    for namespace in (world / "data" / "functions").iterdir():
        if not namespace.is_dir():
            continue
        path_length = len(namespace.as_posix()) + 1
        for file_path in namespace.glob("**/*.mcfunction"):
            if not file_path.is_file():
                continue
            destination = data_pack / "data" / namespace.name.lower() / "function" / file_path.as_posix()[path_length:].lower()
            destination.parent.mkdir(exist_ok=True, parents=True)
            shutil.move(file_path, destination)

    # Get gameLoopFunction value
    if (world / "level.dat").exists():
        file = NBT.NBTFile(world / "level.dat")
        if (
            "Data" in file and
            "GameRules" in file["Data"] and
            "gameLoopFunction" in file["Data"]["GameRules"]
        ):
            ticking_function: str = file["Data"]["GameRules"]["gameLoopFunction"].value.lower()
            if ticking_function:
                tick_json = data_pack / "data" / "minecraft" / "tags" / "function" / "tick.json"
                tick_json.parent.mkdir(exist_ok=True, parents=True)
                utils.safe_file_write(tick_json,
                    json.dumps(
                        {
                        	"values": [
                                ticking_function
                            ]
                        },
                        indent=4
                    )
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
    utils.safe_file_write(data_pack / "pack.mcmeta",
        json.dumps(
            {
            	"pack": {
            		"pack_format": PACK_FORMAT,
            		"description": "Stores advancements which were originally stored in 1.12 worlds."
            	}
            },
            indent=4
        )
    )

    for namespace in (world / "data" / "advancements").iterdir():
        if not namespace.is_dir():
            continue
        path_length = len(namespace.as_posix()) + 1
        for file_path in namespace.glob("**/*.json"):
            if not file_path.is_file():
                continue
            destination = data_pack / "data" / namespace.name.lower() / "advancement" / file_path.as_posix()[path_length:].lower()
            destination.parent.mkdir(exist_ok=True, parents=True)
            shutil.move(file_path, destination)

    log("Stored advancements extracted")



def disable_advancements(world: Path, get_confirmation: bool):
    disable_folder(world, "advancement", get_confirmation)

def disable_recipes(world: Path, get_confirmation: bool):
    disable_folder(world, "recipe", get_confirmation)

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
        utils.safe_file_write(file_path, json.dumps(contents, indent=4))

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
    utils.safe_file_write(world / "datapacks" / "vanilla_disabler" / "pack.mcmeta",
        json.dumps(
            {
            	"pack": {
            		"pack_format": PACK_FORMAT,
            		"description": "Disables various vanilla features so that the critical ones can be enabled."
            	},
            	"filter": {
            	    "block": [
                        {
            	            "namespace": "minecraft",
            	            "path": "advancement/.*"
            	        },
            	        {
            	            "namespace": "minecraft",
            	            "path": "loot_table/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "recipe/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/banner_pattern/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/block/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/cat_variant/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/entity_type/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/fluid/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/game_event/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/instrument/.*"
            	        },
                        {
            	            "namespace": "minecraft",
            	            "path": "tags/item/.*"
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
            indent=4
        )
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
        shutil.make_archive(folder.as_posix(), "zip", folder)
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
    if (world / "datapacks" / (name + " Data Pack") / "data" / "minecraft" / "advancement").exists():
        log("Advancements in the 'minecraft' namespace were found, consider disabling them")
    if (world / "datapacks" / (name + " Data Pack") / "data" / "minecraft" / "recipe").exists():
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
        utils.safe_file_write(file_path_a, json.dumps(json_manager.merge(contents_a, contents_b), indent=4))
        return

    # Overwrite file
    shutil.copy(file_path_b, file_path_a)