# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from typing import cast, Any
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import miscellaneous



# Define functions

def convert_block_to_json(block: dict[str, Any]) -> dict[str, Any]:
    block = cast(dict, nbt_tags.convert_to_json(block))
    return conform_block_to_json(block)

def conform_block_to_json(block: dict[str, Any]) -> dict[str, Any]:

    if "keepPacked" in block:
        block["keepPacked"] = bool(block["keepPacked"])

    if "components" in block:
        block["components"] = conform_item_components_to_json(block["components"])

    if "Items" in block:
        for i in range(len(block["Items"])):
            block["Items"][i] = conform_item_to_json(block["Items"][i])

    return block



def convert_entity_to_json(entity: dict[str, Any]) -> dict[str, Any]:
    entity = cast(dict, nbt_tags.convert_to_json(entity))
    return conform_entity_to_json(entity)

def conform_entity_to_json(entity: dict[str, Any]) -> dict[str, Any]:

    # Handle root booleans
    for tag in [
        "CanPickUpLoot",
        "CustomNameVisible",
        "Fixed",
        "Glowing",
        "HasVisualFire",
        "Invisible",
        "Invulnerable",
        "LeftHanded",
        "NoAI",
        "NoGravity",
        "OnGround",
        "PersistenceRequired",
        "Silent",
    ]:
        if tag in entity:
            entity[tag] = bool(entity[tag])

    # Handle name
    if "CustomName" in entity:
        entity["CustomName"] = conform_text_component_to_json(entity["CustomName"])

    # Handle items
    for key in [
        "ArmorItems",
        "HandItems",
        "Inventory",
    ]:
        if key in entity:
            for i in range(len(entity[key])):
                entity[key][i] = conform_item_to_json(entity[key][i])
    for key in ["body_armor_item"]:
        if key in entity:
            entity[key] = conform_item_to_json(entity[key])
    if "equipment" in entity:
        for key in entity["equipment"]:
            entity["equipment"][key] = conform_item_to_json(entity["equipment"][key])

    # Handle effects
    for effect_key in [
        "active_effects",
        "effects",
    ]:
        if effect_key in entity:
            for effect in entity[effect_key]:
                for key in [
                    "ambient",
                    "show_icon",
                    "show_particles",
                ]:
                    if key in effect:
                        effect[key] = bool(effect[key])



    # Handle brain
    if "Brain" in entity:
        if "memories" in entity["Brain"]:
            memories = entity["Brain"]["memories"]
            for key in [
                "minecraft:admiring_disabled",
                "minecraft:admiring_item",
                "minecraft:hunted_recently",
                "minecraft:universal_anger",
                "minecraft:golem_detected_recently",
                "minecraft:has_hunting_cooldown",
                "minecraft:is_tempted",
            ]:
                if key in memories:
                    if "value" in memories[key]:
                        memories[key]["value"] = bool(memories[key]["value"])
                



    return entity



def convert_item_to_json(item: dict[str, Any]) -> dict[str, Any]:
    item = cast(dict, nbt_tags.convert_to_json(item))
    return conform_item_to_json(item)

def conform_item_to_json(item: dict[str, Any]) -> dict[str, Any]:
    if "components" in item:
        item["components"] = conform_item_components_to_json(item["components"])

    return item



def convert_item_components_to_json(components: dict[str, Any]) -> dict[str, Any]:
    components = cast(dict, nbt_tags.convert_to_json(components))
    return conform_item_components_to_json(components)

def conform_item_components_to_json(components: dict[str, Any]) -> dict[str, Any]:

    # Handle item lists
    for component in [
        "minecraft:bundle_contents",
        "minecraft:charged_projectiles",
    ]:
        if component in components:
            for i in range(len(components[component])):
                components[component][i] = conform_item_to_json(components[component][i])

    # Handle block predicates
    for component in [
        "minecraft:can_break",
        "minecraft:can_place_on",
    ]:
        if component in components:
            if "predicates" in components[component]:
                for predicate in components[component]["predicates"]:
                    if "nbt" in predicate:
                        predicate["nbt"] = conform_block_to_json(predicate["nbt"])



    if "minecraft:bees" in components:
        for bee in components["minecraft:bees"]:
            if "entity_data" in bee:
                bee["entity_data"] = conform_entity_to_json(bee["entity_data"])

    if "minecraft:block_entity_data" in components:
        components["minecraft:block_entity_data"] = conform_block_to_json(components["minecraft:block_entity_data"])

    if "minecraft:bucket_entity_data" in components:
        bucket_entity_data = components["minecraft:bucket_entity_data"]
        for key in [
            "NoAI",
            "Silent",
            "NoGravity",
            "Glowing",
            "Invulnerable",
        ]:
            if key in bucket_entity_data:
                bucket_entity_data[key] = bool(bucket_entity_data[key])

    if "minecraft:consumable" in components:
        consumable = components["minecraft:consumable"]
        if "has_consume_particles" in consumable:
            consumable["has_consume_particles"] = bool(consumable["has_consume_particles"])
        if "on_consume_effects" in consumable:
            for consume_effect in consumable["on_consume_effects"]:
                if "id" not in consume_effect:
                    continue
                consume_effect["id"] = miscellaneous.namespace(consume_effect["id"])
                if consume_effect["id"] == "minecraft:apply_effects" and "effects" in consume_effect:
                    for effect in consume_effect["effects"]:
                        conform_item_component_effect_to_json(effect)

    if "minecraft:container" in components:
        for item in components["minecraft:container"]:
            if "item" in item:
                item["item"] = conform_item_to_json(item["item"])

    if "minecraft:custom_name" in components:
        components["minecraft:custom_name"] = conform_text_component_to_json(components["minecraft:custom_name"])

    if "minecraft:death_protection" in components:
        death_protection = components["minecraft:death_protection"]
        if "death_effects" in death_protection:
            for death_effect in death_protection["death_effects"]:
                if "id" not in death_effect:
                    continue
                death_effect["id"] = miscellaneous.namespace(death_effect["id"])
                if death_effect["id"] == "minecraft:apply_effects" and "effects" in death_effect:
                    for effect in death_effect["effects"]:
                        conform_item_component_effect_to_json(effect)

    if "minecraft:enchantment_glint_override" in components:
        components["minecraft:enchantment_glint_override"] = bool(components["minecraft:enchantment_glint_override"])

    if "minecraft:entity_data" in components:
        components["minecraft:entity_data"] = conform_entity_to_json(components["minecraft:entity_data"])

    if "minecraft:equippable" in components:
        equippable = components["minecraft:equippable"]
        for key in [
            "dispensable",
            "swappable",
            "damage_on_hurt",
            "equip_on_interact",
        ]:
            if key in equippable:
                equippable[key] = bool(equippable[key])

    if "minecraft:firework_explosion" in components:
        firework_explosion = components["minecraft:firework_explosion"]
        for key in [
            "has_trail",
            "has_twinkle",
        ]:
            if key in firework_explosion:
                firework_explosion[key] = bool(firework_explosion[key])
                
    if "minecraft:fireworks" in components:
        if "explosions" in components["minecraft:fireworks"]:
            for explosion in components["minecraft:fireworks"]["explosions"]:
                for key in [
                    "has_trail",
                    "has_twinkle",
                ]:
                    if key in explosion:
                        explosion[key] = bool(explosion[key])

    if "minecraft:food" in components:
        food = components["minecraft:food"]
        if "can_always_eat" in food:
            food["can_always_eat"] = bool(food["can_always_eat"])

    if "minecraft:item_name" in components:
        components["minecraft:item_name"] = conform_text_component_to_json(components["minecraft:item_name"])

    if "minecraft:lodestone_tracker" in components:
        lodestone_tracker = components["minecraft:lodestone_tracker"]
        if "tracked" in lodestone_tracker:
            lodestone_tracker["tracked"] = bool(lodestone_tracker["tracked"])

    if "minecraft:lore" in components:
        for i in range(len(components["minecraft:lore"])):
            components["minecraft:lore"][i] = conform_text_component_to_json(components["minecraft:lore"][i])

    if "minecraft:potion_contents" in components:
        if "custom_effects" in components["minecraft:potion_contents"]:
            for effect in components["minecraft:potion_contents"]["custom_effects"]:
                conform_item_component_effect_to_json(effect)

    if "minecraft:tool" in components:
        if "rules" in components["minecraft:tool"]:
            for rule in components["minecraft:tool"]["rules"]:
                if "correct_for_drops" in rule:
                    rule["correct_for_drops"] = bool(rule["correct_for_drops"])
        if "can_destroy_blocks_in_creative" in components["minecraft:tool"]:
            components["minecraft:tool"]["can_destroy_blocks_in_creative"] = bool(components["minecraft:tool"]["can_destroy_blocks_in_creative"])

    if "minecraft:use_remainder" in components:
        components["minecraft:use_remainder"] = conform_item_to_json(components["minecraft:use_remainder"])

    if "minecraft:written_book_content" in components:
        if "resolved" in components["minecraft:written_book_content"]:
            components["minecraft:written_book_content"]["resolved"] = bool(components["minecraft:written_book_content"]["resolved"])


    return components



def conform_item_component_effect_to_json(effect: dict[str, Any]) -> dict[str, Any]:
    for key in [
        "ambient",
        "show_particles",
        "show_icon",
    ]:
        if key in effect:
            effect[key] = bool(effect[key])

    return effect



def conform_text_component_to_json(text_component: str | dict | list) -> str | dict | list:
    if isinstance(text_component, str):
        return text_component
    if isinstance(text_component, dict):
        return conform_text_compound_to_json(text_component)
    return conform_text_list_to_json(text_component)

def conform_text_compound_to_json(text_component: dict[str, Any]) -> dict[str, Any]:
    for key in ["bold", "italic", "underlined", "strikethrough", "obfuscated"]:
        if key in text_component:
            text_component[key] = bool(text_component[key])

    for key in ["extra", "separator", "with"]:
        if key in text_component:
            text_component[key] = conform_text_component_to_json(text_component[key])

    if "hover_event" in text_component:
        hover_event = text_component["hover_event"]
        if "action" in hover_event:
            if hover_event["action"] == "show_text" and "value" in hover_event:
                hover_event["value"] = conform_text_component_to_json(hover_event["value"])
            if hover_event["action"] == "show_entity" and "name" in hover_event:
                hover_event["name"] = conform_text_component_to_json(hover_event["name"])
            if hover_event["action"] == "show_item" and "components" in hover_event:
                hover_event["components"] = conform_item_components_to_json(hover_event["components"])

    return text_component

def conform_text_list_to_json(text_component: list) -> list:
    for i in range(len(text_component)):
        text_component[i] = conform_text_component_to_json(text_component[i])
    return text_component



def convert_painting_variant_to_json(painting_variant: dict) -> dict[str, Any]:
    painting_variant = cast(dict, nbt_tags.convert_to_json(painting_variant))
    return conform_painting_variant_to_json(painting_variant)

def conform_painting_variant_to_json(painting_variant: dict) -> dict[str, Any]:
    if "title" in painting_variant:
        painting_variant["title"] = conform_text_component_to_json(painting_variant["title"])
    if "author" in painting_variant:
        painting_variant["author"] = conform_text_component_to_json(painting_variant["author"])
    return painting_variant