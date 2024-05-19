# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



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


def conform(components: dict[str]) -> dict[str]:
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

    if "minecraft:can_place_on" in components:
        can_place_on: dict[str] = components["minecraft:can_place_on"]
        if "predicates" not in can_place_on and "show_in_tooltip" not in can_place_on:
            can_place_on = {"predicates": [can_place_on]}
        components["minecraft:can_place_on"] = can_place_on

    if "minecraft:debug_stick_state" in components:
        debug_stick_state: dict[str, str] = components["minecraft:debug_stick_state"]
        block: str
        for block in list(debug_stick_state.keys()):
            namespaced_block = miscellaneous.namespace(block)
            if block != namespaced_block:
                debug_stick_state[namespaced_block] = debug_stick_state[block]
                del debug_stick_state[block]

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


    return components


def extract(item_id: str, components: dict[str], nbt: dict[str], version: int) -> dict[str]:
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

    if "BlockEntityTag" in nbt:
        block_entity_tag: dict[str] = nbt["BlockEntityTag"]

        if "Base" in block_entity_tag:
            components["minecraft:base_color"] = miscellaneous.color(block_entity_tag["Base"].value)
            del block_entity_tag["Base"]

        if "Bees" in block_entity_tag:
            if "minecraft:bees" not in components:
                components["minecraft:bees"] = []
            for bee in block_entity_tag["Bees"]:
                bee_entry: dict[str] = {}
                if "EntityData" in bee:
                    bee_entry["entity_data"] = bee["EntityData"]
                if "TicksInHive" in bee:
                    bee_entry["ticks_in_hive"] = nbt_tags.TypeInt(bee["TicksInHive"])
                if "MinOccupationTicks" in bee:
                    bee_entry["min_ticks_in_hive"] = nbt_tags.TypeInt(bee["MinOccupationTicks"])
                components["minecraft:bees"].append(bee_entry)
            del block_entity_tag["Bees"]

        if "Items" in block_entity_tag:
            if "minecraft:container" not in components:
                components["minecraft:container"] = []
            container = components["minecraft:container"]
            for item in block_entity_tag["Items"]:
                container_entry: dict[str] = {}
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
                components["minecraft:banner_patterns"] = []
            banner_patterns = components["minecraft:banner_patterns"]
            for pattern in block_entity_tag["Patterns"]:
                banner_pattern: dict[str] = {}
                if "Pattern" in pattern:
                    banner_pattern["pattern"] = miscellaneous.banner_pattern(pattern["Pattern"], version)
                if "Color" in pattern:
                    banner_pattern["color"] = miscellaneous.color(pattern["Color"].value)
                banner_patterns.append(banner_pattern)
            del block_entity_tag["Patterns"]

        if "sherds" in block_entity_tag:
            components["minecraft:pot_decorations"] = []
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
            components["minecraft:suspicious_stew_effects"] = []
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
            ][explosion["Type"]]
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
                fireworks["explosions"] = []
            for explosion in nbt["Fireworks"]["Explosions"]:
                firework_explosion = {}
                if "Type" in explosion:
                    firework_explosion["shape"] = [
                        "small_ball",
                        "large_ball",
                        "star",
                        "creeper",
                        "burst",
                    ][explosion["Type"]]
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
        if "minecraft:written_book_contents" not in components:
            components["minecraft:written_book_contents"] = {}
        written_book_contents = components["minecraft:written_book_contents"]
        written_book_contents["generation"] = nbt_tags.TypeInt(nbt["generation"])
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
            components["minecraft:bundle_contents"] = []
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
        x, y, z = 0, 0, 0
        if "x" in nbt["LodestonePos"]:
            x = nbt["LodestonePos"]["x"].value
        if "y" in nbt["LodestonePos"]:
            y = nbt["LodestonePos"]["y"].value
        if "z" in nbt["LodestonePos"]:
            z = nbt["LodestonePos"]["z"].value
        target["pos"] = nbt_tags.TypeIntArray([x,y,z])
        del nbt["LodestonePos"]

    if "LodestoneTracked" in nbt:
        if "minecraft:lodestone_tracker" not in components:
            components["minecraft:lodestone_tracker"] = {}
        lodestone_tracker = components["minecraft:lodestone_tracker"]
        if "target" not in lodestone_tracker:
            lodestone_tracker["target"] = {}
        target = lodestone_tracker["target"]
        target["tracked"] = nbt_tags.TypeByte(nbt["LodestoneTracked"])
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

    if "Recipes" in nbt:
        if "minecraft:recipes" not in components:
            components["minecraft:recipes"] = []
        for recipe in nbt["Recipes"]:
            components["minecraft:recipes"].append(miscellaneous.namespace(recipe))
        del nbt["Recipes"]

    if "RepairCost" in nbt:
        components["minecraft:repair_cost"] = nbt_tags.TypeInt(nbt["RepairCost"])
        del nbt["RepairCost"]

    if "resolved" in nbt:
        if "minecraft:written_book_contents" not in components:
            components["minecraft:written_book_contents"] = {}
        written_book_contents = components["minecraft:written_book_contents"]
        written_book_contents["resolved"] = nbt_tags.TypeByte(nbt["resolved"])
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
                profile["id"] = nbt_tags.TypeIntArray(skull_owner["Id"])
            if "Properties" in skull_owner:
                if "properties" not in profile:
                    profile["properties"] = []
                properties: list = profile["properties"]
                if "textures" in skull_owner["Properties"]:
                    textures: list[dict[str]] = skull_owner["Properties"]["textures"]
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