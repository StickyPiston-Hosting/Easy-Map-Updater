# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from lib.log import log
from lib.data_pack_files import arguments
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import entities
from lib.data_pack_files import numeric_ids
from lib.data_pack_files import tables
from lib.data_pack_files import item_component
from lib import defaults



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def update_from_command(item: str | dict[str, str], version: int, issues: list[dict[str, str]]) -> str:
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
            item_id: str = item["id"]
        if "nbt" in item:
            nbt: str = item["nbt"]
        if "data_value" in item:
            if item["data_value"] != "":
                data_value = int(item["data_value"])
        if "read" in item:
            read: bool = item["read"]
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
    new_item: dict[str, str | int | dict | bool | None] = update(
        {
            "id": item_id,
            "components": item_component.unpack(components),
            "data_value": data_value,
            "nbt": nbt_tags.unpack(nbt),
            "read": read
        },
        pack_version, issues
    )

    # Return item
    if new_item["components"]:
        return new_item["id"] + item_component.pack(new_item["components"])
    return new_item["id"]



def update_from_nbt(item: dict[str, str | dict | nbt_tags.TypeNumeric], version: int, issues: list[dict[str, str]]) -> dict[str, str | int | dict]:
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
        item_id: str | nbt_tags.TypeNumeric = item["id"]
    if "components" in item:
        components: dict = item["components"]
    if "Damage" in item:
        data_value = int(item["Damage"].value)
    if "tag" in item:
        nbt: dict = item["tag"]
    if "count" in item:
        count = int(item["count"].value)
    if "Count" in item:
        count = int(item["Count"].value)
    if "Slot" in item:
        slot = int(item["Slot"].value)

    # Update item
    new_item: dict[str, str | int | dict] = update(
        {
            "id": item_id,
            "components": components,
            "data_value": data_value,
            "nbt": nbt,
            "read": read
        },
        pack_version, issues
    )

    # Return item
    export_item: dict[str, str | int | dict] = {}
    if "id" in new_item and new_item["id"] != None:
        export_item["id"] = new_item["id"]
    if "components" in new_item and new_item["components"] != None:
        export_item["components"] = new_item["components"]
    if count >= 0:
        export_item["count"] = nbt_tags.TypeInt(count)
    if slot != None:
        export_item["Slot"] = nbt_tags.TypeByte(slot)
    
    return export_item



def update(item: dict[str, str | int | dict | bool | None], version: int, issues: list[dict[str, str]]) -> str:
    # Assign version
    global pack_version
    pack_version = version

    # Extract arguments
    item_id: str | nbt_tags.TypeNumeric | None = item["id"]
    components: dict | None = item["components"]
    data_value: int = item["data_value"]
    nbt: dict | None = item["nbt"]
    read: bool = item["read"]

    # Convert item ID
    if item_id != None:
        item_id = update_item_id(item_id, components, data_value, nbt, read, issues)

    # Modify item ID if a spawn egg and the "Riding" tag is present
    old_item_id = item_id
    if item_id != None and item_id.endswith("_spawn_egg") and nbt != None and "EntityTag" in nbt and "Riding" in nbt["EntityTag"]:
        item_id = entities.update(extract_riding_id(nbt["EntityTag"]["Riding"]), pack_version, issues) + "_spawn_egg"

    # Update NBT
    nbt = nbt_tags.direct_update(nbt, pack_version, issues, "item_tag", old_item_id)

    # Conform component format
    if components:
        components = item_component.conform(components)

    # Extract components out of NBT
    if nbt:
        components = item_component.extract(item_id, components, nbt, version)

    # Apply damage to items with durability
    if item_id in tables.ITEMS_WITH_DURABILITY and (data_value >= 1 or (data_value == 0 and read)):
        if components == None or components == "":
            components = {}
        components["minecraft:damage"] = nbt_tags.TypeInt(data_value)

    # Apply pre-1.8 adventure mode fixes
    if pack_version <= 710 and defaults.FIXES["old_adventure_mode_items"] and not read:
        nbt = insert_old_adventure_mode_tags(nbt, item_id)

    return {
        "id": item_id,
        "components": components
    }



def update_item_id(item_id: str | nbt_tags.TypeNumeric, components: dict, data_value: int, nbt: dict, read: bool, issues: list[dict[str, str]]) -> str:
    # Convert if a numeric
    if not isinstance(item_id, str):
        item_id, data_value = numeric_ids.update_block_item(int(item_id.value), data_value)
    elif item_id.isnumeric():
        item_id, data_value = numeric_ids.update_block_item(int(item_id), data_value)

    # Apply namespace to name
    item_id = miscellaneous.namespace(item_id)

    # Convert item ID
    if pack_version <= 1202:
        if read and data_value == -1:
            id_array = tables.ITEM_IDS_READ
            if item_id in id_array:
                item_id = id_array[item_id]

            if "#tag_replacements" in item_id:
                log("Tag replacement data pack must be created!")
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

    if pack_version <= 1302:
        id_array = {
            "minecraft:cactus_green":     "minecraft:green_dye",
            "minecraft:dandelion_yellow": "minecraft:yellow_dye",
            "minecraft:rose_red":         "minecraft:red_dye",
            "minecraft:sign":             "minecraft:oak_sign"
        }
        if item_id in id_array:
            item_id = id_array[item_id]

    if pack_version <= 1502:
        id_array = {
            "minecraft:zombie_pigman_spawn_egg": "minecraft:zombified_piglin_spawn_egg"
        }
        if item_id in id_array:
            item_id = id_array[item_id]

    if pack_version <= 2002:
        id_array = {
            "minecraft:grass": "minecraft:short_grass"
        }
        if item_id in id_array:
            item_id = id_array[item_id]

    return item_id

def extract_riding_id(nbt: dict) -> str:
    if "Riding" in nbt:
        return extract_riding_id(nbt["Riding"])
    elif "id" in nbt:
        return nbt["id"]
    else:
        return "minecraft:pig"
    


def insert_old_adventure_mode_tags(nbt: dict | None, item_id: str):
    if nbt == None or nbt == "":
        nbt = {}
    nbt["adventure"] = nbt_tags.TypeByte(1)
    nbt["HideFlags"] = nbt_tags.TypeInt(24)
    
    if item_id in tables.BLOCK_PLACEABLE:
        nbt["CanPlaceOn"] = nbt_tags.TypeList(["#adventure:all"])
        nbt["CanDestroy"] = nbt_tags.TypeList(["#adventure:mineable/universal"])

    elif item_id in [
        "minecraft:wooden_pickaxe",
        "minecraft:stone_pickaxe",
        "minecraft:golden_pickaxe",
        "minecraft:iron_pickaxe",
        "minecraft:diamond_pickaxe",
        "minecraft:netherite_pickaxe"
    ]:
        nbt["CanDestroy"] = nbt_tags.TypeList(["#minecraft:mineable/pickaxe", "#adventure:mineable/universal"])

    elif item_id in [
        "minecraft:wooden_shovel",
        "minecraft:stone_shovel",
        "minecraft:golden_shovel",
        "minecraft:iron_shovel",
        "minecraft:diamond_shovel",
        "minecraft:netherite_shovel"
    ]:
        nbt["CanDestroy"] = nbt_tags.TypeList(["#minecraft:mineable/shovel", "#adventure:mineable/universal"])

    elif item_id in [
        "minecraft:wooden_axe",
        "minecraft:stone_axe",
        "minecraft:golden_axe",
        "minecraft:iron_axe",
        "minecraft:diamond_axe",
        "minecraft:netherite_axe"
    ]:
        nbt["CanDestroy"] = nbt_tags.TypeList(["#minecraft:mineable/axe", "#adventure:mineable/universal"])

    elif item_id in [
        "minecraft:wooden_hoe",
        "minecraft:stone_hoe",
        "minecraft:golden_hoe",
        "minecraft:iron_hoe",
        "minecraft:diamond_hoe",
        "minecraft:netherite_hoe" 
    ]:
        nbt["CanDestroy"] = nbt_tags.TypeList(["#minecraft:mineable/hoe", "#adventure:mineable/universal"])

    elif item_id in [
        "minecraft:wooden_sword",
        "minecraft:stone_sword",
        "minecraft:golden_sword",
        "minecraft:iron_sword",
        "minecraft:diamond_sword",
        "minecraft:netherite_sword"
    ]:
        nbt["CanDestroy"] = nbt_tags.TypeList(["#adventure:mineable/sword", "#adventure:mineable/universal"])

    elif item_id == "minecraft:shears":
        nbt["CanDestroy"] = nbt_tags.TypeList(["#adventure:mineable/shears", "#adventure:mineable/universal"])

    else:
        nbt["CanDestroy"] = nbt_tags.TypeList(["#adventure:mineable/universal"])



    return nbt