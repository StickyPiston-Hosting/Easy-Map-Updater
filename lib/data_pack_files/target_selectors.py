# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from typing import cast
from lib.log import log
from lib.data_pack_files import arguments
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import entities
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import tables
from lib.data_pack_files.restore_behavior import tag_replacements
from lib import defaults
from lib import utils
from lib import option_manager
import easy_map_updater



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def update(selector: str | dict[str, str | bool | list], version: int, issues: list[dict[str, str | int]], imposed_limit: bool) -> str:
    # Assign version
    global pack_version
    pack_version = version

    # Initialize parameters
    nbt = ""

    # Extract arguments if a dict
    if isinstance(selector, dict):
        if "nbt" in selector:
            nbt = cast(str, selector["nbt"])
        if isinstance(selector["selector"], str):
            selector = selector["selector"]
        elif isinstance(selector["selector"], list):
            if len(selector["selector"]) > 1 and defaults.SEND_WARNINGS:
                log("WARNING: Multiple selectors found in legacy command!")
            selector = cast(str, selector["selector"][0])

    # Return selector if blank
    selector = cast(str, selector).strip()
    if not selector:
        return selector

    # Return selector if a UUID
    if utils.is_uuid(selector):
        return selector

    # Process classical selectors
    if selector[0] == "@":
        # Parse arguments
        if len(selector) > 2:
            return update_arguments(selector, nbt, imposed_limit, issues)
        arguments: dict[str, str | dict | list] = {}
        if selector[1] in ["r", "p"] and pack_version <= 1202:
            arguments["type"] = "minecraft:player"
            arguments["sort"] = {"r": "random", "p": "nearest"}[selector[1]]
            arguments["limit"] = "1"
            selector = "@e"
        if imposed_limit and selector[1] in ["a", "e"]:
            arguments["limit"] = "1"
        if nbt:
            arguments["nbt"] = nbt_tags.update(nbt, pack_version, issues, "entity")
        if arguments:
            new_arguments = pack_arguments(arguments)
            if new_arguments:
                return f'{selector}[{new_arguments}]'
            return selector
        if selector.endswith("[]"):
            return selector[:-2]
        return selector

    # Process names
    if nbt == "":
        return selector
    # Insert NBT
    return f'@a[name={selector},nbt={nbt_tags.update(nbt, pack_version, issues, "entity")}]'


def update_arguments(selector: str, nbt: str, imposed_limit: bool, issues: list[dict[str, str | int]]) -> str:
    # Get selector type
    selector_type = selector[1]

    # Get arguments
    selector_arguments = unpack_arguments(selector[3:-1])

    # Special handling for boat update in 1.21.2
    if pack_version <= 2101 and "type" in selector_arguments:
        handle_boat_split(cast(dict, selector_arguments))

    # Update arguments
    for argument_type in list(selector_arguments.keys()):
        update_argument(selector_type, selector_arguments, argument_type, selector_arguments[argument_type], issues)

    # Handle @r with type
    if selector_type == "r" and "type" in selector_arguments:
        selector_type = "e"
        selector_arguments["sort"] = "random"
        if "limit" not in selector_arguments:
            selector_arguments["limit"] = "1"

    # Handle @r or @p detecting dead players
    if selector_type in ["r", "p"] and pack_version <= 1202:
        selector_arguments["type"] = ["minecraft:player"]
        if "sort" not in selector_arguments:
            selector_arguments["sort"] = {"r": "random", "p": "nearest"}[selector_type]
        if "limit" not in selector_arguments:
            selector_arguments["limit"] = "1"
        selector_type = "e"

    # Add NBT to the list
    if nbt != "":
        if "type" in selector_arguments and not selector_arguments["type"][0].startswith("!"):
            updated_nbt = nbt_tags.update({"nbt": nbt, "object_id": entities.update(selector_arguments["type"][0], pack_version, issues)}, pack_version, issues, "entity")
        else:
            updated_nbt = nbt_tags.update(nbt, pack_version, issues, "entity")

        if "nbt" in selector_arguments:
            cast(list, selector_arguments["nbt"]).append(updated_nbt)
        else:
            selector_arguments["nbt"] = [updated_nbt]

    # Apply imposed limit
    if imposed_limit and selector_type in ["a", "e"]:
        selector_arguments["limit"] = "1"

    if selector_arguments:
        return f'@{selector_type}[{pack_arguments(selector_arguments)}]'
    return f'@{selector_type}'



def unpack_arguments(in_arguments: str, nested: bool = False) -> dict[str, str | dict | list]:
    out_arguments: dict[str, str | dict | list] = {}

    if in_arguments == "":
        return {}

    # Iterate through arguments
    numeric_argument_count = 0
    for argument in arguments.parse(in_arguments, ",", pack_version >= 1400):
        if "=" not in argument:
            try:
                int(argument)
            except:
                continue
            else:
                if numeric_argument_count < 4:
                    argument = f'{["x", "y", "z", "r"][numeric_argument_count]}={argument}'
                numeric_argument_count += 1
        argument_type = argument[:argument.find("=")].strip()
        value = argument[argument.find("=") + 1:].strip()
        if argument_type[-1] == "!":
            argument_type = argument_type[:-1]
            value = f'!{value}'

        if not nested:
            if argument_type in ["advancements", "scores"]:
                out_arguments[argument_type] = unpack_arguments(value[1:-1], True)
                continue

            if argument_type in ["gamemode", "name", "nbt", "predicate", "tag", "team", "type"]:
                if argument_type in out_arguments:
                    cast(list, out_arguments[argument_type]).append(value)
                else:
                    out_arguments[argument_type] = [value]
                continue

        out_arguments[argument_type] = value

    return out_arguments

def pack_arguments(in_arguments: dict[str, str | dict | list], nested: bool = False) -> str:
    out_arguments: list[str] = []
    last_out_arguments: list[str] = []

    if not nested:
        # Iterate through efficient arguments
        for argument_type in ["type", "gamemode", "level", "x", "y", "z", "dx", "dy", "dz", "distance", "tag", "scores", "sort", "limit"]:
            if argument_type in in_arguments:
                packed_argument = pack_argument(argument_type, in_arguments[argument_type])
                if packed_argument:
                    out_arguments.append(packed_argument)
                del in_arguments[argument_type]

        # Iterate through inefficient arguments
        for argument_type in ["predicate", "nbt"]:
            if argument_type in in_arguments:
                packed_argument = pack_argument(argument_type, in_arguments[argument_type])
                if packed_argument:
                    last_out_arguments.append(packed_argument)
                del in_arguments[argument_type]

    # Get the rest of them
    for argument_type in in_arguments:
        out_arguments.append(pack_argument(argument_type, in_arguments[argument_type]))

    if not nested:
        out_arguments.extend(last_out_arguments)

    if len(out_arguments) == 0:
        return ""
    return ",".join(out_arguments)

def pack_argument(argument_type: str, value: str | dict | list[str]) -> str:
    if isinstance(value, dict):
        return f'{argument_type}={{{pack_arguments(value, True)}}}'

    if isinstance(value, list):
        out_arguments: list[str] = []
        positive_arguments: list[str] = []
        negative_arguments: list[str] = []

        for entry in value:
            if len(entry) > 0 and entry[0] == "!":
                negative_arguments.append(entry)
            else:
                positive_arguments.append(entry)

        for array in (
            positive_arguments[:1 if argument_type in ["gamemode", "name", "team", "type"] else len(positive_arguments)],
            negative_arguments
        ):
            for entry in array:
                out_arguments.append(f'{argument_type}={entry}')

        return ",".join(out_arguments)

    return f'{argument_type}={value}'



def update_argument(selector_type: str, selector_arguments: dict[str, str | dict | list], argument_type: str, value: str | dict[str, str | dict] | list[str], issues: list[dict[str, str | int]]):
    # Skip arguments that don't need conversion
    if argument_type in ["advancements", "distance", "dx", "dy", "dz", "level", "limit", "name", "predicate", "scores", "sort", "tag", "team", "x", "x_rotation", "y", "y_rotation", "z"]:
        return

    # Process list-based arguments (arguments which can occur multiple times)
    if isinstance(value, list):
        updated_list = []
        for entry in value:
            updated_argument = update_argument_list(argument_type, entry, selector_arguments, issues)
            if updated_argument is not None:
                updated_list.append(updated_argument)
        selector_arguments[argument_type] = updated_list
        return
    
    # Convert range arguments
    range_arguments = ["distance", "level", "x_rotation", "y_rotation"]
    range_arguments_type: tuple[list[str], str]
    for range_arguments_type in [(["rm", "lm", "rxm", "rym"], "min"), (["r", "l", "rx", "ry"], "max")]:
        if argument_type in range_arguments_type[0]:
            range_argument = range_arguments[range_arguments_type[0].index(argument_type)]
            if range_argument in selector_arguments:
                old_value = cast(str, selector_arguments[range_argument])
            else:
                old_value = ""
            selector_arguments[range_argument] = update_range(cast(str, value), old_value, range_arguments_type[1])
            del selector_arguments[argument_type]
            return
    
    # Convert old scores
    if (
        defaults.FIXES["broken_score_references"] and
        pack_version <= 1202 and
        "score_" not in argument_type and
        (argument_type != argument_type.lower() or "_min" in argument_type)
    ):
        selector_arguments["score_" + argument_type] = selector_arguments[argument_type]
        del selector_arguments[argument_type]
        argument_type = "score_" + argument_type
    if "score_" in argument_type:
        if not utils.is_int(cast(str, value)):
            del selector_arguments[argument_type]
            return
        
        if argument_type[-4:] == "_min":
            objective = argument_type[6:-4]
            range_type = "min"
        else:
            objective = argument_type[6:]
            range_type = "max"

        if "scores" not in selector_arguments:
            selector_arguments["scores"] = {}
        if objective in selector_arguments["scores"]:
            score = cast(dict, selector_arguments["scores"])[objective]
        else:
            score = ""

        cast(dict, selector_arguments["scores"])[objective] = update_range(cast(str, value), score, range_type)
        del selector_arguments[argument_type]
        return
    
    # Convert miscellaneous arguments
    if argument_type == "c":
        selector_arguments["limit"] = str(abs(int(cast(str, value))))
        if selector_type != "r":
            if cast(str, value)[0] == "-":
                selector_arguments["sort"] = "furthest"
            else:
                selector_arguments["sort"] = "nearest"
        del selector_arguments[argument_type]
        return

    if argument_type == "m":
        selector_arguments["gamemode"] = miscellaneous.gamemode(cast(str, value), pack_version, issues)
        del selector_arguments[argument_type]
        return

    # Send warning that argument is not registered
    if defaults.SEND_WARNINGS:
        log(f'WARNING: Target selector argument "{argument_type}" is not registered!')

def update_argument_list(argument_type: str, value: str, selector_arguments: dict[str, str | dict | list], issues: list[dict[str, str | int]]) -> str | None:
    if argument_type == "gamemode":
        return miscellaneous.gamemode(value, pack_version, issues)

    if argument_type == "nbt":
        nbt_input = {"nbt": value}
        if value.startswith("!"):
            nbt_input["nbt"] = value[1:]

        if "type" in selector_arguments and not selector_arguments["type"][0].startswith("!"):
            nbt_input["object_id"] = entities.update(selector_arguments["type"][0], pack_version, issues)

        updated_nbt = nbt_tags.update(nbt_input, pack_version, issues, "entity")
        if updated_nbt == "{}":
            return None
        if value.startswith("!"):
            return "!" + updated_nbt
        return updated_nbt

    if argument_type == "type":
        if value.startswith("!"):
            return "!" + entities.update(value[1:], pack_version, issues)
        return entities.update(value, pack_version, issues)

    return value

def update_range(new_value: str, old_value: str, range_type: str) -> str:
    # Get existing upper and lower bounds
    if old_value == "":
        value_a = ""
        value_b = ""
    elif ".." in old_value:
        if old_value[:2] == "..":
            value_a = ""
            value_b = old_value[2:]
        elif old_value[-2:] == "..":
            value_a = old_value[:-2]
            value_b = ""
        else:
            value_a = old_value[:old_value.index("..")]
            value_b = old_value[old_value.index("..") + 2:]
    else:
        value_a = old_value
        value_b = old_value

    # Insert new value
    if range_type == "min":
        if not value_b or float(new_value) <= float(value_b):
            value_a = new_value
        else:
            value_a = value_b
    elif range_type == "max":
        if not value_a or float(value_a) <= float(new_value):
            value_b = new_value
        else:
            value_b = value_a
    else:
        value_a = new_value
        value_b = new_value

    if value_a == value_b:
        return value_a
    if not value_a:
        return ".." + value_b
    if not value_b:
        return value_a + ".."
    return value_a + ".." + value_b



def handle_boat_split(selector_arguments: dict[str, list[str]]):
    # Get list of all boat types
    boat_type = ""
    negated_boat_types: list[str] = []
    if "nbt" in selector_arguments:
        for nbt_string in selector_arguments["nbt"]:
            negated = nbt_string.startswith("!")
            if negated:
                nbt_string = nbt_string[1:]
            unpacked_nbt = cast(dict[str, str], nbt_tags.unpack(nbt_string))
            if "Type" in unpacked_nbt:
                if negated:
                    negated_boat_types.append(unpacked_nbt["Type"])
                else:
                    boat_type = unpacked_nbt["Type"]

    # Apply boat type information to entity types
    create_chest_boat_tag = False
    added_entity_types: list[str] = []
    for i in range(len(selector_arguments["type"])):
        entity_type = miscellaneous.namespace(selector_arguments["type"][i])
        negated = entity_type.startswith("!")
        if negated:
            entity_type = entity_type[1:]
        if entity_type not in ["minecraft:boat", "minecraft:chest_boat"]:
            continue
        if negated:
            if entity_type == "minecraft:boat":
                selector_arguments["type"][i] = "!#minecraft:boat"
                continue
            if entity_type == "minecraft:chest_boat":
                selector_arguments["type"][i] = "!#tag_replacements:chest_boat"
                create_chest_boat_tag = True
                continue

        # If there is an explicit boat type definition, the entity type will be set according to that
        # Otherwise it will be the tag with each of the negated boat types canceled out
        if boat_type:
            if entity_type == "minecraft:boat":
                id_array = tables.BOAT_TYPES
                if boat_type in id_array:
                    selector_arguments["type"][i] = id_array[boat_type]
                continue
            if entity_type == "minecraft:chest_boat":
                id_array = tables.CHEST_BOAT_TYPES
                if boat_type in id_array:
                    selector_arguments["type"][i] = id_array[boat_type]
                continue

        else:
            if entity_type == "minecraft:boat":
                selector_arguments["type"][i] = "#minecraft:boat"
                id_array = tables.BOAT_TYPES
                for negated_boat_type in negated_boat_types:
                    if negated_boat_type in id_array:
                        added_entity_types.append("!" + id_array[negated_boat_type])
                continue
            if entity_type == "minecraft:chest_boat":
                selector_arguments["type"][i] = "#tag_replacements:chest_boat"
                create_chest_boat_tag = True
                id_array = tables.CHEST_BOAT_TYPES
                for negated_boat_type in negated_boat_types:
                    if negated_boat_type in id_array:
                        added_entity_types.append("!" + id_array[negated_boat_type])
                continue

    selector_arguments["type"].extend(added_entity_types)

    if create_chest_boat_tag:
        tag_replacements.create_pack(
            easy_map_updater.MINECRAFT_PATH / "saves" / option_manager.get_map_name()
        )