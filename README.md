# Easy Map Updater

The Easy Map Updater (E.M.U.) is a toolset implemented in Python for automatically updating Minecraft maps for Java Edition to the latest version. It will update data packs, resource packs, command blocks, and much more. 


## Requirements

E.M.U. requires Python 3.9 or newer.

The following modules are required:

```
pip install nbt
pip install requests
pip install pillow
```


## Getting started

Clone the repository into your Minecraft instance folder (e.g. `.minecraft/Easy-Map-Updater`).

The maps and resource packs that it updates will be in the `saves` and `resourcepacks` folders respectively. By default, the map that will be updated is `saves/world`, and the resource pack that will be updated is `resourcepacks/resources`. This can be changed in `options.json`, which is generated on startup. It is recommended that the resource pack starts inside the world as `resources.zip`.


## Updating your map

To update your map, run `easy_map_updater.py`, then type `update` and hit enter. A few prompts will come up at various stages when user input is needed. Once it is done, you should have the following files:

- `saves/world`: Your updated map.
- `saves/world_original`: Original copy of the map which is left unmodified.
- `saves/world_source`: Source copy of the map used as a reference.
- `saves/world_play`: Play copy of the map. Join this copy to playtest your map to make sure that the update was successful.
- `resourcepacks/resources`: Your updated resource pack. The resource pack will also be zipped and inserted into the world as `resources.zip`.
- `resourcepacks/resources_original`: Original copy of the resource pack used as a reference which is left unmodified.

After you have confirmed the map to be fully-functioning with the play copy, you can distribute the main copy. To clean up all the files when you're done, you can use the `clean` action.

If something went wrong in the update process, you may have to manually edit a file in your map, then you can run `update` again and resume where the update process stopped. Be sure to send us the error traceback so we can fix the issue!


## Running actions manually

For maps that are older or more complex, generally you want to go through the actions manually.

E.M.U. uses a series of command line-like actions which are used at various stages in the map updating process. Not all of them will show right away, but will slowly be shown as you go when they become relevant. This keeps the clutter down and helps you to keep track of what stage you're currently on.


### Administrative actions

Begin by running the `scan` action, which will scan your map to gather any information E.M.U. needs to proceed.

- `reset`: Resets the action list.
- `all`: Shows all actions.
- `update`: Updates your map automatically. It runs all systems in sequence, prompting you when information is needed.
- `scan`: Scans the map for any important information that E.M.U. needs to know, for instance if there is a resource pack inside, what version the map is on, whether there are legacy functions in the `data` folder, etc.


### Original world actions

Before updating, an original copy of your map is created which is not modified at any point during the update process.

- `world.original`: This will create the original copy of your world.
- `world.original.play`: This will create a play copy of your original world in the event that you need to test it.
- `world.reload`: This will overwrite the working copy of your world with the original copy.


### Pre-source world actions

Before you make the source copy of your world, certain actions need to be run to prepare it.

- `rp.import`: If your world contains `resources.zip`, this will extract it out into the `resourcepacks` folder so that it can be updated.
- `rp.original`: This will create the original copy of your resource pack. This is necessary to run before updating it because it is used as an unchanging reference when updating the resource pack.
- `rp.reload`: This will overwrite the working copy of your resource pack with the original copy.
- `rp.purge`: Scans through your resource pack and compares it against a specified local copy of the vanilla resource pack to purge all vanilla files. Many mapmakers leave several vanilla files in their resource packs, so this cuts down the bloat.
- `rp.update`: Updates the working copy of your resource pack to the latest version, using the original copy as a source.
- `rp.fix`: Fixes certain broken features of the resource pack in a very invasive way. Only recommended if needed.

- `dp.unzip`: If there are any zipped data packs in your world, this will unzip them so that they can be updated.
- `dp.log`: This will update the world's internal data pack list from the current set of data packs in the `datapacks` folder.
- `dp.vanilla`: If the vanilla data pack is disabled on your world (to remove advancements, block tags, etc.), this will re-enable it and filter out those things which are commonly removed. As of ~1.19, certain dimension data was stored in the vanilla data pack which prevented worlds from loading correctly if it was disabled.
- `dp.merge`: This will merge all the data packs together. Entirely optional.
- `dp.stored_function`: This will extract functions from `data/functions` and put them into their own data pack. Worlds from 1.12 had functions stored there.
- `dp.stored_advancement`: This will extract advancements from `data/advancements` and put them into their own data pack. Worlds from 1.12 had advancements stored there.
- `dp.advancement`: If a data pack disables vanilla advancements by making all of them impossible, this will remove vanilla advancement overrides and replace them with a data pack that filters out advancements.
- `dp.recipe`: If a data pack disables vanilla recipes by making all of them impossible, this will remove vanilla recipe overrides and replace them with a data pack that filters out recipes.


### Pre-optimization actions

After the above actions are sorted, certain actions need to be run to prepare your world for optimization.

- `world.source`: This will create the source copy of your world. This is necessary to run before updating your data packs because it is used as reference.

- `dp.update`: Updates all of the data packs in the working copy of your world to the latest version, using the source copy as a reference. This may create a data pack called `command_helper` which contains functions that replace certain complex commands which require multiple commands to replicate.


### World optimization

E.M.U. is not equipped to update the region files or `level.dat` directly, though it has tools to assist that. Before proceeding, boot up the latest version of Minecraft and optimize the working copy of your world. World optimization does a shallow update of the regions and dat files, but does not update any commands. The process is also quite buggy when optimizing older maps, which E.M.U. has fixes for. After your world is optimized, run `optimize` to proceed.


### World-fixing actions

Certain aspects of your world will remain broken, even after optimization. The following actions will help to fix those issues.

- `entity.extract`: For worlds older than 1.17, entities are stored in the main region files where blocks are stored. 1.17 changed this by splitting them into entity region files. World optimization does not extract entities into their own regions, so run this to extract them.
- `stats.scan`: For maps between 1.8 and 1.12.2, this will check if `/stats` was used and how it was used. `/stats` is notoriously difficult to update, but it is also seldom used in practice.
- `world.fix`: Fixes various miscellaneous problems with the world left behind by optimization, including but not limited to:
    - 1.8 entity equipment.
    - `CanPlaceOn`/`CanDestroy` tags on items.
    - Old mob spawner data.
    - Entities with duplicate UUIDs.
    - Broken absorption.
    - Old attribute values.
    - Old adventure mode behavior.
    - Corrupted `scoreboard.dat` entries.
    - Dead entities cluttering `scoreboard.dat`.


### Behavior-restoring data packs

Certain old features require entire data packs to be created to properly replicate.

- `dp.bossbar`: In 1.8, mob spawners with boss mobs would display a bossbar. This action adds a data pack to your world that scans your world for mob spawners spawning boss mobs to emulate the old behavior.
- `dp.aec_kill`: Area effect clouds were added in 1.9, so creepers with effects from old maps would unintentionally spawn area effect clouds when they explode. This action adds a data pack to your world that will kill all area effect clouds which aren't used for internal purposes.
- `dp.ore_fixer`: In 1.17, raw iron and raw gold were added, which changed the loot table of iron ore and gold ore. This action adds a data pack to your world that restores the old loot tables in the event that a map depended on the specific drops.
- `dp.water_leaves`: In 1.19, leaves became waterloggable. Certain old maps involve using water buckets on leaves, and broke in 1.19. This action adds a data pack to your world that prevents leaves from becoming waterloggable.
- `dp.adventure`: In 1.7, players in adventure mode could break certain blocks simply by having the correct tool in hand rather than requiring `CanDestroy`, and they could place any block without requiring `CanPlaceOn`. This action adds a data pack to your world that restores the old adventure mode behavior.
- `dp.effect`: In 1.20.5, effects with negative amplifiers were fixed, which were previously used for interesting behaviors. This action adds a data pack to your world that simulates the old effect behavior.
- `dp.tag`: With 1.13's "flattening," many block/item IDs were split up. Certain commands require accessing all of these blocks/items. This action adds a data pack to your world that adds block/item tags to restore the old behavior. The data pack and command block updater will automatically insert references to these tags in your commands.
- `dp.firework`: In 1.11.1, firework explosions damage entities. This action adds a data pack to your world that cancels all firework explosion damage.
- `illegal_chunk`: In 1.13, illegal block states became more difficult for commands like `/setblock` to generate as every block modification triggered a block update. `/clone` is able to copy a block with an illegal state without it reverting back. This action will insert a chunk far away in your world full of blocks with illegal block states that will be cloned from. The data pack and command block updater will automatically replace the block references to reference this special chunk.


### Command block actions

- `cmd.read`: Reads all the command block, command block minecart, and sign data in your world and puts the data into `commands.mcfunction` and `commands_original.mcfunction`. This is where the command block data is updated from. They are put into text files first to allow manual edits to the data.
- `cmd.update`: Updates the commands in `commands.mcfunction` using `commands_original.mcfunction` as a reference. This may create a data pack called `command_helper` which contains functions that replace certain complex commands which require multiple commands to replicate.
- `cmd.write`: Writes the contents of `commands.mcfunction` back into your world.
- `cmd.clear`: Deletes the `command_helper` data pack in case changes were made to the source commands.
- `cmd.extract`: Extracts commands from a specified command block chain in your world and writes them into `command_chain.mcfunction`.


### World finalization actions

When playing a map, various data is generated such as player data, stats, advancement records, etc. It is generally desired to not have this data in your world when publishing it online. These actions will clean up your world to make it more presentable for publishing.

- `final.score`: Scans through `scoreboard.dat` and extracts all potential player names registered to scores or teams. These names are written into `player_names.json` for manual review. Because fakeplayer scores can easily resemble actual player names, they are held for manual review before deletion. Go through the list and remove anything which is not an actual player name.
- `final`: Finalizes your world by removing all clutter data and files including but not limited to:
    - Player data (both singleplayer and multiplayer).
    - Server-generated data packs (e.g. bukkit).
    - 0KB region and poi files (helps for uploading to Realms).
    - `level.dat_old`
    - Advancement records.
    - Stat records.
    - Player scores and team registrations from `scoreboard.dat`.


### Playtesting actions

- `world.play`: Normally, you do not want to test your map on the working copy. This action will make a duplicate of the working copy of your world for playtesting purposes.


### Admin controls

Certain maps, especially minigames, do better off by having admin controls. These allow operators to have full control over the lobby, settings, and when the game starts, and it prevents regular players from controlling these things.

- `admin.kickback`: Adds a template data pack which will kickback non-admin players from defined locations as long as an admin is online. An admin is a player with the `admin` tag. The locations are defined in `data/admin_kickpack/functions/tick.mcfunction`. This is useful to prevent players from entering certain locations or pressing buttons.


### Exportation actions

After the map has been updated and finalized, these actions will help package it up.

- `dp.zip`: Zips all of the data packs to reduce file count and size.
- `rp.export`: Zips the working copy of your resource pack and puts it into your world as `resources.zip`.
- `rp.export_original`: Zips the original copy of your resource pack and puts it into your source world as `resources.zip`.
- `clean`: Deletes the working copies of your world and resource pack, and all the generated duplicates of them.


### Miscellaneous actions

- `version`: Opens a prompt to edit the source version to update from.
- `license`: Shows the software license snippet.
- `exit`: Exits the program.


### Debug actions

- `debug.cmd`: Updates a single command in the prompt for testing purposes.
- `debug.json`: Updates a JSON text component in the prompt for testing purposes.
- `debug`: Toggles debug mode for printing extra data during the update process.


## Contact and contribution

The Easy Map Updater is a work in progress and is missing a lot of features. Post an issue on this repo or contact us on Discord: https://discord.gg/nrqhv6PcqQ
