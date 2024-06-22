# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from nbt import nbt as NBT
import os
import shutil
import requests
import json
from typing import TypedDict
from pathlib import Path
from lib import defaults
from lib import option_manager
from lib import utils
from lib.log import log



# Initialize variables

PROGRAM_PATH = Path(__file__).parent.parent
MINECRAFT_PATH = PROGRAM_PATH.parent



# Define functions

def delete_path(path: Path):
    if path.exists() and path.is_dir():
        shutil.rmtree(path)

def delete_file(file: Path):
    if file.exists() and file.is_file():
        os.remove(file)



def scan_world(world: Path, resource_pack: Path) -> dict[str, bool]:
    log("Scanning world")

    # Initialize booleans
    booleans = {
        "world": False,
        "resource_pack": False,
        "disabled_vanilla": False,
        "zipped_data_packs": False,
        "stored_functions": False,
        "stored_advancements": False,
        "advancements": False,
        "recipes": False
    }

    # Throw error if the world doesn't exist
    if not world.exists():
        log("ERROR: World does not exist!")
        return booleans
    booleans["world"] = True
    
    # Check if there is a resource pack
    if (world / "resources.zip").exists():
        log("'resources.zip' found, import it and scan world again")
        booleans["resource_pack"] = True
            

    # Check if vanilla data pack is disabled
    file = NBT.NBTFile(world / "level.dat")
    if "Data" in file and "DataPacks" in file["Data"] and "Disabled" in file["Data"]["DataPacks"]:
        for data_pack in file["Data"]["DataPacks"]["Disabled"]:
            if str(data_pack) == "vanilla":
                log("Vanilla data pack is disabled, consider fixing the disabled vanilla data pack")
                booleans["disabled_vanilla"] = True

    # List version of world
    if "Data" in file and "Version" in file["Data"] and "Name" in file["Data"]["Version"] and "Id" in file["Data"]["Version"]:
        version_name: str = file["Data"]["Version"]["Name"].value
        version_id: int = file["Data"]["Version"]["Id"].value
        version = defaults.PACK_VERSION
        for data_version in defaults.DATA_VERSIONS:
            if version_id <= data_version:
                version = defaults.DATA_VERSIONS[data_version]
                break
    else:
        version_name = "Unknown"
        version = 809
    option_manager.set_version(version)

    # Check if there are stored functions
    if (world / "data" / "functions").exists():
        log("Stored functions found, extract them and scan world again")
        booleans["stored_functions"] = True

    # Check if there are stored advancements
    if (world / "data" / "advancements").exists():
        log("Stored advancements found, extract them and scan world again")
        booleans["stored_advancements"] = True

    # Iterate through data packs
    if (world / "datapacks").exists() and (world / "datapacks").is_dir():
        for pack in (world / "datapacks").iterdir():
            # Check if there are any zipped data packs
            if not booleans["zipped_data_packs"] and pack.is_file() and pack.suffix == ".zip":
                log("Zipped data packs found, unzip them and scan world again")
                booleans["zipped_data_packs"] = True

            # Check if advancements are present in the minecraft namespace
            if not booleans["advancements"] and pack.is_dir() and (pack / "data" / "minecraft" / "advancements").exists():
                log("Advancements in the 'minecraft' namespace were found, consider disabling them")
                booleans["advancements"] = True

            # Check if recipes are present in the minecraft namespace
            if not booleans["recipes"] and pack.is_dir() and (pack / "data" / "minecraft" / "recipes").exists():
                log("Recipes in the 'minecraft' namespace were found, consider disabling them")
                booleans["recipes"] = True

    if version_name == "Unknown":
        version_name, version = utils.get_version_from_user("Version ID not found, please enter world version: ", False)
        option_manager.set_version(version)
    log(f'Version: {version_name} - {version}')

    log("World scanned")
    return booleans



def finalize(world: Path, resource_pack: Path, get_confirmation: bool):
    log("Finalizing world")

    # Throw error if the world doesn't exist
    if not world.exists():
        log("ERROR: World does not exist!")
        return

    # Get confirmation
    if get_confirmation:
        log(f'This action will change several files in: {world.as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return

    clean_level_dat(world)
    clean_scoreboard_dat(world)
    delete_empty_files(world)
    delete_ds_store(world)
    delete_junk_files(world)
    log_data_packs(world)
    convert_line_endings_folder(world)
    convert_line_endings_folder(resource_pack)
    log("World finalized")



def clean_level_dat(world: Path):
    log("Cleaning level.dat")

    # Open file
    file_path = world / "level.dat"
    file = NBT.NBTFile(file_path)

    # Delete player
    if "Player" in file["Data"]:
        print("")
        confirm = input("Do you wish to remove player data from level.dat? (Y/N): ")
        if confirm in ["Y", "y"]:
            del file["Data"]["Player"]

    # Apply default player data, using the world spawn point as the position
    if "Player" not in file["Data"]:
        file["Data"]["Player"] = NBT.TAG_Compound()
        file["Data"]["Player"]["Pos"] = NBT.TAG_List(type=NBT.TAG_Double)
        file["Data"]["Player"]["Pos"].append(NBT.TAG_Double(
            float(file["Data"]["SpawnX"].value) + 0.5 if "SpawnX" in file["Data"] else 0.0
        ))
        file["Data"]["Player"]["Pos"].append(NBT.TAG_Double(
            float(file["Data"]["SpawnY"].value) if "SpawnY" in file["Data"] else 0.0
        ))
        file["Data"]["Player"]["Pos"].append(NBT.TAG_Double(
            float(file["Data"]["SpawnZ"].value) + 0.5 if "SpawnZ" in file["Data"] else 0.0
        ))
        file["Data"]["Player"]["Rotation"] = NBT.TAG_List(type=NBT.TAG_Float)
        file["Data"]["Player"]["Rotation"].append(NBT.TAG_Float(
            float(file["Data"]["SpawnAngle"].value) if "SpawnAngle" in file["Data"] else 0.0
        ))
        file["Data"]["Player"]["Rotation"].append(NBT.TAG_Float(0.0))

    # Remove modded entries
    if "ServerBrands" in file["Data"]:
        file["Data"]["ServerBrands"] = NBT.TAG_List(type=NBT.TAG_String)
        file["Data"]["ServerBrands"].append(NBT.TAG_String("vanilla"))
        file["Data"]["ServerBrands"].append(NBT.TAG_String("StickyPiston Easy Map Updater"))

    # Set modded boolean
    if "WasModded" in file["Data"]:
        file["Data"]["WasModded"] = NBT.TAG_Byte(0)

    # Close file
    file.write_file(file_path)

class PlayerScoreEntry(TypedDict):
    team: str
    objectives: list[str]

def get_player_names(world: Path):
    log("Getting player names")

    # Stop if scoreboard.dat does not exist
    file_path = world / "data" / "scoreboard.dat"
    if not (file_path).exists():
        log("ERROR: scoreboard.dat does not exist!")
        with (PROGRAM_PATH / "player_names.json").open("w", encoding="utf-8", newline="\n") as file:
            file.write("{}")
        return

    # Get names
    players: dict[str, PlayerScoreEntry] = {}

    file = NBT.NBTFile(file_path)

    if "data" in file:

        # Get player names from teams
        if "Teams" in file["data"]:
            for team in file["data"]["Teams"]:
                for player in team["Players"]:
                    player = str(player)
                    if check_player_name_legality(player, players):
                        players[player]["team"] = str(team["Name"])

        # Get player names from scores
        if "PlayerScores" in file["data"]:
            for score in file["data"]["PlayerScores"]:
                player = str(score["Name"])
                if check_player_name_legality(player, players):
                    players[player]["objectives"].append(str(score["Objective"]))

    # Convert names to strings
    minified_players: dict[str, str] = {}
    for name in players:
        minified_players[name] = str(players[name])

    # Write player names to file
    with (PROGRAM_PATH / "player_names.json").open("w", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(minified_players, indent=4).replace('"{', "{").replace('}"', "}").replace("'", '"'))

    log("Player names logged, check player_names.json")

LEGAL_CHARACTERS = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","0","1","2","3","4","5","6","7","8","9","_"]

def check_player_name_legality(player: str, players: dict[str, PlayerScoreEntry]) -> bool:
    # Stop if name is illegal
    for char in player:
        if char not in LEGAL_CHARACTERS:
            return False
        
    # Add name to the list
    if player not in players:
        players[player] = {"team": "", "objectives": []}

    return True

def check_player_name(player: str, players: dict[str, dict[str, dict[str, str | list[str]]]]) -> int:

    # Skip name if it contains illegal characters
    for char in player:
        if char not in LEGAL_CHARACTERS:
            return 0
        
    # If name is present in either list, return value
    if player in players["non_players"]:
        return 1
    if player in players["players"]:
        return 2

    # If name is present in neither list, check for it
    try:
        response = requests.get("https://api.mojang.com/users/profiles/minecraft/" + player).json()
        if response["name"] == player:
            players["players"][player] = {"team": "", "objectives": []}
            return 2
        else:
            players["non_players"][player] = {"team": "", "objectives": []}
            return 1
    except:
        players["non_players"][player] = {"team": "", "objectives": []}
        return 1

def clean_scoreboard_dat(world: Path):
    log("Cleaning scoreboard.dat")

    # Stop if scoreboard.dat does not exist
    file_path = world / "data" / "scoreboard.dat"
    if not file_path.exists():
        return

    # Get names
    player_names_path = PROGRAM_PATH / "player_names.json"
    if player_names_path.exists():
        with player_names_path.open("r", encoding="utf-8") as file:
            player_names: list[str] = list(json.load(file).keys())
    else:
        player_names: list[str] = []

    file = NBT.NBTFile(file_path)

    if "data" in file:

        # Remove players from teams
        if "Teams" in file["data"]:
            for i in range(len(file["data"]["Teams"])):
                team = file["data"]["Teams"][i]
                length = len(team["Players"])
                for j in range(length):
                    j = length-j-1
                    if str(team["Players"][j]) in player_names:
                        file["data"]["Teams"][i]["Players"].pop(j)

        # Remove player scores
        if "PlayerScores" in file["data"]:
            length = len(file["data"]["PlayerScores"])
            for i in range(length):
                i = length-i-1
                score = file["data"]["PlayerScores"][i]
                if str(score["Name"]) in player_names:
                    file["data"]["PlayerScores"].pop(i)

        file.write_file(file_path)

def delete_empty_files(world: Path):
    log("Deleting empty files")
    delete_empty_files_in_folder(world)
    dimension = world / "DIM-1"
    if dimension.exists():
        delete_empty_files_in_folder(dimension)
    dimension = world / "DIM1"
    if dimension.exists():
        delete_empty_files_in_folder(dimension)

def delete_empty_files_in_folder(path: Path):
    for folder in ["entities", "poi", "region"]:
        if not (path / folder).exists():
            continue
        for file_path in (path / folder).iterdir():
            if file_path.is_file() and file_path.stat().st_size == 0:
                delete_file(file_path)

def delete_ds_store(world: Path):
    if os.name != "nt":
        return
    log("Deleting .DS_Store files")
    for file_path in world.glob("**/*"):
        if file_path.is_file() and file_path.name in [".ds_store", ".DS_Store"]:
            delete_file(file_path)

def delete_junk_files(world: Path):
    log("Deleting unnecessary files")

    delete_path(world / "advancements")
    delete_path(world / "playerdata")
    delete_path(world / "stats")
    delete_path(world / "serverconfig")
    delete_path(world / "gc-logs")
    delete_path(world / "##MCEDIT.TEMP##")
    delete_path(world / "players")
    delete_path(world / "DIM1" / "##MCEDIT.TEMP##")
    delete_path(world / "DIM1" / "players")
    delete_path(world / "DIM-1" / "##MCEDIT.TEMP##")
    delete_path(world / "DIM-1" / "players")
    delete_path(world / "datapacks" / "bukkit")
    delete_path(world / "data" / "advancements")
    delete_path(world / "data" / "functions")

    delete_file(world / "level.dat_old")
    delete_file(world / "level.dat_mcr")
    delete_file(world / "level.dat.bak")
    delete_file(world / "session.lock")
    delete_file(world / "uid.dat")
    delete_file(world / ".gitignore")
    delete_file(world / "world_properties.StickyPiston")
    delete_file(world / "data" / "fabricDynamicRegistry.dat")
    delete_file(world / "data" / "Mineshaft.dat")
    delete_file(world / "data" / "Village.dat")
    delete_file(world / "realms-upload.log")
    delete_file(world / "paper-world.yml")
    delete_file(world / "forcedchunks.dat")
    delete_file(world / "DIM1" / "forcedchunks.dat")
    delete_file(world / "DIM-1" / "forcedchunks.dat")

    for path in [(world / "DIM1"), (world / "DIM-1")]:
        if not (path / "region").exists() or not list((path / "region").iterdir()):
            delete_path(path)

    for path in world.iterdir():
        file_name = path.name
        if (
            file_name.startswith("level") and
            file_name.endswith(".dat") and
            file_name[5:-4].isnumeric()
        ):
            delete_file(path)

def log_data_packs(world: Path):
    # Skip if datapacks don't exist
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if not (world / "datapacks").exists():
        log("ERROR: World has no data packs!")
        return

    # Get data pack list
    data_packs: list[str] = []
    for data_pack_path in (world / "datapacks").iterdir():
        if data_pack_path.is_dir() and (data_pack_path / "pack.mcmeta").exists():
            data_packs.append(f'file/{data_pack_path.name}')
        if data_pack_path.is_file() and data_pack_path.suffix == ".zip":
            data_packs.append(f'file/{data_pack_path.name}')
    data_packs.append("vanilla")

    # Open file
    file_path = world / "level.dat"
    file = NBT.NBTFile(file_path)

    # Create NBT paths if they don't exist
    if "Data" not in file:
        file["Data"] = NBT.TAG_Compound()
    if "DataPacks" not in file["Data"]:
        file["Data"]["DataPacks"] = NBT.TAG_Compound()
    data_packs_compound = file["Data"]["DataPacks"]
    if "Enabled" not in data_packs_compound:
        data_packs_compound["Enabled"] = NBT.TAG_List(NBT.TAG_String)
    if "Disabled" not in data_packs_compound:
        data_packs_compound["Disabled"] = NBT.TAG_List(NBT.TAG_String)

    # Remove disabled packs from the list
    vanilla_disabled = False
    for data_pack in data_packs_compound["Disabled"]:
        if str(data_pack) in data_packs:
            data_packs.remove(str(data_pack))
        if str(data_pack) == "vanilla":
            vanilla_disabled = True

    # Remove enabled packs which do not exist
    removed_packs = 0
    length = len(data_packs_compound["Enabled"])
    for i in range(length):
        i -= removed_packs
        data_pack = str(data_packs_compound["Enabled"][i])

        # Remove if the data pack is already listed in the enabled list
        if utils.nbt_list_contains(data_packs_compound["Enabled"][:i], data_pack):
            data_packs_compound["Enabled"].pop(i)
            removed_packs += 1
        # Skip if the data pack is already listed
        if data_pack in data_packs:
            continue
        # Add/remove .zip and check again
        if data_pack.split(".")[-1] == "zip":
            data_pack = data_pack[:-4]
        else:
            data_pack += ".zip"
        if data_pack in data_packs:
            data_packs_compound["Enabled"][i] = NBT.TAG_String(data_pack)
            continue
        # Remove the data pack from the list if it isn't found
        data_packs_compound["Enabled"].pop(i)
        removed_packs += 1

    # Add unlisted data packs to the enabled list
    for data_pack in data_packs:
        if not utils.nbt_list_contains(data_packs_compound["Enabled"], data_pack):
            data_packs_compound["Enabled"].append(NBT.TAG_String(data_pack))

    # Close file
    file.write_file(file_path)

    log("Data packs logged")

    if vanilla_disabled:
        log("Vanilla data pack is disabled, consider fixing the disabled vanilla data pack")



def convert_line_endings_folder(folder: Path):
    # Iterate through files
    for file_path in folder.glob("**/*"):
        # Skip if file is not a text file
        if not file_path.is_file() or file_path.suffix not in defaults.TEXT_FILE_FORMATS:
            continue

        # Rewrite file
        if defaults.DEBUG_MODE:
            print(file_path.as_posix())
        try:
            with file_path.open("r", encoding="utf-8") as file:
               contents = file.read()
            with file_path.open("w", encoding="utf-8", newline="\n") as file:
               file.write(contents)
        except:
            continue