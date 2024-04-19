# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import math
from pathlib import Path
from nbt import nbt as NBT
from nbt import region
from lib import defaults
from lib import utils
from lib.log import log
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import items
from lib.data_pack_files import json_text_component
from lib.data_pack_files import ids
from lib.data_pack_files import tables
from lib.data_pack_files.restore_behavior import spawner_bossbar
from lib.data_pack_files.restore_behavior import spawner_position



# Initialize variables

PROGRAM_PATH = Path(__file__).parent.parent.parent
DATA_VERSION = defaults.DATA_VERSION
pack_version = defaults.PACK_VERSION
spawner_bossbar_list = NBT.TAG_List(type=NBT.TAG_Compound)
spawner_position_list: list[str] = []
uuid_dict: dict[str, str] = {}
uuid_list: list[str] = []



# Define functions

def fix(world: Path, og_world: Path, version: int) -> dict[str, bool]:
    log("Fixing world data")

    # Set pack version
    global pack_version
    pack_version = version

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if not og_world.exists():
        log("ERROR: Original copy of world does not exist!")
        return

    # Get confirmation
    log(f'This action will modify several region files in: {world.as_posix()}')
    confirm = input("Is this okay? (Y/N): ")
    if confirm not in ["Y", "y"]:
        log("Action canceled")
        return
    
    # Get the time
    global TIME
    TIME = get_time(world)
    
    # Iterate through region files
    log("Fixing regions")
    fix_region_folder(world /           "region"  , og_world /           "region", "minecraft:overworld" )
    fix_entity_folder(world /           "entities", og_world /           "region", "minecraft:overworld" )
    fix_region_folder(world / "DIM-1" / "region"  , og_world / "DIM-1" / "region", "minecraft:the_nether")
    fix_entity_folder(world / "DIM-1" / "entities", og_world / "DIM-1" / "region", "minecraft:the_nether")
    fix_region_folder(world / "DIM1"  / "region"  , og_world / "DIM1"  / "region", "minecraft:the_end"   )
    fix_entity_folder(world / "DIM1"  / "entities", og_world / "DIM1"  / "region", "minecraft:the_end"   )
    dimensions = world / "dimensions"
    og_dimensions = og_world / "dimensions"
    if dimensions.exists():
        for dimension_namespace in dimensions.iterdir():
            og_dimension_namespace = og_dimensions / dimension_namespace.name
            for dimension in dimension_namespace.iterdir():
                og_dimension = og_dimension_namespace / dimension.name
                fix_region_folder(dimension / "region", og_dimension / "region", "custom")
                fix_entity_folder(dimension / "entities", og_dimension / "entities", "custom")
    
    # Fix scoreboard objectives
    log("Fixing scoreboard.dat")
    fix_scoreboard_dat(world)

    # Fix maps
    log("Fixing maps")
    fix_maps(world)
    
    log("World data fixed")

    # Create spawner bossbar storage file
    spawn_bossbar_boolean = False
    if spawner_bossbar_list:
        create_spawner_bossbar_file(world)
        spawn_bossbar_boolean = True

    # Create spawner position data pack
    if spawner_position_list:
        spawner_position.create_pack(world, spawner_position_list)

    return {"spawner_bossbar": spawn_bossbar_boolean}



def get_time(world: Path) -> int:
    file_path = world / "level.dat"
    if not file_path.exists():
        return 0
    
    file = NBT.NBTFile(file_path)
    if "Data" not in file:
        return 0
    if "Time" not in file["Data"]:
        return 0
    return file["Data"]["Time"].value



def fix_region_folder(folder_path: Path, og_folder_path: Path, dimension: str):
    if not folder_path.exists():
        return

    for file_path in folder_path.iterdir():
        fix_region_file(file_path, og_folder_path / file_path.name, dimension)

def fix_region_file(file_path: Path, og_file_path: Path, dimension: str):
    log(f" Fixing region/{file_path.name}")

    global spawner_bossbar_list

    try:
        region_file = region.RegionFile(file_path)
        og_region_file = region.RegionFile(og_file_path)
    except:
        return
    chunk_metadata: region.ChunkMetadata
    for chunk_metadata in region_file.get_metadata():
        chunk = region_file.get_nbt(chunk_metadata.x, chunk_metadata.z)
        og_chunk = og_region_file.get_nbt(chunk_metadata.x, chunk_metadata.z)
        if "block_entities" not in chunk:
            continue
        if defaults.DEBUG_MODE:
            print(f"  Fixing chunk {chunk_metadata.x}, {chunk_metadata.z}")
        block_entities: NBT.TAG_List = chunk["block_entities"]
        if block_entities == None or len(block_entities) == 0:
            continue

        # chunk["Status"] = NBT.TAG_String("minecraft:full")
        # if "hasLegacyStructureData" in chunk:
        #     del chunk["hasLegacyStructureData"]
        # if "LightPopulated" in chunk:
        #     chunk["isLightOn"] = NBT.TAG_Byte(chunk["LightPopulated"].value)
        #     del chunk["LightPopulated"]
        # if "TerrainPopulated" in chunk:
        #     del chunk["TerrainPopulated"]
        # if "V" in chunk:
        #     del chunk["V"]
        # if "yPos" not in chunk:
        #     chunk["yPos"] = NBT.TAG_Int(-4)
        # if "HeightMap" in chunk:
        #     del chunk["HeightMap"]

        # Get list of scheduled command blocks
        scheduled_blocks = get_block_ticks(chunk, og_chunk)

        # Iterate through block entities
        block_entity: NBT.TAG_Compound
        for block_entity in block_entities:
            if "id" not in block_entity:
                continue
            if "keepPacked" not in block_entity:
                block_entity["keepPacked"] = NBT.TAG_Byte(0)
            if "CommandStats" in block_entity and not defaults.FIXES["stats"]:
                log("WARNING: Stats fixer not enabled but stats have been found!")

            fix_block_entity(block_entity)

            if block_entity["id"].value == "minecraft:command_block":

                if "LastOutput" in block_entity:
                    block_entity["LastOutput"] = NBT.TAG_String(json_text_component.update(block_entity["LastOutput"].value, pack_version, [], False))

                if "auto" not in block_entity:
                    block_entity["auto"] = NBT.TAG_Byte(0)
                if "conditionMet" not in block_entity:
                    block_entity["conditionMet"] = NBT.TAG_Byte(1)
                if "LastExecution" not in block_entity:
                    block_entity["LastExecution"] = NBT.TAG_Long(TIME)
                if "UpdateLastExecution" not in block_entity:
                    block_entity["UpdateLastExecution"] = NBT.TAG_Byte(1)

                if "powered" not in block_entity:
                    block_entity["powered"] = NBT.TAG_Byte(0)
                    if (
                        "x" in block_entity and
                        "y" in block_entity and
                        "z" in block_entity
                    ):
                        if (
                            block_entity["x"].value,
                            block_entity["y"].value,
                            block_entity["z"].value
                        ) in scheduled_blocks:
                            block_entity["powered"] = NBT.TAG_Byte(1)

                        block_data = get_block_data(chunk, block_entity["x"].value, block_entity["y"].value, block_entity["z"].value)
                        if (
                            pack_version <= 809 and
                            block_data["Name"].value == "minecraft:command_block" and
                            "Properties" in block_data and
                            "facing" in block_data["Properties"] and
                            block_data["Properties"]["facing"].value == "up"
                        ):
                            block_entity["powered"] = NBT.TAG_Byte(1)

            if block_entity["id"].value == "minecraft:mob_spawner":

                if "SpawnData" in block_entity:
                    if "entity" in block_entity["SpawnData"]:
                        entity = block_entity["SpawnData"]["entity"]

                        if (
                            "id" in entity and
                            entity["id"].value in ["minecraft:wither", "minecraft:ender_dragon"] and
                            pack_version <= 809
                        ):
                            spawner = NBT.TAG_Compound()
                            spawner["x"] = NBT.TAG_Int(0)
                            spawner["y"] = NBT.TAG_Int(0)
                            spawner["z"] = NBT.TAG_Int(0)
                            spawner["Dimension"] = NBT.TAG_String(dimension)
                            spawner["UUID"] = NBT.TAG_Int_Array(name="UUID")
                            spawner["UUID"].value = [0,0,0,0]

                            if "x" in block_entity:
                                spawner["x"] = block_entity["x"]
                            if "y" in block_entity:
                                spawner["y"] = block_entity["y"]
                            if "z" in block_entity:
                                spawner["z"] = block_entity["z"]

                            spawner_bossbar_list.append(spawner)

                        fix_spawner_entity(entity)

                if "SpawnPotentials" in block_entity:
                    for spawn_potential in block_entity["SpawnPotentials"]:
                        if "data" in spawn_potential and "entity" in spawn_potential["data"]:
                            entity = spawn_potential["data"]["entity"]

                            fix_spawner_entity(entity)

            if block_entity["id"].value == "minecraft:sign":
                for i in range(1,5):
                    key = f'Text{i}'
                    if key in block_entity:
                        del block_entity[key]

                if "is_waxed" not in block_entity:
                    block_entity["is_waxed"] = NBT.TAG_Byte(1)

        # Save chunk
        region_file.write_chunk(chunk_metadata.x, chunk_metadata.z, chunk)

def get_block_ticks(chunk: NBT.NBTFile, og_chunk: NBT.NBTFile) -> list[tuple[int]]:
    scheduled_blocks: list[tuple[int]] = []
    if "block_ticks" not in chunk:
        return scheduled_blocks
    block_ticks: NBT.TAG_List = chunk["block_ticks"]
    if block_ticks == None or len(block_ticks) == 0:
        return scheduled_blocks
    
    if "block_ticks" in og_chunk:
        og_block_ticks = og_chunk["block_ticks"]
        use_og_block_ticks = True
    elif "Level" in og_chunk and "TileTicks" in og_chunk["Level"]:
        og_block_ticks = og_chunk["Level"]["TileTicks"]
        use_og_block_ticks = True
    else:
        use_og_block_ticks = False
    
    for i in range(len(block_ticks)-1, -1, -1):
        block_tick: NBT.TAG_Compound = block_ticks[i]

        # Remove block ticks that are actually out of bounds
        if use_og_block_ticks:
            og_block_tick: NBT.TAG_Compound = og_block_ticks[i]
            if (
                not ("x" in block_tick and "x" in og_block_tick and block_tick["x"].value == og_block_tick["x"].value) or
                not ("y" in block_tick and "y" in og_block_tick and block_tick["y"].value == og_block_tick["y"].value) or
                not ("z" in block_tick and "z" in og_block_tick and block_tick["z"].value == og_block_tick["z"].value)
            ):
                block_ticks.tags.pop(i)
                continue

        if (
            not ("i" in block_tick and block_tick["i"].value == "minecraft:command_block") or
            not ("t" in block_tick and block_tick["t"].value <= 1) or
            not ("x" in block_tick and "y" in block_tick and "z" in block_tick)
        ):
            continue
        scheduled_blocks.append((
            block_tick["x"].value,
            block_tick["y"].value,
            block_tick["z"].value
        ))

        if block_tick["t"].value <= 0:
            block_tick["t"] = NBT.TAG_Long(1)

    return scheduled_blocks

def get_block_data(chunk: NBT.NBTFile, x: int, y: int, z: int) -> NBT.TAG_Compound:
    default_block = NBT.TAG_Compound()
    default_block["Name"] = NBT.TAG_String("minecraft:air")

    if "sections" not in chunk:
        return default_block
    
    # Find proper section
    y_section = y//16
    section: NBT.TAG_Compound
    for section in chunk["sections"]:
        if "Y" not in section:
            continue
        if section["Y"].value == y_section:
            break
    else:
        return default_block
    
    # Extract index from data
    palette: NBT.TAG_List = section["block_states"]["palette"]
    palette_length = len(palette)
    if palette_length == 1:
        return palette[0]
    data: NBT.TAG_Long_Array = section["block_states"]["data"]
    index_size = max(int(math.ceil(math.log2(palette_length))), 4)
    index_size_divisor = int(2**index_size)
    indices_per_entry = 64//index_size
    data_index = ((y%16)*256 + (z%16)*16 + (x%16))//indices_per_entry
    long_index = ((y%16)*256 + (z%16)*16 + (x%16))%indices_per_entry
    index = int((data[data_index]//(index_size_divisor**long_index))%index_size_divisor)

    if index >= palette_length:
        return default_block
    return palette[index]

def fix_spawner_entity(entity: NBT.TAG_Compound):
    global spawner_position_list

    entity_output = fix_entity_recursive_passenger(entity, True)

    if (
        "id" in entity and
        "Pos" in entity_output and
        pack_version <= 809
    ):
        if "Tags" not in entity:
            entity["Tags"] = NBT.TAG_List(NBT.TAG_String)
            entity["Tags"].tags = []

        tag = f'{entity_output["Pos"][0]}_{entity_output["Pos"][1]}_{entity_output["Pos"][2]}'
        entity["Tags"].append(NBT.TAG_String(tag))
        
        command = f'teleport @e[type={entity["id"].value},tag={tag}] {entity_output["Pos"][0]} {entity_output["Pos"][1]} {entity_output["Pos"][2]}'
        if command not in spawner_position_list:
            spawner_position_list.append(command)
        command = f'tag @e[type={entity["id"].value},tag={tag}] remove {tag}'
        if command not in spawner_position_list:
            spawner_position_list.append(command)



def fix_block_entity(block_entity: NBT.TAG_Compound):
    if "Items" in block_entity:
        for item in block_entity["Items"]:
            fix_item(item, False)

    if "CustomName" in block_entity:
        block_entity["CustomName"] = NBT.TAG_String(json_text_component.update(block_entity["CustomName"].value, pack_version, [], True))



def fix_entity_folder(folder_path: Path, og_folder_path: Path, dimension: str):
    if not folder_path.exists():
        return

    for file_path in folder_path.iterdir():
        fix_entity_file(file_path, og_folder_path / file_path.name, dimension)

def fix_entity_file(file_path: Path, og_file_path: Path, dimension: str):
    log(f" Fixing entities/{file_path.name}")
    
    global uuid_dict
    global uuid_list

    try:
        region_file = region.RegionFile(file_path)
    except:
        return
    chunk_metadata: region.ChunkMetadata
    for chunk_metadata in region_file.get_metadata():
        chunk = region_file.get_nbt(chunk_metadata.x, chunk_metadata.z)
        if "Entities" not in chunk:
            continue
        entities: NBT.TAG_List = chunk["Entities"]
        if entities == None or len(entities) == 0:
            continue

        # Iterate through entities
        entity: NBT.TAG_Compound
        for entity in entities:
            fix_entity_recursive_passenger(entity, False)

            # Apply fixes to root entity (passengers need not apply)

            # Fix pre-1.9 NoAI horses
            if (
                defaults.FIXES["no_ai_horse_movement"] and
                pack_version <= 809 and
                entity["id"].value == "minecraft:horse" and
                "NoAI" in entity and
                entity["NoAI"].value == 1
            ):
                horse = NBT.TAG_Compound()
                horse.tags = entity.tags.copy()
                for tag in entity:
                    if tag != "Pos":
                        del entity[tag]
                entity["Passengers"] = NBT.TAG_List(NBT.TAG_Compound)
                entity["Passengers"].append(horse)
                entity["Pos"][1].value -= 0.14

                entity["transformation"] = NBT.TAG_Compound()
                entity["transformation"]["left_rotation"] = NBT.TAG_List(NBT.TAG_Float)
                entity["transformation"]["left_rotation"].tags = [
                    NBT.TAG_Float(0.0),
                    NBT.TAG_Float(0.0),
                    NBT.TAG_Float(0.0),
                    NBT.TAG_Float(1.0)
                ]
                entity["transformation"]["right_rotation"] = NBT.TAG_List(NBT.TAG_Float)
                entity["transformation"]["right_rotation"].tags = [
                    NBT.TAG_Float(0.0),
                    NBT.TAG_Float(0.0),
                    NBT.TAG_Float(0.0),
                    NBT.TAG_Float(1.0)
                ]
                entity["transformation"]["scale"] = NBT.TAG_List(NBT.TAG_Float)
                entity["transformation"]["scale"].tags = [
                    NBT.TAG_Float(1.0),
                    NBT.TAG_Float(1.0),
                    NBT.TAG_Float(1.0)
                ]
                entity["transformation"]["translation"] = NBT.TAG_List(NBT.TAG_Float)
                entity["transformation"]["translation"].tags = [
                    NBT.TAG_Float(0.0),
                    NBT.TAG_Float(0.0),
                    NBT.TAG_Float(0.0)
                ]
                entity["Motion"] = NBT.TAG_List(NBT.TAG_Double)
                entity["Motion"].tags = [
                    NBT.TAG_Double(0.0),
                    NBT.TAG_Double(0.0),
                    NBT.TAG_Double(0.0)
                ]
                entity["Rotation"] = NBT.TAG_List(NBT.TAG_Float)
                entity["Rotation"].tags = [
                    NBT.TAG_Float(0.0),
                    NBT.TAG_Float(0.0)
                ]

                entity["Air"] = NBT.TAG_Short(300)
                entity["alignment"] = NBT.TAG_String("center")
                entity["background"] = NBT.TAG_Int(1073741824)
                entity["billboard"] = NBT.TAG_String("fixed")
                entity["default_background"] = NBT.TAG_Byte(0)
                entity["FallDistance"] = NBT.TAG_Float(0.0)
                entity["Fire"] = NBT.TAG_Short(0)
                entity["glow_color_override"] = NBT.TAG_Int(-1)
                entity["height"] = NBT.TAG_Float(0.0)
                entity["id"] = NBT.TAG_String("minecraft:text_display")
                entity["interpolation_duration"] = NBT.TAG_Int(0)
                entity["Invulnerable"] = NBT.TAG_Byte(1)
                entity["line_width"] = NBT.TAG_Int(200)
                entity["OnGround"] = NBT.TAG_Byte(0)
                entity["PortalCooldown"] = NBT.TAG_Int(0)
                entity["see_through"] = NBT.TAG_Byte(0)
                entity["shadow"] = NBT.TAG_Byte(0)
                entity["shadow_radius"] = NBT.TAG_Float(0.0)
                entity["shadow_strength"] = NBT.TAG_Float(1.0)
                entity["text"] = NBT.TAG_String('{"text":""}')
                entity["text_opacity"] = NBT.TAG_Byte(-1)
                entity["view_range"] = NBT.TAG_Float(1.0)
                entity["width"] = NBT.TAG_Float(0.0)
                entity["UUID"] = NBT.TAG_Int_Array(name="UUID")
                entity["UUID"].value = utils.new_uuid()

        # Save chunk
        region_file.write_chunk(chunk_metadata.x, chunk_metadata.z, chunk)

def fix_entity_recursive_passenger(entity: NBT.TAG_Compound, is_from_spawner: bool = False) -> dict[str]:
    global uuid_dict
    global uuid_list

    output: dict[str] = {}

    entity_id = None
    if "id" in entity:
        entity_id: str = entity["id"].value
    
    if entity_id == "minecraft:command_block_minecart":
        if "LastOutput" in entity:
            entity["LastOutput"] = NBT.TAG_String(json_text_component.update(entity["LastOutput"].value, pack_version, [], False))

    if entity_id == "minecraft:item":
        if "Item" not in entity:
            entity["Item"] = NBT.TAG_Compound()
            entity["Item"]["id"] = NBT.TAG_String("minecraft:stone")
            entity["Item"]["Count"] = NBT.TAG_Byte(1)

        # TEMPORARY CODE
        # if "Pos" in entity and is_from_spawner:
        #     entity["Pos"][1].value = math.floor(entity["Pos"][1].value)

    if entity_id == "minecraft:villager":
        if (
            "Offers" in entity and
            "VillagerData" in entity and
            "level" in entity["VillagerData"] and
            entity["VillagerData"]["level"].value <= 1
        ):
            entity["VillagerData"]["level"] = NBT.TAG_Int(2)


    if "CommandStats" in entity and not defaults.FIXES["stats"]:
        log("WARNING: Stats fixer not enabled but stats have been found!")

    if "UUID" in entity:
        if not is_from_spawner:
            uuid = utils.uuid_from_int_array(entity["UUID"].value)
            uuid_dict[uuid[:16]] = uuid
            if uuid in uuid_list:
                new_uuid = utils.new_uuid()
                entity["UUID"].value = new_uuid
                uuid = utils.uuid_from_int_array(new_uuid)
            uuid_list.append(uuid)

        elif pack_version <= 809:
            del entity["UUID"]

    if "CustomName" in entity:
        entity["CustomName"] = NBT.TAG_String(json_text_component.update(entity["CustomName"].value, pack_version, [], True))

    if "Equipment" in entity:
        if "ArmorItems" not in entity or "HandItems" not in entity:
            entity["ArmorItems"] = NBT.TAG_List(NBT.TAG_Compound)
            entity["ArmorItems"].tags = [
                entity["Equipment"][1],
                entity["Equipment"][2],
                entity["Equipment"][3],
                entity["Equipment"][4]
            ]
            entity["HandItems"] = NBT.TAG_List(NBT.TAG_Compound)
            entity["HandItems"].tags = [
                entity["Equipment"][0],
                NBT.TAG_Compound()
            ]

            if "DropChances" in entity:

                entity["ArmorDropChances"] = NBT.TAG_List(NBT.TAG_Float)
                entity["ArmorDropChances"].tags = [
                    entity["DropChances"][1],
                    entity["DropChances"][2],
                    entity["DropChances"][3],
                    entity["DropChances"][4]
                ]
                entity["HandDropChances"] = NBT.TAG_List(NBT.TAG_Float)
                entity["HandDropChances"].tags = [
                    entity["DropChances"][0],
                    NBT.TAG_Float(0.085)
                ]

                del entity["DropChances"]

        else:
            entity["ArmorItems"], entity["HandItems"] = entity["HandItems"], entity["ArmorItems"]

        del entity["Equipment"]

        # Fix 0 count items
        for tag in ["ArmorItems", "HandItems"]:
            for item in entity[tag]:
                if "Count" in item:
                    if item["Count"].value == 0:
                        item["Count"].value = 1
                elif "id" in item:
                    item["Count"] = NBT.TAG_Byte(1)


    absorption_level = None
    if "ActiveEffects" in entity:
        entity["active_effects"] = NBT.TAG_List(NBT.TAG_Compound)
        for effect in entity["ActiveEffects"]:
            entity["active_effects"].append(fix_effect(effect))
            if "id" in effect and effect["id"].value == "minecraft:absorption" and "amplifier" in effect:
                absorption_level = effect["amplifier"].value
        del entity["ActiveEffects"]
    elif "active_effects" in entity:
        for effect in entity["active_effects"]:
            if "id" in effect and effect["id"].value == "minecraft:absorption" and "amplifier" in effect:
                absorption_level = effect["amplifier"].value
                break

    for old_key, new_key in {
        "Effects": "effects",
        "CustomPotionEffects": "custom_potion_effects"
    }.items():
        if old_key in entity:
            entity[new_key] = NBT.TAG_List(NBT.TAG_Compound)
            for effect in entity[old_key]:
                entity[new_key].append(fix_effect(effect))
            del entity[old_key]

    if absorption_level != None:
        if "Attributes" not in entity:
            entity["Attributes"] = NBT.TAG_List(NBT.TAG_Compound)
        for attribute in entity["Attributes"]:
            if "Name" not in attribute:
                continue
            if attribute["Name"] == "minecraft:generic.max_absorption":
                break
        else:
            attribute = NBT.TAG_Compound()
            attribute["Name"] = NBT.TAG_String("minecraft:generic.max_absorption")
            attribute["Base"] = NBT.TAG_Double(0.0)
            attribute["Modifiers"] = NBT.TAG_List(NBT.TAG_Compound)
            
            modifier = NBT.TAG_Compound()
            modifier["Amount"] = NBT.TAG_Double(float(4*(absorption_level + 1)))
            modifier["Operation"] = NBT.TAG_Int(0)
            modifier["Name"] = NBT.TAG_String(f'effect.minecraft.absorption {absorption_level}')
            modifier["UUID"] = NBT.TAG_Int_Array(name="UUID")
            modifier["UUID"].value = utils.new_uuid()
            
            attribute["Modifiers"].append(modifier)
            entity["Attributes"].append(attribute)


    for tag in ["ArmorItems", "HandItems", "Inventory"]:
        if tag in entity:
            for item in entity[tag]:
                fix_item(item, is_from_spawner)
    for tag in ["ArmorItem", "Item", "SaddleItem"]:
        if tag in entity:
            fix_item(entity[tag], is_from_spawner)
    if "Offers" in entity:
        if "Recipes" in entity["Offers"]:
            for recipe in entity["Offers"]["Recipes"]:
                for tag in ["buy", "buyB", "sell"]:
                    if tag in recipe:
                        fix_item(recipe[tag], is_from_spawner)



    if "Attributes" in entity and pack_version <= 710:
        for attribute in entity["Attributes"]:
            if "Name" in attribute and not attribute["Name"].value.startswith("minecraft:"):
                attribute["Name"] = NBT.TAG_String(f'minecraft:{attribute["Name"].value}')
                if attribute["Name"].value == "minecraft:generic.movement_speed":
                    
                    size = 0
                    if entity["id"].value in ["minecraft:slime", "minecraft:magma_cube"] and "Size" in entity:
                        size: int = entity["Size"].value
                    
                    speed_array = {
                        "minecraft:blaze": (0.1, 0.23),
                        "minecraft:cave_spider": (0.8, 0.3),
                        "minecraft:ghast": (0.1, 0.7),
                        "minecraft:magma_cube": (0.2, 0.3 + 0.1*size),
                        "minecraft:spider": (0.8, 0.3),
                        "minecraft:silverfish": (0.6, 0.25),
                        "minecraft:slime": (0.1, 0.3 + 0.1*size),
                        "minecraft:squid": (0.1, 0.7),
                        "minecraft:zombified_piglin": (0.5, 0.23)
                    }

                    if entity["id"].value in speed_array and "Base" in attribute:
                        speed_conversion = speed_array[entity["id"].value]
                        attribute["Base"] = NBT.TAG_Double(attribute["Base"].value * speed_conversion[1] / speed_conversion[0])



    # Tags to nuke
    for tag in ["Dimension", "EntityId", "Riding", "SkeletonType"]:
        if tag in entity:
            del entity[tag]



    # Grab position from the mob to be passed to the mount
    if (
        "id" in entity and
        entity["id"].value in tables.HOSTILE_MOBS and
        "Pos" in entity and
        pack_version <= 809 and
        is_from_spawner
    ):
        output["Pos"] = [
            entity["Pos"][0].value,
            entity["Pos"][1].value,
            entity["Pos"][2].value
        ]
        del entity["Pos"]



    passenger_output: dict[str] = {}
    if "Passengers" in entity:
        for passenger in entity["Passengers"]:
            passenger_output = fix_entity_recursive_passenger(passenger, is_from_spawner)



    for tag in passenger_output:
        output[tag] = passenger_output[tag]
    return output



def fix_item(item: NBT.TAG_Compound, is_from_spawner: bool = False):
    if "id" not in item:
        return

    if not is_from_spawner:
        if "tag" in item:
            item_tag = item["tag"]

            # Handle CanPlaceOn and CanDestroy
            if pack_version <= 904:
                for tag in ["CanPlaceOn", "CanDestroy"]:
                    if tag in item_tag:
                        fix_can_place_on(item_tag, tag)

            # Handle display data
            if "display" in item_tag:
                if "Name" in item_tag["display"]:
                    item_tag["display"]["Name"] = NBT.TAG_String(json_text_component.update(item_tag["display"]["Name"].value, pack_version, [], False))
                if "Lore" in item_tag["display"]:
                    lore = item_tag["display"]["Lore"]
                    for i in range(len(lore)):
                        lore[i] = NBT.TAG_String(json_text_component.update(lore[i].value, pack_version, [], False))

            # Handle book pages
            if "pages" in item_tag:
                pages: NBT.TAG_List = item_tag["pages"]
                for i in range(len(pages)):
                    pages[i] = NBT.TAG_String(json_text_component.update(pages[i].value, pack_version, [], False))

            # Handle effects
            for old_key, new_key in {
                "CustomPotionEffects": "custom_potion_effects"
            }.items():
                if old_key in item_tag:
                    item_tag[new_key] = NBT.TAG_List(NBT.TAG_Compound)
                    for effect in item_tag[old_key]:
                        item_tag[new_key].append(fix_effect(effect))
                    del item_tag[old_key]

            # Handle block entity tag
            if "BlockEntityTag" in item_tag:
                fix_block_entity(item_tag["BlockEntityTag"])

            # Handle entity tag
            if "EntityTag" in item_tag:
                fix_entity_recursive_passenger(item_tag["EntityTag"], False)

        # Handle old adventure mode
        if pack_version <= 710 and defaults.FIXES["old_adventure_mode_items"]:
            item_id = item["id"].value
            insert_old_adventure_mode_tags(item, item_id)

    else:
        item_nbt = nbt_tags.convert_from_lib_format(item)
        item_nbt = items.update_from_nbt(item_nbt, pack_version, [])
        new_item: NBT.TAG_Compound = nbt_tags.convert_to_lib_format(item_nbt)
        for key in item:
            del item[key]
        for key in new_item:
            item[key] = new_item[key]



def fix_can_place_on(item_tag: NBT.TAG_Compound, tag: str):
    new_list: list[str] = []
    block: NBT.TAG_String
    for block in item_tag[tag]:
        if block.value in tables.BLOCK_TAG_REPLACEMENT_KEYS:
            new_list.append(tables.BLOCK_TAG_REPLACEMENT_KEYS[block.value])
        else:
            new_list.append(block.value)
    new_list = utils.deduplicate_list(new_list)
    item_tag[tag] = NBT.TAG_List(NBT.TAG_String)
    for entry in new_list:
        item_tag[tag].append(NBT.TAG_String(entry))



def insert_old_adventure_mode_tags(item: NBT.TAG_Compound, item_id: str):
    if "tag" not in item:
        item["tag"] = NBT.TAG_Compound()
    item_tag = item["tag"]

    item_tag["adventure"] = NBT.TAG_Byte(1)
    item_tag["HideFlags"] = NBT.TAG_Int(24)

    if item_id in tables.BLOCK_PLACEABLE:
        item_tag["CanPlaceOn"] = NBT.TAG_List(NBT.TAG_String)
        item_tag["CanPlaceOn"].tags = [NBT.TAG_String("#adventure:all")]

        item_tag["CanDestroy"] = NBT.TAG_List(NBT.TAG_String)
        item_tag["CanDestroy"].tags = [NBT.TAG_String("#adventure:mineable/universal")]

    elif item_id in [
        "minecraft:wooden_pickaxe",
        "minecraft:stone_pickaxe",
        "minecraft:golden_pickaxe",
        "minecraft:iron_pickaxe",
        "minecraft:diamond_pickaxe",
        "minecraft:netherite_pickaxe"
    ]:
        item_tag["CanDestroy"] = NBT.TAG_List(NBT.TAG_String)
        item_tag["CanDestroy"].tags = [NBT.TAG_String("#minecraft:mineable/pickaxe"), NBT.TAG_String("#adventure:mineable/universal")]

    elif item_id in [
        "minecraft:wooden_shovel",
        "minecraft:stone_shovel",
        "minecraft:golden_shovel",
        "minecraft:iron_shovel",
        "minecraft:diamond_shovel",
        "minecraft:netherite_shovel"
    ]:
        item_tag["CanDestroy"] = NBT.TAG_List(NBT.TAG_String)
        item_tag["CanDestroy"].tags = [NBT.TAG_String("#minecraft:mineable/shovel"), NBT.TAG_String("#adventure:mineable/universal")]

    elif item_id in [
        "minecraft:wooden_axe",
        "minecraft:stone_axe",
        "minecraft:golden_axe",
        "minecraft:iron_axe",
        "minecraft:diamond_axe",
        "minecraft:netherite_axe"
    ]:
        item_tag["CanDestroy"] = NBT.TAG_List(NBT.TAG_String)
        item_tag["CanDestroy"].tags = [NBT.TAG_String("#minecraft:mineable/axe"), NBT.TAG_String("#adventure:mineable/universal")]

    elif item_id in [
        "minecraft:wooden_hoe",
        "minecraft:stone_hoe",
        "minecraft:golden_hoe",
        "minecraft:iron_hoe",
        "minecraft:diamond_hoe",
        "minecraft:netherite_hoe" 
    ]:
        item_tag["CanDestroy"] = NBT.TAG_List(NBT.TAG_String)
        item_tag["CanDestroy"].tags = [NBT.TAG_String("#minecraft:mineable/hoe"), NBT.TAG_String("#adventure:mineable/universal")]

    elif item_id in [
        "minecraft:wooden_sword",
        "minecraft:stone_sword",
        "minecraft:golden_sword",
        "minecraft:iron_sword",
        "minecraft:diamond_sword",
        "minecraft:netherite_sword"
    ]:
        item_tag["CanDestroy"] = NBT.TAG_List(NBT.TAG_String)
        item_tag["CanDestroy"].tags = [NBT.TAG_String("#adventure:mineable/sword"), NBT.TAG_String("#adventure:mineable/universal")]

    elif item_id == "minecraft:shears":
        item_tag["CanDestroy"] = NBT.TAG_List(NBT.TAG_String)
        item_tag["CanDestroy"].tags = [NBT.TAG_String("#adventure:mineable/shears"), NBT.TAG_String("#adventure:mineable/universal")]

    else:
        item_tag["CanDestroy"] = NBT.TAG_List(NBT.TAG_String)
        item_tag["CanDestroy"].tags = [NBT.TAG_String("#adventure:mineable/universal")]



def fix_effect(effect: NBT.TAG_Compound) -> NBT.TAG_Compound:
    if "Id" in effect:
        effect["id"] = NBT.TAG_String(ids.effect(effect["Id"].value, pack_version, []))
        del effect["Id"]
    if "Amplifier" in effect:
        effect["amplifier"] = effect["Amplifier"]
    if "Ambient" in effect:
        effect["ambient"] = effect["Ambient"]
    if "Duration" in effect:
        effect["duration"] = effect["Duration"]
    if "ShowIcon" in effect:
        effect["show_icon"] = effect["ShowIcon"]
    if "ShowParticles" in effect:
        effect["show_particles"] = effect["ShowParticles"]
    if "HiddenEffect" in effect:
        effect["hidden_effect"] = fix_effect(effect["HiddenEffect"])
    return effect



def fix_scoreboard_dat(world: Path):
    file_path = world / "data" / "scoreboard.dat"
    if not file_path.exists():
        return
    
    file = NBT.NBTFile(file_path)
    if "data" not in file:
        return
    
    if "Objectives" in file["data"]:
        objective: NBT.TAG_Compound
        for objective in file["data"]["Objectives"]:
            objective["CriteriaName"].value = ids.scoreboard_objective_criteria({"name": objective["Name"].value, "criteria": objective["CriteriaName"].value}, pack_version, [])

    if "PlayerScores" in file["data"]:
        index_list = list(range(len(file["data"]["PlayerScores"])))
        index_list.reverse()
        for index in index_list:
            player_score: NBT.TAG_Compound = file["data"]["PlayerScores"][index]
            
            if player_score["Name"].value in uuid_dict:
                player_score["Name"] = NBT.TAG_String(uuid_dict[player_score["Name"].value])

            if (
                utils.is_uuid(player_score["Name"].value) and player_score["Name"].value not in uuid_list
            ) or (
                utils.is_partial_uuid(player_score["Name"].value) and player_score["Name"].value not in uuid_dict
            ):
                del file["data"]["PlayerScores"][index]

    file.write_file(file_path)



def fix_maps(world: Path):
    folder_path = world / "data"
    if not folder_path.exists:
        return
    for file_path in folder_path.iterdir():
        if file_path.name.startswith("map_") and file_path.name.endswith(".dat"):
            file = NBT.NBTFile(file_path)
            modified = False
            if "DataVersion" not in file:
                file["DataVersion"] = NBT.TAG_Int(defaults.DATA_VERSION)
                modified = True
            if "data" not in file:
                file["data"] = NBT.TAG_Compound()
                modified = True
            
            data = file["data"]
            if "scale" not in data:
                data["scale"] = NBT.TAG_Byte(0)
                modified = True
            if "dimension" not in data:
                data["dimension"] = NBT.TAG_String("minecraft:overworld")
                modified = True
            if isinstance(data["dimension"].value, int):
                data["dimension"] = NBT.TAG_String({
                    0: "minecraft:overworld",
                    -1: "minecraft:the_nether",
                    1: "minecraft:the_end"
                }[data["dimension"].value])
                modified = True
            if "trackingPosition" not in data:
                data["trackingPosition"] = NBT.TAG_Byte(1)
                modified = True
            if "unlimitedTracking" not in data:
                data["unlimitedTracking"] = NBT.TAG_Byte(1)
                modified = True
            if "locked" not in data:
                data["locked"] = NBT.TAG_Byte(0)
                modified = True
            if "xCenter" not in data:
                data["xCenter"] = NBT.TAG_Int(0)
                modified = True
            if "zCenter" not in data:
                data["zCenter"] = NBT.TAG_Int(0)
                modified = True
            if "banners" not in data:
                data["banners"] = NBT.TAG_List(NBT.TAG_Compound)
                modified = True
            if "frames" not in data:
                data["frames"] = NBT.TAG_List(NBT.TAG_Compound)
                modified = True
            if "colors" not in data:
                data["colors"] = NBT.TAG_Byte_Array()
                data["colors"].value = [0 for i in range(16384)]
                modified = True

            if modified:
                file.write_file(file_path)
            continue
                



def create_spawner_bossbar_file(world: Path):
    log("Boss spawners found")

    folder_path = world / "data"
    folder_path.mkdir(exist_ok=True, parents=True)

    file = NBT.NBTFile()
    file["data"] = NBT.TAG_Compound()
    file["data"]["contents"] = NBT.TAG_Compound()
    file["data"]["contents"]["data"] = NBT.TAG_Compound()
    file["data"]["contents"]["data"]["spawner_list"] = spawner_bossbar_list
    file["DataVersion"] = NBT.TAG_Int(DATA_VERSION)

    file_path = folder_path / "command_storage_bossbar.dat"
    file.write_file(file_path)

    spawner_bossbar.create_pack(world)