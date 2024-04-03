# Add activated tag

tag @s add bossbar.activated







# Initialize variables for recursive search

data modify storage bossbar:data spawner_list_copy set from storage bossbar:data spawner_list
scoreboard players set #spawner_found_boolean bossbar.value 0
execute if data storage bossbar:data spawner_list_copy[0] run function bossbar:recurse_list







# If no spawner was found, terminate

execute if score #spawner_found_boolean bossbar.value matches 0 run function bossbar:terminate