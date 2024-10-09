# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from typing import cast, Any
from lib.log import log
from lib import defaults
from lib import utils



# Define classes

class ItemComponent:
    key: str
    value: Any
    negated: bool
    separator: str | None

    def __init__(self, key: str, value: Any, negated: bool, separator: str | None):
        self.key = key
        self.value = value
        self.negated = negated
        self.separator = separator

    @staticmethod
    def unpack(component: str):
        component = component.strip()

        # Determine whether component is negated
        negated: bool = component.startswith("!")
        if negated:
            component = component[1:]

        # Determine if component is defined using an equal sign or a tilda
        for separator in ["=", "~"]:
            parts = arguments.parse_with_quotes(component, separator, True)
            if len(parts) > 1:
                return ItemComponent(
                    utils.unquote(parts[0].strip()),
                    nbt_tags.unpack(parts[1].strip()),
                    negated,
                    separator
                )

        return ItemComponent(
            utils.unquote(component),
            None,
            negated,
            None
        )

    def pack(self) -> str:
        negated_string = "!" if self.negated else ""
        if self.separator:
            return f"{negated_string}{self.key}{self.separator}{nbt_tags.pack(self.value)}"
        return f"{negated_string}{self.key}"
    
    def set_namespace(self):
        self.key = miscellaneous.namespace(self.key)


class ItemComponentAlternatives:
    alternatives: list[ItemComponent]

    def __init__(self, alternatives: list[ItemComponent]):
        self.alternatives = alternatives

    @staticmethod
    def unpack(parts: list[str]):
        alternatives: list[ItemComponent] = []
        for part in parts:
            alternatives.append(ItemComponent.unpack(part))
        return ItemComponentAlternatives(alternatives)
    
    def pack(self) -> str:
        parts: list[str] = []
        for alternative in self.alternatives:
            parts.append(alternative.pack())
        return "|".join(parts)
    
    def set_namespace(self):
        for alternative in self.alternatives:
            alternative.set_namespace()


class ItemComponents:
    components: list[ItemComponent | ItemComponentAlternatives]

    def __init__(self, components: list[ItemComponent | ItemComponentAlternatives]):
        self.components = components

    @staticmethod
    def unpack(components_string: str):
        if not components_string:
            return ItemComponents([])

        components: list[ItemComponent | ItemComponentAlternatives] = []
        parts = arguments.parse_with_quotes(components_string[1:], ",", True)
        for part in parts:
            alternatives = arguments.parse_with_quotes(part, "|", True)
            if len(alternatives) > 1:
                components.append(ItemComponentAlternatives.unpack(alternatives))
            else:
                components.append(ItemComponent.unpack(part))

        return ItemComponents(components)
    
    @staticmethod
    def unpack_from_dict(components_dict: dict[str, Any] | None, read: bool):
        partial_match_components = [
            "minecraft:attribute_modifiers",
            "minecraft:bundle_contents",
            "minecraft:container",
            "minecraft:custom_data",
            "minecraft:damage",
            "minecraft:firework_explosion",
            "minecraft:fireworks",
            "minecraft:jukebox_playable",
            "minecraft:trim",
            "minecraft:writable_book_content",
            "minecraft:written_book_content",
        ]
        if not components_dict:
            return ItemComponents([])
        components: list[ItemComponent | ItemComponentAlternatives] = []
        for key in components_dict:
            components.append(ItemComponent(key, components_dict[key], False, "~" if (read and key in partial_match_components and isinstance(components_dict[key], dict)) else "="))
        return ItemComponents(components)

    def pack(self) -> str:
        components: list[str] = []
        for component in self.components:
            components.append(component.pack())
        return f"[{",".join(components)}]"
    
    def pack_to_dict(self) -> dict[str, Any]:
        components_dict: dict[str, Any] = {}
        for component in self.components:
            if isinstance(component, ItemComponent):
                components_dict[component.key] = component.value
        return components_dict
    
    def has_components(self) -> bool:
        return len(self.components) > 0
    
    def set_namespaces(self):
        for component in self.components:
            component.set_namespace()

    def __getitem__(self, key: str) -> Any:
        for component in self.components:
            if isinstance(component, ItemComponent) and component.key == key:
                return component.value
                
    def __setitem__(self, key: str, value: Any):
        for component in self.components:
            if isinstance(component, ItemComponent) and component.key == key:
                component.value = value
                return
        self.components.append(ItemComponent(key, value, False, "="))

    def __contains__(self, key: str) -> bool:
        for component in self.components:
            if isinstance(component, ItemComponent) and component.key == key:
                return True
        return False


# Import more stuff to prevent circular loading issues

from lib.data_pack_files import blocks
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import arguments
from lib.data_pack_files import miscellaneous



# Define functions

# def unpack(components: str) -> dict[str, str | None]:
#     if not components:
#         return {}
#     output_components: dict[str, str | None] = {}
#     for entry in arguments.parse_with_quotes(components[1:], ",", True):
#         output_components[utils.unquote(entry.split("=")[0].strip())] = (
#             nbt_tags.unpack(entry.split("=")[1].strip())
#             if "=" in entry else None
#         )
#     return output_components


# def pack(components: dict[str, Any], read: bool) -> str:
#     partial_match_components = [
#         "minecraft:attribute_modifiers",
#         "minecraft:custom_data",
#     ]
#     component_strings: list[str] = []
#     for component in components.keys():
#         if components[component] == None:
#             component_strings.append(component)
#         else:
#             component_strings.append(f"{component}{"~" if read and component in partial_match_components else "="}{nbt_tags.pack(components[component])}")
#     return f"[{",".join(component_strings)}]"


def conform_components(components: ItemComponents, version: int, issues: list[dict[str, str | int]]) -> ItemComponents:
    # Apply namespace to all components
    components.set_namespaces()


    # Adjust formatting of components
    for component in components.components:
        if isinstance(component, ItemComponent):
            conform_component(component, version)
        else:
            for alternative in component.alternatives:
                conform_component(alternative, version)


    return components


def conform_component(component: ItemComponent, version: int):

    if component.value is None:
        return

    if component.key == "minecraft:attribute_modifiers":
        attribute_modifiers = component.value
        if not isinstance(attribute_modifiers, dict):
            attribute_modifiers = {"modifiers": attribute_modifiers}
        for attribute_modifier in attribute_modifiers["modifiers"]:
            if "type" in attribute_modifier:
                attribute_modifier["type"] = miscellaneous.attribute(attribute_modifier["type"], version, [])
            if "name" in attribute_modifier:
                del attribute_modifier["name"]
            if "uuid" in attribute_modifier:
                attribute_modifier["id"] = miscellaneous.namespace(
                    utils.uuid_from_int_array([entry.value for entry in attribute_modifier["uuid"]])
                )
                del attribute_modifier["uuid"]
        component.value = attribute_modifiers

    if component.key == "minecraft:can_break":
        can_break: dict[str, Any] = component.value
        if "predicates" not in can_break and "show_in_tooltip" not in can_break:
            can_break = {"predicates": nbt_tags.TypeList([can_break])}
        if "predicates" in can_break:
            for predicate in cast(nbt_tags.TypeList, can_break["predicates"]):
                if "blocks" in predicate:
                    if isinstance(predicate["blocks"], nbt_tags.TypeList):
                        if len(predicate["blocks"]) == 1:
                            predicate["blocks"] = miscellaneous.namespace(predicate["blocks"][0])
                        else:
                            for i in range(len(predicate["blocks"])):
                                predicate["blocks"][i] = miscellaneous.namespace(predicate["blocks"][i])
                    else:
                        predicate["blocks"] = miscellaneous.namespace(predicate["blocks"])
        component.value = can_break

    if component.key == "minecraft:can_place_on":
        can_place_on: dict[str, Any] = component.value
        if "predicates" not in can_place_on and "show_in_tooltip" not in can_place_on:
            can_place_on = {"predicates": nbt_tags.TypeList([can_place_on])}
        if "predicates" in can_place_on:
            for predicate in cast(nbt_tags.TypeList, can_place_on["predicates"]):
                if "blocks" in predicate:
                    if isinstance(predicate["blocks"], nbt_tags.TypeList):
                        if len(predicate["blocks"]) == 1:
                            predicate["blocks"] = miscellaneous.namespace(predicate["blocks"][0])
                        else:
                            for i in range(len(predicate["blocks"])):
                                predicate["blocks"][i] = miscellaneous.namespace(predicate["blocks"][i])
                    else:
                        predicate["blocks"] = miscellaneous.namespace(predicate["blocks"])
        component.value = can_place_on

    if component.key == "minecraft:debug_stick_state":
        debug_stick_state: dict[str, str] = component.value
        for block in list(debug_stick_state.keys()):
            namespaced_block = miscellaneous.namespace(block)
            if block != namespaced_block:
                debug_stick_state[namespaced_block] = debug_stick_state[block]
                del debug_stick_state[block]

    if component.key == "minecraft:dyed_color":
        dyed_color = component.value
        if not isinstance(dyed_color, dict):
            dyed_color = {"rgb": dyed_color}
        component.value = dyed_color

    if component.key == "minecraft:enchantments":
        enchantments: dict[str, Any] = component.value
        if "levels" not in enchantments and "show_in_tooltip" not in enchantments:
            enchantments = {"levels": enchantments}
        if "levels" in enchantments:
            levels = enchantments["levels"]
            for enchantment in list(levels.keys()):
                namespaced_enchantment = miscellaneous.namespace(enchantment)
                if enchantment != namespaced_enchantment:
                    levels[namespaced_enchantment] = levels[enchantment]
                    del levels[enchantment]
                levels[namespaced_enchantment] = nbt_tags.TypeInt(min(max(levels[namespaced_enchantment].value, 0), 255))
        component.value = enchantments

    if component.key == "minecraft:potion_contents":
        potion_contents = component.value
        if not isinstance(potion_contents, dict):
            potion_contents = {"potion": potion_contents}
        component.value = potion_contents

    if component.key == "minecraft:profile":
        profile = component.value
        if not isinstance(profile, dict):
            profile = {"name": profile}
        component.value = profile

    if component.key == "minecraft:stored_enchantments":
        stored_enchantments: dict[str, Any] = component.value
        if "levels" not in stored_enchantments and "show_in_tooltip" not in stored_enchantments:
            stored_enchantments = {"levels": stored_enchantments}
        if "levels" in stored_enchantments:
            levels = stored_enchantments["levels"]
            for stored_enchantment in list(levels.keys()):
                namespaced_stored_enchantment = miscellaneous.namespace(stored_enchantment)
                if stored_enchantment != namespaced_stored_enchantment:
                    levels[namespaced_stored_enchantment] = levels[stored_enchantment]
                    del levels[stored_enchantment]
        component.value = stored_enchantments

    if component.key == "minecraft:writable_book_content":
        writable_book_content = component.value
        if "pages" not in writable_book_content:
            writable_book_content["pages"] = nbt_tags.TypeList([])
        pages = writable_book_content["pages"]
        for index in range(len(pages)):
            page = pages[index]
            if isinstance(page, str):
                pages[index] = {"raw": page}

    if component.key == "minecraft:written_book_content":
        written_book_content = component.value
        if "pages" not in written_book_content:
            written_book_content["pages"] = nbt_tags.TypeList([])
        pages = written_book_content["pages"]
        for index in range(len(pages)):
            page = pages[index]
            if isinstance(page, str):
                pages[index] = {"raw": page}




def extract(item_id: str, components: dict[str, Any] | None, nbt: dict[str, Any], version: int, issues: list[dict[str, str | int]]) -> dict[str, Any]:
    if components == None:
        components = {}


    # Extract data from NBT into components
    if "Age" in nbt and item_id.endswith("_bucket"):
        if "minecraft:bucket_entity_data" not in components:
            components["minecraft:bucket_entity_data"] = {}
        components["minecraft:bucket_entity_data"]["Age"] = nbt_tags.TypeInt(nbt["Age"])
        del nbt["Age"]

    if "AttributeModifiers" in nbt:
        if "minecraft:attribute_modifiers" not in components:
            components["minecraft:attribute_modifiers"] = {}
        attribute_modifiers = components["minecraft:attribute_modifiers"]
        if "modifiers" not in attribute_modifiers:
            attribute_modifiers["modifiers"] = nbt_tags.TypeList([])
        for attribute_modifier in nbt["AttributeModifiers"]:
            attribute = {}
            if "AttributeName" in attribute_modifier:
                attribute["type"] = miscellaneous.attribute(attribute_modifier["AttributeName"], version, issues)
            elif "Name" in attribute_modifier:
                attribute["type"] = miscellaneous.attribute(attribute_modifier["Name"], version, issues)
            if "Slot" in attribute_modifier:
                attribute["slot"] = attribute_modifier["Slot"]
            if "UUID" in attribute_modifier:
                attribute["id"] = miscellaneous.namespace(
                    utils.uuid_from_int_array([entry.value for entry in attribute_modifier["UUID"]])
                )
            if "Operation" in attribute_modifier:
                attribute["operation"] = ["add_value", "add_multiplied_base", "add_multiplied_total"][attribute_modifier["Operation"].value]
            else:
                attribute["operation"] = "add_value"
            if "Amount" in attribute_modifier:
                attribute["amount"] = nbt_tags.TypeDouble(attribute_modifier["Amount"])
            for key in ["id", "operation", "amount"]:
                if key in attribute_modifier:
                    attribute[key] = attribute_modifier[key]
            attribute_modifiers["modifiers"].append(attribute)
        del nbt["AttributeModifiers"]

    if "author" in nbt:
        if "minecraft:written_book_content" not in components:
            components["minecraft:written_book_content"] = {}
        written_book_content = components["minecraft:written_book_content"]
        written_book_content["author"] = nbt["author"]
        del nbt["author"]

    if "BlockEntityTag" in nbt:
        block_entity_tag: dict[str, Any] = nbt["BlockEntityTag"]

        if "Base" in block_entity_tag:
            components["minecraft:base_color"] = miscellaneous.color(block_entity_tag["Base"].value)
            del block_entity_tag["Base"]

        if "Bees" in block_entity_tag:
            if "minecraft:bees" not in components:
                components["minecraft:bees"] = nbt_tags.TypeList([])
            for bee in block_entity_tag["Bees"]:
                bee_entry: dict[str, Any] = {}
                if "EntityData" in bee:
                    bee_entry["entity_data"] = bee["EntityData"]
                if "TicksInHive" in bee:
                    bee_entry["ticks_in_hive"] = nbt_tags.TypeInt(bee["TicksInHive"])
                if "MinOccupationTicks" in bee:
                    bee_entry["min_ticks_in_hive"] = nbt_tags.TypeInt(bee["MinOccupationTicks"])
                components["minecraft:bees"].append(bee_entry)
            del block_entity_tag["Bees"]

        if "bees" in block_entity_tag:
            if "minecraft:bees" not in components:
                components["minecraft:bees"] = nbt_tags.TypeList([])
            for bee in block_entity_tag["bees"]:
                bee_entry: dict[str, Any] = {}
                if "entity_data" in bee:
                    bee_entry["entity_data"] = bee["entity_data"]
                if "ticks_in_hive" in bee:
                    bee_entry["ticks_in_hive"] = nbt_tags.TypeInt(bee["ticks_in_hive"])
                if "min_ticks_in_hive" in bee:
                    bee_entry["min_ticks_in_hive"] = nbt_tags.TypeInt(bee["min_ticks_in_hive"])
                components["minecraft:bees"].append(bee_entry)
            del block_entity_tag["bees"]

        if "Items" in block_entity_tag:
            if "minecraft:container" not in components:
                components["minecraft:container"] = nbt_tags.TypeList([])
            container = components["minecraft:container"]
            for item in block_entity_tag["Items"]:
                container_entry: dict[str, Any] = {}
                if "Slot" in item:
                    container_entry["slot"] = nbt_tags.TypeInt(item["Slot"])
                container_entry["item"] = {}
                if "id" in item:
                    container_entry["item"]["id"] = miscellaneous.namespace(item["id"])
                if "count" in item:
                    container_entry["item"]["count"] = nbt_tags.TypeInt(item["count"])
                if "components" in item:
                    container_entry["item"]["components"] = item["components"]
                container.append(container_entry)
            del block_entity_tag["Items"]

        if "Lock" in block_entity_tag:
            components["minecraft:lock"] = block_entity_tag["Lock"]
            del block_entity_tag["Lock"]

        if "LootTable" in block_entity_tag:
            if "minecraft:container_loot" not in components:
                components["minecraft:container_loot"] = {}
            components["minecraft:container_loot"]["loot_table"] = miscellaneous.namespace(block_entity_tag["LootTable"])
            del block_entity_tag["LootTable"]

        if "LootTableSeed" in block_entity_tag:
            if "minecraft:container_loot" not in components:
                components["minecraft:container_loot"] = {}
            components["minecraft:container_loot"]["seed"] = nbt_tags.TypeLong(block_entity_tag["LootTableSeed"])
            del block_entity_tag["LootTableSeed"]

        if "note_block_sound" in block_entity_tag:
            components["minecraft:note_block_sound"] = miscellaneous.namespace(block_entity_tag["note_block_sound"])
            del block_entity_tag["note_block_sound"]

        if "Patterns" in block_entity_tag:
            if "minecraft:banner_patterns" not in components:
                components["minecraft:banner_patterns"] = nbt_tags.TypeList([])
            banner_patterns = components["minecraft:banner_patterns"]
            for pattern in block_entity_tag["Patterns"]:
                banner_pattern: dict[str, Any] = {}
                if "Pattern" in pattern:
                    banner_pattern["pattern"] = miscellaneous.banner_pattern(pattern["Pattern"], version, issues)
                if "Color" in pattern:
                    banner_pattern["color"] = miscellaneous.banner_color(pattern["Color"], version, issues)
                banner_patterns.append(banner_pattern)
            del block_entity_tag["Patterns"]

        if "patterns" in block_entity_tag:
            if "minecraft:banner_patterns" not in components:
                components["minecraft:banner_patterns"] = nbt_tags.TypeList([])
            banner_patterns = components["minecraft:banner_patterns"]
            for pattern in block_entity_tag["patterns"]:
                banner_pattern: dict[str, Any] = {}
                if "pattern" in pattern:
                    banner_pattern["pattern"] = miscellaneous.namespace(pattern["pattern"])
                if "color" in pattern:
                    banner_pattern["color"] = pattern["color"]
                banner_patterns.append(banner_pattern)
            del block_entity_tag["patterns"]

        if "sherds" in block_entity_tag:
            components["minecraft:pot_decorations"] = nbt_tags.TypeList([])
            for sherd in block_entity_tag["sherds"]:
                components["minecraft:pot_decorations"].append(miscellaneous.namespace(sherd))
            del block_entity_tag["sherds"]

        if block_entity_tag:
            if "minecraft:block_entity_data" not in components:
                components["minecraft:block_entity_data"] = {}
            block_entity_data = components["minecraft:block_entity_data"]
            if "id" not in block_entity_data and "id" not in block_entity_tag:
                block_entity_data["id"] = item_id
            for key in block_entity_tag.keys():
                block_entity_data[key] = block_entity_tag[key]
        
        del nbt["BlockEntityTag"]

    if "BlockStateTag" in nbt:
        if "minecraft:block_state" not in components:
            components["minecraft:block_state"] = {}
        for state in nbt["BlockStateTag"]:
            components["minecraft:block_state"][state] = nbt["BlockStateTag"][state]
        del nbt["BlockStateTag"]

    if "BucketVariantTag" in nbt and item_id.endswith("_bucket"):
        if "minecraft:bucket_entity_data" not in components:
            components["minecraft:bucket_entity_data"] = {}
        components["minecraft:bucket_entity_data"]["Variant"] = nbt_tags.TypeInt(nbt["BucketVariantTag"])
        del nbt["BucketVariantTag"]

    if "CanDestroy" in nbt:
        if "minecraft:can_break" not in components:
            components["minecraft:can_break"] = {}
        can_break = components["minecraft:can_break"]
        if "predicates" not in can_break:
            can_break["predicates"] = nbt_tags.TypeList([])
        predicates: list[dict[str, Any]] = [{"blocks": nbt_tags.TypeList([])}]
        block: str
        for block in nbt["CanDestroy"]:
            if block.startswith("#"):
                predicates.append({"blocks": block})
            else:
                if "[" in block:
                    predicates.append({
                        "blocks": block[:block.find("[")],
                        "state": blocks.unpack_block_states(block[block.find("["):])
                    })
                else:
                    predicates[0]["blocks"].append(block)
        if len(predicates[0]["blocks"]) == 0:
            predicates.pop(0)
        elif len(predicates[0]["blocks"]) == 1:
            predicates[0]["blocks"] = predicates[0]["blocks"][0]
        can_break["predicates"].extend(predicates)
        if len(can_break["predicates"]) == 0:
            can_break["predicates"].append({})
        del nbt["CanDestroy"]

    if "CanPlaceOn" in nbt:
        if "minecraft:can_place_on" not in components:
            components["minecraft:can_place_on"] = {}
        can_place_on = components["minecraft:can_place_on"]
        if "predicates" not in can_place_on:
            can_place_on["predicates"] = nbt_tags.TypeList([])
        predicates = [{"blocks": nbt_tags.TypeList([])}]
        block: str
        for block in nbt["CanPlaceOn"]:
            if block.startswith("#"):
                predicates.append({"blocks": block})
            else:
                if "[" in block:
                    predicates.append({
                        "blocks": block[:block.find("[")],
                        "state": blocks.unpack_block_states(block[block.find("["):])
                    })
                else:
                    predicates[0]["blocks"].append(block)
        if len(predicates[0]["blocks"]) == 0:
            predicates.pop(0)
        elif len(predicates[0]["blocks"]) == 1:
            predicates[0]["blocks"] = predicates[0]["blocks"][0]
        can_place_on["predicates"].extend(predicates)
        if len(can_place_on["predicates"]) == 0:
            can_place_on["predicates"].append({})
        del nbt["CanPlaceOn"]

    if "Charged" in nbt:
        del nbt["Charged"]
    if "ChargedProjectiles" in nbt:
        if "minecraft:charged_projectiles" not in components:
            components["minecraft:charged_projectiles"] = nbt_tags.TypeList([])
        charged_projectiles = components["minecraft:charged_projectiles"]
        for charged_projectile in nbt["ChargedProjectiles"]:
            if "id" in charged_projectile:
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

    if "DebugProperty" in nbt:
        if "minecraft:debug_stick_state" not in components:
            components["minecraft:debug_stick_state"] = {}
        for block in nbt["DebugProperty"].keys():
            components["minecraft:debug_stick_state"][miscellaneous.namespace(block)] = nbt["DebugProperty"][block]
        del nbt["DebugProperty"]

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

    if "effects" in nbt:
        if "minecraft:suspicious_stew_effects" not in components:
            components["minecraft:suspicious_stew_effects"] = nbt_tags.TypeList([])
        components["minecraft:suspicious_stew_effects"].extend(nbt["effects"])
        del nbt["effects"]

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
        if not enchantments["levels"]:
            components["minecraft:enchantment_glint_override"] = nbt_tags.TypeByte(1)
            del enchantments["levels"]
        if not enchantments:
            del components["minecraft:enchantments"]
        del nbt["Enchantments"]

    if "EntityTag" in nbt:
        if "minecraft:entity_data" not in components:
            components["minecraft:entity_data"] = {}
        entity_data = components["minecraft:entity_data"]
        if "id" not in entity_data and "id" not in nbt["EntityTag"]:
            entity_data["id"] = miscellaneous.entity_id_from_item(item_id)
        for key in nbt["EntityTag"].keys():
            entity_data[key] = nbt["EntityTag"][key]
        del nbt["EntityTag"]

    if "Explosion" in nbt:
        if "minecraft:firework_explosion" not in components:
            components["minecraft:firework_explosion"] = {}
        firework_explosion = components["minecraft:firework_explosion"]
        explosion = nbt["Explosion"]
        if "Type" in explosion:
            firework_explosion["shape"] = [
                "small_ball",
                "large_ball",
                "star",
                "creeper",
                "burst",
            ][explosion["Type"].value]
        if "Colors" in explosion:
            firework_explosion["colors"] = nbt_tags.TypeIntArray(explosion["Colors"])
        if "FadeColors" in explosion:
            firework_explosion["fade_colors"] = nbt_tags.TypeIntArray(explosion["FadeColors"])
        if "Trail" in explosion:
            firework_explosion["has_trail"] = nbt_tags.TypeByte(explosion["Trail"])
        if "Flicker" in explosion:
            firework_explosion["has_twinkle"] = nbt_tags.TypeByte(explosion["Flicker"])
        del nbt["Explosion"]

    if "Fireworks" in nbt:
        if "minecraft:fireworks" not in components:
            components["minecraft:fireworks"] = {}
        fireworks = components["minecraft:fireworks"]
        if "Explosions" in nbt["Fireworks"]:
            if "explosions" not in fireworks:
                fireworks["explosions"] = nbt_tags.TypeList([])
            for explosion in nbt["Fireworks"]["Explosions"]:
                firework_explosion = {}
                if "Type" in explosion:
                    firework_explosion["shape"] = [
                        "small_ball",
                        "large_ball",
                        "star",
                        "creeper",
                        "burst",
                    ][explosion["Type"].value]
                if "Colors" in explosion:
                    firework_explosion["colors"] = nbt_tags.TypeIntArray(explosion["Colors"])
                if "FadeColors" in explosion:
                    firework_explosion["fade_colors"] = nbt_tags.TypeIntArray(explosion["FadeColors"])
                if "Trail" in explosion:
                    firework_explosion["has_trail"] = nbt_tags.TypeByte(explosion["Trail"])
                if "Flicker" in explosion:
                    firework_explosion["has_twinkle"] = nbt_tags.TypeByte(explosion["Flicker"])
                fireworks["explosions"].append(firework_explosion)
        if "Flight" in nbt["Fireworks"]:
            fireworks["flight_duration"] = nbt_tags.TypeByte(nbt["Fireworks"]["Flight"])
        del nbt["Fireworks"]

    if "generation" in nbt:
        if "minecraft:written_book_content" not in components:
            components["minecraft:written_book_content"] = {}
        written_book_content = components["minecraft:written_book_content"]
        written_book_content["generation"] = nbt_tags.TypeInt(nbt["generation"])
        del nbt["generation"]

    if "Glowing" in nbt and item_id.endswith("_bucket"):
        if "minecraft:bucket_entity_data" not in components:
            components["minecraft:bucket_entity_data"] = {}
        components["minecraft:bucket_entity_data"]["Glowing"] = nbt_tags.TypeByte(nbt["Glowing"])
        del nbt["Glowing"]

    if "Health" in nbt and item_id.endswith("_bucket"):
        if "minecraft:bucket_entity_data" not in components:
            components["minecraft:bucket_entity_data"] = {}
        components["minecraft:bucket_entity_data"]["Health"] = nbt_tags.TypeFloat(nbt["Health"])
        del nbt["Health"]

    if "HuntingCooldown" in nbt and item_id.endswith("_bucket"):
        if "minecraft:bucket_entity_data" not in components:
            components["minecraft:bucket_entity_data"] = {}
        components["minecraft:bucket_entity_data"]["HuntingCooldown"] = nbt["HuntingCooldown"]
        del nbt["HuntingCooldown"]

    if "instrument" in nbt:
        components["minecraft:instrument"] = miscellaneous.namespace(nbt["instrument"])
        del nbt["instrument"]

    if "Invulnerable" in nbt and item_id.endswith("_bucket"):
        if "minecraft:bucket_entity_data" not in components:
            components["minecraft:bucket_entity_data"] = {}
        components["minecraft:bucket_entity_data"]["Invulnerable"] = nbt_tags.TypeByte(nbt["Invulnerable"])
        del nbt["Invulnerable"]

    if "Items" in nbt:
        if "minecraft:bundle_contents" not in components:
            components["minecraft:bundle_contents"] = nbt_tags.TypeList([])
        bundle_contents = components["minecraft:bundle_contents"]
        bundle_contents.extend(nbt["Items"])
        del nbt["Items"]

    if "LodestoneDimension" in nbt:
        if "minecraft:lodestone_tracker" not in components:
            components["minecraft:lodestone_tracker"] = {}
        lodestone_tracker = components["minecraft:lodestone_tracker"]
        if "target" not in lodestone_tracker:
            lodestone_tracker["target"] = {}
        target = lodestone_tracker["target"]
        target["dimension"] = miscellaneous.namespace(nbt["LodestoneDimension"])
        del nbt["LodestoneDimension"]

    if "LodestonePos" in nbt:
        if "minecraft:lodestone_tracker" not in components:
            components["minecraft:lodestone_tracker"] = {}
        lodestone_tracker = components["minecraft:lodestone_tracker"]
        if "target" not in lodestone_tracker:
            lodestone_tracker["target"] = {}
        target = lodestone_tracker["target"]
        x, y, z = nbt_tags.TypeInt(0), nbt_tags.TypeInt(0), nbt_tags.TypeInt(0)
        if "X" in nbt["LodestonePos"]:
            x = nbt["LodestonePos"]["X"]
        if "Y" in nbt["LodestonePos"]:
            y = nbt["LodestonePos"]["Y"]
        if "Z" in nbt["LodestonePos"]:
            z = nbt["LodestonePos"]["Z"]
        target["pos"] = nbt_tags.TypeIntArray([x,y,z])
        del nbt["LodestonePos"]

    if "LodestoneTracked" in nbt:
        if "minecraft:lodestone_tracker" not in components:
            components["minecraft:lodestone_tracker"] = {}
        lodestone_tracker = components["minecraft:lodestone_tracker"]
        lodestone_tracker["tracked"] = nbt_tags.TypeByte(nbt["LodestoneTracked"])
        del nbt["LodestoneTracked"]

    if "map" in nbt:
        components["minecraft:map_id"] = nbt_tags.TypeInt(nbt["map"])
        del nbt["map"]

    if "NoAI" in nbt and item_id.endswith("_bucket"):
        if "minecraft:bucket_entity_data" not in components:
            components["minecraft:bucket_entity_data"] = {}
        components["minecraft:bucket_entity_data"]["NoAI"] = nbt_tags.TypeByte(nbt["NoAI"])
        del nbt["NoAI"]

    if "NoGravity" in nbt and item_id.endswith("_bucket"):
        if "minecraft:bucket_entity_data" not in components:
            components["minecraft:bucket_entity_data"] = {}
        components["minecraft:bucket_entity_data"]["NoGravity"] = nbt_tags.TypeByte(nbt["NoGravity"])
        del nbt["NoGravity"]

    if "pages" in nbt:
        if item_id == "minecraft:writable_book":
            if "minecraft:writable_book_content" not in components:
                components["minecraft:writable_book_content"] = {}
            writable_book_content = components["minecraft:writable_book_content"]
            if "pages" not in writable_book_content:
                writable_book_content["pages"] = nbt_tags.TypeList([])
            pages = writable_book_content["pages"]
            for page in nbt["pages"]:
                pages.append({"raw": page})

        else:
            if "minecraft:written_book_content" not in components:
                components["minecraft:written_book_content"] = {}
            written_book_content = components["minecraft:written_book_content"]
            if "pages" not in written_book_content:
                written_book_content["pages"] = nbt_tags.TypeList([])
            pages = written_book_content["pages"]
            for page in nbt["pages"]:
                pages.append({"raw": page})

        del nbt["pages"]

    if "Potion" in nbt:
        if "minecraft:potion_contents" not in components:
            components["minecraft:potion_contents"] = {}
        components["minecraft:potion_contents"]["potion"] = nbt["Potion"]
        del nbt["Potion"]

    if "Recipes" in nbt:
        if "minecraft:recipes" not in components:
            components["minecraft:recipes"] = nbt_tags.TypeList([])
        for recipe in nbt["Recipes"]:
            components["minecraft:recipes"].append(miscellaneous.namespace(recipe))
        del nbt["Recipes"]

    if "RepairCost" in nbt:
        components["minecraft:repair_cost"] = nbt_tags.TypeInt(nbt["RepairCost"])
        del nbt["RepairCost"]

    if "resolved" in nbt:
        if "minecraft:written_book_content" not in components:
            components["minecraft:written_book_content"] = {}
        written_book_content = components["minecraft:written_book_content"]
        written_book_content["resolved"] = nbt_tags.TypeByte(nbt["resolved"])
        del nbt["resolved"]

    if "Silent" in nbt and item_id.endswith("_bucket"):
        if "minecraft:bucket_entity_data" not in components:
            components["minecraft:bucket_entity_data"] = {}
        components["minecraft:bucket_entity_data"]["Silent"] = nbt_tags.TypeByte(nbt["Silent"])
        del nbt["Silent"]

    if "SkullOwner" in nbt:
        if "minecraft:profile" not in components:
            components["minecraft:profile"] = {}
        profile = components["minecraft:profile"]
        skull_owner = nbt["SkullOwner"]
        if isinstance(skull_owner, str):
            profile["name"] = skull_owner
        else:
            if "Name" in skull_owner:
                profile["name"] = skull_owner["Name"]
            if "Id" in skull_owner:
                profile["id"] = miscellaneous.uuid_from_string(skull_owner["Id"], version, issues)
            if "Properties" in skull_owner:
                if "properties" not in profile:
                    profile["properties"] = nbt_tags.TypeList([])
                properties: list = profile["properties"]
                if "textures" in skull_owner["Properties"]:
                    textures: list[dict[str, Any]] = skull_owner["Properties"]["textures"]
                    for texture in textures:
                        property_entry = {"name": "textures"}
                        if "Value" in texture:
                            property_entry["value"] = texture["Value"]
                        if "Signature" in texture:
                            property_entry["signature"] = texture["Signature"]
                        properties.append(property_entry)
        del nbt["SkullOwner"]

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
        if "minecraft:written_book_content" not in components:
            components["minecraft:written_book_content"] = {}
        written_book_content = components["minecraft:written_book_content"]
        written_book_content["title"] = {"raw": nbt["title"]}
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

    if "Variant" in nbt and item_id.endswith("_bucket"):
        if "minecraft:bucket_entity_data" not in components:
            components["minecraft:bucket_entity_data"] = {}
        components["minecraft:bucket_entity_data"]["Variant"] = nbt_tags.TypeInt(nbt["Variant"])
        del nbt["Variant"]

    if "HideFlags" in nbt:
        if nbt["HideFlags"].value%2 == 1 and "minecraft:enchantments" in components:
            components["minecraft:enchantments"]["show_in_tooltip"] = nbt_tags.TypeByte(0)
        if nbt["HideFlags"].value//2%2 == 1 and "minecraft:minecraft:attribute_modifiers" in components:
            components["minecraft:minecraft:attribute_modifiers"]["show_in_tooltip"] = nbt_tags.TypeByte(0)
        if nbt["HideFlags"].value//4%2 == 1 and "minecraft:unbreakable" in components:
            components["minecraft:unbreakable"]["show_in_tooltip"] = nbt_tags.TypeByte(0)
        if nbt["HideFlags"].value//8%2 == 1 and "minecraft:can_break" in components:
            components["minecraft:can_break"]["show_in_tooltip"] = nbt_tags.TypeByte(0)
        if nbt["HideFlags"].value//16%2 == 1 and "minecraft:can_place_on" in components:
            components["minecraft:can_place_on"]["show_in_tooltip"] = nbt_tags.TypeByte(0)
        if nbt["HideFlags"].value//32%2 == 1:
            if "minecraft:stored_enchantments" in components:
                components["minecraft:stored_enchantments"]["show_in_tooltip"] = nbt_tags.TypeByte(0)
            if "minecraft:hide_additional_tooltip" not in components:
                components["minecraft:hide_additional_tooltip"] = {}
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



def update_path(path_parts: list[str], version: int, issues: list[dict[str, str | int]]) -> list[str]:

    if defaults.DEBUG_MODE:
        log(f'Path: {path_parts}')

    if len(path_parts) < 2:
        return path_parts
    
    if path_parts[1] == "Age":
        return ["components", "minecraft:bucket_entity_data", "Age"]

    if path_parts[1] == "AttributeModifiers":
        if len(path_parts) == 2:
            return ["components", "minecraft:attribute_modifiers", "modifiers"]
        if len(path_parts) == 3:
            return ["components", "minecraft:attribute_modifiers", "modifiers", path_parts[2]]
        if path_parts[3] == "AttributeName":
            return ["components", "minecraft:attribute_modifiers", "modifiers", path_parts[2], "type"]
        if path_parts[3] == "Slot":
            return ["components", "minecraft:attribute_modifiers", "modifiers", path_parts[2], "slot"]
        if path_parts[3] == "UUID":
            return ["components", "minecraft:attribute_modifiers", "modifiers", path_parts[2], "uuid"] + path_parts[4:]
        if path_parts[3] == "Name":
            return ["components", "minecraft:attribute_modifiers", "modifiers", path_parts[2], "name"]
        if path_parts[3] == "Operation":
            return ["components", "minecraft:attribute_modifiers", "modifiers", path_parts[2], "operation"]
        if path_parts[3] == "Amount":
            return ["components", "minecraft:attribute_modifiers", "modifiers", path_parts[2], "amount"]
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Invalid child of item tag "AttributeModifiers{path_parts[2]}": {path_parts[3]}')
        return ["components", "minecraft:attribute_modifiers", "modifiers", path_parts[2]]

    if path_parts[1] == "author":
        return ["components", "minecraft:written_book_content", "author"]

    if path_parts[1] == "BlockEntityTag":
        if len(path_parts) == 2:
            return ["components", "minecraft:block_entity_data"]
        if path_parts[2] == "Base":
            return ["components", "minecraft:base_color"]
        if path_parts[2] == "Bees":
            if len(path_parts) == 3:
                return ["components", "minecraft:bees"]
            if len(path_parts) == 4:
                return ["components", "minecraft:bees", path_parts[3]]
            if path_parts[4] == "EntityData":
                return ["components", "minecraft:bees", path_parts[3], "entity_data"] + path_parts[5:]
            if path_parts[4] == "TicksInHive":
                return ["components", "minecraft:bees", path_parts[3], "ticks_in_hive"]
            if path_parts[4] == "MinOccupationTicks":
                return ["components", "minecraft:bees", path_parts[3], "min_ticks_in_hive"]
        if path_parts[2] == "Items":
            if len(path_parts) == 3:
                return ["components", "minecraft:container"]
            if len(path_parts) == 4:
                return ["components", "minecraft:container", path_parts[3]]
            if path_parts[4] == "Slot":
                return ["components", "minecraft:container", path_parts[3], "slot"]
            if path_parts[4] == "id":
                return ["components", "minecraft:container", path_parts[3], "item", "id"]
            if path_parts[4] == "count":
                return ["components", "minecraft:container", path_parts[3], "item", "count"]
            if path_parts[4] == "components":
                return ["components", "minecraft:container", path_parts[3], "item", "components"] + path_parts[5:]
        if path_parts[2] == "Lock":
            return ["components", "minecraft:lock"]
        if path_parts[2] == "LootTable":
            return ["components", "minecraft:container_loot", "loot_table"]
        if path_parts[2] == "LootTableSeed":
            return ["components", "minecraft:container_loot", "seed"]
        if path_parts[2] == "note_block_sound":
            return ["components", "minecraft:note_block_sound"]
        if path_parts[2] == "Patterns":
            if len(path_parts) == 3:
                return ["components", "minecraft:banner_patterns"]
            if len(path_parts) == 4:
                return ["components", "minecraft:banner_patterns", path_parts[3]]
            if path_parts[4] == "Pattern":
                return ["components", "minecraft:banner_patterns", path_parts[3], "pattern"]
            if path_parts[4] == "Color":
                return ["components", "minecraft:banner_patterns", path_parts[3], "color"]
        if path_parts[2] == "sherds":
            return ["components", "minecraft:pot_decorations"] + path_parts[3:]
        return ["components", "minecraft:block_entity_tag"] + path_parts[2:]

    if path_parts[1] == "BlockStateTag":
        return ["components", "minecraft:block_state"] + path_parts[2:]

    if path_parts[1] == "BucketVariantTag":
        return ["components", "minecraft:bucket_entity_data", "Variant"]

    if path_parts[1] == "CanDestroy":
        if len(path_parts) == 2:
            return ["components", "minecraft:can_break", "predicates"]
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Children of item tag {path_parts[1]} are not handled yet in component conversion')
        return ["components", "minecraft:can_break"] + path_parts[2:]

    if path_parts[1] == "CanPlaceOn":
        if len(path_parts) == 2:
            return ["components", "minecraft:can_place_on"]
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Children of item tag {path_parts[1]} are not handled yet in component conversion')
        return ["components", "minecraft:can_place_on"] + path_parts[2:]

    if path_parts[1] == "Charged":
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Item tag "Charged" was removed')
        return ["components", "minecraft:charged_projectiles"]

    if path_parts[1] == "ChargedProjectiles":
        return ["components", "minecraft:charged_projectiles"] + path_parts[2:]

    if path_parts[1] == "CustomModelData":
        return ["components", "minecraft:custom_model_data"]

    if path_parts[1] == "CustomPotionColor":
        return ["components", "minecraft:potion_contents", "custom_color"]

    if path_parts[1] == "custom_potion_effects":
        return ["components", "minecraft:potion_contents", "custom_effects"] + path_parts[2:]

    if path_parts[1] == "Damage":
        return ["components", "minecraft:damage"]

    if path_parts[1] == "DebugProperty":
        if len(path_parts) == 2:
            return ["components", "minecraft:debug_stick_state"]
        return ["components", "minecraft:debug_stick_state", miscellaneous.namespace(path_parts[2])] + path_parts[3:]

    if path_parts[1] == "Decorations":
        if len(path_parts) == 2:
            return ["components", "minecraft:map_decorations"]
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Children of item tag "Decorations" are not handled yet in component conversion')
        return ["components", "minecraft:map_decorations"] + path_parts[2:]

    if path_parts[1] == "display":
        if len(path_parts) == 2:
            if defaults.SEND_WARNINGS:
                log(f'WARNING: Item tag "display" cannot properly be fetched on its own as a component')
            return ["components", "minecraft:custom_name"]
        if path_parts[2] == "Name":
            return ["components", "minecraft:custom_name"]
        if path_parts[2] == "Lore":
            return ["components", "minecraft:lore"] + path_parts[3:]
        if path_parts[2] == "color":
            return ["components", "minecraft:dyed_color", "rgb"]
        if path_parts[2] == "MapColor":
            return ["components", "minecraft:map_color"]
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Invalid child of item tag "display": {path_parts[2]}')
        return ["components", "minecraft:custom_name"]

    if path_parts[1] == "effects":
        return ["components", "minecraft:suspicious_stew_effects"] + path_parts[2:]

    if path_parts[1] == "Enchantments":
        if len(path_parts) == 2:
            return ["components", "minecraft:enchantments"]
        # Get specific enchantment index if an object with an ID is defined
        if path_parts[2].startswith("["):
            index = path_parts[2][1:-1].strip()
            if index.startswith("{"):
                unpacked_index = cast(dict[str, Any], nbt_tags.unpack(index))
                if (
                    "id" in unpacked_index and
                    "lvl" not in unpacked_index and
                    len(path_parts) == 4 and
                    path_parts[3] == "lvl"
                ):
                    return ["components", "minecraft:enchantments", "levels", unpacked_index["id"]]
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Children of item tag {path_parts[1]} are not handled yet in component conversion')
        return ["components", "minecraft:enchantments"] + path_parts[2:]

    if path_parts[1] == "EntityTag":
        return ["components", "minecraft:entity_data"] + path_parts[2:]

    if path_parts[1] == "Explosion":
        if len(path_parts) == 2:
            return ["components", "minecraft:firework_explosion"]
        if path_parts[2] == "Type":
            return ["components", "minecraft:firework_explosion", "shape"]
        if path_parts[2] == "Colors":
            return ["components", "minecraft:firework_explosion", "colors"] + path_parts[3:]
        if path_parts[2] == "FadeColors":
            return ["components", "minecraft:firework_explosion", "fade_colors"] + path_parts[3:]
        if path_parts[2] == "Trail":
            return ["components", "minecraft:firework_explosion", "has_trail"]
        if path_parts[2] == "Flicker":
            return ["components", "minecraft:firework_explosion", "has_twinkle"]
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Invalid child of item tag "Explosion": {path_parts[2]}')
        return ["components", "minecraft:firework_explosion"]

    if path_parts[1] == "Fireworks":
        if len(path_parts) == 2:
            return ["components", "minecraft:fireworks"]
        if path_parts[2] == "Explosions":
            if len(path_parts) == 3:
                return ["components", "minecraft:fireworks", "explosions"]
            if len(path_parts) == 4:
                return ["components", "minecraft:fireworks", "explosions", path_parts[3]]
            if path_parts[4] == "Type":
                return ["components", "minecraft:fireworks", "explosions", path_parts[3], "shape"]
            if path_parts[4] == "Colors":
                return ["components", "minecraft:fireworks", "explosions", path_parts[3], "colors"] + path_parts[5:]
            if path_parts[4] == "FadeColors":
                return ["components", "minecraft:fireworks", "explosions", path_parts[3], "fade_colors"] + path_parts[5:]
            if path_parts[4] == "Trail":
                return ["components", "minecraft:fireworks", "explosions", path_parts[3], "has_trail"]
            if path_parts[4] == "Flicker":
                return ["components", "minecraft:fireworks", "explosions", path_parts[3], "has_twinkle"]
            if defaults.SEND_WARNINGS:
                log(f'WARNING: Invalid child of item tag "Fireworks.Explosions{path_parts[3]}": {path_parts[4]}')
            return ["components", "minecraft:fireworks", "explosions", path_parts[3]]
        if path_parts[2] == "Flight":
            return ["components", "minecraft:fireworks", "flight_duration"]
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Invalid child of item tag "Fireworks": {path_parts[2]}')
        return ["components", "minecraft:fireworks"]

    if path_parts[1] == "generation":
        return ["components", "minecraft:written_book_content", "generation"]

    if path_parts[1] == "Glowing":
        return ["components", "minecraft:bucket_entity_data", "Glowing"]

    if path_parts[1] == "Health":
        return ["components", "minecraft:bucket_entity_data", "Health"]
    
    if path_parts[1] == "HideFlags":
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Item tag {path_parts[1]} cannot be converted for NBT paths')
        return ["components", "minecraft:custom_data", "HideFlags"]

    if path_parts[1] == "HuntingCooldown":
        return ["components", "minecraft:bucket_entity_data", "HuntingCooldown"]

    if path_parts[1] == "instrument":
        return ["components", "minecraft:instrument"]

    if path_parts[1] == "Invulnerable":
        return ["components", "minecraft:bucket_entity_data", "Invulnerable"]

    if path_parts[1] == "Items":
        return ["components", "minecraft:bundle_contents"] + path_parts[2:]

    if path_parts[1] == "LodestoneDimension":
        return ["components", "minecraft:lodestone_tracker", "target", "dimension"]

    if path_parts[1] == "LodestonePos":
        if len(path_parts) == 2:
            return ["components", "minecraft:lodestone_tracker", "target", "pos"]
        return ["components", "minecraft:lodestone_tracker", "target", "pos", f'[{["X", "Y", "Z"].index(path_parts[2])}]']

    if path_parts[1] == "LodestoneTracked":
        return ["components", "minecraft:lodestone_tracker", "target", "tracked"]

    if path_parts[1] == "map":
        return ["components", "minecraft:map_id"]

    if path_parts[1] == "NoAI":
        return ["components", "minecraft:bucket_entity_data", "NoAI"]

    if path_parts[1] == "NoGravity":
        return ["components", "minecraft:bucket_entity_data", "NoGravity"]

    if path_parts[1] == "pages":
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Item tag {path_parts[1]} depends on item context, item is either minecraft:writable_book or minecraft:written_book')
        if len(path_parts) == 2:
            return ["components", "minecraft:written_book_content", "pages"]
        return ["components", "minecraft:written_book_content", "pages", path_parts[2], "raw"]

    if path_parts[1] == "Potion":
        return ["components", "minecraft:potion_contents", "potion"] + path_parts[2:]

    if path_parts[1] == "Recipes":
        return ["components", "minecraft:recipes"] + path_parts[2:]

    if path_parts[1] == "RepairCost":
        return ["components", "minecraft:repair_cost"]

    if path_parts[1] == "resolved":
        return ["components", "minecraft:written_book_content", "resolved"]

    if path_parts[1] == "Silent":
        return ["components", "minecraft:bucket_entity_data", "Silent"]

    if path_parts[1] == "SkullOwner":
        if len(path_parts) == 2:
            return ["components", "minecraft:profile", "name"]
        if path_parts[2] == "Name":
            return ["components", "minecraft:profile", "name"]
        if path_parts[2] == "Id":
            return ["components", "minecraft:profile", "id"] + path_parts[3:]
        if path_parts[2] == "Properties":
            if len(path_parts) == 3:
                return ["components", "minecraft:profile", "properties"]
            if path_parts[3] == "textures":
                if len(path_parts) == 4:
                    return ["components", "minecraft:profile", "properties"]
                if len(path_parts) == 5:
                    return ["components", "minecraft:profile", "properties", path_parts[4]]
                if path_parts[5] == "Value":
                    return ["components", "minecraft:profile", "properties", path_parts[4], "value"]
                if path_parts[5] == "Signature":
                    return ["components", "minecraft:profile", "properties", path_parts[4], "signature"]
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Invalid child of item tag "SkullOwner": {path_parts[2]}')
        return ["components", "minecraft:profile", "name"]

    if path_parts[1] == "StoredEnchantments":
        if len(path_parts) == 2:
            return ["components", "minecraft:stored_enchantments"]
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Children of item tag {path_parts[1]} are not handled yet in component conversion')
        return ["components", "minecraft:stored_enchantments"] + path_parts[2:]

    if path_parts[1] == "title":
        return ["components", "minecraft:written_book_content", "title", "raw"]

    if path_parts[1] == "Trim":
        if len(path_parts) == 2:
            return ["components", "minecraft:trim"]
        if path_parts[2] == "pattern":
            return ["components", "minecraft:trim", "pattern"]
        if path_parts[2] == "material":
            return ["components", "minecraft:trim", "material"]
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Invalid child of item tag "Trim": {path_parts[2]}')
        return ["components", "minecraft:trim"]

    if path_parts[1] == "Unbreakable":
        return ["components", "minecraft:unbreakable"]

    if path_parts[1] == "Variant":
        return ["components", "minecraft:bucket_entity_data", "Variant"]
    

    return ["components", "minecraft:custom_data"] + path_parts[1:]