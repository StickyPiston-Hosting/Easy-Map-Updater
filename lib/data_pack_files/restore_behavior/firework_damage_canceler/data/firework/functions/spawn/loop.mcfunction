# Spawn entities

summon area_effect_cloud ~ ~ ~ {Tags:["firework.target","easy_map_updater.no_kill"],WaitTime:0,Duration:1,Age:-1,Radius:0.0f,ReapplicationDelay:-1,effects:[{id:"minecraft:instant_damage",amplifier:0b,duration:1}]}
execute as @e[type=area_effect_cloud,tag=firework.target,distance=..1,limit=1] run function firework:spawn/entity







# Run function recursively

scoreboard players remove #entity_count firework.value 1
execute if score #entity_count firework.value matches 1.. run function firework:spawn/loop