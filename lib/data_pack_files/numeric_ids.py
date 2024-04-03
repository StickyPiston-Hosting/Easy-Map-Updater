# Import things

from lib.log import log
from lib import defaults
from lib.data_pack_files import tables



# Define functions

def update_block_item(numeric_id: int, data_value: int | str) -> tuple[str, int | str]:
    # Extract new data value if the current one is too big
    if numeric_id >= 4096:
        numeric_id, data_value = numeric_id%4096, numeric_id//4096

    id_array = tables.BLOCK_ITEM_NUMERIC_IDS
    if numeric_id not in id_array:
        return "minecraft:air"
    return (id_array[numeric_id], data_value)

def update_entity(numeric_id: int) -> str:
    id_array = tables.ENTITY_NUMERIC_IDS
    if numeric_id not in id_array:
        return "minecraft:pig"
    return id_array[numeric_id]