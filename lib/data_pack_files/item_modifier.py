# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from typing import cast, Any
from lib.log import log
from lib import defaults
from lib import utils
from lib import json_manager
from lib.data_pack_files import ids
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import nbt_paths
from lib.data_pack_files import nbt_to_json
from lib.data_pack_files import predicate
from lib.data_pack_files import json_text_component
from lib.data_pack_files import loot_table
from lib.data_pack_files import items
from lib.data_pack_files import item_component



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def update(file_path: Path, source_file_path: Path, version: int):
    global pack_version
    pack_version = version

    # Read file
    contents, load_bool = json_manager.safe_load(source_file_path)
    if not load_bool:
        return

    # Write to new location
    file_path.parent.mkdir(parents=True, exist_ok=True)
    utils.safe_file_write(file_path, json.dumps(item_modifier(contents, version), indent=4))



def item_modifier(contents: dict[str, Any] | list, version: int, object_id: str = "") -> dict[str, Any] | list:
    global pack_version
    pack_version = version

    # Handle lists
    if isinstance(contents, list):
        output = []
        for entry in contents:
            entry = item_modifier(entry, version, object_id)
            if isinstance(entry, list):
                output.extend(entry)
            else:
                output.append(entry)

        # Consolidate custom data overwrites
        set_custom_data_index = -1
        custom_data_array: list[dict] = []
        for i in range(len(output)-1, -1, -1):
            entry = output[i]
            
            if entry["function"] == "minecraft:set_custom_data":
                if isinstance(entry["tag"], str):
                    custom_data_array.append(nbt_tags.unpack(entry["tag"]))
                else:
                    custom_data_array.append(nbt_tags.convert_from_json(entry["tag"]))
                set_custom_data_index = i
                output.pop(i)

            if entry["function"] == "minecraft:set_components" and "minecraft:custom_data" in entry["components"]:
                custom_data_array.append(nbt_tags.convert_from_json(entry["components"]["minecraft:custom_data"]))
                del entry["components"]["minecraft:custom_data"]

        custom_data = {}
        for entry in custom_data_array:
            custom_data = nbt_tags.merge_nbt(custom_data, entry)

        if custom_data:
            modifier = {
                "function": "minecraft:set_custom_data",
                "tag": nbt_tags.pack(custom_data)
            }
            if set_custom_data_index == -1:
                output.append(modifier)
            else:
                output.insert(set_custom_data_index, modifier)

        return output



    if "conditions" in contents:
        for i in range(len(contents["conditions"])):
            contents["conditions"][i] = predicate.predicate(contents["conditions"][i], version)



    # Process different functions
    function_id: str = contents["function"]
    function_id = miscellaneous.namespace(function_id)
    contents["function"] = function_id



    if function_id == "minecraft:copy_custom_data":
        source = contents["source"]
        if isinstance(source, dict):
            source["type"] = miscellaneous.namespace(source["type"])
            source_type = source["type"]
            if source_type == "minecraft:context":
                source["target"] = miscellaneous.loot_context_alt(source["target"])
        else:
            contents["source"] = miscellaneous.loot_context_alt(source)

    if function_id == "minecraft:copy_name":
        if "source" in contents:
            contents["source"] = miscellaneous.loot_context_alt(contents["source"])

    if function_id == "minecraft:copy_nbt":
        contents["function"] = "minecraft:copy_custom_data"
        source = contents["source"]
        if isinstance(source, dict):
            source["type"] = miscellaneous.namespace(source["type"])
            source_type = source["type"]
            if source_type == "minecraft:context":
                source["target"] = miscellaneous.loot_context_alt(source["target"])
                nbt_source = source["target"]
            else:
                nbt_source = "storage"
        else:
            contents["source"] = miscellaneous.loot_context_alt(source)
            nbt_source = contents["source"]

        for operation in contents["ops"]:
            id_array = {
                "block_entity": "block",
                "this": "entity",
                "attacking_entity": "entity",
                "last_damage_player": "entity",
                "storage": "arbitrary",
            }
            if nbt_source in id_array:
                nbt_source = id_array[nbt_source]
            else:
                nbt_source = "arbitrary"
            operation["source"] = nbt_paths.update(operation["source"], version, [], nbt_source)
            target_path = nbt_paths.direct_update(nbt_paths.unpack(operation["target"]), version, [], "item_tag")
            if target_path[0] == "minecraft:custom_data":
                operation["target"] = nbt_paths.pack(target_path[1:])
            else:
                operation["target"] = nbt_paths.pack(target_path)
                if defaults.SEND_WARNINGS:
                    log(f'WARNING: Item modifier function "minecraft:copy_nbt" could not be converted to "minecraft:copy_components", target path changed to: {operation["target"]}')
    
    if function_id == "minecraft:enchant_randomly":
        if "enchantments" in contents:
            contents["options"] = contents["enchantments"]
            del contents["enchantments"]
    
    if function_id == "minecraft:enchant_with_levels":
        contents["levels"] = miscellaneous.number_provider(contents["levels"])
        if "treasure" in contents:
            del contents["treasure"]

    if function_id == "minecraft:enchanted_count_increase":
        contents["count"] = miscellaneous.number_provider(contents["count"])
        if "enchantment" in contents:
            contents["enchantment"] = ids.enchantment(contents["enchantment"], version, [])

    if function_id == "minecraft:fill_player_head":
        if "entity" in contents:
            contents["entity"] = miscellaneous.loot_context(contents["entity"])

    if function_id == "minecraft:filtered":
        if "item_filter" in contents:
            contents["item_filter"] = predicate.predicate(contents["item_filter"], version)
        if "modifier" in contents:
            contents["modifier"] = item_modifier(contents["modifier"], version, object_id)

    if function_id == "minecraft:limit_count":
        limit = contents["limit"]
        if isinstance(limit, dict):
            if "min" in limit:
                limit["min"] = miscellaneous.number_provider(limit["min"])
            if "max" in limit:
                limit["max"] = miscellaneous.number_provider(limit["max"])

    if function_id == "minecraft:modify_contents":
        if "modifier" in contents:
            contents["modifier"] = item_modifier(contents["modifier"], version, object_id)

    if function_id == "minecraft:set_attributes":
        if "modifiers" in contents:
            for modifier in contents["modifiers"]:
                if "amount" in modifier:
                    modifier["amount"] = miscellaneous.number_provider(modifier["amount"])
                if "attribute" in modifier:
                    modifier["attribute"] = miscellaneous.attribute(modifier["attribute"], version, [])
                if "id" in modifier:
                    modifier["id"] = miscellaneous.namespace(modifier["id"])
                else:
                    modifier["id"] = miscellaneous.namespace(utils.uuid_from_int_array(utils.new_uuid()))
                if "name" in modifier:
                    del modifier["name"]
                if "operation" in modifier:
                    id_array = {
                        "addition": "add_value",
                        "multiply_base": "add_multiplied_base",
                        "multiply_total": "add_multiplied_total",
                    }
                    if modifier["operation"] in id_array:
                        modifier["operation"] = id_array[modifier["operation"]]

    if function_id == "minecraft:set_components":
        if "components" in contents:
            item_components = item_component.ItemComponents.unpack_from_dict(nbt_tags.convert_from_json(contents["components"]), False)
            updated_item_components = item_component.conform_components(item_components, version, []).pack_to_dict()
            contents["components"] = nbt_to_json.convert_item_components_to_json(updated_item_components)

    if function_id == "minecraft:set_contents":
        if "entries" in contents:
            for entry in contents["entries"]:
                loot_table.update_entry(entry, version)
        if "type" in contents:
            if miscellaneous.namespace(contents["type"]) == "minecraft:bundle":
                contents["component"] = "minecraft:bundle_contents"
            elif miscellaneous.namespace(contents["type"]) == "minecraft:crossbow":
                contents["component"] = "minecraft:charged_projectiles"
            else:
                contents["component"] = "minecraft:container"
            del contents["type"]
        elif "component" not in contents:
            if miscellaneous.namespace(object_id) == "minecraft:bundle":
                contents["component"] = "minecraft:bundle_contents"
            elif miscellaneous.namespace(object_id) == "minecraft:crossbow":
                contents["component"] = "minecraft:charged_projectiles"
            else:
                contents["component"] = "minecraft:container"

    if function_id == "minecraft:set_count":
        contents["count"] = miscellaneous.number_provider(contents["count"])

    if function_id == "minecraft:set_custom_model_data":
        if "value" in contents:
            contents["floats"] = {
                "values": [contents["value"]],
                "mode": "replace_all"
            }
            del contents["value"]

        for key in ["colors", "floats"]:
            if key in contents:
                for i in range(len(contents[key]["values"])):
                    contents[key]["values"][i] = miscellaneous.number_provider(contents[key]["values"][i])

    if function_id == "minecraft:set_damage":
        contents["damage"] = miscellaneous.number_provider(contents["damage"])

    if function_id == "minecraft:set_enchantments":
        for enchantment in contents["enchantments"]:
            contents["enchantments"][enchantment] = miscellaneous.number_provider(contents["enchantments"][enchantment])

    if function_id == "minecraft:set_item":
        if "item" in contents:
            contents["item"] = items.update_from_command(contents["item"], version, [])

    if function_id == "minecraft:set_lore":
        for i in range(len(contents["lore"])):
            contents["lore"][i] = nbt_to_json.conform_text_component_to_json(nbt_tags.convert_to_json(json_text_component.update_component(nbt_tags.convert_from_json(contents["lore"][i]), version, [])))
        if "replace" in contents:
            contents["mode"] = "replace_all" if contents["replace"] else "append"
            del contents["replace"]
        if "mode" not in contents:
            contents["mode"] = "append"
        if "entity" in contents:
            contents["entity"] = miscellaneous.loot_context(contents["entity"])

    if function_id == "minecraft:set_name":
        contents["name"] = nbt_to_json.conform_text_component_to_json(nbt_tags.convert_to_json(json_text_component.update_component(nbt_tags.convert_from_json(contents["name"]), version, [])))
        if "entity" in contents:
            contents["entity"] = miscellaneous.loot_context(contents["entity"])

    if function_id == "minecraft:set_nbt":
        updated_data = cast(dict[str, Any], nbt_tags.direct_update(nbt_tags.unpack(contents["tag"]), version, [], "item_tag", "", False))
        if "minecraft:custom_data" in updated_data:
            set_custom_data = {
                "function": "minecraft:set_custom_data",
                "tag": nbt_tags.pack(updated_data["minecraft:custom_data"])
            }
            if "conditions" in contents:
                set_custom_data["conditions"] = contents["conditions"]
            del updated_data["minecraft:custom_data"]
        else:
            set_custom_data = None
        if len(updated_data):
            set_components = {
                "function": "minecraft:set_components",
                "components": nbt_to_json.convert_item_components_to_json(updated_data)
            }
            if "conditions" in contents:
                set_components["conditions"] = contents["conditions"]
        else:
            set_components = None
        if set_custom_data and set_components:
            return [set_custom_data, set_components]
        if set_custom_data:
            return set_custom_data
        if set_components:
            return set_components
        return []
    
    if function_id == "minecraft:set_stew_effect":
        for effect in contents["effects"]:
            if "duration" in effect:
                effect["duration"] = miscellaneous.number_provider(effect["duration"])


    return contents