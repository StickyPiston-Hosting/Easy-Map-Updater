# Set random Y coordinate

scoreboard players set #input firework.value 100000
function firework:rng
scoreboard players add #output firework.value 10000







# Prepare NBT

data modify storage firework:data tag.Pos set from entity @s Pos
execute store result storage firework:data tag.Pos[1] double 1 run scoreboard players get #output firework.value
execute store result storage firework:data tag.Age int -1 run scoreboard players get #entity_count firework.value
data modify entity @s {} merge from storage firework:data tag







# Remove tag

tag @s remove firework.target







# Spawn bat

execute at @s run summon minecraft:bat ~ ~ ~ {Tags:["firework.target"],DeathLootTable:"",NoAI:1b,Silent:1b,Health:1.0f,PersistenceRequired:1b}