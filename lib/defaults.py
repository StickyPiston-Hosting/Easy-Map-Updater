# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Set default variables

DISCORD_INVITE = "https://discord.gg/nrqhv6PcqQ"

PACK_VERSION = 2006
DATA_PACK_FORMAT = 41
RESOURCE_PACK_FORMAT = 32
DATA_VERSION = 3839
DEBUG_MODE = False
SEND_WARNINGS = True
TEXT_FILE_FORMATS = [".txt", ".json", ".mcmeta", ".fsh", ".vsh", ".glsl"]
FIXES = {
    "no_ai_horse_movement": True,
    "clean_clone": True,
    "broken_score_references": True,
    "setblock_illegal_block": True,
    "stats": True,
    "old_adventure_mode_items": True,
    "safe_nbt_interpret": True,
    "stats_options": {
        "block_stats_used": True,
        "block_positions_dynamic": False,
        "commands_written_to_sensitive_position": False,
        "commands_written_to_arbitrary_position": False,
        "entity_stats_used": False,
        "entity_types_dynamic": False,
        "complex_stat_usage": False
    }
}
BREAKPOINT_MODE = "spreadplayers"

DATA_VERSIONS = {
    169: 900,
    175: 901,
    176: 902,
    183: 903,
    184: 904,
    510: 1000,
    511: 1001,
    512: 1002,
    819: 1100,
    921: 1101,
    922: 1102,
    1139: 1200,
    1241: 1201,
    1343: 1202,
    1519: 1300,
    1628: 1301,
    1631: 1302,
    1952: 1400,
    1957: 1401,
    1963: 1402,
    1968: 1403,
    1976: 1404,
    2225: 1500,
    2227: 1501,
    2230: 1502,
    2566: 1600,
    2567: 1601,
    2578: 1602,
    2580: 1603,
    2584: 1604,
    2586: 1605,
    2724: 1700,
    2730: 1701,
    2860: 1800,
    2865: 1801,
    2975: 1802,
    3105: 1900,
    3117: 1901,
    3120: 1902,
    3218: 1903,
    3337: 1904,
    3463: 2000,
    3465: 2001,
    3578: 2002,
    3698: 2003,
    3700: 2004,
    3837: 2005,
    1000000000: 2006,
}