# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Set default variables

PACK_VERSION = 2004
DATA_PACK_FORMAT = 26
RESOURCE_PACK_FORMAT = 22
DATA_VERSION = 3700
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