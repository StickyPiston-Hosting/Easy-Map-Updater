# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import math
from pathlib import Path
from typing import cast, TypedDict, NotRequired, Any
from lib import utils
from lib.data_pack_files import command
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import nbt_paths
from lib.data_pack_files import target_selectors
from lib.data_pack_files import tables
from lib.data_pack_files import entities
from lib import json_manager
from lib import defaults
from lib import option_manager



# Initialize variables

EASY_MAP_UPDATER_PATH = Path(__file__).parent.parent.parent
MINECRAFT_PATH = EASY_MAP_UPDATER_PATH.parent
pack_version = defaults.PACK_VERSION
translation_keys_retrieved = False
translation_keys: dict[str, int] = {}



# Define functions

def update_merge(strings: dict[str, list[str]], version: int, issues: list[dict[str, str | int]], params: dict):
    # Assign version
    global pack_version
    pack_version = version

    if len(strings["json_text_component"]) == 0:
        return ""

    return update(" ".join(strings["json_text_component"]), version, issues, params)

def update_from_lib_format(string, version: int, issues: list[dict[str, str | int]], mangled: bool):
    return nbt_tags.convert_to_lib_format(direct_update(nbt_tags.convert_from_lib_format(string), version, issues, mangled))

def update(string: str, version: int, issues: list[dict[str, str | int]], params: dict):
    global pack_version
    pack_version = version

    # Unpack string
    if not isinstance(string, str):
        unpacked_component = string
    elif pack_version <= 2104:
        unpacked_component = json_manager.unpack(string)
    else:
        unpacked_component = nbt_tags.unpack(string)

    updated_component = direct_update(unpacked_component, version, issues, params["mangled"] if "mangled" in params else False)

    if "pack" in params and params["pack"]:
        return nbt_tags.pack(updated_component)
    else:
        return updated_component

def direct_update(unpacked_component: dict | list | str, version: int, issues: list[dict[str, str | int]], mangled: bool):
    global pack_version
    pack_version = version

    # Process input based on type
    if isinstance(unpacked_component, str):
        updated_component = update_string(unpacked_component)
    else:
        updated_component = update_component(unpacked_component, version, issues)

    if mangled:
        return pack_mangled(updated_component)

    return updated_component

def update_string(string: str):
    # Return string if there are no section symbols
    if "§" not in string:
        return string

    # Initialize variables
    color = "white"
    bold = False
    italic = False
    underlined = False
    strikethrough = False
    obfuscated = False

    components = []

    # Iterate through string
    after_first = False
    for section in string.split("§"):
        # Process section sign
        if after_first:
            # Change color
            id_array = {
                "0": "black",
                "1": "dark_blue",
                "2": "dark_green",
                "3": "dark_aqua",
                "4": "dark_red",
                "5": "dark_purple",
                "6": "gold",
                "7": "gray",
                "8": "dark_gray",
                "9": "blue",
                "a": "green",
                "b": "aqua",
                "c": "red",
                "d": "light_purple",
                "e": "yellow",
                "f": "white"
            }
            if section[0] in id_array:
                color = id_array[section[0]]

            # Misc parameters
            if section[0] == "k":
                obfuscated = True
            if section[0] == "l":
                bold = True
            if section[0] == "m":
                strikethrough = True
            if section[0] == "n":
                underlined = True
            if section[0] == "o":
                italic = True
            if section[0] == "r":
                color = "white"
                bold = False
                italic = False
                underlined = False
                strikethrough = False
                obfuscated = False

            # Chop control character off of string
            section = section[1:]

        # Add parameters to current section
        component: dict[str, Any] = {"text": section}
        component["color"] = color
        if obfuscated:
            component["obfuscated"] = nbt_tags.TypeByte(1)
        if bold:
            component["bold"] = nbt_tags.TypeByte(1)
        if strikethrough:
            component["strikethrough"] = nbt_tags.TypeByte(1)
        if underlined:
            component["underlined"] = nbt_tags.TypeByte(1)
        if italic:
            component["italic"] = nbt_tags.TypeByte(1)
        
        # Append to output list
        components.append(section)

        # Set first boolean
        after_first = True

    # Return JSON text component
    return components

# class JSONTextComponentCompound(TypedDict("JSONTextComponentCompound", {"with": list[str]})):
#     type: NotRequired[str]
#     text: str
#     color: str
#     bold: str
#     italic: str
#     underlined: str
#     strikethrough: str
#     obfuscated: str
#     selector: str
#     score: dict[str, str]
#     clickEvent: dict[str, str]
#     hoverEvent: dict[str, Any]
#     translate: str
#     nbt: str
#     source: str
#     block: NotRequired[str]
#     entity: NotRequired[str]
#     storage: NotRequired[str]
#     extra: list
#     separator: Any
#     shadow_color: int | list[int]

def update_component(component: str | list | dict, version: int, issues: list[dict[str, str | int]]) -> str | list | dict:
    global pack_version
    pack_version = version

    if isinstance(component, list):
        return update_list(component, issues)
    if isinstance(component, dict):
        return update_compound(component, issues)
    if component == None:
        return {"type":"text","text":""}
    return component

def update_list(component: list, issues: list[dict[str, str | int]]) -> list | dict:
    # Iterate through list
    for i in range(len(component)):
        component[i] = update_component(component[i], pack_version, issues)
    if len(component) == 0:
        return {"type":"text","text":""}
    return component

def update_compound(component: str | dict, issues: list[dict[str, str | int]]) -> str | dict:
    if not isinstance(component, dict):
        return component

    # Iterate through keys
    for key in list(component.keys()):
        if key == "clickEvent":
            component["click_event"] = update_click_event(component[key])
            del component[key]
        if key == "click_event":
            component[key] = update_click_event(component[key])
            del component[key]
        if key == "color":
            if not component[key].startswith("#"):
                if component[key] not in tables.COLORS:
                    del component[key]
            else:
                component[key] = component[key][0: min(7, len(component[key]))].upper() + "0"*max(0, 7-len(component[key]))
        if key == "selector":
            component[key] = target_selectors.update(component[key], pack_version, issues, False)
        if key in ["extra", "separator", "with"]:
            component[key] = update_component(component[key], pack_version, issues)
        if key == "hoverEvent":
            component["hover_event"] = update_hover_event(component[key], issues)
            del component[key]
        if key == "hover_event":
            component[key] = update_hover_event(component[key], issues)
        if key == "nbt":
            update_nbt(component, issues)
        if key == "score":
            component[key] = update_score(component[key], issues)
        if key in ["bold", "italic", "underlined", "strikethrough", "obfuscated"]:
            if component[key] in ["true", "True"]:
                component[key] = nbt_tags.TypeByte(1)
            elif component[key] in ["false", "False"]:
                component[key] = nbt_tags.TypeByte(0)
            else:
                component[key] = nbt_tags.TypeByte(1 if component[key] else 0)
        if key == "translate":
            update_translate(component)

    # Add type tag if it doesn't exist
    if "type" not in component:
        for key_pair in [
            ("text", "text"),
            ("translate", "translatable"),
            ("score", "score"),
            ("selector", "selector"),
            ("keybind", "keybind"),
            ("nbt", "nbt"),
        ]:
            if key_pair[0] in component:
                component["type"] = key_pair[1]

    return component

def update_click_event(component: dict) -> dict:
    if "action" not in component:
        return component

    if "value" in component:
        for key_pair in [
            ("open_url", "url"),
            ("open_file", "path"),
            ("run_command", "command"),
            ("suggest_command", "command"),
            ("change_page", "page"),
            ("copy_to_clipboard", "value"),
        ]:
            if component["action"] == key_pair[0]:
                component[key_pair[1]] = component["value"]
                if key_pair[1] != "value":
                    del component["value"]

    # Conform data types of tags
    for key in [
        "url",
        "path",
        "command",
        "command",
        "value",
    ]:
        if key in component:
            component[key] = str(component[key])

    if "page" in component:
        component["page"] = nbt_tags.TypeInt(int(component["page"]))


    if component["action"] == "run_command":
        component["command"] = "/" + command.update(component["command"], pack_version, "Text Component")
    
    return component

def update_hover_event(component: dict[str, Any], issues: list[dict[str, str | int]]) -> dict[str, str]:
    if "action" not in component:
        return component

    if component["action"] == "show_text":
        if "value" not in component:
            component["value"] = update_component(component["contents"], pack_version, issues)
            del component["contents"]
        else:
            component["value"] = update_component(component["value"], pack_version, issues)

    if component["action"] == "show_item":
        if "contents" not in component:
            if "value" in component:
                if isinstance(component["value"], str):
                    item_nbt = component["value"]
                elif isinstance(component["value"], dict) and "text" in component["value"]:
                    item_nbt = component["value"]["text"]
                else:
                    item_nbt = '{id:"minecraft:air"}'
                item_nbt = nbt_tags.unpack(item_nbt)

            else:
                item_nbt = {}
                if "id" in component:
                    item_nbt["id"] = component["id"]
                if "count" in component:
                    item_nbt["count"] = nbt_tags.TypeInt(component["count"])
                if "Count" in component:
                    item_nbt["count"] = nbt_tags.TypeInt(component["Count"])
                if "tag" in component:
                    item_nbt["tag"] = nbt_tags.unpack(component["tag"])
                if "components" in component:
                    item_nbt["components"] = nbt_tags.unpack(component["components"])

        else:
            item_nbt = {}
            contents = cast(dict[str, Any], component["contents"])
            if "id" in component["contents"]:
                item_nbt["id"] = contents["id"]
            if "count" in contents:
                item_nbt["count"] = nbt_tags.TypeInt(contents["count"])
            if "Count" in contents:
                item_nbt["count"] = nbt_tags.TypeInt(contents["Count"])
            if "tag" in contents:
                item_nbt["tag"] = nbt_tags.unpack(contents["tag"])
            if "components" in contents:
                item_nbt["components"] = nbt_tags.unpack(contents["components"])

        item_nbt = cast(dict, nbt_tags.direct_update(item_nbt, pack_version, issues, "item", ""))
        component = {"action": "show_item"}
        if "id" in item_nbt:
            component["id"] = item_nbt["id"]
        if "count" in item_nbt:
            component["count"] = item_nbt["count"]
        if "components" in item_nbt:
            component["components"] = item_nbt["components"]

    if component["action"] == "show_entity":
        if "contents" in component:
            contents = component["contents"]
            if "name" in contents:
                component["name"] = update_component(contents["name"], pack_version, issues)
            if "type" in contents:
                component["id"] = entities.update(contents["type"], pack_version, issues)
            if "id" in contents:
                component["uuid"] = contents["id"]
            del component["contents"]

        else:
            if "name" in component:
                component["name"] = update_component(component["name"], pack_version, issues)
            if "id" in component:
                component["id"] = entities.update(component["id"], pack_version, issues)

    return component

def update_nbt(component: dict, issues: list[dict[str, str | int]]):
    # Iterate through keys
    for key in list(component.keys()):
        if key == "entity" and key in component:
            component[key] = target_selectors.update(component[key], pack_version, issues, False)
        if key == "nbt":
            for source in ["block", "entity"]:
                if source in component:
                    component[key] = nbt_paths.update(component[key], pack_version, issues, source)

    # Add source tag if it doesn't exist
    if "source" not in component:
        for key in ["block", "entity", "storage"]:
            if key in component:
                component["source"] = key

    # Make NBT interprets safe
    if (
        pack_version <= 2002 and
        "interpret" in component and component["interpret"] and
        option_manager.FIXES["command_helper"]["safe_nbt_interpret"] and
        not component["nbt"].startswith("safe_nbt_interpret")
    ):
        # Get latest index
        index = 0
        for issue in issues:
            if issue["type"] == "safe_nbt_interpret":
                index += 1

        issues.append({
            "type": "safe_nbt_interpret",
            "source": component["source"],
            "object": component[component["source"]],
            "path": component["nbt"],
            "index": index
        })
        for key in ["block", "entity"]:
            if key in component:
                del component[key]
        component["source"] = "storage"
        component["storage"] = "help:data"
        component["nbt"] = f'safe_nbt_interpret.v{index}'

def update_score(component: dict, issues: list[dict[str, str | int]]) -> dict:
    if "name" not in component:
        return component

    component["name"] = target_selectors.update(component["name"], pack_version, issues, pack_version <= 1202)

    return component

def update_translate(component: dict):
    # Get translation key data
    global translation_keys_retrieved
    if not translation_keys_retrieved:
        retrieve_translation_keys()
        translation_keys_retrieved = True

    if component["translate"] not in translation_keys:
        return
    if translation_keys[component["translate"]] == 0:
        return
    if "with" not in component:
        component["with"] = ["" for i in range(translation_keys[component["translate"]])]
    else:
        for i in range(translation_keys[component["translate"]] - len(component["with"])):
            component["with"].append("")



def retrieve_translation_keys():
    global translation_keys

    resource_pack_path = MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack() / "assets"
    if not resource_pack_path.exists():
        return
    
    for namespace_path in resource_pack_path.iterdir():
        if namespace_path.is_file():
            continue
        lang_folder = namespace_path / "lang"
        if not lang_folder.exists():
            continue
        for file_path in lang_folder.glob("**/*.json"):
            if not file_path.is_file():
                continue
            contents, load_bool = json_manager.safe_load(file_path)
            if not load_bool:
                continue
            for key in contents:
                translation_keys[key] = contents[key].count("%s") + contents[key].count("$s")



def pack_mangled(component: str | list | dict) -> str | list | dict:
    component = reorder_data(component)
    component = prune_data(component)
    return component

def reorder_data(component: str | list | dict) -> dict:
    if isinstance(component, str):
        return {"text": component}
    
    if isinstance(component, list):
        if len(component) == 0:
            return {"text": ""}
        output_component = reorder_data(component[0])
        if len(component) > 1:
            if "extra" not in output_component:
                output_component["extra"] = []
            output_component["extra"].extend(component[1:])
        component = output_component

    for key in list(component.keys()):
        if key in ["extra", "with"]:
            for i in range(len(component[key])):
                component[key][i] = reorder_data(component[key][i])
        if key == "hover_event":
            if "action" in component[key]:
                if component[key]["action"] == "show_text" and "value" in component[key]:
                    component[key]["value"] = reorder_data(component[key]["value"])
                if component[key]["action"] == "show_item" and "count" in component[key]:
                    if "count" in component[key]:
                        if component[key]["count"] == 1:
                            del component[key]["count"]
                if component[key]["action"] == "show_entity":
                    if "name" in component[key]:
                        component[key]["name"] = reorder_data(component[key]["name"])
                    if "uuid" in component[key]:
                        if isinstance(component[key]["uuid"], str):
                            component[key]["uuid"] = nbt_tags.uuid_from_int_array(utils.uuid_from_string(component[key]["uuid"]))
        if key == "separator":
            component[key] = reorder_data(component[key])
        if key == "shadow_color":
            if isinstance(component[key], nbt_tags.TypeList):
                converted = [0,0,0,0]
                for i in range(min(len(component[key]), 4)):
                    # This formula is based on an analysis of data collected from the game
                    converted[i] = int(math.floor(255*component[key][i]))
                component[key] = utils.int_range(converted[2] + converted[1]*256 + converted[0]*65536 + converted[3]*16777216)
            component[key] = nbt_tags.TypeInt(component[key])

    if "entity" in component:
        if "block" in component:
            del component["block"]
        if "storage" in component:
            del component["storage"]
    if "block" in component:
        if "storage" in component:
            del component["storage"]

    return component

def prune_data(component: dict) -> str | dict:
    for key in ["type", "source"]:
        if key in component:
            del component[key]

    keys = list(component.keys())
    if "text" in keys and len(keys) == 1:
        return component["text"]
    
    for key in keys:
        if key in ["extra", "with"]:
            for i in range(len(component[key])):
                component[key][i] = prune_data(component[key][i])
        if key == "hover_event":
            if "action" in component[key]:
                if component[key]["action"] == "show_text" and "value" in component[key]:
                    component[key]["value"] = prune_data(component[key]["value"])
                if component[key]["action"] == "show_entity" and "name" in component[key]:
                    component[key]["name"] = prune_data(component[key]["name"])
        if key == "separator":
            component[key] = prune_data(component[key])
    
    return component



def convert_lock_string(string):
    # Unpack string
    unpacked_component = nbt_tags.unpack(string)

    # Extract raw string
    raw_string = extract_raw_string(unpacked_component)

    # Replace escapable characters 
    raw_string = raw_string.replace('"', "_DQ_").replace("'", "_SQ_").replace("\\", "_BS_")

    return {"extra": [raw_string], "text": "EMU"}

def convert_lock_string_from_lib_format(string):
    return nbt_tags.convert_to_lib_format(convert_lock_string(nbt_tags.convert_from_lib_format(string)))


def extract_raw_string(component: str | dict | list) -> str:
    if isinstance(component, dict):
        return extract_raw_string_compound(component)
    if isinstance(component, list):
        return extract_raw_string_list(component)
    return component

def extract_raw_string_compound(component: dict) -> str:
    raw_string = ""
    for key in [
        "text",
        "selector",
        # Keybind and translate should never be used in a key to open a locked container
        # They will remain unsupported until further notice
        "keybind",
        "translate",
    ]:
        if key in component:
            raw_string += component[key]

    if "extra" in component:
        raw_string += extract_raw_string_list(component["extra"])
    
    return raw_string

def extract_raw_string_list(component: list) -> str:
    raw_string = ""
    for entry in component:
        raw_string += extract_raw_string(entry)
    return raw_string