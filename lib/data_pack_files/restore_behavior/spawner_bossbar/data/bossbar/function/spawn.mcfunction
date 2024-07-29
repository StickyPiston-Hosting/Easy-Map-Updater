# Assign tags and data

tag @s add bossbar.bossbar
tag @s add bossbar.target

data merge entity @s {Invulnerable:1b,NoAI:1b,Silent:1b,DeathLootTable:"",CustomNameVisible:0b}







# Assign UUID to spawner register

data modify storage bossbar:data spawner.UUID set from entity @s UUID
execute store result score @s bossbar.uuid_0 run data get storage bossbar:data spawner.UUID[0]
execute store result score @s bossbar.uuid_1 run data get storage bossbar:data spawner.UUID[1]
execute store result score @s bossbar.uuid_2 run data get storage bossbar:data spawner.UUID[2]
execute store result score @s bossbar.uuid_3 run data get storage bossbar:data spawner.UUID[3]