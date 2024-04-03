# Check last entry

execute store result score #local bossbar.uuid_0 run data get storage bossbar:data spawner_list_copy[-1].UUID[0]
execute store result score #local bossbar.uuid_1 run data get storage bossbar:data spawner_list_copy[-1].UUID[1]
execute store result score #local bossbar.uuid_2 run data get storage bossbar:data spawner_list_copy[-1].UUID[2]
execute store result score #local bossbar.uuid_3 run data get storage bossbar:data spawner_list_copy[-1].UUID[3]

execute if score @s bossbar.uuid_0 = #local bossbar.uuid_0 if score @s bossbar.uuid_1 = #local bossbar.uuid_1 if score @s bossbar.uuid_2 = #local bossbar.uuid_2 if score @s bossbar.uuid_3 = #local bossbar.uuid_3 run scoreboard players set #spawner_found_boolean bossbar.value 1







# Execute function recursively

data remove storage bossbar:data spawner_list_copy[-1]
execute if score #spawner_found_boolean bossbar.value matches 0 if data storage bossbar:data spawner_list_copy[0] run function bossbar:recurse_list