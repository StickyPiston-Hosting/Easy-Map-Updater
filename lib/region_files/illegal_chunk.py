# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import shutil
from nbt import nbt as NBT
from pathlib import Path
from lib.log import log
from lib import defaults
from lib import utils
from lib import finalize
from lib.data_pack_files import blocks



# Initialize variables

PROGRAM_PATH = Path(__file__).parent

STAIRS = [
    "minecraft:acacia_stairs",
    "minecraft:andesite_stairs",
    "minecraft:birch_stairs",
    "minecraft:brick_stairs",
    "minecraft:cobblestone_stairs",
    "minecraft:dark_oak_stairs",
    "minecraft:dark_prismarine_stairs",
    "minecraft:diorite_stairs",
    "minecraft:end_stone_brick_stairs",
    "minecraft:granite_stairs",
    "minecraft:jungle_stairs",
    "minecraft:mossy_cobblestone_stairs",
    "minecraft:mossy_stone_brick_stairs",
    "minecraft:nether_brick_stairs",
    "minecraft:oak_stairs",
    "minecraft:polished_andesite_stairs",
    "minecraft:polished_diorite_stairs",
    "minecraft:polished_granite_stairs",
    "minecraft:prismarine_brick_stairs",
    "minecraft:prismarine_stairs",
    "minecraft:purpur_stairs",
    "minecraft:quartz_stairs",
    "minecraft:red_nether_brick_stairs",
    "minecraft:red_sandstone_stairs",
    "minecraft:sandstone_stairs",
    "minecraft:smooth_quartz_stairs",
    "minecraft:smooth_red_sandstone_stairs",
    "minecraft:smooth_sandstone_stairs",
    "minecraft:spruce_stairs",
    "minecraft:stone_brick_stairs",
    "minecraft:stone_stairs"
]

STAIR_BLOCK_STATES = {
    "shape": [
        "inner_left",
        "inner_right",
        "outer_left",
        "outer_right"
    ],
    "facing": [
        "north",
        "south",
        "west",
        "east"
    ],
    "half": [
        "bottom",
        "top"
    ],
    "waterlogged": [
        "false",
        "true"
    ]
}

MISCELLANEOUS_BLOCKS = [
    "minecraft:cactus"
]



# Define functions

def insert_chunk(world: Path):
    log("Inserting illegal block state chunk")

    if not world.exists():
        log("ERROR: World does not exist!")
        return

    # Clone region file
    region_file_name = "r.19531.39062.mca"
    region_path = world / "region"
    region_path.mkdir(exist_ok=True, parents=True)
    shutil.copyfile(PROGRAM_PATH / region_file_name, world / "region" / region_file_name)



    # Insert chunk forceload state
    x = 10000000//16
    z = 20000000//16
    x %= 4294967296
    z %= 4294967296
    chunk_id = x + z*4294967296
    chunk_file_path = world / "data" / "chunks.dat"
    if not chunk_file_path.exists():
        chunk_file_path.parent.mkdir(exist_ok=True, parents=True)
        chunk_file = NBT.NBTFile()
    else:
        chunk_file = NBT.NBTFile(chunk_file_path)
    if "DataVersion" not in chunk_file:
        chunk_file["DataVersion"] = NBT.TAG_Int(defaults.DATA_VERSION)
    if "data" not in chunk_file:
        chunk_file["data"] = NBT.TAG_Compound()
    if "Forced" not in chunk_file["data"]:
        chunk_file["data"]["Forced"] = NBT.TAG_Long_Array()
        chunk_file["data"]["Forced"].value = [chunk_id]
    else:
        if not utils.nbt_num_array_contains(chunk_file["data"]["Forced"], chunk_id):
            chunk_file["data"]["Forced"].append(chunk_id)
    chunk_file.write_file(chunk_file_path)



    # Insert data pack which forces the chunk to always be forceloaded
    data_pack_folder = world / "datapacks"
    data_pack_folder.mkdir(exist_ok=True, parents=True)
    shutil.copyfile(PROGRAM_PATH / "illegal_chunk_forceloader.zip", data_pack_folder / "illegal_chunk_forceloader.zip")

    log("Illegal block state chunk inserted")

    finalize.log_data_packs(world)



def replace_command(command: list[str]) -> str:
    # Extract block states
    block = command[4].split("{")[0]
    if "[" in block:
        block_id = block[:block.find("[")]
        block_states = blocks.unpack_block_states(block[block.find("["):])
    else:
        block_id = block
        block_states: dict[str, str] = {}

    # Handle stairs
    if block_id.endswith("_stairs"):
        # Apply default block states
        for default_state in [
            ("facing", "north"),
            ("half", "bottom"),
            ("shape", "straight"),
            ("waterlogged", "false")
        ]:
            if default_state[0] not in block_states:
                block_states[default_state[0]] = default_state[1]

        # Cancel if shape is straight
        if block_states["shape"] == "straight":
            return " ".join(command)
        
        # Generate coordinates
        xz = (
            STAIR_BLOCK_STATES["shape"      ].index(block_states["shape"      ]) +
            STAIR_BLOCK_STATES["facing"     ].index(block_states["facing"     ])*4 +
            STAIR_BLOCK_STATES["half"       ].index(block_states["half"       ])*8 +
            STAIR_BLOCK_STATES["waterlogged"].index(block_states["waterlogged"])*16
        )
        x = xz%8*2 + 10000000
        z = xz//8*2 + 20000000
        if block_id in STAIRS:
            y = STAIRS.index(block_id)*2 - 64
        else:
            y = -64

        log("Illegal block found! Insert the illegal block chunk into the world")
        return f'clone from minecraft:overworld {x} {y} {z} {x} {y} {z} {command[1]} {command[2]} {command[3]}'
    
    # Handle miscellaneous blocks
    if block_id in MISCELLANEOUS_BLOCKS:
        index = MISCELLANEOUS_BLOCKS.index(block_id)
        x = index%8*2 + 10000016
        z = index//8%8*2 + 20000000
        y = index//64*2 - 64
        log("Illegal block found! Insert the illegal block chunk into the world")
        return f'clone from minecraft:overworld {x} {y} {z} {x} {y} {z} {command[1]} {command[2]} {command[3]}'

    return " ".join(command)