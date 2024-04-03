# Import things

import json
from pathlib import Path
from lib import utils
from lib.data_pack_files import command
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import nbt_paths
from lib.data_pack_files import target_selectors
from lib.data_pack_files import tables
from lib.data_pack_files import entities
from lib import json_manager
from lib import defaults



# Initialize variables

EASY_MAP_UPDATER_PATH = Path(__file__).parent.parent.parent
MINECRAFT_PATH = EASY_MAP_UPDATER_PATH.parent
pack_version = defaults.PACK_VERSION
translation_keys_retrieved = False
translation_keys: dict[str, int] = {}



# Define functions

def update_merge(strings: dict[str, list[str]], version: int, issues: list[dict[str, str]], mangled: bool) -> str:
    # Assign version
    global pack_version
    pack_version = version

    if len(strings["json_text_component"]) == 0:
        return ""

    return update(" ".join(strings["json_text_component"]), version, issues, mangled)

def update(string: str, version: int, issues: list[dict[str, str]], mangled: bool) -> str:
    global pack_version
    pack_version = version

    # Convert to string if not a string
    if not isinstance(string, str):
        string = nbt_tags.pack(string)

    # Unpack string
    unpacked_component = json_manager.unpack(string)

    # Process input based on type
    if isinstance(unpacked_component, str):
        updated_component = update_string(unpacked_component)
    else:
        updated_component = update_component(unpacked_component, issues)

    # Pack based on mangling rule
    if mangled:
        return pack_mangled(updated_component)
    else:
        return json_manager.pack(updated_component)

def update_string(string: str) -> list[dict[str, str | bool]] | str:
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

    components: list[dict[str, str | bool]] = []

    # Iterate through string
    after_first = False
    for section in string[1:-1].split("§"):
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
        component: dict[str, str | bool] = {"text": section}
        component["color"] = color
        if obfuscated:
            component["obfuscated"] = True
        if bold:
            component["bold"] = True
        if strikethrough:
            component["strikethrough"] = True
        if underlined:
            component["underlined"] = True
        if italic:
            component["italic"] = True
        
        # Append to output list
        components.append(section)

        # Set first boolean
        after_first = True

    # Return JSON text component
    return components

def update_component(component: list | dict[str, str | dict] | str, issues: list[dict[str, str]]) -> list | dict[str, str | dict] | str:
    if isinstance(component, list):
        return update_list(component, issues)
    if isinstance(component, dict):
        return update_compound(component, issues)
    if component == None:
        return {"type":"text","text":""}
    return component

def update_list(component: list, issues: list[dict[str, str]]) -> list:
    # Iterate through list
    for i in range(len(component)):
        component[i] = update_component(component[i], issues)
    if len(component) == 0:
        return {"type":"text","text":""}
    return component

def update_compound(component: dict[str, str | dict] | str, issues: list[dict[str, str]]) -> dict[str, str | dict]:
    if not isinstance(component, dict):
        return component

    # Iterate through keys
    for key in list(component.keys()):
        if key == "clickEvent":
            component[key] = update_click_event(component[key])
        if key == "color":
            if not component[key].startswith("#"):
                if component[key] not in tables.COLORS:
                    component[key] = "white"
            else:
                component[key] = component[key][0: min(7, len(component[key]))] + "0"*max(0, 7-len(component[key]))
        if key == "selector":
            component[key] = target_selectors.update(component[key], pack_version, issues, False)
        if key in ["extra", "separator", "with"]:
            component[key] = update_component(component[key], issues)
        if key == "hoverEvent":
            component[key] = update_hover_event(component[key], issues)
        if key == "nbt":
            update_nbt(component, issues)
        if key == "score":
            component[key] = update_score(component[key], issues)
        if key in ["bold", "italic", "underlined", "strikethrough", "obfuscated"]:
            if component[key] in ["true", "True"]:
                component[key] = True
            elif component[key] in ["false", "False"]:
                component[key] = False
        if key == "translate":
            update_translate(component)

    # Add type tag if it doesn't exist
    if "type" not in component:
        for key in ["text", "translatable", "score", "selector", "keybind", "nbt"]:
            if key in component:
                component["type"] = key

    return component

def update_click_event(component: dict[str, str]) -> dict[str, str]:
    if "value" not in component or "action" not in component:
        return component

    if component["action"] == "run_command":
        component["value"] = "/" + command.update(component["value"], pack_version, "JSON Text Component")
    
    return component

def update_hover_event(component: dict[str, str], issues: list[dict[str, str]]) -> dict[str, str]:
    if ("value" not in component and "contents" not in component) or "action" not in component:
        return component

    if component["action"] == "show_text":
        if "contents" not in component:
            component["contents"] = update_component(component["value"], issues)
        else:
            component["contents"] = update_component(component["contents"], issues)

    if component["action"] == "show_item":
        if "contents" not in component:
            if isinstance(component["value"], str):
                item_nbt = component["value"]
            elif isinstance(component["value"], dict) and "text" in component["value"]:
                item_nbt = component["value"]["text"]
            else:
                item_nbt = '{id:"minecraft:air"}'
            item_nbt = nbt_tags.unpack(item_nbt)
        else:
            item_nbt = {}
            if "id" in component["contents"]:
                item_nbt["id"] = component["contents"]["id"]
            if "count" in component["contents"]:
                item_nbt["Count"] = nbt_tags.TypeByte(component["contents"]["count"])
            if "tag" in component["contents"]:
                item_nbt["tag"] = nbt_tags.unpack(component["contents"]["tag"])
        item_nbt = nbt_tags.direct_update(item_nbt, pack_version, issues, "item", "")
        component["contents"] = {}
        if "id" in item_nbt:
            component["contents"]["id"] = item_nbt["id"]
        if "Count" in item_nbt:
            component["contents"]["count"] = item_nbt["Count"].value
        if "tag" in item_nbt:
            component["contents"]["tag"] = nbt_tags.pack(item_nbt["tag"])

    if component["action"] == "show_entity":
        if "contents" not in component:
            print('WARNING: "show_entity" not handled without "contents"')
        else:
            if "name" in component["contents"]:
                component["contents"]["name"] = update_component(component["contents"]["name"], issues)
            if "type" in component["contents"]:
                component["contents"]["type"] = entities.update(component["contents"]["type"], pack_version, issues)

    if "value" in component:
        del component["value"]
    return component

def update_nbt(component: dict[str, str | dict], issues: list[dict[str, str]]):
    # Iterate through keys
    for key in list(component.keys()):
        if key == "entity":
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
        defaults.FIXES["safe_nbt_interpret"] and
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

def update_score(component: dict[str, str], issues: list[dict[str, str]]) -> dict[str, str]:
    if "name" not in component:
        return component

    component["name"] = target_selectors.update(component["name"], pack_version, issues, pack_version <= 1202)

    return component

def update_translate(component: dict[str, str | dict]):
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

    file_path = EASY_MAP_UPDATER_PATH / "options.json"
    with file_path.open("r", encoding="utf-8") as file:
        contents: dict[str, str] = json.load(file)
    resource_pack_path = MINECRAFT_PATH / "resourcepacks" / contents["resource_pack"] / "assets"
    if not resource_pack_path.exists():
        return
    
    for namespace_path in resource_pack_path.iterdir():
        if namespace_path.is_file():
            continue
        lang_folder = namespace_path / "lang"
        if not lang_folder.exists():
            continue
        for file_path in lang_folder.glob("**/*.json"):
            contents, load_bool = json_manager.safe_load(file_path)
            if not load_bool:
                continue
            for key in contents:
                translation_keys[key] = contents[key].count("%s") + contents[key].count("$s")



def pack_mangled(component: list | dict[str, str | dict] | str) -> str:
    component = reorder_data(component)
    component = prune_data(component)
    return pack_mangled_component(component)

def reorder_data(component: list | dict[str, str | dict] | str) -> dict[str, str | dict | list]:
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
        if key == "hoverEvent":
            if "action" in component[key] and "contents" in component[key]:
                if component[key]["action"] == "show_text":
                    component[key]["contents"] = reorder_data(component[key]["contents"])
                if component[key]["action"] == "show_item":
                    if "count" in component[key]["contents"]:
                        if component[key]["contents"]["count"] == 1:
                            del component[key]["contents"]["count"]
                if component[key]["action"] == "show_entity":
                    if "name" in component[key]["contents"]:
                        component[key]["contents"]["name"] = reorder_data(component[key]["contents"]["name"])
                    if "id" in component[key]["contents"]:
                        if isinstance(component[key]["contents"]["id"], str):
                            component[key]["contents"]["id"] = utils.uuid_from_string(component[key]["contents"]["id"])
        if key == "separator":
            component[key] = reorder_data(component[key])

    if "entity" in component:
        if "block" in component:
            del component["block"]
        if "storage" in component:
            del component["storage"]
    if "block" in component:
        if "storage" in component:
            del component["storage"]

    return component

def prune_data(component: dict[str, str | dict | list]) -> dict[str, str | dict | list] | str:
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
        if key == "hoverEvent":
            if "action" in component[key] and "contents" in component[key]:
                if component[key]["action"] == "show_text":
                    component[key]["contents"] = prune_data(component[key]["contents"])
                if component[key]["action"] == "show_entity":
                    if "name" in component[key]["contents"]:
                        component[key]["contents"]["name"] = prune_data(component[key]["contents"]["name"])
        if key == "separator":
            component[key] = prune_data(component[key])
    
    return component

def pack_mangled_component(component: dict[str, str | dict | list] | list | str) -> str:
    if isinstance(component, list):
        return pack_mangled_list(component)
    if isinstance(component, dict):
        return pack_mangled_compound(component)
    if type(component).__name__ == "str":
        return utils.pack_string(component, force_double=True)
    if type(component).__name__ == "bool":
        if component:
            return "true"
        return "false"
    if component == None:
        return "null"
    return str(component)

def pack_mangled_list(component: list) -> str:
    out_list = []
    for entry in component:
        out_list.append(pack_mangled_component(entry))

    return f'[{",".join(out_list)}]'

def pack_mangled_compound(component: dict[str, str | dict | list]) -> str:
    tags: list[str] = []

    for key in [
        "text",
        "translate", "fallback", "with",
        "keybind",
        "score",
        "selector",
        "nbt",
        "separator",
        "entity", "block", "storage",
        "extra",
        "hoverEvent",
        "insertion", "font", "obfuscated",
        "clickEvent",
        "italic", "underlined", "strikethrough", "color", "bold",
    ]:
        if key in component:
            if key == "clickEvent":
                tags.append(f'"{key}":{pack_mangled_compound_primitive(component[key], ["action", "value"])}')
            elif key in ["extra", "with"]:
                tags.append(f'"{key}":{pack_mangled_list(component[key])}')
            elif key == "hoverEvent":
                tags.append(f'"{key}":{pack_mangled_hover_event(component[key])}')
            elif key == "score":
                tags.append(f'"{key}":{pack_mangled_compound_primitive(component[key], ["name", "objective"])}')
            else:
                tags.append(f'"{key}":{pack_mangled_component(component[key])}')
    
    return f'{{{",".join(tags)}}}'

def pack_mangled_compound_primitive(component: dict[str, str | dict | list], keys: list[str]) -> str:
    tags: list[str] = []

    for key in keys:
        if key in component:
            tags.append(f'"{key}":{pack_mangled_component(component[key])}')

    return f'{{{",".join(tags)}}}'

def pack_mangled_hover_event(component: dict[str, str | dict | list]) -> str:
    tags: list[str] = []

    for key in ["contents", "action"]:
        if key in component:
            if key == "contents":
                tags.append(f'"{key}":{pack_mangled_hover_event_contents(component[key], component["action"] if "action" in component else "show_text")}')
            else:
                tags.append(f'"{key}":{pack_mangled_component(component[key])}')

    return f'{{{",".join(tags)}}}'

def pack_mangled_hover_event_contents(component: dict[str, str], action: str) -> str:
    if action == "show_text":
        return pack_mangled_component(component)

    elif action == "show_item":
        return pack_mangled_compound_primitive(component, ["id", "count", "tag"])

    elif action == "show_entity":
        return pack_mangled_compound_primitive(component, ["type", "id", "name"])
    
    return '""'