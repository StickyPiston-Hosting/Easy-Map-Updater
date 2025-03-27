# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from pathlib import Path
import json
from typing import cast, TypedDict, NotRequired
from nbt import nbt as NBT
from nbt import region
from lib import option_manager
from lib.data_pack_files import command
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import target_selectors
from lib.region_files import fix_world
from lib import defaults
from lib import utils
from lib.log import log
import math



# Initialize variables

pack_version = defaults.PACK_VERSION
PROGRAM_PATH = Path(__file__).parent.parent.parent
MINECRAFT_PATH = PROGRAM_PATH.parent



# Define functions

class CommandGuide(TypedDict("CommandGuide", {"list": str})):
    coordinates: str
    region: str
    chunk_x: int
    chunk_z: int
    index: int
    tag: str
    command: str
    uuid: NotRequired[list[int]]
    CommandStats: NotRequired[dict]



def read_commands(world: Path):
    log("Reading command block data")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return

    commands: list[str] = []

    # Iterate through region files
    for path in [world, world / "DIM1", world / "DIM-1"]:
        region_output = read_commands_from_region_folder(world, path)
        if region_output != None and region_output != "":
            commands.append(region_output)
    dimensions = (world / "dimensions")
    if dimensions.exists():
        for dimension_namespace in dimensions.iterdir():
            for dimension in dimension_namespace.iterdir():
                region_output = read_commands_from_region_folder(world, dimension)
                if region_output != None and region_output != "":
                    commands.append(region_output)

    # Write results to file
    utils.safe_file_write(PROGRAM_PATH / "commands.mcfunction", "\n".join(commands))
    utils.safe_file_write(PROGRAM_PATH / "commands_original.mcfunction", "\n".join(commands))

    log("Command block data read")

def read_commands_from_region_folder(world: Path, folder_path: Path) -> str | None:
    if not folder_path.exists():
        return

    commands: list[str] = []
    # Iterate between region and entities
    folder: tuple[str, str]
    for folder in [("region", "block_entities"), ("entities", "Entities")]:
        if not (folder_path / folder[0]).exists():
            continue
        for file_path in (folder_path / folder[0]).iterdir():
            region_output = read_commands_from_region(world, file_path, folder[1])
            if region_output != None and region_output != "":
                commands.append(region_output)

    return "\n".join(commands)

def read_commands_from_region(world: Path, file_path: Path, list_name: str) -> str | None:
    commands: list[str] = []

    log(f" Reading {file_path.name}")
    try:
        region_file = region.RegionFile(file_path)
    except:
        return
    chunk_metadata: region.ChunkMetadata
    for chunk_metadata in region_file.get_metadata():
        try:
            chunk = region_file.get_nbt(chunk_metadata.x, chunk_metadata.z)
        except:
            continue
        if not chunk:
            continue
        if list_name not in chunk:
            continue
        block_entities: NBT.TAG_List = chunk[list_name]
        if block_entities == None or len(block_entities) == 0:
            continue

        # Iterate through block entities
        for index in range(len(block_entities)):
            block_entity: NBT.TAG_Compound = block_entities[index]
            block_entity_id: NBT.TAG_String = block_entity["id"]

            if list_name == "block_entities":

                x: int = block_entity["x"].value
                y: int = block_entity["y"].value
                z: int = block_entity["z"].value

                if block_entity_id.value == "minecraft:command_block":
                    tag = "Command"
                    if tag not in block_entity:
                        continue
                    command_string: NBT.TAG_String = block_entity[tag]
                    if not command_string or not command_string.value:
                        continue

                    data = cast(CommandGuide, {
                        "coordinates": f"{x} {y} {z}",
                        "region": file_path.as_posix()[len(world.as_posix())+1:],
                        "chunk_x": chunk_metadata.x,
                        "chunk_z": chunk_metadata.z,
                        "list": list_name,
                        "index": index,
                        "tag": tag
                    })
                    if "CommandStats" in block_entity:
                        data["CommandStats"] = {}
                        for key in block_entity["CommandStats"]:
                            data["CommandStats"][key] = block_entity["CommandStats"][key].value
                    commands.append(
                        f'# {json.dumps(data)}\n{command.remove_slash(command_string.value)}'
                    )

                if block_entity_id.value == "minecraft:sign":
                    sign_nbt = {}
                    for tag in ["front_text", "back_text"]:
                        if tag not in block_entity:
                            continue
                        text = block_entity[tag]
                        if "messages" not in text:
                            continue
                        sign_nbt[tag] = {"messages": []}
                        for message in text["messages"]:
                            sign_nbt[tag]["messages"].append(message.value)

                    data = cast(CommandGuide, {
                        "coordinates": f"{x} {y} {z}",
                        "region": file_path.as_posix()[len(world.as_posix())+1:],
                        "chunk_x": chunk_metadata.x,
                        "chunk_z": chunk_metadata.z,
                        "list": list_name,
                        "index": index,
                        "tag": "sign_edge_case"
                    })
                    if "CommandStats" in block_entity:
                        data["CommandStats"] = {}
                        for key in block_entity["CommandStats"]:
                            data["CommandStats"][key] = block_entity["CommandStats"][key].value
                    commands.append(
                        f'# {json.dumps(data)}\ndata merge block ~ ~ ~ {nbt_tags.pack(sign_nbt)}'
                    )

            if list_name == "Entities" and block_entity_id.value == "minecraft:command_block_minecart":
                tag = "Command"
                if tag not in block_entity:
                    continue
                command_string: NBT.TAG_String = block_entity[tag]
                x = int(math.floor(block_entity["Pos"][0].value))
                y = int(math.floor(block_entity["Pos"][1].value))
                z = int(math.floor(block_entity["Pos"][2].value))
                uuid: list[int] = [
                    block_entity["UUID"][0],
                    block_entity["UUID"][1],
                    block_entity["UUID"][2],
                    block_entity["UUID"][3]
                ]
                if command_string == None or command_string.value == "":
                    continue
                data = cast(CommandGuide, {
                    "coordinates": f"{x} {y} {z}",
                    "region": file_path.as_posix()[len(world.as_posix())+1:],
                    "chunk_x": chunk_metadata.x,
                    "chunk_z": chunk_metadata.z,
                    "list": list_name,
                    "index": index,
                    "tag": tag,
                    "uuid": uuid
                })
                if "CommandStats" in block_entity:
                    data["CommandStats"] = {}
                    for key in block_entity["CommandStats"]:
                        data["CommandStats"][key] = block_entity["CommandStats"][key].value
                commands.append(
                    f'# {json.dumps(data)}\n{command.remove_slash(command_string.value)}'
                )

    return "\n".join(commands)



def write_commands(world: Path, get_confirmation: bool):
    log("Writing command block data")

    # Check for errors
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if not (PROGRAM_PATH / "commands.mcfunction").exists():
        log("ERROR: commands.mcfunction does not exist!")
        return

    # Get confirmation
    if get_confirmation:
        log(f'This action will modify several region files in: {world.as_posix()}')
        confirm = input("Is this okay? (Y/N): ")
        if confirm not in ["Y", "y"]:
            log("Action canceled")
            return

    # Extract commands from file
    commands = utils.safe_file_read(PROGRAM_PATH / "commands.mcfunction").split("\n")
    region_change = False
    chunk_change = False
    init_bool = False
    # Iterate through commands
    guide = cast(CommandGuide, {"coordinates": "", "region": "", "chunk_x": None, "chunk_z": None, "list": None, "index": None, "tag": None})
    previous_guide = guide.copy()
    region_file = None
    chunk = NBT.NBTFile()
    block_entities = NBT.TAG_List()
    block_entity = NBT.TAG_Compound()
    for command in commands:
        if not command:
            continue

        # Manage the guide
        if command.startswith("# {"):
            previous_guide = guide.copy()
            guide = cast(CommandGuide, json.loads(command[2:]))
            region_change = guide["region"] != previous_guide["region"]
            chunk_change = guide["chunk_x"] != previous_guide["chunk_x"] or guide["chunk_z"] != previous_guide["chunk_z"] or region_change

            # Write chunk to region file
            if chunk_change and init_bool and region_file:
                region_file.write_chunk(previous_guide["chunk_x"], previous_guide["chunk_z"], chunk)

            # Manage region file
            if region_change:
                region_file = region.RegionFile(world / guide["region"])

            # Manage chunk
            if chunk_change and region_file:
                chunk: NBT.NBTFile = region_file.get_nbt(guide["chunk_x"], guide["chunk_z"])
                if chunk:
                    if guide["list"] not in chunk:
                        chunk[guide["list"]] = NBT.TAG_List(value=[])
                    block_entities: NBT.TAG_List = chunk[guide["list"]]

            init_bool = True
            continue

        # Get block entity
        search_list = False
        if len(block_entities) > guide["index"]:
            block_entity = block_entities[guide["index"]]
            if not test_block_entity(guide, block_entity):
                search_list = True
        else:
            search_list = True
        if search_list:
            for block_entity in block_entities:
                if test_block_entity(guide, block_entity):
                    break
            else:
                log(f'Skipping block: {guide["coordinates"]} - {guide["chunk_x"]}, {guide["chunk_z"]} - {guide["region"]}')
                continue

        # Write command to chunk
        if guide["tag"] == "sign_edge_case":
            sign_nbt: dict[str, dict[str, nbt_tags.TypeList | str | nbt_tags.TypeByte]] = nbt_tags.unpack(command[23:])
            for sign_side in sign_nbt:
                if sign_side not in block_entity:
                    block_entity[sign_side] = NBT.TAG_Compound()
                for key in sign_nbt[sign_side]:
                    tag = sign_nbt[sign_side][key]
                    if isinstance(tag, str):
                        block_entity[sign_side][key] = NBT.TAG_String(tag)
                    if isinstance(tag, nbt_tags.TypeByte):
                        block_entity[sign_side][key] = NBT.TAG_Byte(tag.value)
                    if isinstance(tag, nbt_tags.TypeList):
                        block_entity[sign_side][key] = NBT.TAG_List(type=NBT.TAG_String)
                        for entry in tag:
                            block_entity[sign_side][key].append(NBT.TAG_String(entry))

        else:
            block_entity[guide["tag"]] = NBT.TAG_String(command)

    if init_bool and region_file:
        region_file.write_chunk(guide["chunk_x"], guide["chunk_z"], chunk)

    log("Command block data written")

def test_block_entity(guide: CommandGuide, block_entity: NBT.TAG_Compound) -> bool:
    if "uuid" in guide:
        uuid: NBT.TAG_Int_Array = block_entity["UUID"]
        return (
            uuid[0] == guide["uuid"][0] and
            uuid[1] == guide["uuid"][1] and
            uuid[2] == guide["uuid"][2] and
            uuid[3] == guide["uuid"][3]
        )
    else:
        coordinates = guide["coordinates"].split(" ")
        return (
            block_entity["x"].value == int(coordinates[0]) and
            block_entity["y"].value == int(coordinates[1]) and
            block_entity["z"].value == int(coordinates[2])
        )



def update_commands(version: int):
    log("Updating command block data")

    # Set pack version
    global pack_version
    pack_version = version

    # Check for errors
    if not (PROGRAM_PATH / "commands_original.mcfunction").exists():
        log("ERROR: commands_original.mcfunction does not exist!")
        return

    # Read commands
    contents = utils.safe_file_read(PROGRAM_PATH / "commands_original.mcfunction")

    # Split up the lines
    lines = contents.split("\n")

    # Iterate and convert the lines
    comment_info = cast(CommandGuide, {})
    for line_index in range(len(lines)):
        line = lines[line_index]

        # Skip line if it is blank or a comment
        if not line:
            continue
        if line.startswith("# {"):
            comment_info = cast(CommandGuide, json.loads(line[2:]))
        if line[0] in ["#", " "]:
            continue

        # Convert command
        line = command.update(line, pack_version, "commands.mcfunction")

        # Apply simplistic stat update
        if "CommandStats" in comment_info and pack_version >= 800 and pack_version <= 1202:
            stats_options = option_manager.FIXES["stats_options"]
            if (
                option_manager.FIXES["stats"] and
                stats_options["block_stats_used"] and
                not stats_options["block_positions_dynamic"] and
                not stats_options["commands_written_to_sensitive_position"] and
                not stats_options["commands_written_to_arbitrary_position"] and
                not stats_options["entity_stats_used"] and
                not stats_options["entity_types_dynamic"] and
                not stats_options["complex_stat_usage"]
            ):
                key: str
                used_stat = ""
                for key in comment_info["CommandStats"]:
                    if key.endswith("Name"):
                        used_stat = key[:-4]
                        break
                line = command.remove_run_execute(f'execute store result score {target_selectors.update(comment_info["CommandStats"][f"{used_stat}Name"], pack_version, [], True)} {comment_info["CommandStats"][f"{used_stat}Objective"]} run {line}')

        # Write line to list
        lines[line_index] = line

    utils.safe_file_write(PROGRAM_PATH / "commands.mcfunction", "\n".join(lines))
    function_path = MINECRAFT_PATH / "saves" / "Testing World" / "datapacks" / "Test Data Pack" / "data" / "test" / "function"
    if function_path.exists():
        utils.safe_file_write(function_path / "commands.mcfunction", "\n".join(lines))

    log("Command block data updated")



def extract_commands(world: Path):
    location = input("Coordinates of command block chain to extract: ").split(" ")
    if (
        len(location) < 3 or
        not utils.is_int(location[0]) or
        not utils.is_int(location[1]) or
        not utils.is_int(location[2])
    ):
        log("ERROR: Location is malformed!")
        return
    x, y, z = int(location[0]), int(location[1]), int(location[2])
    
    if len(location) < 4:
        dimension = "region"
    elif location[3] == "nether":
        dimension = "DIM-1/region"
    elif location[3] == "end":
        dimension = "DIM1/region"
    else:
        dimension = "region"


    command_data = compile_command_data("commands.mcfunction")
    og_command_data = compile_command_data("commands_original.mcfunction")


    extracted_commands: list[str] = []

    region_change = False
    chunk_change = False
    init_bool = False
    guide = cast(CommandGuide, {"region": "", "chunk_x": None, "chunk_z": None})
    region_file = None
    chunk = NBT.NBTFile()
    for i in range(1000):
        if (x,y,z) in command_data[dimension]:
            extracted_commands.append(command_data[dimension][(x,y,z)]["command"])
            # command_data[dimension][(x,y,z)]["command"] = "#" + command_data[dimension][(x,y,z)]["command"]
            # og_command_data[dimension][(x,y,z)]["command"] = "#" + og_command_data[dimension][(x,y,z)]["command"]

        previous_guide = guide.copy()
        guide = {"region": f'{dimension}/r.{x//512}.{z//512}.mca', "chunk_x": x//16%32, "chunk_z": z//16%32}
        region_change = guide["region"] != previous_guide["region"]
        chunk_change = guide["chunk_x"] != previous_guide["chunk_x"] or guide["chunk_z"] != previous_guide["chunk_z"] or region_change

        if region_change:
            region_file = region.RegionFile(world / guide["region"])

        if chunk_change and region_file:
            chunk: NBT.NBTFile = region_file.get_nbt(guide["chunk_x"], guide["chunk_z"])

        block_data = fix_world.get_block_data(chunk, x, y, z)
        if (
            block_data["Name"].value not in ["minecraft:command_block", "minecraft:chain_command_block", "minecraft:repeating_command_block"] or
            "Properties" not in block_data or
            "facing" not in block_data["Properties"] or
            (init_bool and block_data["Name"].value != "minecraft:chain_command_block")
        ):
            break
        if block_data["Properties"]["facing"].value == "west":
            x -= 1
        elif block_data["Properties"]["facing"].value == "east":
            x += 1
        elif block_data["Properties"]["facing"].value == "down":
            y -= 1
        elif block_data["Properties"]["facing"].value == "up":
            y += 1
        elif block_data["Properties"]["facing"].value == "north":
            z -= 1
        elif block_data["Properties"]["facing"].value == "south":
            z += 1
        else:
            break

        init_bool = True

    utils.safe_file_write(PROGRAM_PATH / "command_chain.mcfunction", "\n".join(extracted_commands))

    log("Command block chain extracted")



def compile_command_data(source: str) -> dict[str, dict[tuple[int, int, int], CommandGuide]]:
    commands = utils.safe_file_read(PROGRAM_PATH / source).split("\n")

    command_data: dict[str, dict[tuple[int, int, int], CommandGuide]] = {}
    guide = cast(CommandGuide, {"coordinates": "", "region": "", "chunk_x": None, "chunk_z": None, "list": None, "index": None, "tag": None})
    region_key = "region"
    coordinate_key = (0,0,0)
    for command in commands:
        if not command:
            continue

        if command.startswith("# {"):
            guide = cast(CommandGuide, json.loads(command[2:]))
            region_key = "/".join(guide["region"].split("/")[:-1])
            coordinate_key = coord_tuple(guide["coordinates"])
            if region_key not in command_data:
                command_data[region_key] = {}
            command_data[region_key][coordinate_key] = guide.copy()
            continue

        command_data[region_key][coordinate_key]["command"] = command
    
    return command_data

def coord_tuple(string: str) -> tuple[int, int, int]:
    split_string = string.split(" ")
    return (
        int(split_string[0]),
        int(split_string[1]),
        int(split_string[2])
    )