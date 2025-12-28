# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from typing import cast
from lib.log import log
from lib.data_pack_files import nbt_tags
from lib.data_pack_files import miscellaneous
from lib.data_pack_files import items
from lib.data_pack_files import blocks
from lib.data_pack_files import entities
from lib.data_pack_files import tables
from lib.data_pack_files import item_component
from lib.data_pack_files.restore_behavior import scoreboard_objective_splitter
from lib import defaults
from lib import option_manager



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def biome(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    global pack_version
    pack_version = version

    name = miscellaneous.namespace(name)

    # Update biome names for 1.13
    if version <= 1202:
        id_array = {
            "minecraft:beaches": "minecraft:beach",
            "minecraft:cold_beach": "minecraft:snowy_beach",
            "minecraft:extreme_hills_with_trees": "minecraft:wooded_mountains",
            "minecraft:extreme_hills": "minecraft:mountains",
            "minecraft:forest_hills": "minecraft:wooded_hills",
            "minecraft:hell": "minecraft:nether",
            "minecraft:ice_flats": "minecraft:snowy_tundra",
            "minecraft:ice_mountains": "minecraft:snowy_mountains",
            "minecraft:mesa_clear_rock": "minecraft:badlands_plateau",
            "minecraft:mesa_rock": "minecraft:wooded_badlands_plateau",
            "minecraft:mesa": "minecraft:badlands",
            "minecraft:mushroom_island_shore": "minecraft:mushroom_field_shore",
            "minecraft:mushroom_island": "minecraft:mushroom_fields",
            "minecraft:mutated_birch_forest_hills": "minecraft:tall_birch_hills",
            "minecraft:mutated_birch_forest": "minecraft:tall_birch_forest",
            "minecraft:mutated_desert": "minecraft:desert_lakes",
            "minecraft:mutated_extreme_hills_with_trees": "minecraft:modified_gravelly_mountains",
            "minecraft:mutated_extreme_hills": "minecraft:gravelly_mountains",
            "minecraft:mutated_forest": "minecraft:flower_forest",
            "minecraft:mutated_ice_flats": "minecraft:ice_spikes",
            "minecraft:mutated_jungle_edge": "minecraft:modified_jungle_edge",
            "minecraft:mutated_jungle": "minecraft:modified_jungle",
            "minecraft:mutated_mesa_clear_rock": "minecraft:modified_badlands_plateau",
            "minecraft:mutated_mesa_rock": "minecraft:modified_wooded_badlands_plateau",
            "minecraft:mutated_mesa": "minecraft:eroded_badlands",
            "minecraft:mutated_plains": "minecraft:sunflower_plains",
            "minecraft:mutated_redwood_taiga_hills": "minecraft:giant_spruce_taiga_hills",
            "minecraft:mutated_redwood_taiga": "minecraft:giant_spruce_taiga",
            "minecraft:mutated_roofed_forest": "minecraft:dark_forest_hills",
            "minecraft:mutated_savanna_rock": "minecraft:shattered_savanna_plateau",
            "minecraft:mutated_savanna": "minecraft:shattered_savanna",
            "minecraft:mutated_swampland": "minecraft:swamp_hills",
            "minecraft:mutated_taiga_cold": "minecraft:snowy_taiga_mountains",
            "minecraft:mutated_taiga": "minecraft:taiga_mountains",
            "minecraft:redwood_taiga_hills": "minecraft:giant_tree_taiga_hills",
            "minecraft:redwood_taiga": "minecraft:giant_tree_taiga",
            "minecraft:roofed_forest": "minecraft:dark_forest",
            "minecraft:savanna_rock": "minecraft:savanna_plateau",
            "minecraft:sky": "minecraft:the_end",
            "minecraft:smaller_extreme_hills": "minecraft:mountain_edge",
            "minecraft:stone_beach": "minecraft:stone_shore",
            "minecraft:swampland": "minecraft:swamp",
            "minecraft:taiga_cold_hills": "minecraft:snowy_taiga_hills",
            "minecraft:taiga_cold": "minecraft:snowy_taiga",
            "minecraft:void": "minecraft:the_void",
        }
        if name in id_array:
            name = id_array[name]

    # Update biome names for 1.16
    id_array = {
        "minecraft:nether": "minecraft:nether_wastes",
    }
    if name in id_array:
        name = id_array[name]

    # Update biome names for 1.18
    id_array = {
        "minecraft:giant_spruce_taiga": "minecraft:old_growth_spruce_taiga",
        "minecraft:giant_tree_taiga": "minecraft:old_growth_pine_taiga",
        "minecraft:gravelly_mountains": "minecraft:windswept_gravelly_hills",
        "minecraft:jungle_edge": "minecraft:sparse_jungle",
        "minecraft:mountains": "minecraft:windswept_hills",
        "minecraft:shattered_savanna": "minecraft:windswept_savanna",
        "minecraft:snowy_tundra": "minecraft:snowy_plains",
        "minecraft:stone_shore": "minecraft:stony_shore",
        "minecraft:tall_birch_forest": "minecraft:old_growth_birch_forest",
        "minecraft:wooded_badlands_plateau": "minecraft:wooded_badlands",
        "minecraft:wooded_mountains": "minecraft:windswept_forest",

        # The following biomes were removed, and so are being replaced with the nearest biome

        "minecraft:badlands_plateau": "minecraft:badlands",
        "minecraft:bamboo_jungle_hills": "minecraft:bamboo_jungle",
        "minecraft:birch_forest_hills": "minecraft:birch_forest",
        "minecraft:dark_forest_hills": "minecraft:dark_forest",
        "minecraft:deep_warm_ocean": "minecraft:warm_ocean",
        "minecraft:desert_hills": "minecraft:desert",
        "minecraft:desert_lakes": "minecraft:desert",
        "minecraft:giant_spruce_taiga_hills": "minecraft:old_growth_spruce_taiga",
        "minecraft:giant_tree_taiga_hills": "minecraft:old_growth_pine_taiga",
        "minecraft:modified_gravelly_mountains": "minecraft:windswept_gravelly_hills",
        "minecraft:jungle_hills": "minecraft:jungle",
        "minecraft:modified_badlands_plateau": "minecraft:badlands",
        "minecraft:modified_jungle": "minecraft:jungle",
        "minecraft:modified_jungle_edge": "minecraft:jungle",
        "minecraft:modified_wooded_badlands_plateau": "minecraft:wooded_badlands",
        "minecraft:mountain_edge": "minecraft:windswept_hills",
        "minecraft:mushroom_field_shore": "minecraft:mushroom_fields",
        "minecraft:shattered_savanna_plateau": "minecraft:windswept_savanna",
        "minecraft:snowy_mountains": "minecraft:snowy_plains",
        "minecraft:snowy_taiga_hills": "minecraft:snowy_taiga",
        "minecraft:snowy_taiga_mountains": "minecraft:snowy_taiga",
        "minecraft:swamp_hills": "minecraft:swamp",
        "minecraft:taiga_hills": "minecraft:taiga",
        "minecraft:taiga_mountains": "minecraft:taiga",
        "minecraft:tall_birch_hills": "minecraft:old_growth_birch_forest",
        "minecraft:wooded_hills": "minecraft:forest",
    }
    if name in id_array:
        name = id_array[name]

    return name

def effect(name: int | str | nbt_tags.TypeNumeric, version: int, issues: list[dict[str, str | int]]) -> str:
    global pack_version
    pack_version = version

    if isinstance(name, nbt_tags.TypeNumeric):
        name = int(name.value)

    if isinstance(name, str) and name.isnumeric():
        name = int(name)
        
    if isinstance(name, int):
        id_array = tables.EFFECT_IDS
        if name in id_array:
            name = id_array[name]
        else:
            name = "minecraft:speed"
    
    return miscellaneous.namespace(name)

def enchantment(name: str | int | nbt_tags.TypeNumeric, version: int, issues: list[dict[str, str | int]]) -> str:
    global pack_version
    pack_version = version

    # Convert if a numeric
    if isinstance(name, nbt_tags.TypeNumeric):
        name = int(name.value)

    # Convert if a number
    if isinstance(name, int):
        id_array = tables.ENCHANTMENT_IDS
        if name in id_array:
            name = id_array[name]
        else:
            name = "minecraft:protection"

    name = miscellaneous.namespace(name)

    # Update enchantment names for 1.20.5
    id_array = {
        "minecraft:sweeping": "minecraft:sweeping_edge"
    }
    if name in id_array:
        name = id_array[name]

    return name

def game_rule(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    global pack_version
    pack_version = version

    if pack_version <= 2110:
        id_array = {
            "allowEnteringNetherUsingPortals": "minecraft:allow_entering_nether_using_portals",
            "announceAdvancements": "minecraft:show_advancement_messages",
            "blockExplosionDropDecay": "minecraft:block_explosion_drop_decay",
            "command_modification_block_limit": "minecraft:max_block_modifications",
            "commandBlockOutput": "minecraft:command_block_output",
            "commandBlocksEnabled": "minecraft:command_blocks_work",
            "disableElytraMovementCheck": "minecraft:elytra_movement_check",
            "disablePlayerMovementCheck": "minecraft:player_movement_check",
            "disableRaids": "minecraft:raids",
            "doDaylightCycle": "minecraft:advance_time",
            "doEntityDrops": "minecraft:entity_drops",
            "doImmediateRespawn": "minecraft:immediate_respawn",
            "doInsomnia": "minecraft:spawn_phantoms",
            "doLimitedCrafting": "minecraft:limited_crafting",
            "doMobLoot": "minecraft:mob_drops",
            "doMobSpawning": "minecraft:spawn_mobs",
            "doPatrolSpawning": "minecraft:spawn_patrols",
            "doTileDrops": "minecraft:block_drops",
            "doTraderSpawning": "minecraft:spawn_wandering_traders",
            "doVinesSpread": "minecraft:spread_vines",
            "doWardenSpawning": "minecraft:spawn_wardens",
            "doWeatherCycle": "minecraft:advance_weather",
            "drowningDamage": "minecraft:drowning_damage",
            "enderPearlsVanishOnDeath": "minecraft:ender_pearls_vanish_on_death",
            "fallDamage": "minecraft:fall_damage",
            "fireDamage": "minecraft:fire_damage",
            "fireSpreadRadiusAroundPlayer": "minecraft:fire_spread_radius_around_player",
            "forgiveDeadPlayers": "minecraft:forgive_dead_players",
            "freezeDamage": "minecraft:freeze_damage",
            "globalSoundEvents": "minecraft:global_sound_events",
            "keepInventory": "minecraft:keep_inventory",
            "lavaSourceConversion": "minecraft:lava_source_conversion",
            "locatorBar": "minecraft:locator_bar",
            "logAdminCommands": "minecraft:log_admin_commands",
            "maxCommandChainLength": "minecraft:max_command_sequence_length",
            "maxCommandForkCount": "minecraft:max_command_forks",
            "maxEntityCramming": "minecraft:max_entity_cramming",
            "maxMinecartSpeed": "minecraft:max_minecart_speed",
            "mobExplosionDropDecay": "minecraft:mob_explosion_drop_decay",
            "mobGriefing": "minecraft:mob_griefing",
            "naturalRegeneration": "minecraft:natural_health_regeneration",
            "playersNetherPortalCreativeDelay": "minecraft:players_nether_portal_creative_delay",
            "playersNetherPortalDefaultDelay": "minecraft:players_nether_portal_default_delay",
            "playersSleepingPercentage": "minecraft:players_sleeping_percentage",
            "projectilesCanBreakBlocks": "minecraft:projectiles_can_break_blocks",
            "pvp": "minecraft:pvp",
            "randomTickSpeed": "minecraft:random_tick_speed",
            "reducedDebugInfo": "minecraft:reduced_debug_info",
            "sendCommandFeedback": "minecraft:send_command_feedback",
            "showDeathMessages": "minecraft:show_death_messages",
            "snowAccumulationHeight": "minecraft:max_snow_accumulation_height",
            "spawnerBlocksEnabled": "minecraft:spawner_blocks_work",
            "spawnMonsters": "minecraft:spawn_monsters",
            "spawnRadius": "minecraft:respawn_radius",
            "spectatorsGenerateChunks": "minecraft:spectators_generate_chunks",
            "tntExplodes": "minecraft:tnt_explodes",
            "tntExplosionDropDecay": "minecraft:tnt_explosion_drop_decay",
            "universalAnger": "minecraft:universal_anger",
            "waterSourceConversion": "minecraft:water_source_conversion",
        }
        if name in id_array:
            name = id_array[name]

    name = miscellaneous.namespace(name)
    return name

def poi(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    global pack_version
    pack_version = version

    name = miscellaneous.namespace(name)

    return name

def scoreboard_objective_criteria(objective: dict[str, str], version: int, issues: list[dict[str, str | int]]) -> str:
    global pack_version
    pack_version = version

    name = objective["name"]
    criteria = objective["criteria"]

    if pack_version <= 1202:
        if criteria.split(".")[0] == "stat":
            block_stats = {
                "mineBlock": "minecraft.mined:minecraft."
            }
            item_stats = {
                "breakItem": "minecraft.broken:minecraft.",
                "craftItem": "minecraft.crafted:minecraft.",
                "drop": "minecraft.dropped:minecraft.",
                "useItem": "minecraft.used:minecraft."
            }
            entity_stats = {
                "entityKilledBy": "minecraft.killed_by:minecraft.",
                "killEntity": "minecraft.killed:minecraft."
            }

            stat = criteria.split(".")[1]
            object_id = ":".join(criteria.split(".")[2:])

            if stat in block_stats:
                block_id = cast(str, blocks.update({"id": object_id, "data_value": -1, "block_states": {}, "nbt": {}, "read": True}, pack_version, issues)["id"])
                if block_id in tables.BLOCK_TAG_REPLACEMENTS:
                    scoreboard_objective_splitter.insert_objective(name, block_stats[stat], tables.BLOCK_TAG_REPLACEMENTS[block_id])
                    return "dummy"
                return block_stats[stat] + block_id[10:]
            
            elif stat in item_stats:
                item_id = cast(str, items.update({"id": object_id, "data_value": -1, "components": item_component.ItemComponents([]), "nbt": {}, "read": True}, pack_version, issues)["id"])
                if item_id in tables.ITEM_TAG_REPLACEMENTS:
                    scoreboard_objective_splitter.insert_objective(name, item_stats[stat], tables.ITEM_TAG_REPLACEMENTS[item_id])
                    return "dummy"
                return item_stats[stat] + item_id[10:]

            elif stat in entity_stats:
                return entity_stats[stat] + entities.update(object_id, pack_version, issues)[10:]
            
            else:
                id_array = tables.SCOREBOARD_STATISTIC_IDS
                if stat in id_array:
                    return "minecraft.custom:minecraft." + id_array[stat]

            

            if stat == "mineBlock":
                return "minecraft.mined:minecraft."     + blocks.update_from_command(object_id, pack_version, issues)[10:]
            elif stat == "breakItem":
                return "minecraft.broken:minecraft."    + items.update_from_command( object_id, pack_version, issues)[10:]
            elif stat == "craftItem":
                return "minecraft.crafted:minecraft."   + items.update_from_command( object_id, pack_version, issues)[10:]
            elif stat == "drop":
                return "minecraft.dropped:minecraft."   + items.update_from_command( object_id, pack_version, issues)[10:]
            elif stat == "useItem":
                return "minecraft.used:minecraft."      + items.update_from_command( object_id, pack_version, issues)[10:]
            elif stat == "entityKilledBy":
                return "minecraft.killed_by:minecraft." + entities.update(           object_id, pack_version, issues)[10:]
            elif stat == "killEntity":
                return "minecraft.killed:minecraft."    + entities.update(           object_id, pack_version, issues)[10:]
            else:
                id_array = tables.SCOREBOARD_STATISTIC_IDS
                if stat in id_array:
                    return "minecraft.custom:minecraft." + id_array[stat]
        else:
            return criteria

    return criteria

def sound_event(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    global pack_version
    pack_version = version

    # Apply namespace
    name = miscellaneous.namespace(name)

    # Convert ID based on version
    if pack_version <= 809:
        id_array = tables.SOUND_EVENTS_1_8
        if name in id_array:
            name = id_array[name]
    if pack_version <= 1202:
        id_array = tables.SOUND_EVENTS_1_12
        if name in id_array:
            name = id_array[name]

    # Wolf howl was removed in 1.21.5
    if name == "minecraft:entity.wolf.howl":
        log('WARNING: Sound event "minecraft:entity.wolf.howl" was removed!')

    post_fixes = option_manager.FIXES["post_fixes"]

    if pack_version <= 2105 or post_fixes:
        id_array = {
            "minecraft:block.sand.wind": "minecraft:block.dry_grass.ambient"
        }
        if name in id_array:
            name = id_array[name]

    return name

def structure(name: str, version: int, issues: list[dict[str, str | int]]) -> str:
    global pack_version
    pack_version = version

    name = miscellaneous.namespace(name)

    return name