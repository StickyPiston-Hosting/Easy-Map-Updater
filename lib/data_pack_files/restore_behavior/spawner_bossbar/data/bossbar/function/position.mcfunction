# Move to position

data modify storage bossbar:data tag.Pos set value [0.0d,0.0d,0.0d]
execute store result storage bossbar:data tag.Pos[0] double 1 run data get storage bossbar:data spawner.x
execute store result storage bossbar:data tag.Pos[1] double 1 run data get storage bossbar:data spawner.y
execute store result storage bossbar:data tag.Pos[2] double 1 run data get storage bossbar:data spawner.z
data modify entity @s Pos set from storage bossbar:data tag.Pos







# Check position if chunk is loaded

scoreboard players set #bossbar_boolean bossbar.value 1
execute at @s if loaded ~ ~ ~ run function bossbar:check_location







# Terminate

kill @s