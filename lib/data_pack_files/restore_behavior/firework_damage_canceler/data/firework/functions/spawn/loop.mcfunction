# Spawn entities

summon minecraft:area_effect_cloud ~ ~ ~ {Tags:["firework.target","easy_map_updater.no_kill"],WaitTime:0,Duration:1,Age:-1,Radius:0.0f,ReapplicationDelay:-1,potion_contents:{custom_effects:[{id:"minecraft:instant_damage",duration:1}]}}
execute as @e[type=minecraft:area_effect_cloud,tag=firework.target,distance=..1,limit=1] run function firework:spawn/entity







# Run function recursively

scoreboard players remove #entity_count firework.value 1
execute if score #entity_count firework.value matches 1.. run function firework:spawn/loop