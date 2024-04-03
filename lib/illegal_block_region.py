from nbt import nbt as NBT
from nbt import region
from pathlib import Path
import defaults
import math

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



# 10,000,000, 20,000,000
# r 19531, 39062
# c 8, 16

def create_region():
    file_path = PROGRAM_PATH / "region_files" / f'r.19531.39062.mca'
    with file_path.open("wb") as file:
        file.write(b"")

    region_file = region.RegionFile(file_path)
    for coords in [
        (-1,-1),
        ( 0,-1),
        ( 1,-1),
        ( 2,-1),
        (-1, 0),
        ( 2, 0),
        (-1, 1),
        ( 0, 1),
        ( 1, 1),
        ( 2, 1),
        (-1, 2),
        ( 0, 2),
        ( 1, 2),
        ( 2, 2)
    ]:
        x = 10000000 + coords[0]*16
        z = 20000000 + coords[1]*16
        chunk = create_chunk(x, z)
        region_file.write_chunk(x//16%32, z//16%32, chunk)

    # Stairs
    chunk = create_chunk(10000000, 20000000)
    block_count = 0
    for stair in STAIRS:
        for waterlogged in STAIR_BLOCK_STATES["waterlogged"]:
            for half in STAIR_BLOCK_STATES["half"]:
                for facing in STAIR_BLOCK_STATES["facing"]:
                    for shape in STAIR_BLOCK_STATES["shape"]:
                        block = NBT.TAG_Compound()
                        block["Name"] = NBT.TAG_String(stair)
                        block["Properties"] = NBT.TAG_Compound()
                        block["Properties"]["facing"] = NBT.TAG_String(facing)
                        block["Properties"]["half"] = NBT.TAG_String(half)
                        block["Properties"]["shape"] = NBT.TAG_String(shape)
                        block["Properties"]["waterlogged"] = NBT.TAG_String(waterlogged)

                        chunk["sections"][block_count//512]["block_states"]["palette"].append(block)
                        block_count += 1
    insert_indices(chunk, block_count)
    region_file.write_chunk(8, 16, chunk)

    # Miscellaneous blocks
    chunk = create_chunk(10000016, 20000000)
    block_count = 0
    for block_id in ["minecraft:cactus"]:
        block = NBT.TAG_Compound()
        block["Name"] = NBT.TAG_String(block_id)
        chunk["sections"][block_count//512]["block_states"]["palette"].append(block)
        block_count += 1
    insert_indices(chunk, block_count)
    region_file.write_chunk(9, 16, chunk)



def create_chunk(x: int, z: int) -> NBT.NBTFile:
    chunk = NBT.NBTFile()

    chunk["DataVersion"] = NBT.TAG_Int(defaults.DATA_VERSION)
    chunk["xPos"] = NBT.TAG_Int(x//16)
    chunk["yPos"] = NBT.TAG_Int(-4)
    chunk["zPos"] = NBT.TAG_Int(z//16)
    chunk["Status"] = NBT.TAG_String("minecraft:full")
    chunk["LastUpdate"] = NBT.TAG_Long(0)
    chunk["InhabitedTime"] = NBT.TAG_Long(0)

    chunk["blendingData"] = NBT.TAG_Compound()
    chunk["blendingData"]["min_section"] = NBT.TAG_Int(-4)
    chunk["blendingData"]["max_section"] = NBT.TAG_Int(20)
    
    chunk["structures"] = NBT.TAG_Compound()
    chunk["structures"]["References"] = NBT.TAG_Compound()
    chunk["structures"]["starts"] = NBT.TAG_Compound()

    chunk["block_entities"] = NBT.TAG_List(NBT.TAG_Compound)
    chunk["block_ticks"] = NBT.TAG_List(NBT.TAG_Compound)
    chunk["fluid_ticks"] = NBT.TAG_List(NBT.TAG_Compound)
    chunk["PostProcessing"] = NBT.TAG_List(NBT.TAG_List)
    for i in range(24):
        chunk["PostProcessing"].append(NBT.TAG_List(NBT.TAG_Short))

    chunk["sections"] = NBT.TAG_List(NBT.TAG_Compound)
    for i in range(24):
        section = NBT.TAG_Compound()

        section["biomes"] = NBT.TAG_Compound()
        section["biomes"]["palette"] = NBT.TAG_List(NBT.TAG_String)
        section["biomes"]["palette"].append(NBT.TAG_String("minecraft:the_void"))
        
        section["block_states"] = NBT.TAG_Compound()
        section["block_states"]["palette"] = NBT.TAG_List(NBT.TAG_Compound)
        section["block_states"]["palette"].append(NBT.TAG_Compound())
        section["block_states"]["palette"][0]["Name"] = NBT.TAG_String("minecraft:air")

        section["Y"] = NBT.TAG_Byte(i-4)

        section["SkyLight"] = NBT.TAG_Byte_Array()
        section["SkyLight"].value = []
        for j in range(2048):
            section["SkyLight"].append(255)

        chunk["sections"].append(section)

    return chunk



def insert_indices(chunk: NBT.NBTFile, block_count: int):
    for section_index in range((block_count-1)//512 + 1):
        section: NBT.TAG_Compound = chunk["sections"][section_index]
        palette: NBT.TAG_List = section["block_states"]["palette"]
        palette_length = len(palette)
        index_size = max(int(math.ceil(math.log2(palette_length))), 4)
        index_size_divisor = int(2**index_size)
        indices_per_entry = 64//index_size
        
        data: list[int] = []
        for i in range(int(math.ceil(4096/indices_per_entry))):
            data.append(0)
        for i in range(min(block_count - 512*section_index, 512)):
            x = i%8*2
            z = i//8%8*2
            y = i//64*2
            data_index = (y*256 + z*16 + x)//indices_per_entry
            long_index = (y*256 + z*16 + x)%indices_per_entry
            long = data[data_index]

            right_point = int(index_size_divisor**long_index)
            left_point = right_point*index_size_divisor
            data[data_index] = (
                (i + 1)*right_point + # The index of the block in the palette
                (long%right_point) + # The part of the long to the right of the inserted index
                (long//left_point)*left_point # The part of the long to the left of the inserted index
            )

        section["block_states"]["data"] = NBT.TAG_Long_Array()
        section["block_states"]["data"].value = data



create_region()