# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from nbt import nbt as NBT
from pathlib import Path
from lib.log import log
from lib.data_pack_files import tables
from lib import defaults
from lib import utils



# Initialize variables

pack_version = defaults.PACK_VERSION

PROGRAM_PATH = Path(__file__).parent
with (PROGRAM_PATH / "nbt_tree.json").open("r", encoding="utf-8") as file:
    NBT_TREE: dict[str, dict[str, str]] = json.load(file)



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
        if num_type == "int":
            return int(value)
        return float(value)

class TypeByte(TypeNumeric):
    def __init__(self, value):
        TypeNumeric.__init__(self, value, "int")
        self.suffix = "b"

class TypeShort(TypeNumeric):
    def __init__(self, value):
        TypeNumeric.__init__(self, value, "int")
        self.suffix = "s"

class TypeInt(TypeNumeric):
    def __init__(self, value):
        TypeNumeric.__init__(self, value, "int")

class TypeLong(TypeNumeric):
    def __init__(self, value):
        TypeNumeric.__init__(self, value, "int")
        self.suffix = "L"

class TypeFloat(TypeNumeric):
    def __init__(self, value):
        TypeNumeric.__init__(self, value, "float")
        self.suffix = "f"

class TypeDouble(TypeNumeric):
    def __init__(self, value):
        TypeNumeric.__init__(self, value, "float")
        self.suffix = "d"

class TypeDecimal(TypeNumeric):
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



# Import more stuff to prevent circular loading issues

from lib.data_pack_files import command
from lib.data_pack_files import arguments
from lib.data_pack_files import items
from lib.data_pack_files import blocks
from lib.data_pack_files import entities
from lib.data_pack_files import json_text_component
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import ids



# Define functions

def update(nbt: str | dict[str, str], version: int, issues: list[dict[str, str]], source: str) -> str:
    global pack_version
    pack_version = version

    object_id = ""

    # Extract arguments if a dict
    if isinstance(nbt, dict):
        if "object_id" in nbt:
            object_id: str = nbt["object_id"]
        nbt: str = nbt["nbt"]

    # Return if not SNBT
    if nbt == "":
        return nbt
    if nbt[0] != "{":
        return nbt

    nbt: dict = unpack(nbt)
    return pack(get_source({}, nbt, source, object_id, issues))

def direct_update(nbt: dict | None, version: int, issues: list[dict[str, str]], source: str, object_id: str) -> dict | None:
    global pack_version
    pack_version = version

    if not isinstance(nbt, dict):
        return
    
    return get_source({}, nbt, source, object_id, issues)

def update_with_guide(nbt: str, version: int, issues: list[dict[str, str]], source: str, guide: dict, callback: str) -> str:
    global pack_version
    pack_version = version

    # Return if not SNBT
    if not nbt:
        return nbt
    
    if defaults.DEBUG_MODE:
        log(f'CALLBACK: {callback} - GUIDE: {guide}')

    nbt: dict = unpack(nbt)
    match callback:
        case "branch":
            return pack(branch({}, nbt, guide, source, "", issues))
        case "tags":
            if "necessary_tags" in guide:
                return update_tags({}, nbt, guide, source, "", guide["necessary_tags"], issues)
            return pack(update_tags({}, nbt, guide, source, "", {}, issues))
        case "list":
            return pack(update_list({}, nbt, guide, source, "", issues))
    




def unpack(nbt: str):
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
        if "." in nbt:
            return TypeDecimal(nbt)
        return TypeInt(nbt)
    if len(nbt) > 1 and utils.is_num(nbt[:-1]):
        if nbt[-1] in ["b", "B"]:
            return TypeByte(nbt[:-1])
        if nbt[-1] in ["s", "S"]:
            return TypeShort(nbt[:-1])
        if nbt[-1] in ["l", "L"]:
            return TypeLong(nbt[:-1])
        if nbt[-1] in ["f", "F"]:
            return TypeFloat(nbt[:-1])
        if nbt[-1] in ["d", "D"]:
            return TypeDouble(nbt[:-1])
    
    if nbt == "true":
        return TypeByte(1)
    if nbt == "false":
        return TypeByte(0)

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

def pack_compound(nbt: dict[str]) -> str:
    # Prepare tag list
    tags: list[str] = []

    # Iterate through keys
    for key in nbt:
        pack_bool = ":" in key or '"' in key or "'" in key
        tags.append(f'{utils.pack_string(key) if pack_bool else key}:{pack(nbt[key])}')
    
    # Return stringified version of compound
    return "{" + ",".join(tags) + "}"

def pack_list(nbt: list) -> str:
    out_list = []
    for entry in nbt:
        out_list.append(pack(entry))
    return f'[{",".join(out_list)}]'



def get_source(parent: dict, nbt: dict, source: str, object_id: str, issues: list[dict[str, str]]) -> dict:
    # Get guide
    if source not in NBT_TREE["sources"]:
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Source "{source}" is not registered!')
        return nbt
    return branch(parent, nbt, NBT_TREE["sources"][source], source, object_id, issues)

def branch(parent: dict, nbt, guide: dict, source: str, object_id: str, issues: list[dict[str, str]]) -> dict:
    # Return function based on contents of guide
    if "edge_case" in guide:
        return edge_case(parent, nbt, guide["edge_case"], source, object_id, issues)
    if "source" in guide:
        return get_source(parent, nbt, guide["source"], object_id, issues)
    if "tags" in guide:
        if "necessary_tags" in guide:
            return update_tags(parent, nbt, guide["tags"], source, object_id, guide["necessary_tags"], issues)
        return update_tags(parent, nbt, guide["tags"], source, object_id, {}, issues)
    if "list" in guide:
        return update_list(parent, nbt, guide["list"], source, object_id, issues)
    if "data_type" in guide:
        return update_data(parent, nbt, guide, source, object_id, issues)
    return nbt

def update_tags(parent: dict, nbt: dict, guide: dict, source: str, object_id: str, necessary_tags: dict, issues: list[dict[str, str]]) -> dict:
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
        if source in ["block", "entity"] and key == "CommandStats" and not defaults.FIXES["stats"]:
            log("WARNING: Stats fixer not enabled but stats have been found!")
        if key in guide and key in nbt:
            if "rename" in guide[key]:
                nbt[guide[key]["rename"]] = branch(nbt, nbt[key], guide[key], source, object_id, issues)
                if key in nbt:
                    del nbt[key]
            elif "remove" in guide[key] and guide[key]["remove"]:
                branch(nbt, nbt[key], guide[key], source, object_id, issues)
                if key in nbt:
                    del nbt[key]
            else:
                value = branch(nbt, nbt[key], guide[key], source, object_id, issues)
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
                    if condition not in nbt:
                        skip = True
                        break
                    value = nbt[condition]
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

            if generator == "item_entity":
                nbt[key] = {"id": "minecraft:stone", "Count": TypeByte(1)}
            if generator == "uuid":
                nbt[key] = miscellaneous.new_uuid_int_array()

    return nbt

def update_list(parent: dict, nbt: TypeList, guide: dict, source: str, object_id: str, issues: list[dict[str, str]]) -> TypeList:
    if not isinstance(nbt, TypeList):
        return nbt

    # Iterate through elements
    for i in range(len(nbt.value)):
        nbt[i] = branch(parent, nbt[i], guide, source, object_id, issues)
    return nbt

def update_data(parent: dict, nbt, guide: dict, source: str, object: str, issues: list[dict[str, str]]) -> str:
    # Get types
    data_type: str = guide["data_type"]
    output_data_type = data_type
    if "output_data_type" in guide:
        output_data_type = guide["output_data_type"]
    argument_type = "carry"
    if "argument_type" in guide:
        argument_type: str = guide["argument_type"]

    # Convert numeric types
    nbt = apply_data_type(nbt, data_type)

    # Put together parameters
    if "parameters" in guide:
        parameters = {}
        for key in guide["parameters"]:
            obj = retrieve(parent, guide["parameters"][key])
            if obj != None:
                parameters[key] = obj
        return apply_data_type(command.update_argument(parameters, argument_type), output_data_type)

    # Convert based on argument type
    return apply_data_type(command.update_argument(nbt, argument_type, issues), output_data_type)

def apply_data_type(nbt, data_type: str):
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
    return nbt

def invert_riding(nbt: dict) -> dict:
    output_nbt = nbt["Riding"]
    del nbt["Riding"]
    output_nbt["Passengers"] = TypeList([nbt])
    if "Riding" in output_nbt:
        output_nbt = invert_riding(output_nbt)
    return output_nbt



def edge_case(parent: dict, nbt, case: str | dict[str, str], source: str, object_id: str, issues: list[dict[str, str]]):
    # Get case
    if isinstance(case, dict):
        case_type: str = case["case"]
    else:
        case_type = case

    # Process NBT based on case
    if case_type == "banner_base":
        return edge_case_banner_base(parent, object_id, issues)
    if case_type == "block_entity":
        return blocks.update_from_nbt(parent, pack_version, issues)
    if case_type == "can_place_on":
        return edge_case_can_place_on(nbt, issues)
    if case_type == "entity_id":
        return edge_case_entity_id(parent, nbt, object_id, issues)
    if case_type == "equipment":
        return edge_case_equipment(parent, nbt, object_id, issues)
    if case_type == "fuse":
        return edge_case_fuse(parent, object_id)
    if case_type == "item":
        return items.update_from_nbt(nbt, pack_version, issues)
    if case_type == "mooshroom_stew":
        return edge_case_mooshroom_stew(parent, pack_version, issues)
    if case_type == "old_spawn_potential_entity":
        return edge_case_old_spawn_potential_entity(parent, nbt, object_id, issues)
    if case_type == "sign_text":
        return edge_case_sign_text(parent, issues)
    if case_type == "spawn_data":
        return edge_case_spawn_data(nbt, object_id, issues)
    if case_type == "spawn_potential_entity":
        return edge_case_spawn_potential_entity(parent, nbt, object_id, issues)
    if case_type == "uuid_long":
        return edge_case_uuid_long(parent, case)

    if defaults.SEND_WARNINGS:
        log(f'WARNING: "{case_type}" case is not registered!')
    return nbt

def edge_case_banner_base(parent: dict[str, TypeInt], object_id: str, issues: list[dict[str, str]]):
    if miscellaneous.namespace(object_id) == "minecraft:shield":
        parent["Base"] = miscellaneous.banner_color(parent["Base"], pack_version, issues)
    else:
        del parent["Base"]

def edge_case_can_place_on(nbt: list[str], issues: list[dict[str, str]]):
    new_list: list[str] = []
    for block in nbt:
        new_block = blocks.update(
            {
                "id": block,
                "data_value": -1,
                "block_states": {},
                "nbt": {},
                "read": True
            },
            pack_version, issues
        )["id"]
        new_list.append(new_block)
    return TypeList(utils.deduplicate_list(new_list))

def edge_case_entity_id(parent: dict, nbt: str, object_id: str, issues: list[dict[str, str]]):
    if "SpawnData" in parent:
        parent["SpawnData"] = edge_case_spawn_data(parent["SpawnData"], object_id)
    else:
        parent["SpawnData"] = {}
    if "entity" not in parent["SpawnData"]:
        parent["SpawnData"]["entity"] = {}
    parent["SpawnData"]["entity"]["id"] = entities.update(nbt, pack_version, issues)

def edge_case_equipment(parent: dict, nbt: TypeList, object_id: str, issues: list[dict[str, str]]):
    parent["ArmorItems"] = TypeList([{},{},{},{}])
    parent["HandItems"] = TypeList([{},{}])
    length = len(nbt)
    if length >= 5:
        parent["ArmorItems"][3] = get_source(parent, nbt[4], "item", object_id, issues)
    if length >= 4:
        parent["ArmorItems"][2] = get_source(parent, nbt[3], "item", object_id, issues)
    if length >= 3:
        parent["ArmorItems"][1] = get_source(parent, nbt[2], "item", object_id, issues)
    if length >= 2:
        parent["ArmorItems"][0] = get_source(parent, nbt[1], "item", object_id, issues)
    if length >= 1:
        parent["HandItems"][0]  = get_source(parent, nbt[0], "item", object_id, issues)

    # Fix false item rendering in 1.8
    index: tuple[int, str]
    for index in [(0, "boots"), (1, "leggings"), (2, "chestplate"), (3, "helmet")]:
        i: int = index[0]
        armor: str = index[1]
        if "id" in parent["ArmorItems"][i]:
            if "Count" not in parent["ArmorItems"][i]:
                parent["ArmorItems"][i]["Count"] = TypeByte(1)
            item_id: str = parent["ArmorItems"][i]["id"]
            for armor_test in ["boots", "leggings", "chestplate", "helmet"]:
                if len(item_id) < len(armor_test):
                    continue
                if item_id[-len(armor_test):] == armor_test:
                    parent["ArmorItems"][i]["id"] = item_id[:-len(armor_test)] + armor
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
        object_id = miscellaneous.namespace(object_id)
        if object_id == "minecraft:tnt":
            del parent["Fuse"]
        if object_id == "minecraft:creeper":
            del parent["fuse"]

def edge_case_mooshroom_stew(parent: dict, pack_version: int, issues: list[dict[str, str]]):
    parent["stew_effects"] = TypeList([{}])
    if "EffectId" in parent:
        parent["stew_effects"][0]["id"] = ids.effect(parent["EffectId"], pack_version, issues)
        del parent["EffectId"]
    if "EffectDuration" in parent:
        parent["stew_effects"][0]["duration"] = parent["EffectDuration"]
        del parent["EffectDuration"]

def edge_case_old_spawn_potential_entity(parent: dict[str], nbt: dict[str], object_id: str, issues: list[dict[str, str]]):
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
    parent["data"]["entity"] = get_source(parent["data"], parent["data"]["entity"], "entity", object_id, issues)

def edge_case_sign_text(parent: dict, issues: list[dict[str, str]]):
    # Prepare front text
    if "front_text" not in parent:
        parent["front_text"] = {}

    for i in range(4):
        key = f"Text{i+1}"
        if key in parent:
            if "messages" not in parent["front_text"]:
                parent["front_text"]["messages"] = ['""', '""', '""', '""']
            parent["front_text"]["messages"][i] = json_text_component.update(parent[key], pack_version, issues, False)
            del parent[key]
    if "Color" in parent:
        parent["front_text"]["color"] = parent["Color"]
        del parent["Color"]
    if "GlowingText" in parent:
        parent["front_text"]["has_glowing_text"] = parent["GlowingText"]
        del parent["GlowingText"]

def edge_case_spawn_data(nbt: dict[str], object_id: str, issues: list[dict[str, str]]):
    # Move tags into "entity" if they aren't there already
    if "entity" not in nbt:
        entity = nbt.copy()
        for key in list(nbt.keys()):
            del nbt[key]
        nbt["entity"] = entity

    # Update entity data
    nbt["entity"] = get_source(nbt, nbt["entity"], "entity", object_id, issues)
    return nbt

def edge_case_spawn_potential_entity(parent: dict[str], nbt: dict[str], object_id: str, issues: list[dict[str, str]]):
    if "data" not in parent:
        parent["data"] = {}
    parent["data"]["entity"] = get_source(parent["data"], parent["data"]["entity"], "entity", object_id, issues)

def edge_case_uuid_long(parent: dict, case: dict[str, str]):
    least_tag = case["least"]
    most_tag = case["most"]
    if least_tag in parent:
        least: int = parent[least_tag].value
        del parent[least_tag]
    if most_tag in parent:
        most: int = parent[most_tag].value
        del parent[most_tag]
    parent[case["output"]] = TypeIntArray([
        TypeInt(utils.int_range(most  // 4294967296)),
        TypeInt(utils.int_range(most  %  4294967296)),
        TypeInt(utils.int_range(least // 4294967296)),
        TypeInt(utils.int_range(least %  4294967296))
    ])


def retrieve(nbt, address: str):
    # Return current object if address is blank
    if address == "":
        return nbt
    
    # Return object based on index
    if "." not in address and "[" not in address:
        if address in nbt:
            return nbt[address]
        return
    if address[0] == "[":
        i = int(address[1:address.find("]")])
        if i < len(nbt.value):
            return retrieve(nbt[i], address[address.find("]") + 1:])
        return
    i = address[:address.find(".")]
    if i in nbt:
        return retrieve(nbt[i], address[address.find(".") + 1:])
    






def convert_to_lib_format(nbt: dict[str] | TypeList | TypeNumeric | str) -> NBT.TAG:
    if isinstance(nbt, dict):
        return convert_to_lib_format_compound(nbt)
    if isinstance(nbt, TypeList):
        return convert_to_lib_format_list(nbt)
    if isinstance(nbt, TypeNumeric):
        return convert_to_lib_format_numeric(nbt)
    if isinstance(nbt, str):
        return convert_to_lib_format_string(nbt)
    log("ERROR: convert_to_lib_format: NBT type not determined!")
    
def convert_to_lib_format_compound(nbt: dict[str]) -> NBT.TAG_Compound:
    output_nbt = NBT.TAG_Compound()
    for key in nbt:
        output_nbt[key] = convert_to_lib_format(nbt[key])
    return output_nbt

def convert_to_lib_format_list(nbt: TypeList):
    if isinstance(nbt, TypeByteArray):
        output = NBT.TAG_Byte_Array()
        output.value = [ int(nbt[i].value) for i in range(len(nbt)) ]
    elif isinstance(nbt, TypeIntArray):
        output = NBT.TAG_Int_Array()
        output.value = [ int(nbt[i].value) for i in range(len(nbt)) ]
    elif isinstance(nbt, TypeLongArray):
        output = NBT.TAG_Long_Array()
        output.value = [ int(nbt[i].value) for i in range(len(nbt)) ]
    else:
        data = [ convert_to_lib_format(nbt[i]) for i in range(len(nbt)) ]
        if data:
            output = NBT.TAG_List(type(data[0]))
        else:
            output = NBT.TAG_List(NBT.TAG_Compound)
        output.tags = data
    return output

def convert_to_lib_format_numeric(nbt: TypeNumeric):
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



def convert_from_lib_format(nbt: NBT.TAG):
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
    
def convert_from_lib_format_compound(nbt: NBT.TAG_Compound) -> dict[str]:
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

def convert_from_lib_format_string(nbt: NBT.TAG_String) -> str:
    return nbt.value