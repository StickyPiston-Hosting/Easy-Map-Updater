# Import things

from lib.data_pack_files import nbt_tags
from lib.data_pack_files import arguments
from lib.data_pack_files import miscellaneous
from lib import utils



# Define functions

def unpack(components: str):
    if not components:
        return {}
    output_block_states: dict[str, str] = {}
    for entry in arguments.parse_with_quotes(components[1:], ",", True):
        if "=" in entry:
            output_block_states[utils.unquote(entry.split("=")[0].strip())] = nbt_tags.unpack(entry.split("=")[1].strip())
    return output_block_states


def pack(components: dict[str]) -> str:
    component_strings: list[str] = []
    for component in components.keys():
        component_strings.append(f'{component}={nbt_tags.pack(components[component])}')
    return f'[{",".join(component_strings)}]'


def extract(item_id: str, components: dict[str], nbt: dict[str]) -> dict[str]:
    if components == None:
        components = {}


    # Apply namespace to all components
    for component in list(components.keys()):
        namespaced_component = miscellaneous.namespace(component)
        if component != namespaced_component:
            components[namespaced_component] = components[component]
            del components[component]


    # Adjust formatting of components
    if "minecraft:can_break" in components:
        can_break: dict[str] = components["minecraft:can_break"]
        if "predicates" not in can_break and "show_in_tooltip" not in can_break:
            can_break = {"predicates": [can_break]}
        components["minecraft:can_break"] = can_break

    if "minecraft:dyed_color" in components:
        dyed_color = components["minecraft:dyed_color"]
        if not isinstance(dyed_color, dict):
            dyed_color = {"rgb": dyed_color}
        components["minecraft:dyed_color"] = dyed_color

    if "minecraft:enchantments" in components:
        enchantments: dict[str] = components["minecraft:enchantments"]
        if "levels" not in enchantments and "show_in_tooltip" not in enchantments:
            enchantments = {"levels": enchantments}
        if "levels" in enchantments:
            levels = enchantments["levels"]
            for enchantment in list(levels.keys()):
                namespaced_enchantment = miscellaneous.namespace(enchantment)
                if enchantment != namespaced_enchantment:
                    levels[namespaced_enchantment] = levels[enchantment]
                    del levels[enchantment]
        components["minecraft:enchantments"] = enchantments

    if "minecraft:stored_enchantments" in components:
        stored_enchantments: dict[str] = components["minecraft:stored_enchantments"]
        if "levels" not in stored_enchantments and "show_in_tooltip" not in stored_enchantments:
            stored_enchantments = {"levels": stored_enchantments}
        if "levels" in stored_enchantments:
            levels = stored_enchantments["levels"]
            for stored_enchantment in list(levels.keys()):
                namespaced_stored_enchantment = miscellaneous.namespace(stored_enchantment)
                if stored_enchantment != namespaced_stored_enchantment:
                    levels[namespaced_stored_enchantment] = levels[stored_enchantment]
                    del levels[stored_enchantment]
        components["minecraft:stored_enchantments"] = stored_enchantments

    if "minecraft:writable_book_contents" in components:
        writable_book_contents = components["minecraft:writable_book_contents"]
        if "pages" not in writable_book_contents:
            writable_book_contents["pages"] = []
        pages = writable_book_contents["pages"]
        for index in range(len(pages)):
            page = pages[index]
            if isinstance(page, str):
                pages[index] = {"raw": page}

    if "minecraft:written_book_contents" in components:
        written_book_contents = components["minecraft:written_book_contents"]
        if "pages" not in written_book_contents:
            written_book_contents["pages"] = []
        pages = written_book_contents["pages"]
        for index in range(len(pages)):
            page = pages[index]
            if isinstance(page, str):
                pages[index] = {"raw": page}


    # Extract data from NBT into components
    if "AttributeModifiers" in nbt:
        if "minecraft:attribute_modifiers" not in components:
            components["minecraft:attribute_modifiers"] = {}
        attribute_modifiers = components["minecraft:attribute_modifiers"]
        if "modifiers" not in attribute_modifiers:
            attribute_modifiers["modifiers"] = []
        for attribute_modifier in nbt["AttributeModifiers"]:
            attribute = {}
            if "AttributeName" in attribute_modifier:
                attribute["type"] = attribute_modifier["AttributeName"]
            if "Slot" in attribute_modifier:
                attribute["slot"] = attribute_modifier["Slot"]
            if "UUID" in attribute_modifier:
                attribute["uuid"] = attribute_modifier["UUID"]
            if "Name" in attribute_modifier:
                attribute["name"] = attribute_modifier["Name"]
            if "Operation" in attribute_modifier:
                attribute["operation"] = ["add_value", "add_multiplied_base", "add_multiplied_total"][attribute_modifier["Operation"].value]
            if "Amount" in attribute_modifier:
                attribute["amount"] = nbt_tags.TypeDouble(attribute_modifier["Amount"])
            attribute_modifiers["modifiers"].append(attribute)
        del nbt["AttributeModifiers"]

    if "author" in nbt:
        if "minecraft:written_book_contents" not in components:
            components["minecraft:written_book_contents"] = {}
        written_book_contents = components["minecraft:written_book_contents"]
        written_book_contents["author"] = nbt["author"]
        del nbt["author"]

    if "CanDestroy" in nbt:
        if "minecraft:can_break" not in components:
            components["minecraft:can_break"] = {}
        can_break = components["minecraft:can_break"]
        if "predicates" not in can_break:
            can_break["predicates"] = []
        predicates = [{"blocks": []}]
        block: str
        for block in nbt["CanDestroy"]:
            if block.startswith("#"):
                predicates.append({"blocks": block})
            else:
                predicates[0]["blocks"].append(block)
        can_break["predicates"].extend(predicates)
        del nbt["CanDestroy"]

    if "CanPlaceOn" in nbt:
        if "minecraft:can_place_on" not in components:
            components["minecraft:can_place_on"] = {}
        can_place_on = components["minecraft:can_place_on"]
        if "predicates" not in can_place_on:
            can_place_on["predicates"] = []
        predicates = [{"blocks": []}]
        block: str
        for block in nbt["CanPlaceOn"]:
            if block.startswith("#"):
                predicates.append({"blocks": block})
            else:
                predicates[0]["blocks"].append(block)
        can_break["predicates"].extend(predicates)
        del nbt["CanPlaceOn"]

    if "Charged" in nbt:
        del nbt["Charged"]
    if "ChargedProjectiles" in nbt:
        if "minecraft:charged_projectiles" not in components:
            components["minecraft:charged_projectiles"] = []
        charged_projectiles = components["minecraft:charged_projectiles"]
        for charged_projectile in nbt["ChargedProjectiles"]:
            charged_projectiles.append(charged_projectile)
        del nbt["ChargedProjectiles"]

    if "CustomModelData" in nbt:
        components["minecraft:custom_model_data"] = nbt_tags.TypeInt(nbt["CustomModelData"])
        del nbt["CustomModelData"]

    if "CustomPotionColor" in nbt:
        if "minecraft:potion_contents" not in components:
            components["minecraft:potion_contents"] = {}
        components["minecraft:potion_contents"]["custom_color"] = nbt_tags.TypeInt(nbt["CustomPotionColor"])
        del nbt["CustomPotionColor"]

    if "custom_potion_effects" in nbt:
        if "minecraft:potion_contents" not in components:
            components["minecraft:potion_contents"] = {}
        components["minecraft:potion_contents"]["custom_effects"] = nbt["custom_potion_effects"]
        del nbt["custom_potion_effects"]

    if "Damage" in nbt:
        components["minecraft:damage"] = nbt_tags.TypeInt(nbt["Damage"])
        del nbt["Damage"]

    if "Decorations" in nbt:
        if "minecraft:map_decorations" not in components:
            components["minecraft:map_decorations"] = {}
        map_decorations = components["minecraft:map_decorations"]
        for decoration in nbt["Decorations"]:
            if "id" in decoration:
                map_decorations[decoration["id"]] = {}
                map_decoration = map_decorations[decoration["id"]]
                if "type" in decoration:
                    map_decoration["type"] = [
                        "player",
                        "frame",
                        "red_marker",
                        "blue_marker",
                        "target_x",
                        "target_point",
                        "player_off_map",
                        "player_off_limits",
                        "mansion",
                        "monument",
                        "banner_white",
                        "banner_orange",
                        "banner_magenta",
                        "banner_light_blue",
                        "banner_yellow",
                        "banner_lime",
                        "banner_pink",
                        "banner_gray",
                        "banner_light_gray",
                        "banner_cyan",
                        "banner_purple",
                        "banner_blue",
                        "banner_brown",
                        "banner_green",
                        "banner_red",
                        "banner_black",
                        "red_x",
                        "village_desert",
                        "village_plains",
                        "village_savanna",
                        "village_snowy",
                        "village_taiga",
                        "jungle_temple",
                        "swamp_hut",
                    ][decoration["type"].value]
                if "x" in decoration:
                    map_decoration["x"] = nbt_tags.TypeDouble(decoration["x"])
                if "z" in decoration:
                    map_decoration["z"] = nbt_tags.TypeDouble(decoration["z"])
                if "rot" in decoration:
                    map_decoration["rotation"] = nbt_tags.TypeFloat(decoration["rot"])
        del nbt["Decorations"]

    if "display" in nbt:
        display = nbt["display"]
        
        if "Name" in display:
            components["minecraft:custom_name"] = display["Name"]
        
        if "Lore" in display:
            components["minecraft:lore"] = display["Lore"]

        if "color" in display:
            if "minecraft:dyed_color" not in components:
                components["minecraft:dyed_color"] = {}
            components["minecraft:dyed_color"]["rgb"] = nbt_tags.TypeInt(display["color"])

        if "MapColor" in display:
            components["minecraft:map_color"] = nbt_tags.TypeInt(display["MapColor"])
        
        del nbt["display"]

    if "Enchantments" in nbt:
        if "minecraft:enchantments" not in components:
            components["minecraft:enchantments"] = {}
        enchantments = components["minecraft:enchantments"]
        if "levels" not in enchantments:
            enchantments["levels"] = {}
        for enchantment in nbt["Enchantments"]:
            if "id" in enchantment:
                if "lvl" in enchantment:
                    enchantments["levels"][miscellaneous.namespace(enchantment["id"])] = nbt_tags.TypeInt(enchantment["lvl"])
                else:
                    enchantments["levels"][miscellaneous.namespace(enchantment["id"])] = nbt_tags.TypeInt(0)
        del nbt["Enchantments"]

    if "generation" in nbt:
        if "minecraft:written_book_contents" not in components:
            components["minecraft:written_book_contents"] = {}
        written_book_contents = components["minecraft:written_book_contents"]
        written_book_contents["generation"] = nbt_tags.TypeInt(nbt["generation"])
        del nbt["generation"]

    if "Items" in nbt:
        if "minecraft:bundle_contents" not in components:
            components["minecraft:bundle_contents"] = []
        bundle_contents = components["minecraft:bundle_contents"]
        bundle_contents.extend(nbt["Items"])
        del nbt["Items"]

    if "map" in nbt:
        components["minecraft:map_id"] = nbt_tags.TypeInt(nbt["map"])
        del nbt["map"]

    if "pages" in nbt:
        if item_id == "minecraft:writable_book":
            if "minecraft:writable_book_contents" not in components:
                components["minecraft:writable_book_contents"] = {}
            writable_book_contents = components["minecraft:writable_book_contents"]
            if "pages" not in writable_book_contents:
                writable_book_contents["pages"] = []
            pages = writable_book_contents["pages"]
            for page in nbt["pages"]:
                pages.append({"raw": page})

        if item_id == "minecraft:written_book":
            if "minecraft:written_book_contents" not in components:
                components["minecraft:written_book_contents"] = {}
            written_book_contents = components["minecraft:written_book_contents"]
            if "pages" not in written_book_contents:
                written_book_contents["pages"] = []
            pages = written_book_contents["pages"]
            for page in nbt["pages"]:
                pages.append({"raw": page})

        del nbt["pages"]

    if "Potion" in nbt:
        if "minecraft:potion_contents" not in components:
            components["minecraft:potion_contents"] = {}
        components["minecraft:potion_contents"]["potion"] = nbt["Potion"]
        del nbt["Potion"]

    if "RepairCost" in nbt:
        components["minecraft:repair_cost"] = nbt_tags.TypeInt(nbt["RepairCost"])
        del nbt["RepairCost"]

    if "resolved" in nbt:
        if "minecraft:written_book_contents" not in components:
            components["minecraft:written_book_contents"] = {}
        written_book_contents = components["minecraft:written_book_contents"]
        written_book_contents["resolved"] = nbt_tags.TypeByte(nbt["resolved"])
        del nbt["resolved"]

    if "StoredEnchantments" in nbt:
        if "minecraft:stored_enchantments" not in components:
            components["minecraft:stored_enchantments"] = {}
        stored_enchantments = components["minecraft:stored_enchantments"]
        if "levels" not in stored_enchantments:
            stored_enchantments["levels"] = {}
        for stored_enchantment in nbt["StoredEnchantments"]:
            if "id" in stored_enchantment:
                if "lvl" in stored_enchantment:
                    stored_enchantments["levels"][miscellaneous.namespace(stored_enchantment["id"])] = nbt_tags.TypeInt(stored_enchantment["lvl"])
                else:
                    stored_enchantments["levels"][miscellaneous.namespace(stored_enchantment["id"])] = nbt_tags.TypeInt(0)
        del nbt["StoredEnchantments"]

    if "title" in nbt:
        if "minecraft:written_book_contents" not in components:
            components["minecraft:written_book_contents"] = {}
        written_book_contents = components["minecraft:written_book_contents"]
        written_book_contents["title"] = {"raw": nbt["title"]}
        del nbt["title"]

    if "Trim" in nbt:
        if "minecraft:trim" not in components:
            components["minecraft:trim"] = {}
        trim = components["minecraft:trim"]
        if "pattern" in nbt["Trim"]:
            trim["pattern"] = nbt["Trim"]["pattern"]
        if "material" in nbt["Trim"]:
            trim["material"] = nbt["Trim"]["material"]
        del nbt["Trim"]

    if "Unbreakable" in nbt:
        if "minecraft:unbreakable" not in components:
            components["minecraft:unbreakable"] = {}
        del nbt["Unbreakable"]

    if "HideFlags" in nbt:
        if nbt["HideFlags"].value%2 == 1 and "minecraft:enchantments" in components:
            components["minecraft:enchantments"]["show_in_tooltip"] = nbt_tags.TypeByte(0)
        if nbt["HideFlags"].value%2 == 1 and "minecraft:minecraft:attribute_modifiers" in components:
            components["minecraft:minecraft:attribute_modifiers"]["show_in_tooltip"] = nbt_tags.TypeByte(0)
        if nbt["HideFlags"].value//4%2 == 1 and "minecraft:unbreakable" in components:
            components["minecraft:unbreakable"]["show_in_tooltip"] = nbt_tags.TypeByte(0)
        if nbt["HideFlags"].value//8%2 == 1 and "minecraft:can_break" in components:
            components["minecraft:can_break"]["show_in_tooltip"] = nbt_tags.TypeByte(0)
        if nbt["HideFlags"].value//16%2 == 1 and "minecraft:can_place_on" in components:
            components["minecraft:can_place_on"]["show_in_tooltip"] = nbt_tags.TypeByte(0)
        if nbt["HideFlags"].value//32%2 == 1 and "minecraft:stored_enchantments" in components:
            components["minecraft:stored_enchantments"]["show_in_tooltip"] = nbt_tags.TypeByte(0)
        if nbt["HideFlags"].value//64%2 == 1 and "minecraft:dyed_color" in components:
            components["minecraft:dyed_color"]["show_in_tooltip"] = nbt_tags.TypeByte(0)
        if nbt["HideFlags"].value//128%2 == 1 and "minecraft:trim" in components:
            components["minecraft:trim"]["show_in_tooltip"] = nbt_tags.TypeByte(0)
        del nbt["HideFlags"]

    if nbt:
        if "minecraft:custom_data" in components:
            for key in nbt.keys():
                components["minecraft:custom_data"][key] = nbt[key]
        else:
            components["minecraft:custom_data"] = nbt


    return components