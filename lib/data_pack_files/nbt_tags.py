# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
import math
from typing import cast, Any
from nbt import nbt as NBT
from pathlib import Path
from lib.log import log
from lib import defaults
from lib import utils
from lib import option_manager
from lib import json_manager



# Initialize variables

pack_version = defaults.PACK_VERSION

PROGRAM_PATH = Path(__file__).parent
with (PROGRAM_PATH / "nbt_tree.json").open("r", encoding="utf-8") as file:
    NBT_TREE: dict[str, Any] = json.load(file)



# Define data type classes

class TypeNumeric:
    def __init__(self, value, num_type: str):
        # Assign value
        if type(value).__name__ not in ["int", "float", "str"]:
            self.value = self.num(value.value, num_type)
        else:
            self.value = self.num(value, num_type)
        self.suffix = ""

    def pack(self):
        return str(self.value) + self.suffix

    def num(self, value, num_type: str):
        if isinstance(value, str):
            is_hex = len(value) >= 3 and value.startswith("0x")
            for char in ["b", "B", "s", "S", "i", "I", "l", "L", "f", "F", "d", "D"]:
                if char in ["f", "F"] and is_hex:
                    continue
                if char in ["b", "B"] and is_hex and not (value.endswith("s" + char) or value.endswith("u" + char)):
                    continue
                if value.endswith(char):
                    value = value[:-1]
                    for char in ["s", "u"]:
                        if value.endswith(char):
                            value = value[:-1]
                            break
                    break
            value = value.replace("_", "")
        if num_type == "int":
            return utils.cast_int(value)
        return float(value)

    def __bool__(self) -> bool:
        return bool(self.value)

class TypeByte(TypeNumeric):
    def __init__(self, value):
        TypeNumeric.__init__(self, value, "int")
        self.value = utils.byte_range(self.value)
        self.suffix = "b"

class TypeShort(TypeNumeric):
    value: int
    def __init__(self, value):
        TypeNumeric.__init__(self, value, "int")
        self.value = utils.short_range(self.value)
        self.suffix = "s"

class TypeInt(TypeNumeric):
    value: int
    def __init__(self, value):
        TypeNumeric.__init__(self, value, "int")
        self.value = utils.int_range(self.value)

class TypeLong(TypeNumeric):
    value: int
    def __init__(self, value):
        TypeNumeric.__init__(self, value, "int")
        self.value = utils.long_range(self.value)
        self.suffix = "L"

class TypeFloat(TypeNumeric):
    value: float
    def __init__(self, value):
        TypeNumeric.__init__(self, value, "float")
        self.suffix = "f"

class TypeDouble(TypeNumeric):
    value: float
    def __init__(self, value):
        TypeNumeric.__init__(self, value, "float")
        self.suffix = "d"

class TypeDecimal(TypeNumeric):
    value: float
    def __init__(self, value):
        TypeNumeric.__init__(self, value, "float")

class TypeList:
    def __init__(self, value):
        # Assign value
        if not isinstance(value, list):
            self.value: list = value.value.copy()
        else:
            self.value = value.copy()
        self.i = -1
        self.prefix = ""

    def __iter__(self):
        return self

    def __next__(self):
        self.i += 1
        if self.i < len(self.value):
            return self.value[self.i]
        raise StopIteration

    def __getitem__(self, i):
        return self.value[i]

    def __setitem__(self, i, value):
        self.value[i] = value

    def __len__(self):
        return len(self.value)
    
    def append(self, value):
        self.value.append(value)

    def extend(self, value):
        self.value.extend(value)
    
    def pop(self, i):
        return self.value.pop(i)

    def pack(self) -> str:
        # Prepare list
        out_list = []
        for entry in self.value:
            out_list.append(pack(entry))

        return f'[{self.prefix}{",".join(out_list)}]'

class TypeByteArray(TypeList):
    def __init__(self, value):
        TypeList.__init__(self, value)
        self.prefix = "B;"

class TypeIntArray(TypeList):
    def __init__(self, value):
        TypeList.__init__(self, value)
        self.prefix = "I;"

class TypeLongArray(TypeList):
    def __init__(self, value):
        TypeList.__init__(self, value)
        self.prefix = "L;"

class TypeMacroToken:
    token: str
    suffix: str
    def __init__(self, token: str, suffix: str = ""):
        self.token = token
        self.suffix = suffix

    def pack(self) -> str:
        return self.token + self.suffix
    
    def __bool__(self) -> bool:
        return bool(self.token)



# Import more stuff to prevent circular loading issues

from lib.data_pack_files import command
from lib.data_pack_files import arguments
from lib.data_pack_files import items
from lib.data_pack_files import blocks
from lib.data_pack_files import entities
from lib.data_pack_files import json_text_component
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import ids
from lib.data_pack_files import nbt_paths
from lib.data_pack_files import item_component
from lib.data_pack_files import tables
from lib.data_pack_files.restore_behavior import lock_fixer



# Define functions

def update(snbt: str | dict, version: int, issues: list[dict[str, str | int]], source: str) -> str:
    global pack_version
    pack_version = version

    object_id = ""
    read = False

    # Extract arguments if a dict
    if isinstance(snbt, dict):
        if "object_id" in snbt:
            object_id: str = miscellaneous.namespace(snbt["object_id"])
        if "read" in snbt:
            read = snbt["read"]
        snbt = cast(str, snbt["nbt"])

    # Return if not SNBT
    if snbt == "":
        return snbt
    if snbt[0] != "{":
        if source != "arbitrary":
            return snbt
        if snbt[0] != "[" and snbt[0] != '"':
            return snbt

    nbt: dict = cast(dict, unpack(snbt))
    return pack(get_source({}, nbt, source, object_id, read, issues))

def direct_update(nbt: dict | None, version: int, issues: list[dict[str, str | int]], source: str, object_id: str, read: bool) -> dict | None:
    global pack_version
    pack_version = version

    if not isinstance(nbt, dict):
        return
    
    return get_source({}, nbt, source, object_id, read, issues)

def update_with_guide(snbt: str, version: int, issues: list[dict[str, str | int]], source: str, read: bool, guide: dict, callback: str) -> str:
    global pack_version
    pack_version = version

    # Return if not SNBT
    if not snbt:
        return snbt
    
    return pack(direct_update_with_guide(unpack(snbt), version, issues, source, read, guide, callback))

def direct_update_with_guide(nbt: dict, version: int, issues: list[dict[str, str | int]], source: str, read: bool, guide: dict, callback: str) -> dict | TypeList:
    global pack_version
    pack_version = version

    # Return if not NBT
    if not nbt:
        return nbt
    
    if defaults.DEBUG_MODE:
        log(f'CALLBACK: {callback} - GUIDE: {guide}')

    match callback:
        case "branch":
            return branch({}, nbt, guide, source, "", read, issues)
        case "tags":
            if "necessary_tags" in guide:
                return update_tags({}, nbt, guide, source, "", read, guide["necessary_tags"], issues)
            return update_tags({}, nbt, guide, source, "", read, {}, issues)
        case "list":
            return update_list({}, cast(TypeList, nbt), guide, source, "", read, issues)
        
    return nbt
    




def unpack(nbt: str) -> Any:
    if not isinstance(nbt, str):
        return nbt
    if nbt == "":
        return

    # Unpack based on type
    if nbt.startswith("{"):
        return unpack_compound(nbt)
    if nbt.startswith("["):
        return unpack_list(nbt)
    if nbt[0] in ['"', "'"]:
        return utils.unpack_string(nbt)
    if utils.is_num(nbt):
        try:
            int(nbt.replace("_", ""), 0)
        except:
            return TypeDecimal(nbt)
        else:
            return TypeInt(nbt)
    is_hex = len(nbt) >= 3 and nbt.startswith("0x")
    if len(nbt) > 1 and utils.is_num(nbt[:-1]):
        if nbt[-1] in ["b", "B"] and not is_hex:
            return TypeByte(nbt[:-1])
        if nbt[-1] in ["s", "S"]:
            return TypeShort(nbt[:-1])
        if nbt[-1] in ["i", "I"]:
            return TypeInt(nbt[:-1])
        if nbt[-1] in ["l", "L"]:
            return TypeLong(nbt[:-1])
        if nbt[-1] in ["f", "F"] and not is_hex:
            return TypeFloat(nbt[:-1])
        if nbt[-1] in ["d", "D"]:
            return TypeDouble(nbt[:-1])
    if len(nbt) > 2 and utils.is_num(nbt[:-2]) and nbt[-2] in ["s", "u"]:
        if nbt[-1] in ["b", "B"]:
            return TypeByte(nbt[:-2])
        if nbt[-1] in ["s", "S"]:
            return TypeShort(nbt[:-2])
        if nbt[-1] in ["i", "I"]:
            return TypeInt(nbt[:-2])
        if nbt[-1] in ["l", "L"]:
            return TypeLong(nbt[:-2])
        if nbt[-1] in ["f", "F"] and not is_hex:
            return TypeFloat(nbt[:-2])
        if nbt[-1] in ["d", "D"]:
            return TypeDouble(nbt[:-2])
    
    if nbt == "true":
        return TypeByte(1)
    if nbt == "false":
        return TypeByte(0)
    
    if miscellaneous.is_macro_token(nbt):
        return TypeMacroToken(nbt)
    if nbt[-1].lower() in ["b", "s", "i", "l", "f", "d"] and miscellaneous.is_macro_token(nbt[:-1]):
        return TypeMacroToken(nbt[:-1], nbt[-1])

    return nbt

def unpack_compound(nbt: str) -> dict:
    # Prepare compound
    compound = {}

    # Stop if NBT is blank
    if nbt.strip() == "" or nbt.strip()[1:-1].strip() == "":
        return compound

    # Add tags to compound
    for tag in arguments.parse_with_quotes(nbt.strip()[1:], ",", pack_version >= 1400):
        if ":" not in tag:
            continue
        values = arguments.parse_with_quotes(tag, ":", pack_version >= 1400)
        name = utils.unpack_string_check(values[0].strip())
        value = ":".join(values[1:]).strip()
        compound[name] = unpack(value)

    return compound

def unpack_list(nbt: str) -> TypeList:
    # Prepare list
    out_list = []

    # Stop if NBT is blank
    if nbt.strip() == "" or nbt.strip()[1:-1].strip() == "":
        return TypeList(out_list)

    # Set list prefix
    prefix = ""
    if len(nbt) >= 4 and nbt[1:3] in ["B;", "I;", "L;"]:
        prefix = nbt[1:3]
        nbt = "[" + nbt[3:]

    # Add tags to list
    for tag in arguments.parse_with_quotes(nbt.strip()[1:], ",", pack_version >= 1400):
        tag = tag.strip()
        if tag != "":
            if ":" in tag and tag.split(":")[0].isnumeric():
                tag = ":".join(tag.split(":")[1:])
            out_list.append(unpack(tag))

    # Convert list type
    if prefix == "B;":
        return TypeByteArray(out_list)
    if prefix == "I;":
        return TypeIntArray(out_list)
    if prefix == "L;":
        return TypeLongArray(out_list)

    return TypeList(out_list)



def pack(nbt) -> str:
    # Pack based on type
    if nbt == None:
        return ""
    if isinstance(nbt, dict):
        return pack_compound(nbt)
    if isinstance(nbt, list):
        return pack_list(nbt)
    if type(nbt).__name__ == "str":
        return utils.pack_string(nbt)

    return nbt.pack()

def pack_compound(nbt: dict[str, Any]) -> str:
    # Prepare tag list
    tags: list[str] = []

    # Return value if it's an array shortcut
    if len(nbt) == 1 and "" in nbt:
        return pack(nbt[""])

    # Iterate through keys
    for key in nbt:
        pack_bool = ":" in key or '"' in key or "'" in key or key == ""
        tags.append(f'{utils.pack_string(key) if pack_bool else key}:{pack(nbt[key])}')
    
    # Return stringified version of compound
    return "{" + ",".join(tags) + "}"

def pack_list(nbt: list) -> str:
    out_list = []
    for entry in nbt:
        out_list.append(pack(entry))
    return f'[{",".join(out_list)}]'



def get_source(parent: dict, nbt: dict, source: str, object_id: str, read: bool, issues: list[dict[str, str | int]]) -> Any:
    # Get guide
    if source not in NBT_TREE["sources"]:
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Source "{source}" is not registered!')
        return nbt
    return branch(parent, nbt, NBT_TREE["sources"][source], source, object_id, read, issues)

def branch(parent: dict, nbt, guide: dict, source: str, object_id: str, read: bool, issues: list[dict[str, str | int]]) -> Any:
    # Return function based on contents of guide
    if "edge_case" in guide:
        return edge_case(parent, nbt, guide["edge_case"], source, object_id, read, issues)
    if "source" in guide:
        return get_source(parent, nbt, guide["source"], object_id, read, issues)
    if "tags" in guide:
        if "necessary_tags" in guide:
            return update_tags(parent, nbt, guide["tags"], source, object_id, read, guide["necessary_tags"], issues)
        return update_tags(parent, nbt, guide["tags"], source, object_id, read, {}, issues)
    if "list" in guide:
        return update_list(parent, nbt, guide["list"], source, object_id, read, issues)
    if "data_type" in guide:
        return update_data(parent, nbt, guide, source, object_id, read, issues)
    return nbt

def update_tags(parent: dict, nbt: dict, guide: dict, source: str, object_id: str, read: bool, necessary_tags: dict, issues: list[dict[str, str | int]]) -> dict:
    if not isinstance(nbt, dict):
        return nbt

    # Invert order if it contains a "Riding" tag
    if source == "entity" and "Riding" in nbt:
        no_upper_id = "id" not in nbt
        if no_upper_id and object_id != "":
            if object_id.endswith("_spawn_egg"):
                nbt["id"] = object_id[:-10]
            else:
                nbt["id"] = object_id
        nbt = invert_riding(nbt)
        if no_upper_id and "id" in nbt:
            del nbt["id"]

    # Iterate through tags
    key: str
    for key in list(nbt.keys()):
        if source in ["block", "entity"] and key == "CommandStats" and not option_manager.FIXES["stats"]:
            log("WARNING: Stats fixer not enabled but stats have been found!")
        if key in guide and key in nbt:
            if (
                "remove" in guide[key] and
                (
                    (isinstance(guide[key]["remove"], bool) and guide[key]["remove"]) or
                    (isinstance(guide[key]["remove"], dict) and (
                        "matches" in guide[key]["remove"] and (
                            (isinstance(nbt[key], TypeNumeric) and nbt[key].value == guide[key]["remove"]["matches"]) or
                            (isinstance(nbt[key], str) and nbt[key] == guide[key]["remove"]["matches"])
                        )
                    ))
                )
            ):
                branch(nbt, nbt[key], guide[key], source, object_id, read, issues)
                if key in nbt:
                    del nbt[key]
            elif "rename" in guide[key]:
                nbt[guide[key]["rename"]] = branch(nbt, nbt[key], guide[key], source, object_id, read, issues)
                if key in nbt:
                    del nbt[key]
            else:
                value = branch(nbt, nbt[key], guide[key], source, object_id, read, issues)
                if value != None:
                    nbt[key] = value

    # Apply necessary tags
    if necessary_tags:
        for key in necessary_tags:
            if key in nbt:
                continue
            generator = necessary_tags[key]["generator"]

            if "conditions" in necessary_tags[key]:
                skip = False
                for condition in necessary_tags[key]["conditions"]:
                    if condition in nbt:
                        value = nbt[condition]
                    elif condition == "id":
                        value = object_id
                    else:
                        skip = True
                        break
                    if isinstance(value, str):
                        if value != necessary_tags[key]["conditions"][condition]:
                            skip = True
                            break
                    elif isinstance(value, TypeNumeric):
                        if value.value != necessary_tags[key]["conditions"][condition].value:
                            skip = True
                            break
                    else:
                        skip = True
                        break
                if skip:
                    continue

            if "read" in necessary_tags[key]:
                if necessary_tags[key]["read"] != read:
                    continue

            if "version" in necessary_tags[key]:
                if "min" in necessary_tags[key]:
                    if pack_version < necessary_tags[key]["min"]:
                        continue
                if "max" in necessary_tags[key]:
                    if pack_version > necessary_tags[key]["max"]:
                        continue

            if generator == "area_effect_cloud_radius":
                if pack_version <= 2104:
                    nbt[key] = TypeFloat(0)
            if generator == "item_entity":
                nbt[key] = {"id": "minecraft:stone", "count": TypeInt(1)}
            if generator == "tnt_fuse":
                nbt[key] = TypeShort(0)
            if generator == "uuid":
                nbt[key] = miscellaneous.new_uuid_int_array()

    return nbt

def update_list(parent: dict, nbt: TypeList, guide: dict, source: str, object_id: str, read: bool, issues: list[dict[str, str | int]]) -> TypeList:
    if not isinstance(nbt, TypeList):
        return nbt

    # Iterate through elements
    for i in range(len(nbt.value)):
        nbt[i] = branch(parent, nbt[i], guide, source, object_id, read, issues)
    return nbt

def update_data(parent: dict, nbt, guide: dict, source: str, object_id: str, read: bool, issues: list[dict[str, str | int]]):
    # Return if a macro token
    if isinstance(nbt, TypeMacroToken):
        return nbt

    # Get types
    data_type: str = guide["data_type"]
    output_data_type = data_type
    if "output_data_type" in guide:
        output_data_type = guide["output_data_type"]
    argument_type = "carry"
    if "argument_type" in guide:
        argument_type: str = guide["argument_type"]

    # Convert numeric types
    nbt = apply_data_type(parent, nbt, data_type)

    # Put together parameters
    if "parameters" in guide:
        parameters = {}
        for key in guide["parameters"]:
            obj = nbt_paths.extract_nbt_from_path(parent, nbt_paths.unpack(guide["parameters"][key]))
            if obj != None:
                parameters[key] = obj
        return apply_data_type(parent, command.update_argument(parameters, argument_type, issues), output_data_type)

    # Convert based on argument type
    return apply_data_type(parent, command.update_argument(nbt, argument_type, issues), output_data_type)

def apply_data_type(parent: dict, nbt, data_type: str) -> Any:
    try:
        if data_type == "byte":
            return TypeByte(nbt)
        if data_type == "short":
            return TypeShort(nbt)
        if data_type == "int":
            return TypeInt(nbt)
        if data_type == "long":
            return TypeLong(nbt)
        if data_type == "float":
            return TypeFloat(nbt)
        if data_type == "double":
            return TypeDouble(nbt)
        if data_type == "list":
            return TypeList(nbt)
        if data_type == "byte_array":
            return TypeByteArray(nbt)
        if data_type == "int_array":
            return TypeIntArray(nbt)
        if data_type == "long_array":
            return TypeLongArray(nbt)
    except:
        log(f"Could not cast {pack(nbt)} as {data_type} from {pack(parent)}")
        return nbt
    return nbt

def invert_riding(nbt: dict) -> dict:
    output_nbt = nbt["Riding"]
    del nbt["Riding"]
    output_nbt["Passengers"] = TypeList([nbt])
    if "Riding" in output_nbt:
        output_nbt = invert_riding(output_nbt)
    return output_nbt



def edge_case(parent: dict, nbt, case: str | dict[str, str], source: str, object_id: str, read: bool, issues: list[dict[str, str | int]]) -> Any:
    # Get case
    if isinstance(case, dict):
        case_type: str = case["case"]
    else:
        case_type = case

    # Process NBT based on case
    if case_type == "anchor_pos":
        return edge_case_anchor_pos(parent)
    if case_type == "arbitrary_data":
        return edge_case_arbitrary_data(nbt)
    if case_type == "armor_drop_chances":
        return edge_case_armor_drop_chances(parent)
    if case_type == "armor_item":
        return edge_case_armor_item(parent, object_id, read, issues)
    if case_type == "armor_items":
        return edge_case_armor_items(parent, object_id, read, issues)
    if case_type == "attribute_id":
        return edge_case_attribute_id(parent)
    if case_type == "banner_base":
        return edge_case_banner_base(parent, object_id, issues)
    if case_type == "block_entity":
        return blocks.update_from_nbt(cast(blocks.BlockInputFromNBT, parent), pack_version, issues)
    if case_type == "block_pos":
        return edge_case_block_pos(parent)
    if case_type == "boat_type":
        return edge_case_boat_type(parent)
    if case_type == "body_armor_drop_chance":
        return edge_case_body_armor_drop_chance(parent)
    if case_type == "body_armor_item":
        return edge_case_body_armor_item(parent, object_id, read, issues)
    if case_type == "bound_pos":
        return edge_case_bound_pos(parent)
    if case_type == "can_place_on":
        return edge_case_can_place_on(nbt, issues)
    if case_type == "color":
        return edge_case_color(parent, object_id)
    if case_type == "custom_potion_effects":
        return edge_case_custom_potion_effects(parent, object_id, read, issues)
    if case_type == "effects":
        return edge_case_effects(parent, object_id, read, issues)
    if case_type == "entity_id":
        return edge_case_entity_id(parent, nbt, object_id, read, issues)
    if case_type == "equipment":
        return edge_case_equipment(parent, nbt, object_id, read, issues)
    if case_type == "fuse":
        return edge_case_fuse(parent, object_id)
    if case_type == "hand_drop_chances":
        return edge_case_hand_drop_chances(parent)
    if case_type == "hand_items":
        return edge_case_hand_items(parent, object_id, read, issues)
    if case_type == "home_pos":
        return edge_case_home_pos(parent)
    if case_type == "inventory":
        return edge_case_inventory(parent, issues)
    if case_type == "item":
        return items.update_from_nbt(nbt, pack_version, issues)
    if case_type == "item_components":
        return edge_case_item_components(nbt, pack_version, issues)
    if case_type == "item_tag":
        return edge_case_item_tag(parent, nbt, object_id, read, pack_version, issues)
    if case_type == "lock":
        return edge_case_lock(nbt)
    if case_type == "mooshroom_stew":
        return edge_case_mooshroom_stew(parent, pack_version, issues)
    if case_type == "old_spawn_potential_entity":
        return edge_case_old_spawn_potential_entity(parent, nbt, object_id, read, issues)
    if case_type == "potion":
        return edge_case_potion(parent, object_id)
    if case_type == "power":
        return edge_case_power(parent)
    if case_type == "recipes":
        return edge_case_recipes(nbt, issues)
    if case_type == "respawn":
        return edge_case_respawn(parent)
    if case_type == "saddle":
        return edge_case_saddle(parent)
    if case_type == "saddle_item":
        return edge_case_saddle_item(parent, object_id, read, issues)
    if case_type == "shot_from_crossbow":
        return edge_case_shot_from_crossbow(parent)
    if case_type == "sign_text":
        return edge_case_sign_text(parent, issues)
    if case_type == "size":
        return edge_case_size(parent, object_id)
    if case_type == "skull_owner":
        return edge_case_skull_owner(nbt)
    if case_type == "sleeping_pos":
        return edge_case_sleeping_pos(parent)
    if case_type == "spawn_data":
        return edge_case_spawn_data(nbt, object_id, read, issues)
    if case_type == "spawn_potential_entity":
        return edge_case_spawn_potential_entity(parent, nbt, object_id, read, issues)
    if case_type == "uuid_long":
        return edge_case_uuid_long(parent, cast(dict, case))

    if defaults.SEND_WARNINGS:
        log(f'WARNING: "{case_type}" case is not registered!')
    return nbt

def edge_case_anchor_pos(parent: dict[str, Any]):
    if "anchor_pos" in parent:
        return
    parent["anchor_pos"] = TypeIntArray([
        TypeInt(0),
        TypeInt(0),
        TypeInt(0),
    ])
    if "AX" in parent:
        parent["anchor_pos"][0] = TypeInt(parent["AX"])
    if "AY" in parent:
        parent["anchor_pos"][1] = TypeInt(parent["AY"])
    if "AZ" in parent:
        parent["anchor_pos"][2] = TypeInt(parent["AZ"])

def edge_case_arbitrary_data(nbt):
    return process_arbitrary_nbt(nbt)

def edge_case_armor_drop_chances(parent: dict[str, Any]):
    if "drop_chances" not in parent:
        parent["drop_chances"] = {}

    length = len(parent["ArmorDropChances"])

    parent["drop_chances"]["feet"] = TypeFloat(parent["ArmorDropChances"][0]) if length > 0 else TypeFloat(0.085)
    parent["drop_chances"]["legs"] = TypeFloat(parent["ArmorDropChances"][1]) if length > 1 else TypeFloat(0.085)
    parent["drop_chances"]["chest"] = TypeFloat(parent["ArmorDropChances"][2]) if length > 2 else TypeFloat(0.085)
    parent["drop_chances"]["head"] = TypeFloat(parent["ArmorDropChances"][3]) if length > 3 else TypeFloat(0.085)

def edge_case_armor_item(parent: dict[str, Any], object_id: str, read: bool, issues: list[dict[str, str | int]]):
    if "equipment" not in parent:
        parent["equipment"] = {}

    parent["equipment"]["body"] = get_source(parent, parent["ArmorItem"], "item", object_id, read, issues)

def edge_case_armor_items(parent: dict[str, Any], object_id: str, read: bool, issues: list[dict[str, str | int]]):
    if "equipment" not in parent:
        parent["equipment"] = {}

    length = len(parent["ArmorItems"])

    if length > 0 and parent["ArmorItems"][0]:
        parent["equipment"]["feet"] = get_source(parent, parent["ArmorItems"][0], "item", object_id, read, issues)
    elif option_manager.FIXES["empty_equipment_override"]:
        parent["equipment"]["feet"] = {"id": "minecraft:air", "count": TypeInt(0)}
    if length > 1 and parent["ArmorItems"][1]:
        parent["equipment"]["legs"] = get_source(parent, parent["ArmorItems"][1], "item", object_id, read, issues)
    elif option_manager.FIXES["empty_equipment_override"]:
        parent["equipment"]["legs"] = {"id": "minecraft:air", "count": TypeInt(0)}
    if length > 2 and parent["ArmorItems"][2]:
        parent["equipment"]["chest"] = get_source(parent, parent["ArmorItems"][2], "item", object_id, read, issues)
    elif option_manager.FIXES["empty_equipment_override"]:
        parent["equipment"]["chest"] = {"id": "minecraft:air", "count": TypeInt(0)}
    if length > 3 and parent["ArmorItems"][3]:
        parent["equipment"]["head"] = get_source(parent, parent["ArmorItems"][3], "item", object_id, read, issues)
    elif option_manager.FIXES["empty_equipment_override"]:
        parent["equipment"]["head"] = {"id": "minecraft:air", "count": TypeInt(0)}

def edge_case_attribute_id(parent: dict[str, Any]):
    if "UUID" in parent:
        parent["id"] = miscellaneous.namespace(
            utils.uuid_from_int_array([entry.value for entry in parent["UUID"]])
        )

    elif "UUIDLeast" in parent or "UUIDMost" in parent:
        if "UUIDLeast" in parent:
            least: int = parent["UUIDLeast"].value
        else:
            least = 0
        if "UUIDMost" in parent:
            most: int = parent["UUIDMost"].value
        else:
            most = 0
        parent["id"] = miscellaneous.namespace(utils.uuid_from_int_array([
            utils.int_range(most  // 4294967296),
            utils.int_range(most  %  4294967296),
            utils.int_range(least // 4294967296),
            utils.int_range(least %  4294967296)
        ]))

    for key in ["UUID", "UUIDLeast", "UUIDMost"]:
        if key in parent:
            del parent[key]

def edge_case_banner_base(parent: dict[str, TypeInt], object_id: str, issues: list[dict[str, str | int]]):
    if miscellaneous.namespace(object_id) == "minecraft:shield":
        parent["Base"] = miscellaneous.banner_color_numeric(parent["Base"], pack_version)
    else:
        del parent["Base"]

def edge_case_block_pos(parent: dict[str, Any]):
    if "block_pos" in parent:
        return
    parent["block_pos"] = TypeIntArray([
        TypeInt(0),
        TypeInt(0),
        TypeInt(0),
    ])
    if "TileX" in parent:
        parent["block_pos"][0] = TypeInt(parent["TileX"])
    if "TileY" in parent:
        parent["block_pos"][1] = TypeInt(parent["TileY"])
    if "TileZ" in parent:
        parent["block_pos"][2] = TypeInt(parent["TileZ"])

def edge_case_boat_type(parent: dict[str, str]):
    if "id" not in parent:
        return
    entity_id = miscellaneous.namespace(parent["id"])

    boat_type = "oak"
    if "Type" in parent:
        boat_type = parent["Type"]

    if entity_id in ["minecraft:boat", "minecraft:oak_boat"]:
        id_array = tables.BOAT_TYPES
        if boat_type in id_array:
            parent["id"] = id_array[boat_type]

    if entity_id in ["minecraft:chest_boat", "minecraft:oak_chest_boat"]:
        id_array = tables.CHEST_BOAT_TYPES
        if boat_type in id_array:
            parent["id"] = id_array[boat_type]

def edge_case_body_armor_drop_chance(parent: dict[str, Any]):
    if "drop_chances" not in parent:
        parent["drop_chances"] = {}

    parent["drop_chances"]["body"] = TypeFloat(parent["body_armor_drop_chances"])

def edge_case_body_armor_item(parent: dict[str, Any], object_id: str, read: bool, issues: list[dict[str, str | int]]):
    if "equipment" not in parent:
        parent["equipment"] = {}

    parent["equipment"]["body"] = get_source(parent, parent["body_armor_item"], "item", object_id, read, issues)

def edge_case_bound_pos(parent: dict[str, Any]):
    if "bound_pos" in parent:
        return
    parent["bound_pos"] = TypeIntArray([
        TypeInt(0),
        TypeInt(0),
        TypeInt(0),
    ])
    if "BoundX" in parent:
        parent["bound_pos"][0] = TypeInt(parent["BoundX"])
    if "BoundY" in parent:
        parent["bound_pos"][1] = TypeInt(parent["BoundY"])
    if "BoundZ" in parent:
        parent["bound_pos"][2] = TypeInt(parent["BoundZ"])

def edge_case_can_place_on(nbt: list[str], issues: list[dict[str, str | int]]):
    new_list: list[str] = []
    for block in nbt:
        new_block = blocks.update(
            {
                "id": block[:block.find("[")] if "[" in block else block,
                "data_value": -1,
                "block_states": blocks.unpack_block_states(block[block.find("["):]) if "[" in block else {},
                "nbt": {},
                "read": True
            },
            pack_version, issues
        )
        new_list.append(cast(str, new_block["id"]) + (blocks.pack_block_states(new_block["block_states"]) if new_block["block_states"] else ""))
    return TypeList(utils.deduplicate_list(new_list))

def edge_case_color(parent: dict, object_id: str):
    if object_id == "minecraft:area_effect_cloud":
        if "potion_contents" not in parent:
            parent["potion_contents"] = {}
        parent["potion_contents"]["custom_color"] = TypeInt(parent["Color"].value)
        del parent["Color"]

def edge_case_custom_potion_effects(parent: dict, object_id: str, read: bool, issues: list[dict[str, str | int]]):
    if "item" not in parent:
        parent["item"] = {}
    if "id" not in parent["item"]:
        parent["item"]["id"] = "minecraft:arrow"
    if "count" not in parent["item"]:
        parent["item"]["count"] = TypeInt(1)
    if "components" not in parent["item"]:
        parent["item"]["components"] = {}
    if "minecraft:potion_contents" not in parent["item"]["components"]:
        parent["item"]["components"]["minecraft:potion_contents"] = {}
    if "custom_effects" not in parent["item"]["components"]["minecraft:potion_contents"]:
        parent["item"]["components"]["minecraft:potion_contents"]["custom_effects"] = TypeList([])
    if "CustomPotionEffects" in parent:
        key = "CustomPotionEffects"
    else:
        key = "custom_potion_effects"
    for effect in parent[key]:
        parent["item"]["components"]["minecraft:potion_contents"]["custom_effects"].append(get_source(parent, effect, "effect", object_id, read, issues))

def edge_case_effects(parent: dict, object_id: str, read: bool, issues: list[dict[str, str | int]]):
    if "potion_contents" not in parent:
        parent["potion_contents"] = {}
    parent["potion_contents"]["custom_effects"] = TypeList([])
    for effect in parent["effects"]:
        parent["potion_contents"]["custom_effects"].append(get_source(parent, effect, "effect", object_id, read, issues))

def edge_case_entity_id(parent: dict, nbt: str, object_id: str, read: bool, issues: list[dict[str, str | int]]):
    if "SpawnData" in parent:
        parent["SpawnData"] = edge_case_spawn_data(parent["SpawnData"], object_id, read, issues)
    else:
        parent["SpawnData"] = {}
    if "entity" not in parent["SpawnData"]:
        parent["SpawnData"]["entity"] = {}
    parent["SpawnData"]["entity"]["id"] = entities.update(nbt, pack_version, issues)

def edge_case_equipment(parent: dict, nbt: TypeList, object_id: str, read: bool, issues: list[dict[str, str | int]]):
    if "equipment" not in parent:
        parent["equipment"] = {}

    length = len(nbt)

    if length > 4 and nbt[4]:
        parent["equipment"]["head"] = get_source(parent, nbt[4], "item", object_id, read, issues)
    elif option_manager.FIXES["empty_equipment_override"]:
        parent["equipment"]["head"] = {"id": "minecraft:air", "count": TypeInt(0)}
    if length > 3 and nbt[3]:
        parent["equipment"]["chest"] = get_source(parent, nbt[3], "item", object_id, read, issues)
    elif option_manager.FIXES["empty_equipment_override"]:
        parent["equipment"]["chest"] = {"id": "minecraft:air", "count": TypeInt(0)}
    if length > 2 and nbt[2]:
        parent["equipment"]["legs"] = get_source(parent, nbt[2], "item", object_id, read, issues)
    elif option_manager.FIXES["empty_equipment_override"]:
        parent["equipment"]["legs"] = {"id": "minecraft:air", "count": TypeInt(0)}
    if length > 1 and nbt[1]:
        parent["equipment"]["feet"] = get_source(parent, nbt[1], "item", object_id, read, issues)
    elif option_manager.FIXES["empty_equipment_override"]:
        parent["equipment"]["feet"] = {"id": "minecraft:air", "count": TypeInt(0)}
    if length > 0 and nbt[0]:
        parent["equipment"]["mainhand"] = get_source(parent, nbt[0], "item", object_id, read, issues)
    elif option_manager.FIXES["empty_equipment_override"]:
        parent["equipment"]["mainhand"] = {"id": "minecraft:air", "count": TypeInt(0)}

    # Fix false item rendering in 1.8
    index: tuple[str, str]
    for index in [("feet", "boots"), ("legs", "leggings"), ("chest", "chestplate"), ("head", "helmet")]:
        slot: str = index[0]
        armor: str = index[1]
        if slot in parent["equipment"] and "id" in parent["equipment"][slot]:
            if "count" not in parent["equipment"][slot]:
                parent["equipment"][slot]["count"] = TypeInt(1)
            item_id: str = parent["equipment"][slot]["id"]
            for armor_test in ["boots", "leggings", "chestplate", "helmet"]:
                if len(item_id) < len(armor_test):
                    continue
                if item_id[-len(armor_test):] == armor_test:
                    parent["equipment"][slot]["id"] = item_id[:-len(armor_test)] + armor
                    break

def edge_case_fuse(parent: dict, object_id: str):
    if (
        pack_version <= 2002 and
        "Fuse" in parent and
        "fuse" not in parent
    ):
        parent["Fuse"] = TypeShort(parent["Fuse"].value)
        parent["fuse"] = TypeShort(parent["Fuse"].value)
        if "id" in parent:
            object_id = parent["id"]
        if miscellaneous.namespace(object_id) == "minecraft:tnt":
            del parent["Fuse"]
        if miscellaneous.namespace(object_id) == "minecraft:creeper":
            del parent["fuse"]

def edge_case_hand_drop_chances(parent: dict[str, Any]):
    if "drop_chances" not in parent:
        parent["drop_chances"] = {}

    length = len(parent["HandDropChances"])

    parent["drop_chances"]["mainhand"] = TypeFloat(parent["HandDropChances"][0]) if length > 0 else TypeFloat(0.085)
    parent["drop_chances"]["offhand"] = TypeFloat(parent["HandDropChances"][1]) if length > 1 else TypeFloat(0.085)

def edge_case_hand_items(parent: dict[str, Any], object_id: str, read: bool, issues: list[dict[str, str | int]]):
    if "equipment" not in parent:
        parent["equipment"] = {}

    length = len(parent["HandItems"])

    if length > 0 and parent["HandItems"][0]:
        parent["equipment"]["mainhand"] = get_source(parent, parent["HandItems"][0], "item", object_id, read, issues)
    elif option_manager.FIXES["empty_equipment_override"]:
        parent["equipment"]["mainhand"] = {"id": "minecraft:air", "count": TypeInt(0)}
    if length > 1 and parent["HandItems"][1]:
        parent["equipment"]["offhand"] = get_source(parent, parent["HandItems"][1], "item", object_id, read, issues)
    elif option_manager.FIXES["empty_equipment_override"]:
        parent["equipment"]["offhand"] = {"id": "minecraft:air", "count": TypeInt(0)}

def edge_case_home_pos(parent: dict[str, Any]):
    if "home_pos" in parent:
        return
    parent["home_pos"] = TypeIntArray([
        TypeInt(0),
        TypeInt(0),
        TypeInt(0),
    ])
    if "HomePosX" in parent:
        parent["home_pos"][0] = TypeInt(parent["HomePosX"])
    if "HomePosY" in parent:
        parent["home_pos"][1] = TypeInt(parent["HomePosY"])
    if "HomePosZ" in parent:
        parent["home_pos"][2] = TypeInt(parent["HomePosZ"])

def edge_case_inventory(parent: dict[str, Any], issues: list[dict[str, str | int]]):
    inventory: list[dict] = []
    equipment_slots = [100, 101, 102, 103, -106]
    for item in parent["Inventory"]:
        item = items.update_from_nbt(item, pack_version, issues)
        moved_to_equipment = False
        if "Slot" in item:
            slot: int = item["Slot"].value
            if slot in equipment_slots:
                moved_to_equipment = True
                del item["Slot"]
                if "equipment" not in parent:
                    parent["equipment"] = {}
                equipment = parent["equipment"]
                if slot == 100:
                    equipment["feet"] = item
                if slot == 101:
                    equipment["legs"] = item
                if slot == 102:
                    equipment["chest"] = item
                if slot == 103:
                    equipment["head"] = item
                if slot == -106:
                    equipment["offhand"] = item
        if not moved_to_equipment:
            inventory.append(item)
    parent["Inventory"] = inventory
    if len(inventory) == 0:
        del parent["Inventory"]


def edge_case_item_components(nbt: dict[str, Any], version: int, issues: list[dict[str, str | int]]) -> dict[str, Any]:
    return item_component.conform_components(item_component.ItemComponents.unpack_from_dict(nbt, False), version, issues).pack_to_dict()

def edge_case_item_tag(parent: dict[str, Any], nbt: dict[str, Any], object_id: str, read: bool, pack_version: int, issues: list[dict[str, str | int]]) -> dict[str, Any]:
    nbt = update_tags(parent, nbt, NBT_TREE["sources"]["item_tag"]["tags"], "item_tag", object_id, read, {}, issues)
    return item_component.extract(object_id, parent["components"] if "components" in parent else {}, nbt, pack_version, issues)

def edge_case_lock(nbt: str) -> dict:
    if option_manager.FIXES["lock_fixer"]:
        lock_fixer.fix_locks()
        return {
            "components": {
                "minecraft:item_name": json_text_component.convert_lock_string(nbt)
            }
        }
    else:
        return {
            "components": {
                "minecraft:custom_name": nbt
            }
        }

def edge_case_mooshroom_stew(parent: dict, pack_version: int, issues: list[dict[str, str | int]]):
    parent["stew_effects"] = TypeList([{}])
    if "EffectId" in parent:
        parent["stew_effects"][0]["id"] = ids.effect(parent["EffectId"], pack_version, issues)
        del parent["EffectId"]
    if "EffectDuration" in parent:
        parent["stew_effects"][0]["duration"] = parent["EffectDuration"]
        del parent["EffectDuration"]

def edge_case_old_spawn_potential_entity(parent: dict[str, Any], nbt: dict[str, Any], object_id: str, read: bool, issues: list[dict[str, str | int]]):
    if "data" not in parent:
        parent["data"] = {}
    if "entity" not in parent["data"]:
        parent["data"]["entity"] = {}
    if "Properties" in parent:
        parent["data"]["entity"] = parent["Properties"].copy()
        del parent["Properties"]
    if "Type" in parent:
        parent["data"]["entity"]["id"] = entities.update(parent["Type"], pack_version, issues)
        del parent["Type"]
    parent["data"]["entity"] = get_source(parent["data"], parent["data"]["entity"], "entity", object_id, read, issues)

def edge_case_potion(parent: dict, object_id: str):
    # Handle tipped arrow case
    if (
        ("id" in parent and miscellaneous.namespace(parent["id"]) == "minecraft:arrow") or
        ("id" not in parent and miscellaneous.namespace(object_id) == "minecraft:arrow")
    ):
        if "item" not in parent:
            parent["item"] = {}
        if "id" not in parent["item"]:
            parent["item"]["id"] = "minecraft:arrow"
        if "count" not in parent["item"]:
            parent["item"]["count"] = TypeInt(1)
        if "components" not in parent["item"]:
            parent["item"]["components"] = {}
        if "minecraft:potion_contents" not in parent["item"]["components"]:
            parent["item"]["components"]["minecraft:potion_contents"] = {}
        parent["item"]["components"]["minecraft:potion_contents"]["potion"] = miscellaneous.namespace(parent["Potion"])

    else:
        # Handle area effect cloud case by default
        if "potion_contents" not in parent:
            parent["potion_contents"] = {}
        parent["potion_contents"]["potion"] = miscellaneous.namespace(parent["Potion"])

def edge_case_power(parent: dict):
    if "Motion" not in parent:
        parent["Motion"] = TypeList([TypeDouble(0) for i in range(3)])
    for i in range(3):
        parent["Motion"][i] = TypeDouble(parent["Motion"][i].value + parent["power"][i].value)
    parent["acceleration_power"] = TypeDouble(math.sqrt(
        parent["power"][0].value*parent["power"][0].value +
        parent["power"][1].value*parent["power"][1].value +
        parent["power"][2].value*parent["power"][2].value
    ))

def edge_case_recipes(nbt: list, issues: list[dict[str, str | int]]):
    for i in range(len(nbt)):
        entry: str | dict = nbt[i]
        if isinstance(entry, dict):
            if "id" in entry:
                entry = entry["id"]
            else:
                entry = "minecraft:stick"
        nbt[i] = items.update_from_command(cast(str, entry), pack_version, issues)

def edge_case_respawn(parent: dict[str, Any]):
    if "respawn" in parent:
        return
    parent["respawn"] = {}

    if "SpawnX" in parent:
        if "pos" not in parent["respawn"]:
            parent["respawn"]["pos"] = TypeIntArray([TypeInt(0), TypeInt(0), TypeInt(0)])
        parent["respawn"]["pos"][0] = TypeInt(parent["SpawnX"])
    if "SpawnY" in parent:
        if "pos" not in parent["respawn"]:
            parent["respawn"]["pos"] = TypeIntArray([TypeInt(0), TypeInt(0), TypeInt(0)])
        parent["respawn"]["pos"][1] = TypeInt(parent["SpawnY"])
    if "SpawnZ" in parent:
        if "pos" not in parent["respawn"]:
            parent["respawn"]["pos"] = TypeIntArray([TypeInt(0), TypeInt(0), TypeInt(0)])
        parent["respawn"]["pos"][2] = TypeInt(parent["SpawnZ"])

    if "SpawnAngle" in parent:
        parent["respawn"]["angle"] = TypeFloat(parent["SpawnAngle"])
    if "SpawnDimension" in parent:
        parent["respawn"]["dimension"] = miscellaneous.namespace(parent["SpawnDimension"])
    if "SpawnForced" in parent:
        parent["respawn"]["forced"] = TypeByte(parent["SpawnForced"])

def edge_case_saddle(parent: dict[str, Any]):
    if not parent["Saddle"].value:
        return

    if "equipment" not in parent:
        parent["equipment"] = {}
    if "drop_chances" not in parent:
        parent["drop_chances"] = {}
    
    parent["equipment"]["saddle"] = {"id": "minecraft:saddle", "count": TypeInt(1)}
    parent["drop_chances"]["saddle"] = TypeFloat(2)

def edge_case_saddle_item(parent: dict[str, Any], object_id: str, read: bool, issues: list[dict[str, str | int]]):
    if "equipment" not in parent:
        parent["equipment"] = {}
    if "drop_chances" not in parent:
        parent["drop_chances"] = {}

    parent["equipment"]["saddle"] = get_source(parent, parent["SaddleItem"], "item", object_id, read, issues)
    parent["drop_chances"]["saddle"] = TypeFloat(2)

def edge_case_shot_from_crossbow(parent: dict):
    if parent["ShotFromCrossbow"].value == 1:
        parent["weapon"] = {
            "id": "minecraft:crossbow",
            "count": TypeInt(1)
        }
    else:
        log(f'WARNING: Entity tag "ShotFromCrossbow:0b" was used, make sure it isn\'t being read')

def edge_case_sign_text(parent: dict, issues: list[dict[str, str | int]]):
    # Prepare front text
    if "front_text" not in parent:
        parent["front_text"] = {}

    for i in range(4):
        key = f"Text{i+1}"
        if key in parent:
            if "messages" not in parent["front_text"]:
                parent["front_text"]["messages"] = ['""', '""', '""', '""']
            parent["front_text"]["messages"][i] = json_text_component.update(parent[key], pack_version, issues, {"mangled": False, "pack": False})
            del parent[key]
    if "Color" in parent:
        parent["front_text"]["color"] = parent["Color"]
        del parent["Color"]
    if "GlowingText" in parent:
        parent["front_text"]["has_glowing_text"] = parent["GlowingText"]
        del parent["GlowingText"]

def edge_case_size(parent: dict, object_id: str):
    if (
        pack_version <= 2104 and
        "Size" in parent and
        "size" not in parent
    ):
        parent["Size"] = TypeInt(parent["Size"].value)
        parent["size"] = TypeInt(parent["Size"].value)
        if "id" in parent:
            object_id = parent["id"]
        if miscellaneous.namespace(object_id) == "minecraft:phantom":
            del parent["Size"]
        if miscellaneous.namespace(object_id) in ["minecraft:slime", "minecraft:magma_cube"]:
            del parent["size"]

def edge_case_skull_owner(nbt: dict | str):
    if isinstance(nbt, str):
        return {"name": nbt}

    if "Id" in nbt:
        nbt["id"] = nbt["Id"]
        del nbt["Id"]
    if "id" in nbt:
        nbt["id"] = miscellaneous.uuid_from_string(nbt["id"], pack_version, [])

    if "Name" in nbt:
        nbt["name"] = nbt["Name"]
        del nbt["Name"]

    if "Properties" in nbt:
        nbt["properties"] = TypeList([])
        if "textures" in nbt["Properties"]:
            for texture in nbt["Properties"]["textures"]:
                property = {"name": "textures"}
                if "Value" in texture:
                    property["value"] = texture["Value"]
                if "Signature" in texture:
                    property["signature"] = texture["Signature"]
                nbt["properties"].append(property) 
        del nbt["Properties"]

    return nbt

def edge_case_sleeping_pos(parent: dict[str, Any]):
    if "sleeping_pos" in parent:
        return
    parent["sleeping_pos"] = TypeIntArray([
        TypeInt(0),
        TypeInt(0),
        TypeInt(0),
    ])
    if "SleepingX" in parent:
        parent["sleeping_pos"][0] = TypeInt(parent["SleepingX"])
    if "SleepingY" in parent:
        parent["sleeping_pos"][1] = TypeInt(parent["SleepingY"])
    if "SleepingZ" in parent:
        parent["sleeping_pos"][2] = TypeInt(parent["SleepingZ"])

def edge_case_spawn_data(nbt: dict[str, Any], object_id: str, read: bool, issues: list[dict[str, str | int]]):
    # Move tags into "entity" if they aren't there already
    if "entity" not in nbt:
        entity = nbt.copy()
        for key in list(nbt.keys()):
            del nbt[key]
        nbt["entity"] = entity

    # Update entity data
    nbt["entity"] = get_source(nbt, nbt["entity"], "entity", object_id, read, issues)
    return nbt

def edge_case_spawn_potential_entity(parent: dict[str, Any], nbt: dict[str, Any], object_id: str, read: bool, issues: list[dict[str, str | int]]):
    if "data" not in parent:
        parent["data"] = {}
    parent["data"]["entity"] = get_source(parent["data"], parent["data"]["entity"], "entity", object_id, read, issues)

def edge_case_uuid_long(parent: dict, case: dict[str, str]):
    least_tag = case["least"]
    most_tag = case["most"]
    if least_tag in parent:
        least: int = parent[least_tag].value
        del parent[least_tag]
    else:
        least = 0
    if most_tag in parent:
        most: int = parent[most_tag].value
        del parent[most_tag]
    else:
        most = 0
    parent[case["output"]] = TypeIntArray([
        TypeInt(utils.int_range(most  // 4294967296)),
        TypeInt(utils.int_range(most  %  4294967296)),
        TypeInt(utils.int_range(least // 4294967296)),
        TypeInt(utils.int_range(least %  4294967296))
    ])
    






def convert_to_lib_format(nbt: dict | list | TypeList | TypeNumeric | str) -> NBT.TAG:
    if isinstance(nbt, dict):
        return convert_to_lib_format_compound(nbt)
    if isinstance(nbt, TypeList):
        return convert_to_lib_format_nbt_list(nbt)
    if isinstance(nbt, list):
        return convert_to_lib_format_list(nbt)
    if isinstance(nbt, TypeNumeric):
        return convert_to_lib_format_numeric(nbt)
    if isinstance(nbt, str):
        return convert_to_lib_format_string(nbt)
    log(f"ERROR: convert_to_lib_format: NBT type not determined: {nbt}")
    
def convert_to_lib_format_compound(nbt: dict[str, Any]) -> NBT.TAG_Compound:
    output_nbt = NBT.TAG_Compound()
    for key in nbt:
        output_nbt[key] = convert_to_lib_format(nbt[key])
    return output_nbt

def convert_to_lib_format_nbt_list(nbt: TypeList) -> Any:
    if isinstance(nbt, TypeByteArray):
        output = NBT.TAG_Byte_Array()
        output.value = cast(bytearray, [ int(nbt[i].value) for i in range(len(nbt)) ])
    elif isinstance(nbt, TypeIntArray):
        output = NBT.TAG_Int_Array()
        output.value = [ int(nbt[i].value) for i in range(len(nbt)) ]
    elif isinstance(nbt, TypeLongArray):
        output = NBT.TAG_Long_Array()
        output.value = [ int(nbt[i].value) for i in range(len(nbt)) ]
    else:
        data = [ convert_to_lib_format(nbt[i]) for i in range(len(nbt)) ]
        if data:
            # If there are multiple data types present, conform all entries to the standardized format
            data_type = type(data[0])
            for entry in data:
                if data_type == type(entry):
                    continue
                for i in range(len(data)):
                    if type(data[i]) == NBT.TAG_Compound:
                        continue
                    value = data[i]
                    data[i] = NBT.TAG_Compound()
                    cast(NBT.TAG_Compound, data[i])[""] = value
                break
            output = NBT.TAG_List(type(data[0]))
        else:
            output = NBT.TAG_List(NBT.TAG_Compound)
        output.tags = data
    return output

def convert_to_lib_format_list(nbt: list) -> Any:
    data = [ convert_to_lib_format(nbt[i]) for i in range(len(nbt)) ]
    if data:
        output = NBT.TAG_List(type(data[0]))
    else:
        output = NBT.TAG_List(NBT.TAG_Compound)
    output.tags = data
    return output

def convert_to_lib_format_numeric(nbt: TypeNumeric) -> Any:
    if isinstance(nbt, TypeByte):
        return NBT.TAG_Byte(int(nbt.value))
    if isinstance(nbt, TypeShort):
        return NBT.TAG_Short(int(nbt.value))
    if isinstance(nbt, TypeInt):
        return NBT.TAG_Int(int(nbt.value))
    if isinstance(nbt, TypeLong):
        return NBT.TAG_Long(int(nbt.value))
    if isinstance(nbt, TypeFloat):
        return NBT.TAG_Float(float(nbt.value))
    if isinstance(nbt, TypeDouble):
        return NBT.TAG_Double(float(nbt.value))
    log("ERROR: convert_to_lib_format_numeric: Numeric type not determined!")

def convert_to_lib_format_string(nbt: str) -> NBT.TAG_String:
    return NBT.TAG_String(nbt)



def convert_from_lib_format(nbt: NBT.TAG) -> Any:
    if isinstance(nbt, NBT.TAG_Compound):
        return convert_from_lib_format_compound(nbt)
    if isinstance(nbt, NBT.TAG_List):
        return convert_from_lib_format_list(nbt)
    if isinstance(nbt, NBT.TAG_Byte_Array):
        return convert_from_lib_format_byte_array(nbt)
    if isinstance(nbt, NBT.TAG_Int_Array):
        return convert_from_lib_format_int_array(nbt)
    if isinstance(nbt, NBT.TAG_Long_Array):
        return convert_from_lib_format_long_array(nbt)
    if isinstance(nbt, NBT._TAG_Numeric):
        return convert_from_lib_format_numeric(nbt)
    if isinstance(nbt, NBT.TAG_String):
        return convert_from_lib_format_string(nbt)
    log("ERROR: convert_from_lib_format: NBT type not determined!")
    
def convert_from_lib_format_compound(nbt: NBT.TAG_Compound) -> dict[str, Any]:
    output_nbt: dict = {}
    for key in nbt:
        output_nbt[key] = convert_from_lib_format(nbt[key])
    return output_nbt

def convert_from_lib_format_list(nbt: NBT.TAG_List) -> TypeList:
    return TypeList([ convert_from_lib_format(nbt[i]) for i in range(len(nbt)) ])

def convert_from_lib_format_byte_array(nbt: NBT.TAG_Byte_Array) -> TypeByteArray:
    return TypeByteArray([ TypeByte(nbt[i]) for i in range(len(nbt)) ])

def convert_from_lib_format_int_array(nbt: NBT.TAG_Int_Array) -> TypeIntArray:
    return TypeIntArray([ TypeInt(nbt[i]) for i in range(len(nbt)) ])

def convert_from_lib_format_long_array(nbt: NBT.TAG_Long_Array) -> TypeLongArray:
    return TypeLongArray([ TypeLong(nbt[i]) for i in range(len(nbt)) ])

def convert_from_lib_format_numeric(nbt: NBT._TAG_Numeric) -> TypeNumeric:
    if isinstance(nbt, NBT.TAG_Byte):
        return TypeByte(nbt.value)
    if isinstance(nbt, NBT.TAG_Short):
        return TypeShort(nbt.value)
    if isinstance(nbt, NBT.TAG_Int):
        return TypeInt(nbt.value)
    if isinstance(nbt, NBT.TAG_Long):
        return TypeLong(nbt.value)
    if isinstance(nbt, NBT.TAG_Float):
        return TypeFloat(nbt.value)
    if isinstance(nbt, NBT.TAG_Double):
        return TypeDouble(nbt.value)
    log("ERROR: convert_from_lib_format_numeric: Numeric type not determined!")
    return TypeInt(0)

def convert_from_lib_format_string(nbt: NBT.TAG_String) -> str:
    return nbt.value



def copy_lib_format(nbt: NBT.TAG) -> NBT.TAG:
    return convert_to_lib_format(convert_from_lib_format(nbt))



def convert_to_json(nbt: dict | TypeList | TypeNumeric | str):
    if isinstance(nbt, dict):
        return convert_to_json_compound(nbt)
    if isinstance(nbt, TypeList):
        return convert_to_json_list(nbt)
    if isinstance(nbt, TypeNumeric):
        return convert_to_json_numeric(nbt)
    if isinstance(nbt, str):
        return nbt
    log("ERROR: convert_to_json: NBT type not determined!")
    
def convert_to_json_compound(nbt: dict[str, Any]) -> dict[str, Any]:
    output_nbt = {}
    for key in nbt:
        output_nbt[key] = convert_to_json(nbt[key])
    return output_nbt

def convert_to_json_list(nbt: TypeList) -> list:
    if isinstance(nbt, TypeByteArray):
        return [ int(nbt[i].value) for i in range(len(nbt)) ]
    elif isinstance(nbt, TypeIntArray):
        return [ int(nbt[i].value) for i in range(len(nbt)) ]
    elif isinstance(nbt, TypeLongArray):
        return [ int(nbt[i].value) for i in range(len(nbt)) ]
    else:
        return [ convert_to_json(nbt[i]) for i in range(len(nbt)) ]

def convert_to_json_numeric(nbt: TypeNumeric) -> Any:
    if isinstance(nbt, TypeByte):
        return int(nbt.value)
    if isinstance(nbt, TypeShort):
        return int(nbt.value)
    if isinstance(nbt, TypeInt):
        return int(nbt.value)
    if isinstance(nbt, TypeLong):
        return int(nbt.value)
    if isinstance(nbt, TypeFloat):
        return float(nbt.value)
    if isinstance(nbt, TypeDouble):
        return float(nbt.value)
    if isinstance(nbt, TypeDecimal):
        return float(nbt.value)
    log("ERROR: convert_to_json_numeric: Numeric type not determined!")



def convert_from_json(nbt: dict | list | int | float | str | bool) -> Any:
    if isinstance(nbt, dict):
        return convert_from_json_compound(nbt)
    if isinstance(nbt, list):
        return convert_from_json_list(nbt)
    if isinstance(nbt, bool):
        return convert_from_json_bool(nbt)
    if isinstance(nbt, float):
        return convert_from_json_float(nbt)
    if isinstance(nbt, int):
        return convert_from_json_int(nbt)
    if isinstance(nbt, str):
        return convert_from_json_string(nbt)
    log("ERROR: convert_from_json: NBT type not determined!")
    
def convert_from_json_compound(nbt: dict) -> dict[str, Any]:
    output_nbt: dict = {}
    for key in nbt:
        output_nbt[key] = convert_from_json(nbt[key])
    return output_nbt

def convert_from_json_list(nbt: list) -> TypeList:
    return TypeList([ convert_from_json(nbt[i]) for i in range(len(nbt)) ])

def convert_from_json_bool(nbt: bool) -> TypeByte:
    if nbt:
        return TypeByte(1)
    return TypeByte(0)

def convert_from_json_int(nbt: int) -> TypeInt:
    return TypeInt(nbt)

def convert_from_json_float(nbt: float) -> TypeDecimal:
    return TypeDecimal(nbt)

def convert_from_json_string(nbt: str) -> str:
    return nbt



def merge_nbt(base: dict, addition: dict) -> dict:
    for key in addition:
        if key not in base:
            base[key] = addition[key]
        elif isinstance(base[key], dict) and isinstance(addition[key], dict):
            base[key] = merge_nbt(base[key], addition[key])
        else:
            base[key] = addition[key]
    return base



def uuid_from_int_array(uuid: list[int]) -> TypeIntArray:
    return TypeIntArray([TypeInt(uuid[i]) for i in range(3)])



def conform_lib_format_list(nbt: NBT.TAG_List):
    if len(nbt) == 0:
        return
    
    tag_type = nbt[0].id
    for tag in nbt:
        if tag_type != tag.id:
            nbt.tagID = NBT.TAG_COMPOUND
            for index in range(len(nbt)):
                if nbt[index].id != NBT.TAG_COMPOUND:
                    compound = NBT.TAG_Compound()
                    compound[""] = nbt[index]
                    nbt[index] = compound
            return
        
    nbt.tagID = nbt[0].id



def get_value(nbt, cast_type = None):
    if isinstance(nbt, TypeMacroToken):
        return nbt
    if cast_type:
        return cast_type(nbt.value)
    return nbt.value

def set_value(nbt, cast_type = None):
    if isinstance(nbt, TypeMacroToken):
        return nbt
    if cast_type:
        return cast_type(nbt)
    return nbt



def process_arbitrary_nbt(nbt, version: int | None = None):
    global pack_version
    if version is not None:
        pack_version = version

    if isinstance(nbt, dict):
        return process_arbitrary_nbt_compound(nbt)
    if isinstance(nbt, TypeList):
        return process_arbitrary_nbt_list(nbt)
    if isinstance(nbt, str):
        return process_arbitrary_nbt_string(nbt)
    return nbt
    
def process_arbitrary_nbt_compound(nbt: dict[str, Any]) -> dict[str, Any]:
    for key in nbt:
        nbt[key] = process_arbitrary_nbt(nbt[key])
    return nbt

def process_arbitrary_nbt_list(nbt: TypeList) -> TypeList:
    for i in range(len(nbt)):
        nbt[i] = process_arbitrary_nbt(nbt[i])
    return nbt

def process_arbitrary_nbt_string(nbt: str):
    if (
        option_manager.FIXES["json_text_components_in_storage"] and
        pack_version <= 2104 and
        (nbt.startswith("{") or nbt.startswith("[") or nbt.startswith('"'))
    ):
        return json_text_component.direct_update(convert_from_json(json_manager.unpack(nbt)), pack_version, [], False)

    return nbt