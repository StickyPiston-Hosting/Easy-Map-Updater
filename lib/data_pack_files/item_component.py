# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from typing import cast, Any
from lib.log import log
from lib import defaults
from lib import utils
from lib import option_manager
from lib.data_pack_files import command_helper
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import nbt_to_json
import easy_map_updater



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

    def is_instance(self, object) -> bool:
        return isinstance(self.value, object)


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

    def set_separator(self, key: str, separator: str):
        for component in self.components:
            if isinstance(component, ItemComponent) and component.key == key:
                component.separator = separator

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
    
    def __delitem__(self, key: str):
        for i in range(len(self.components)):
            component = self.components[i]
            if isinstance(component, ItemComponent) and component.key == key:
                del self.components[i]
                return



# Import more stuff to prevent circular loading issues

from lib.data_pack_files import blocks
from lib.data_pack_files import items
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import json_text_component
from lib.data_pack_files import arguments
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import ids
from lib.data_pack_files import entities



# Set constants

default_components = {
    "minecraft:banner_patterns": [
        "minecraft:white_banner",
        "minecraft:orange_banner",
        "minecraft:magenta_banner",
        "minecraft:light_blue_banner",
        "minecraft:yellow_banner",
        "minecraft:lime_banner",
        "minecraft:pink_banner",
        "minecraft:gray_banner",
        "minecraft:light_gray_banner",
        "minecraft:cyan_banner",
        "minecraft:purple_banner",
        "minecraft:blue_banner",
        "minecraft:brown_banner",
        "minecraft:green_banner",
        "minecraft:red_banner",
        "minecraft:black_banner",
    ],
    "minecraft:bees": ["minecraft:bee_nest", "minecraft:beehive"],
    "minecraft:block_entity_data": [],
    "minecraft:block_state": [],
    "minecraft:bundle_contents": ["minecraft:bundle"],
    "minecraft:charged_projectiles": ["minecraft:crossbow"],
    "minecraft:container": [],
    "minecraft:container_loot": [],
    "minecraft:firework_explosion": ["minecraft:firework_star"],
    "minecraft:fireworks": ["minecraft:firework_rocket"],
    "minecraft:instrument": ["minecraft:note_block"],
    "minecraft:map_id": ["minecraft:filled_map"],
    "minecraft:painting/variant": ["minecraft:painting"],
    "minecraft:pot_decorations": ["minecraft:decorated_pot"],
    "minecraft:potion_contents": ["minecraft:potion"],
    "minecraft:tropical_fish/pattern": ["minecraft:tropical_fish_bucket"],
    "minecraft:written_book_content": ["minecraft:written_book"],
}



# Define functions

def conform_components(item_id: str, components: ItemComponents, version: int, issues: list[dict[str, str | int]], read: bool) -> ItemComponents:
    # Apply namespace to all components
    components.set_namespaces()


    # In at least 1.21.5 (maybe earlier), potion names cannot be assigned by minecraft:item_name
    if (
        item_id in ["minecraft:potion", "minecraft:splash_potion", "minecraft:lingering_potion"] and
        "minecraft:item_name" in components and
        "minecraft:custom_name" not in components
    ):
        name = nbt_tags.unpack(nbt_tags.pack(components["minecraft:item_name"]))
        if isinstance(name, str):
            name = {"text": name, "italic": nbt_tags.TypeByte(0)}
        elif isinstance(name, dict):
            if "italic" not in name:
                name["italic"] = nbt_tags.TypeByte(0)
        elif isinstance(name, nbt_tags.TypeList) or isinstance(name, list):
            if len(name) > 0:
                name_entry = name[0]
                if isinstance(name_entry, str):
                    name_entry = {"text": name_entry, "italic": nbt_tags.TypeByte(0)}
                elif isinstance(name_entry, dict):
                    if "italic" not in name_entry:
                        name_entry["italic"] = nbt_tags.TypeByte(0)
                name[0] = name_entry
        components["minecraft:custom_name"] = name


    # minecraft:food component got extracted out in 1.21.2
    if "minecraft:food" in components and "minecraft:consumable" not in components:
        food: dict[str, Any] = components["minecraft:food"]
        consumable = {}
        if "eat_seconds" in food:
            consumable["consume_seconds"] = food["eat_seconds"]
            del food["eat_seconds"]
        if "effects" in food:
            on_consume_effect = {
                "type": "minecraft:apply_effects",
                "effects": food["effects"],
            }
            consumable["on_consume_effects"] = nbt_tags.TypeList([on_consume_effect])
            del food["effects"]
        if consumable:
            components["minecraft:consumable"] = consumable
        if "using_converts_to" in food:
            components["minecraft:use_remainder"] = food["using_converts_to"]
            del food["using_converts_to"]


    # In 1.21.5, minecraft:hide_additional_tooltip, minecraft:hide_tooltip, and the show_in_tooltip were removed
    if "minecraft:hide_additional_tooltip" in components:
        if "minecraft:tooltip_display" in components:
            tooltip_display = components["minecraft:tooltip_display"]
        else:
            tooltip_display = {}
        if "hidden_components" not in tooltip_display:
            tooltip_display["hidden_components"] = nbt_tags.TypeList([])

        for component_id in default_components:
            if component_id in components:
                tooltip_display["hidden_components"].append(component_id)
            elif item_id in default_components[component_id]:
                tooltip_display["hidden_components"].append(component_id)
        del components["minecraft:hide_additional_tooltip"]

        if tooltip_display["hidden_components"]:
            components["minecraft:tooltip_display"] = tooltip_display

    if "minecraft:hide_tooltip" in components:
        if "minecraft:tooltip_display" not in components:
            components["minecraft:tooltip_display"] = {}
        components["minecraft:tooltip_display"]["hide_tooltip"] = nbt_tags.TypeByte(1)
        del components["minecraft:hide_tooltip"]

    for component_id in [
        "minecraft:attribute_modifiers",
        "minecraft:dyed_color",
        "minecraft:can_place_on",
        "minecraft:can_break",
        "minecraft:enchantments",
        "minecraft:stored_enchantments",
        "minecraft:jukebox_playable",
        "minecraft:trim",
        "minecraft:unbreakable",
    ]:
        if component_id not in components:
            continue
        component = components[component_id]
        if not isinstance(component, dict):
            continue
        if "show_in_tooltip" in component:
            if component["show_in_tooltip"].value == 0:
                if "minecraft:tooltip_display" not in components:
                    components["minecraft:tooltip_display"] = {}
                tooltip_display = components["minecraft:tooltip_display"]
                if "hidden_components" not in tooltip_display:
                    tooltip_display["hidden_components"] = nbt_tags.TypeList([])
                
                tooltip_display["hidden_components"].append(component_id)
            
            del component["show_in_tooltip"]



    # Adjust formatting of components
    for component in components.components:
        if isinstance(component, ItemComponent):
            conform_component(component, version)
        else:
            for alternative in component.alternatives:
                conform_component(alternative, version)

                if alternative.key == "minecraft:food":
                    food = alternative.value
                    if "eat_seconds" in food:
                        del food["eat_seconds"]
                    if "effects" in food:
                        del food["effects"]
                    if "using_converts_to" in food:
                        del food["using_converts_to"]

                if alternative.key in [
                    "minecraft:attribute_modifiers",
                    "minecraft:dyed_color",
                    "minecraft:can_place_on",
                    "minecraft:can_break",
                    "minecraft:enchantments",
                    "minecraft:stored_enchantments",
                    "minecraft:jukebox_playable",
                    "minecraft:trim",
                    "minecraft:unbreakable",
                ]:
                    component = alternative.value
                    if not isinstance(component, dict):
                        continue
                    if "show_in_tooltip" in component:
                        del component["show_in_tooltip"]


    # In 1.21.2, container locks got converted into item predicates
    # The raw character data of the custom name will be extracted out into the item name for comparison
    if version <= 2101 and "minecraft:custom_name" in components and option_manager.FIXES["lock_fixer"]:
        components["minecraft:item_name"] = json_text_component.convert_lock_string(components["minecraft:custom_name"])
        if "minecraft:custom_data" not in components:
            components["minecraft:custom_data"] = {}
        components["minecraft:custom_data"]["emu_lock_name"] = components["minecraft:custom_name"]


    return components


def conform_component(component: ItemComponent, version: int):

    if component.value is None:
        return

    if component.key == "minecraft:attribute_modifiers":
        attribute_modifiers = component.value
        if isinstance(attribute_modifiers, dict) and "modifiers" in attribute_modifiers:
            attribute_modifiers = attribute_modifiers["modifiers"]
        for attribute_modifier in attribute_modifiers:
            if "type" in attribute_modifier:
                attribute_modifier["type"] = miscellaneous.attribute(attribute_modifier["type"], version, [])
            if "name" in attribute_modifier:
                del attribute_modifier["name"]
            if "uuid" in attribute_modifier:
                attribute_modifier["id"] = miscellaneous.namespace(
                    utils.uuid_from_int_array([entry.value for entry in attribute_modifier["uuid"]])
                )
                del attribute_modifier["uuid"]
            if "display" in attribute_modifier:
                if "value" in attribute_modifier["display"]:
                    attribute_modifier["display"]["value"] = json_text_component.update(attribute_modifier["display"]["value"], version, [], {"mangled": False, "pack": False})
        component.value = attribute_modifiers

    if component.key == "minecraft:bees":
        for bee in component.value:
            if "entity_data" in bee:
                bee["entity_data"] = nbt_tags.direct_update(bee["entity_data"], version, [], "entity", bee["entity_data"]["id"] if "id" in bee["entity_data"] else "", False)

    if component.key == "minecraft:block_entity_data":
        component.value = nbt_tags.direct_update(component.value, version, [], "block", component.value["id"] if "id" in component.value else "", False)

    if component.key == "minecraft:bundle_contents":
        for i in range(len(component.value)):
            component.value[i] = nbt_tags.direct_update(component.value[i], version, [], "item", component.value[i]["id"] if "id" in component.value else "", False)

    if component.key == "minecraft:can_break":
        can_break: dict[str, Any] | nbt_tags.TypeList = component.value
        if isinstance(can_break, dict) and "predicates" in can_break:
            can_break = can_break["predicates"]
        if isinstance(can_break, dict):
            can_break = nbt_tags.TypeList([can_break])
        for predicate in cast(nbt_tags.TypeList, can_break):
            if "blocks" in predicate:
                if isinstance(predicate["blocks"], nbt_tags.TypeList):
                    if len(predicate["blocks"]) == 1:
                        predicate["blocks"] = blocks.update_from_command(predicate["blocks"][0], version, [])
                    else:
                        for i in range(len(predicate["blocks"])):
                            predicate["blocks"][i] = blocks.update_from_command(predicate["blocks"][i], version, [])
                else:
                    predicate["blocks"] = blocks.update_from_command(predicate["blocks"], version, [])
        if len(can_break) == 1:
            can_break = can_break[0]
        component.value = can_break

    if component.key == "minecraft:can_place_on":
        can_place_on: dict[str, Any] | nbt_tags.TypeList = component.value
        if isinstance(can_place_on, dict) and "predicates" in can_place_on:
            can_place_on = can_place_on["predicates"]
        if isinstance(can_place_on, dict):
            can_place_on = nbt_tags.TypeList([can_place_on])
        for predicate in cast(nbt_tags.TypeList, can_place_on):
            if "blocks" in predicate:
                if isinstance(predicate["blocks"], nbt_tags.TypeList):
                    if len(predicate["blocks"]) == 1:
                        predicate["blocks"] = blocks.update_from_command(predicate["blocks"][0], version, [])
                    else:
                        for i in range(len(predicate["blocks"])):
                            predicate["blocks"][i] = blocks.update_from_command(predicate["blocks"][i], version, [])
                else:
                    predicate["blocks"] = blocks.update_from_command(predicate["blocks"], version, [])
        if len(can_place_on) == 1:
            can_place_on = can_place_on[0]
        component.value = can_place_on

    if component.key == "minecraft:charged_projectiles":
        for i in range(len(component.value)):
            component.value[i] = nbt_tags.direct_update(component.value[i], version, [], "item", component.value[i]["id"] if "id" in component.value else "", False)

    if component.key == "minecraft:consumable":
        consumable: dict[str, Any] = component.value
        if "on_consume_effects" in consumable:
            for on_consume_effect in consumable["on_consume_effects"]:
                if "type" not in on_consume_effect:
                    continue
                on_consume_effect["type"] = miscellaneous.namespace(on_consume_effect["type"])
                if on_consume_effect["type"] == "minecraft:apply_effects":
                    if "effects" in on_consume_effect:
                        for effect in on_consume_effect["effects"]:
                            if "id" in effect:
                                effect["id"] = ids.effect(effect["id"], version, [])
                if on_consume_effect["type"] == "minecraft:remove_effects":
                    if "effects" in on_consume_effect:
                        for i in range(len(on_consume_effect["effects"])):
                            on_consume_effect["effects"][i] = ids.effect(on_consume_effect["effects"][i], version, [])

    if component.key == "minecraft:custom_data":
        custom_data: dict[str, Any] = component.value
        if "emu_lock_name" in custom_data and version <= 2104:
            custom_data["emu_lock_name"] = json_text_component.update(custom_data["emu_lock_name"], version, [], {"mangled": True})
        component.value = nbt_tags.process_arbitrary_nbt(component.value, version)

    if component.key == "minecraft:custom_model_data":
        if version <= 2103 and not component.is_instance(dict):
            component.value = {
                "floats": nbt_tags.TypeList([nbt_tags.TypeFloat(component.value)])
            }

    if component.key == "minecraft:custom_name":
        component.value = json_text_component.update(component.value, version, [], {"mangled": True, "pack": False})

    if component.key == "minecraft:death_protection":
        if "death_effects" in component.value:
            for death_effect in component.value["death_effects"]:
                if "effects" in death_effect:
                    if isinstance(death_effect["effects"], nbt_tags.TypeList):
                        for i in range(len(death_effect["effects"])):
                            if isinstance(death_effect["effects"][i], dict):
                                if "id" in death_effect["effects"][i]:
                                    death_effect["effects"][i]["id"] = ids.effect(death_effect["effects"][i]["id"], version, [])
                            else:
                                death_effect["effects"][i] = ids.effect(death_effect["effects"][i], version, [])
                    else:
                        death_effect["effects"] = ids.effect(death_effect["effects"], version, [])

    if component.key == "minecraft:debug_stick_state":
        debug_stick_state: dict[str, str] = component.value
        for block in list(debug_stick_state.keys()):
            updated_block = blocks.update_from_command(block, version, [])
            if block != updated_block:
                debug_stick_state[updated_block] = debug_stick_state[block]
                del debug_stick_state[block]

    if component.key == "minecraft:dyed_color":
        dyed_color = component.value
        if isinstance(dyed_color, dict) and "rgb" in dyed_color:
            dyed_color = dyed_color["rgb"]
        component.value = dyed_color

    if component.key == "minecraft:enchantments":
        enchantments: dict[str, Any] = component.value
        if "levels" in enchantments:
            enchantments = enchantments["levels"]
        
        for enchantment in list(enchantments.keys()):
            updated_enchantment = ids.enchantment(enchantment, version, [])
            if enchantment != updated_enchantment:
                enchantments[updated_enchantment] = enchantments[enchantment]
                del enchantments[enchantment]
            enchantments[updated_enchantment] = nbt_tags.TypeInt(min(max(enchantments[updated_enchantment].value, 0), 255))
        component.value = enchantments

    if component.key == "minecraft:entity_data":
        component.value = nbt_tags.direct_update(component.value, version, [], "entity", component.value["id"] if "id" in component.value else "", False)

    if component.key == "minecraft:equippable":
        if "model" in component.value:
            component.value["asset_id"] = component.value["model"]
            del component.value["model"]
        if "allowed_entities" in component.value:
            if isinstance(component.value["allowed_entities"], nbt_tags.TypeList):
                for i in range(len(component.value["allowed_entities"])):
                    component.value["allowed_entities"][i] = entities.update(component.value["allowed_entities"][i], version, [])
            else:
                component.value["allowed_entities"] = entities.update(component.value["allowed_entities"], version, [])

    if component.key == "minecraft:fire_resistant":
        component.key = "minecraft:damage_resistant"
        component.value = {"types": "#minecraft:is_fire"}

    if component.key == "minecraft:item_model" and version <= 2103:
        component.value = conform_item_model_component(component.value)

    if component.key == "minecraft:item_name":
        component.value = json_text_component.update(component.value, version, [], {"mangled": True, "pack": False})

    if component.key == "minecraft:lore":
        lore = component.value
        for i in range(len(lore)):
            lore[i] = json_text_component.update(lore[i], version, [], {"mangled": True, "pack": False})

    if component.key == "minecraft:painting/variant":
        painting_variant = component.value
        if isinstance(painting_variant, dict):
            painting_variant = command_helper.create_painting_variant(json.dumps(nbt_to_json.convert_painting_variant_to_json(painting_variant)))
        component.value = painting_variant

    if component.key == "minecraft:potion_contents":
        if not isinstance(component.value, dict):
            component.value = {"potion": component.value}
        if "custom_effects" in component.value:
            for custom_effect in component.value["custom_effects"]:
                if "id" in custom_effect:
                    custom_effect["id"] = ids.effect(custom_effect["id"], version, [])

    if component.key == "minecraft:profile":
        profile = component.value
        if not isinstance(profile, dict):
            profile = {"name": profile}
        component.value = profile

    if component.key == "minecraft:recipes":
        for i in range(len(component.value)):
            component.value[i] = items.update_from_command(component.value[i], version, [])

    if component.key == "minecraft:repairable":
        repairable: dict[str, str | nbt_tags.TypeList] = component.value
        if "items" in repairable:
            if isinstance(repairable["items"], nbt_tags.TypeList):
                for i in range(len(repairable["items"])):
                    cast(nbt_tags.TypeList, repairable["items"])[i] = items.update_from_command(repairable["items"][i], version, [])
            else:
                repairable["items"] = items.update_from_command(cast(str, repairable["items"]), version, [])

    if component.key == "minecraft:stored_enchantments":
        stored_enchantments: dict[str, Any] = component.value
        if "levels" in stored_enchantments:
            stored_enchantments = stored_enchantments["levels"]
        
        for enchantment in list(stored_enchantments.keys()):
            updated_enchantment = ids.enchantment(enchantment, version, [])
            if enchantment != updated_enchantment:
                stored_enchantments[updated_enchantment] = stored_enchantments[enchantment]
                del stored_enchantments[enchantment]
            stored_enchantments[updated_enchantment] = nbt_tags.TypeInt(min(max(stored_enchantments[updated_enchantment].value, 0), 255))
        component.value = stored_enchantments

    if component.key == "minecraft:suspicious_stew_effects":
        for suspicious_stew_effect in component.value:
            if "id" in suspicious_stew_effect:
                suspicious_stew_effect["id"] = ids.effect(suspicious_stew_effect["id"], version, [])

    if component.key == "minecraft:tool":
        if "rules" in component.value:
            for rule in component.value["rules"]:
                if "blocks" in rule:
                    if isinstance(rule["blocks"], nbt_tags.TypeList):
                        for i in range(len(rule["blocks"])):
                            rule["blocks"][i] = blocks.update_from_command(rule["blocks"], version, [])
                    else:
                        rule["blocks"] = blocks.update_from_command(rule["blocks"], version, [])

    if component.key == "minecraft:use_remainder":
        component.value = items.update_from_nbt(cast(items.ItemInputFromNBT, component.value), version, [])

    if component.key == "minecraft:weapon":
        weapon = component.value
        if "damage_per_attack" in weapon:
            weapon["item_damage_per_attack"] = weapon["damage_per_attack"]
            del weapon["damage_per_attack"]

    if component.key == "minecraft:writable_book_content":
        writable_book_content = component.value
        if "pages" not in writable_book_content:
            writable_book_content["pages"] = nbt_tags.TypeList([])
        pages = writable_book_content["pages"]
        for index in range(len(pages)):
            page = pages[index]
            if isinstance(page, str):
                pages[index] = {"raw": page}
            if "raw" in pages[index]:
                page_content = pages[index]["raw"]
            else:
                page_content = pages[index]
            pages[index] = {"raw": json_text_component.update(page_content, version, [], {"mangled": True, "pack": False})}

    if component.key == "minecraft:written_book_content":
        written_book_content = component.value
        if "pages" not in written_book_content:
            written_book_content["pages"] = nbt_tags.TypeList([])
        pages = written_book_content["pages"]
        for index in range(len(pages)):
            page = pages[index]
            if isinstance(page, str):
                pages[index] = {"raw": page}
            if "raw" in pages[index]:
                page_content = pages[index]["raw"]
            else:
                page_content = pages[index]
            pages[index] = {"raw": json_text_component.update(page_content, version, [], {"mangled": True, "pack": False})}



def conform_item_model_component(value: str) -> str:
    resource_pack_path = easy_map_updater.MINECRAFT_PATH / "resourcepacks" / option_manager.get_resource_pack()
    if not resource_pack_path.exists():
        log(f"WARNING: Resource pack must exist to update component minecraft:item_model")
    else:
        item_model = miscellaneous.namespace(value)
        updated_item_model = item_model.replace(":", "/")
        item_definition_path = resource_pack_path / "assets" / "emu" / "items" / f"{updated_item_model}.json"
        item_definition_path.parent.mkdir(parents=True, exist_ok=True)
        with item_definition_path.open("w", encoding="utf-8", newline="\n") as file:
            json.dump(
                {
                    "model": {
                        "type": "minecraft:model",
                        "model": item_model.replace(":", ":item/")
                    }
                },
                file,
                indent=4
            )
        value = f"emu:{updated_item_model}"
    return value



def conform_component_paths(path_parts: list[str], version: int, issues: list[dict[str, str | int]]) -> list[str]:
    
    if defaults.DEBUG_MODE:
        log(f'Path: {path_parts}')

    if len(path_parts) < 2:
        return path_parts
    
    if version <= 2103:
        if path_parts[1] == "minecraft:custom_model_data":
            return ["components", "minecraft:custom_model_data", "floats", "[0]", "__CUSTOM_MODEL_PATH__"]
        
    
    return path_parts




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
            components["minecraft:attribute_modifiers"] = nbt_tags.TypeList([])
        attribute_modifiers = components["minecraft:attribute_modifiers"]
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
            attribute_modifiers.append(attribute)
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
            components["minecraft:can_break"] = nbt_tags.TypeList([{"blocks": nbt_tags.TypeList([])}])
        can_break = components["minecraft:can_break"]
        block: str
        for block in nbt["CanDestroy"]:
            if block.startswith("#"):
                can_break.append({"blocks": block})
            else:
                if "[" in block:
                    can_break.append({
                        "blocks": block[:block.find("[")],
                        "state": blocks.unpack_block_states(block[block.find("["):])
                    })
                else:
                    can_break[0]["blocks"].append(block)
        if len(can_break[0]["blocks"]) == 0:
            can_break.pop(0)
        elif len(can_break[0]["blocks"]) == 1:
            can_break[0]["blocks"] = can_break[0]["blocks"][0]
        if len(can_break) == 1:
            can_break = can_break[0]
        del nbt["CanDestroy"]

    if "CanPlaceOn" in nbt:
        if "minecraft:can_place_on" not in components:
            components["minecraft:can_place_on"] = nbt_tags.TypeList([{"blocks": nbt_tags.TypeList([])}])
        can_place_on = components["minecraft:can_place_on"]
        block: str
        for block in nbt["CanPlaceOn"]:
            if block.startswith("#"):
                can_place_on.append({"blocks": block})
            else:
                if "[" in block:
                    can_place_on.append({
                        "blocks": block[:block.find("[")],
                        "state": blocks.unpack_block_states(block[block.find("["):])
                    })
                else:
                    can_place_on[0]["blocks"].append(block)
        if len(can_place_on[0]["blocks"]) == 0:
            can_place_on.pop(0)
        elif len(can_place_on[0]["blocks"]) == 1:
            can_place_on[0]["blocks"] = can_place_on[0]["blocks"][0]
        if len(can_place_on) == 1:
            can_place_on = can_place_on[0]
        del nbt["CanPlaceOn"]

    if "Charged" in nbt:
        if "minecraft:charged_projectiles" not in components:
            components["minecraft:charged_projectiles"] = nbt_tags.TypeList([])
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
        components["minecraft:custom_model_data"] = {
            "floats": nbt_tags.TypeList([nbt_tags.TypeFloat(nbt["CustomModelData"])])
        }
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
            if option_manager.FIXES["lock_fixer"]:
                components["minecraft:item_name"] = json_text_component.convert_lock_string(display["Name"])
        
        if "Lore" in display:
            components["minecraft:lore"] = display["Lore"]

        if "color" in display:
            components["minecraft:dyed_color"] = nbt_tags.TypeInt(display["color"])

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
        for enchantment in nbt["Enchantments"]:
            if "id" in enchantment:
                if "lvl" in enchantment:
                    enchantments[miscellaneous.namespace(enchantment["id"])] = nbt_tags.TypeInt(enchantment["lvl"])
                else:
                    enchantments[miscellaneous.namespace(enchantment["id"])] = nbt_tags.TypeInt(0)
        if len(enchantments) == 0:
            components["minecraft:enchantment_glint_override"] = nbt_tags.TypeByte(1)
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
        for item in nbt["Items"]:
            bundle_contents_entry: dict[str, Any] = {}
            if "id" in item:
                bundle_contents_entry["id"] = miscellaneous.namespace(item["id"])
            if "count" in item:
                bundle_contents_entry["count"] = nbt_tags.TypeInt(item["count"])
            if "components" in item:
                bundle_contents_entry["components"] = item["components"]
            bundle_contents.append(bundle_contents_entry)
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
        for stored_enchantment in nbt["StoredEnchantments"]:
            if "id" in stored_enchantment:
                if "lvl" in stored_enchantment:
                    stored_enchantments[miscellaneous.namespace(stored_enchantment["id"])] = nbt_tags.TypeInt(stored_enchantment["lvl"])
                else:
                    stored_enchantments[miscellaneous.namespace(stored_enchantment["id"])] = nbt_tags.TypeInt(0)
        if len(stored_enchantments) == 0:
            components["minecraft:enchantment_glint_override"] = nbt_tags.TypeByte(1)
            del components["minecraft:stored_enchantments"]
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
        if "minecraft:tooltip_display" in components:
            tooltip_display = components["minecraft:tooltip_display"]
        else:
            tooltip_display = {}
        if "hidden_components" not in tooltip_display:
            tooltip_display["hidden_components"] = nbt_tags.TypeList([])
        hidden_components = cast(nbt_tags.TypeList, tooltip_display["hidden_components"])

        if nbt["HideFlags"].value%2 == 1:
            hidden_components.append("minecraft:enchantments")
        if nbt["HideFlags"].value//2%2 == 1:
            hidden_components.append("minecraft:attribute_modifiers")
        if nbt["HideFlags"].value//4%2 == 1:
            hidden_components.append("minecraft:unbreakable")
        if nbt["HideFlags"].value//8%2 == 1:
            hidden_components.append("minecraft:can_break")
        if nbt["HideFlags"].value//16%2 == 1:
            hidden_components.append("minecraft:can_place_on")
        if nbt["HideFlags"].value//32%2 == 1:
            hidden_components.append("minecraft:stored_enchantments")

            for component_id in default_components:
                if component_id in components:
                    hidden_components.append(component_id)
                elif item_id in default_components[component_id]:
                    hidden_components.append(component_id)

        if nbt["HideFlags"].value//64%2 == 1:
            hidden_components.append("minecraft:dyed_color")
        if nbt["HideFlags"].value//128%2 == 1:
            hidden_components.append("minecraft:trim")
        del nbt["HideFlags"]

        if hidden_components:
            components["minecraft:tooltip_display"] = tooltip_display

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
    
    if path_parts[1].startswith("{"):
        updated_nbt = nbt_tags.update(path_parts[1], version, issues, "item_tag")
        updated_path = update_path(path_parts[:1] + path_parts[2:], version, issues)
        updated_path.insert(1, updated_nbt)
        return updated_path
    
    if path_parts[1] == "Age":
        return ["components", "minecraft:bucket_entity_data", "Age"]

    if path_parts[1] == "AttributeModifiers":
        if len(path_parts) == 2:
            return ["components", "minecraft:attribute_modifiers"]
        if len(path_parts) == 3:
            return ["components", "minecraft:attribute_modifiers", path_parts[2]]
        if path_parts[3] == "AttributeName":
            return ["components", "minecraft:attribute_modifiers", path_parts[2], "type"]
        if path_parts[3] == "Slot":
            return ["components", "minecraft:attribute_modifiers", path_parts[2], "slot"]
        if path_parts[3] == "UUID":
            return ["components", "minecraft:attribute_modifiers", path_parts[2], "uuid"] + path_parts[4:]
        if path_parts[3] == "Name":
            return ["components", "minecraft:attribute_modifiers", path_parts[2], "name"]
        if path_parts[3] == "Operation":
            return ["components", "minecraft:attribute_modifiers", path_parts[2], "operation"]
        if path_parts[3] == "Amount":
            return ["components", "minecraft:attribute_modifiers", path_parts[2], "amount"]
        if defaults.SEND_WARNINGS:
            log(f'WARNING: Invalid child of item tag "AttributeModifiers{path_parts[2]}": {path_parts[3]}')
        return ["components", "minecraft:attribute_modifiers", path_parts[2]]

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
            return ["components", "minecraft:can_break"]
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
        return ["components", "minecraft:custom_model_data", "floats", "[0]"]

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
            return ["components", "minecraft:dyed_color"]
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
                    return ["components", "minecraft:enchantments", unpacked_index["id"]]
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