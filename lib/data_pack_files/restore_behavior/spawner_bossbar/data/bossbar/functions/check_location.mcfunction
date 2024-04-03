# Check if spawner would produce a bossbar

scoreboard players set #bossbar_boolean bossbar.value 0
execute if block ~ ~ ~ minecraft:spawner{SpawnData:{entity:{id:"minecraft:wither"}}} run scoreboard players set #bossbar_boolean bossbar.value 1
execute if block ~ ~ ~ minecraft:spawner{SpawnData:{entity:{id:"minecraft:ender_dragon"}}} run scoreboard players set #bossbar_boolean bossbar.value 1







# Target wither

execute store result score #local bossbar.uuid_0 run data get storage bossbar:data spawner.UUID[0]
execute store result score #local bossbar.uuid_1 run data get storage bossbar:data spawner.UUID[1]
execute store result score #local bossbar.uuid_2 run data get storage bossbar:data spawner.UUID[2]
execute store result score #local bossbar.uuid_3 run data get storage bossbar:data spawner.UUID[3]

execute as @e[type=minecraft:wither,tag=bossbar.bossbar] if score @s bossbar.uuid_0 = #local bossbar.uuid_0 if score @s bossbar.uuid_1 = #local bossbar.uuid_1 if score @s bossbar.uuid_2 = #local bossbar.uuid_2 if score @s bossbar.uuid_3 = #local bossbar.uuid_3 run tag @s add bossbar.target

execute if score #bossbar_boolean bossbar.value matches 0 as @e[type=minecraft:wither,tag=bossbar.bossbar,tag=bossbar.target] run function bossbar:terminate
execute if score #bossbar_boolean bossbar.value matches 1 run teleport @e[type=minecraft:wither,tag=bossbar.bossbar,tag=bossbar.target] @s
execute if score #bossbar_boolean bossbar.value matches 1 unless entity @e[type=minecraft:wither,tag=bossbar.bossbar,tag=bossbar.target] summon minecraft:wither run function bossbar:spawn
execute if score #bossbar_boolean bossbar.value matches 1 if data block ~ ~ ~ SpawnData.entity.CustomName run data modify entity @e[type=minecraft:wither,tag=bossbar.bossbar,tag=bossbar.target,limit=1] CustomName set from block ~ ~ ~ SpawnData.entity.CustomName
execute if score #bossbar_boolean bossbar.value matches 1 unless data block ~ ~ ~ SpawnData.entity.CustomName run data remove entity @e[type=minecraft:wither,tag=bossbar.bossbar,tag=bossbar.target,limit=1] CustomName

tag @e[type=minecraft:wither,tag=bossbar.bossbar] remove bossbar.target