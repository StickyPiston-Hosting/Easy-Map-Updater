# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from typing import TypedDict
from enum import Enum
from pathlib import Path
from lib import defaults



# Initialize variables

PROGRAM_PATH = Path(__file__).parent.parent
OPTIONS_PATH = PROGRAM_PATH / "options.json"

class Option(Enum):
    MAP_NAME = "map_name"
    RESOURCE_PACK = "resource_pack"
    FANCY_NAME = "fancy_name"
    VERSION = "version"

class Options(TypedDict):
    map_name: str
    resource_pack: str
    fancy_name: str
    version: int



# Define functions

def get_default_options() -> Options:
    return {
        Option.MAP_NAME.value: "world",
        Option.RESOURCE_PACK.value: "resources",
        Option.FANCY_NAME.value: "Map",
        Option.VERSION.value: defaults.PACK_VERSION
    }

def set_options(options: Options):
    with OPTIONS_PATH.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(options, file, indent=4)

def get_options():
    if OPTIONS_PATH.exists():
        with OPTIONS_PATH.open("r", encoding="utf-8") as file:
            options: Options = json.load(file)
    else:
        options = get_default_options()
        set_options(options)

    return options



def get_map_name() -> str:
    options = get_options()
    return options[Option.MAP_NAME.value]

def get_resource_pack() -> str:
    options = get_options()
    return options[Option.RESOURCE_PACK.value]

def get_fancy_name() -> str:
    options = get_options()
    return options[Option.FANCY_NAME.value]

def get_version() -> int:
    options = get_options()
    return options[Option.VERSION.value]



def set_map_name(map_name: str):
    options = get_options()
    options[Option.MAP_NAME.value] = map_name
    set_options(options)

def set_resource_pack(resource_pack: str):
    options = get_options()
    options[Option.RESOURCE_PACK.value] = resource_pack
    set_options(options)

def set_fancy_name(fancy_name: str):
    options = get_options()
    options[Option.FANCY_NAME.value] = fancy_name
    set_options(options)

def set_version(version: int):
    options = get_options()
    options[Option.VERSION.value] = version
    set_options(options)