# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from typing import cast, Any
from lib.data_pack_files import nbt_tags



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

    # Handle items
    for key in [
        "ArmorItems",
        "HandItems",
        "Inventory",
    ]:
        if key in entity:
            for i in range(len(entity[key])):
                entity[key][i] = conform_item_to_json(entity[key][i])
    for key in [
        "body_armor_item",
    ]:
        if key in entity:
            entity[key] = conform_item_to_json(entity[key])

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

    # Handle show in tooltip
    for component in [
        "minecraft:attribute_modifiers",
        "minecraft:can_break",
        "minecraft:can_place_on",
        "minecraft:dyed_color",
        "minecraft:enchantments",
        "minecraft:jukebox_playable",
        "minecraft:stored_enchantments",
        "minecraft:trim",
        "minecraft:unbreakable",
    ]:
        if component in components and "show_in_tooltip" in components[component]:
            components[component]["show_in_tooltip"] = bool(components[component]["show_in_tooltip"])

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

    if "minecraft:container" in components:
        for item in components["minecraft:container"]:
            if "item" in item:
                item["item"] = conform_item_to_json(item["item"])

    if "minecraft:enchantment_glint_override" in components:
        components["minecraft:enchantment_glint_override"] = bool(components["minecraft:enchantment_glint_override"])

    if "minecraft:entity_data" in components:
        components["minecraft:entity_data"] = conform_entity_to_json(components["minecraft:entity_data"])

    if "minecraft:firework_explosion" in components:
        for key in [
            "has_trail",
            "has_twinkle",
        ]:
            if key in components["minecraft:firework_explosion"]:
                components["minecraft:firework_explosion"][key] = bool(components["minecraft:firework_explosion"][key])
                
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
        if "using_converts_to" in food:
            food["using_converts_to"] = conform_item_to_json(food["using_converts_to"])
        if "effects" in food:
            for effect in food["effects"]:
                for key in [
                    "ambient",
                    "show_particles",
                    "show_icon",
                ]:
                    if key in effect:
                        effect[key] = bool(effect[key])

    if "minecraft:lodestone_tracker" in components:
        if "tracked" in components["minecraft:lodestone_tracker"]:
            components["minecraft:lodestone_tracker"]["tracked"] = bool(components["minecraft:lodestone_tracker"]["tracked"])

    if "minecraft:potion_contents" in components:
        if "custom_effects" in components["minecraft:potion_contents"]:
            for effect in components["minecraft:potion_contents"]["custom_effects"]:
                for key in [
                    "ambient",
                    "show_particles",
                    "show_icon",
                ]:
                    if key in effect:
                        effect[key] = bool(effect[key])

    if "minecraft:tool" in components:
        if "rules" in components["minecraft:tool"]:
            for rule in components["minecraft:tool"]["rules"]:
                if "correct_for_drops" in rule:
                    rule["correct_for_drops"] = bool(rule["correct_for_drops"])

    if "minecraft:written_book_content" in components:
        if "resolved" in components["minecraft:written_book_content"]:
            components["minecraft:written_book_content"]["resolved"] = bool(components["minecraft:written_book_content"]["resolved"])


    return components