# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from typing import cast, TypedDict, NotRequired, Any
from lib.log import log
from lib.data_pack_files import arguments
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import nbt_to_json
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import entities
from lib.data_pack_files import numeric_ids
from lib.data_pack_files import tables
from lib.data_pack_files import item_component
from lib.data_pack_files.restore_behavior import tag_replacements
from lib import defaults
from lib import option_manager
import easy_map_updater



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

class ItemInputFromCommand(TypedDict):
    id: str
    nbt: NotRequired[str]
    data_value: str
    read: NotRequired[bool]

class ItemOutputFromCommand(TypedDict):
    id: str
    components: item_component.ItemComponents

def update_from_command_read(item: str | ItemInputFromCommand, version: int, issues: list[dict[str, str | int]]) -> str:
    if isinstance(item, dict):
        item["read"] = True
    else:
        item = cast(ItemInputFromCommand, {
            "id": item,
            "read": True,
        })
    return update_from_command(item, version, issues)

def update_from_command(item: str | ItemInputFromCommand, version: int, issues: list[dict[str, str | int]]) -> str:
    # Assign version
    global pack_version
    pack_version = version

    # Initialize parameters
    item_id = "minecraft:air"
    components = ""
    data_value = -1
    nbt = ""
    read = False

    # Extract arguments if a dict
    if isinstance(item, dict):
        if "id" in item:
            item_id = item["id"]
        if "nbt" in item:
            nbt = item["nbt"]
        if "data_value" in item:
            if item["data_value"] != "":
                data_value = int(item["data_value"])
        if "read" in item:
            read = item["read"]
    else:
        item_id = item

    # Assign NBT if present in ID
    if "{" in item_id:
        tokens = arguments.parse(item_id, "", True)
        if tokens[-1][0] == "{":
            nbt = item_id[-len(tokens[-1]):]
            item_id = item_id[:-len(tokens[-1])]

    # Assign components if present in ID
    if "[" in item_id:
        components = item_id[item_id.find("["):]
        item_id = item_id[:item_id.find("[")]

    # Remove iconcrack
    if "iconcrack_" in item_id and item_id[:10] == "iconcrack_":
        item_id = item_id[10:]

    # Update item
    new_item = cast(ItemOutputFromCommand, update(
        {
            "id": item_id,
            "components": item_component.ItemComponents.unpack(components),
            "data_value": data_value,
            "nbt": nbt_tags.unpack(nbt),
            "read": read
        },
        pack_version, issues
    ))

    # Return item
    if new_item["components"].has_components():
        return new_item["id"] + new_item["components"].pack()
    return new_item["id"]



class ItemInputFromNBT(TypedDict):
    id: str | nbt_tags.TypeNumeric
    components: dict
    tag: dict
    Damage: nbt_tags.TypeNumeric
    Count: nbt_tags.TypeNumeric
    count: nbt_tags.TypeNumeric
    Slot: nbt_tags.TypeNumeric

def update_from_nbt(item: ItemInputFromNBT, version: int, issues: list[dict[str, str | int]]) -> dict[str, Any]:
    # Assign version
    global pack_version
    pack_version = version

    # Initialize parameters
    item_id = None
    components = None
    data_value = -1
    nbt = None
    count = -1
    slot = None
    read = False

    # Extract arguments
    if "id" in item:
        item_id = item["id"]
    if "components" in item:
        components = item["components"]
    if "Damage" in item:
        data_value = int(item["Damage"].value)
    if "tag" in item:
        nbt = item["tag"]
    if "Count" in item:
        count = int(item["Count"].value)
    if "count" in item:
        count = int(item["count"].value)
    if "Slot" in item:
        slot = int(item["Slot"].value)

    # Update item
    new_item = update(
        {
            "id": item_id,
            "components": item_component.ItemComponents.unpack_from_dict(components, read),
            "data_value": data_value,
            "nbt": nbt,
            "read": read
        },
        pack_version, issues
    )

    # Return item
    export_item: dict[str, Any] = {}
    if "id" in new_item and new_item["id"] != None:
        export_item["id"] = new_item["id"]
    if new_item["components"].has_components():
        export_item["components"] = new_item["components"].pack_to_dict()
    if count >= 0:
        export_item["count"] = nbt_tags.TypeInt(count)
    if slot != None:
        export_item["Slot"] = nbt_tags.TypeByte(slot)
    
    return export_item



class ItemInputFromJSON(TypedDict):
    id: str
    components: NotRequired[dict | None]
    nbt: NotRequired[str | None]

def update_from_json(item: ItemInputFromJSON, version: int, issues: list[dict[str, str | int]]) -> dict[str, Any]:
    # Assign version
    global pack_version
    pack_version = version

    # Initialize parameters
    item_id = None
    components = None
    nbt = None

    # Extract arguments
    if "id" in item:
        item_id = item["id"]
    if "components" in item:
        components = item["components"]
    if "nbt" in item:
        nbt = item["nbt"]

    # Update item
    new_item = update(
        {
            "id": item_id,
            "components": item_component.ItemComponents.unpack_from_dict(nbt_tags.convert_from_json(components) if components else None, False),
            "data_value": -1,
            "nbt": nbt_tags.unpack(nbt) if nbt else None,
            "read": False
        },
        pack_version, issues
    )

    return {
        "id": new_item["id"],
        "components": nbt_to_json.convert_item_components_to_json(new_item["components"].pack_to_dict()) if new_item["components"].has_components() else None,
    }



class ItemInput(TypedDict):
    id: str | nbt_tags.TypeNumeric | None
    data_value: int
    components: item_component.ItemComponents
    nbt: dict | None
    read: bool

class ItemOutput(TypedDict):
    id: str | None
    components: item_component.ItemComponents

def update(item: ItemInput, version: int, issues: list[dict[str, str | int]]) -> ItemOutput:
    # Assign version
    global pack_version
    pack_version = version

    # Extract arguments
    item_id = item["id"]
    components = item["components"]
    data_value = item["data_value"]
    nbt = item["nbt"]
    read = item["read"]

    # Convert item ID
    if item_id != None:
        item_id = update_item_id(item_id, components, data_value, nbt, read, issues)

    # Modify item ID if a spawn egg and the "Riding" tag is present
    old_item_id = item_id
    if item_id != None and item_id.endswith("_spawn_egg") and nbt != None and "EntityTag" in nbt and "Riding" in nbt["EntityTag"]:
        item_id = entities.update(extract_riding_id(nbt["EntityTag"]["Riding"]), pack_version, issues) + "_spawn_egg"

    # Update NBT
    if nbt:
        components = item_component.ItemComponents.unpack_from_dict(nbt_tags.direct_update(nbt, pack_version, issues, "item_tag", old_item_id or "minecraft:stone"), read)

    # Conform component format
    components = item_component.conform_components(components, version, issues)

    # Apply damage to items with durability
    if item_id in tables.ITEMS_WITH_DURABILITY and (data_value >= 1 or (data_value == 0 and read)):
        components["minecraft:damage"] = nbt_tags.TypeInt(data_value)

    # Apply pre-1.8 adventure mode fixes
    if pack_version <= 710 and defaults.FIXES["old_adventure_mode_items"] and not read:
        components = insert_old_adventure_mode_tags(components, item_id or "minecraft:stone")

    return {
        "id": item_id,
        "components": components
    }



def update_item_id(item_id: str | nbt_tags.TypeNumeric, components: item_component.ItemComponents | None, data_value: int, nbt: dict | None, read: bool, issues: list[dict[str, str | int]]) -> str:
    # Convert if a numeric
    if not isinstance(item_id, str):
        item_id, data_value = cast(tuple[str, int], numeric_ids.update_block_item(int(item_id.value), data_value))
    elif item_id.isnumeric():
        item_id, data_value = cast(tuple[str, int], numeric_ids.update_block_item(int(item_id), data_value))

    # Return if an asterisk
    if item_id == "*":
        return item_id

    # Apply namespace to name
    item_id = miscellaneous.namespace(item_id)

    # Convert item ID
    if pack_version <= 1202:
        if read and data_value == -1:
            id_array = tables.ITEM_IDS_READ
            if item_id in id_array:
                item_id = id_array[item_id]

            if "#tag_replacements" in item_id:
                tag_replacements.create_pack(
                    easy_map_updater.MINECRAFT_PATH / "saves" / option_manager.get_map_name()
                )
        else:
            id_array = tables.ITEM_IDS_DATA

            if item_id == "minecraft:spawn_egg":
                if pack_version >= 900:
                    if nbt != None and "EntityTag" in nbt and "id" in nbt["EntityTag"]:
                        item_id = entities.update(nbt["EntityTag"]["id"], pack_version, issues) + "_spawn_egg"
                    else:
                        item_id = "minecraft:pig_spawn_egg"
                else:
                    if data_value == -1:
                        item_id = "minecraft:pig_spawn_egg"
                    else:
                        item_id = entities.update(numeric_ids.update_entity(data_value), pack_version, issues) + "_spawn_egg"

            elif item_id in id_array:
                data_array = id_array[item_id]
                if len(data_array) <= data_value:
                    item_id = data_array[0]
                else:
                    item_id = data_array[max(data_value, 0)]

    if pack_version <= 1302 or defaults.FIXES["post_fixes"]:
        id_array = {
            "minecraft:cactus_green":     "minecraft:green_dye",
            "minecraft:dandelion_yellow": "minecraft:yellow_dye",
            "minecraft:rose_red":         "minecraft:red_dye",
            "minecraft:sign":             "minecraft:oak_sign"
        }
        if item_id in id_array:
            item_id = id_array[item_id]

    if pack_version <= 1502 or defaults.FIXES["post_fixes"]:
        id_array = {
            "minecraft:zombie_pigman_spawn_egg": "minecraft:zombified_piglin_spawn_egg"
        }
        if item_id in id_array:
            item_id = id_array[item_id]

    if pack_version <= 2002 or defaults.FIXES["post_fixes"]:
        id_array = {
            "minecraft:grass": "minecraft:short_grass"
        }
        if item_id in id_array:
            item_id = id_array[item_id]

    if pack_version <= 2004 or defaults.FIXES["post_fixes"]:
        id_array = {
            "minecraft:scute": "minecraft:turtle_scute"
        }
        if item_id in id_array:
            item_id = id_array[item_id]
        if item_id == "#minecraft:tools":
            item_id = "#tag_replacements:tools"
            tag_replacements.create_pack(
                easy_map_updater.MINECRAFT_PATH / "saves" / option_manager.get_map_name()
            )

    if pack_version <= 2006 or defaults.FIXES["post_fixes"]:
        if item_id == "#minecraft:music_discs":
            item_id = "#tag_replacements:music_discs"
            tag_replacements.create_pack(
                easy_map_updater.MINECRAFT_PATH / "saves" / option_manager.get_map_name()
            )

    return item_id

def extract_riding_id(nbt: dict) -> str:
    if "Riding" in nbt:
        return extract_riding_id(nbt["Riding"])
    elif "id" in nbt:
        return nbt["id"]
    else:
        return "minecraft:pig"
    


def insert_old_adventure_mode_tags(components: item_component.ItemComponents, item_id: str) -> item_component.ItemComponents:
    if "minecraft:custom_data" not in components:
        components["minecraft:custom_data"] = {}
    components["minecraft:custom_data"]["adventure"] = nbt_tags.TypeByte(1)

    can_place_on = nbt_tags.TypeList([])
    can_break = nbt_tags.TypeList([])
    
    if item_id in tables.BLOCK_PLACEABLE:
        can_place_on = nbt_tags.TypeList([{"blocks": "#adventure:all"}])
        can_break = nbt_tags.TypeList([{"blocks": "#adventure:mineable/universal"}])

    elif item_id.endswith("_pickaxe"):
        can_break = nbt_tags.TypeList([{"blocks": "#minecraft:mineable/pickaxe"}, {"blocks": "#adventure:mineable/universal"}])

    elif item_id.endswith("_shovel"):
        can_break = nbt_tags.TypeList([{"blocks": "#minecraft:mineable/shovel"}, {"blocks": "#adventure:mineable/universal"}])

    elif item_id.endswith("_axe"):
        can_break = nbt_tags.TypeList([{"blocks": "#minecraft:mineable/axe"}, {"blocks": "#adventure:mineable/universal"}])

    elif item_id.endswith("_hoe"):
        can_break = nbt_tags.TypeList([{"blocks": "#minecraft:mineable/hoe"}, {"blocks": "#adventure:mineable/universal"}])

    elif item_id.endswith("_sword"):
        can_break = nbt_tags.TypeList([{"blocks": "#adventure:mineable/sword"}, {"blocks": "#adventure:mineable/universal"}])

    elif item_id == "minecraft:shears":
        can_break = nbt_tags.TypeList([{"blocks": "#adventure:mineable/shears"}, {"blocks": "#adventure:mineable/universal"}])

    else:
        can_break = nbt_tags.TypeList([{"blocks": "#adventure:mineable/universal"}])

    if len(can_place_on):
        components["minecraft:can_place_on"] = {"predicates": can_place_on, "show_in_tooltip": nbt_tags.TypeByte(0)}
    if len(can_break):
        components["minecraft:can_break"] = {"predicates": can_break, "show_in_tooltip": nbt_tags.TypeByte(0)}

    return components