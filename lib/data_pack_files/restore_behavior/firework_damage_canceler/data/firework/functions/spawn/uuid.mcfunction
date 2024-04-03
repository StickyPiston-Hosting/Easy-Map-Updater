# Get UUID of player

data modify storage firework:data tag.UUID set from entity @s UUID
execute store result score @s firework.uuid_0 run data get storage firework:data tag.UUID[0]
execute store result score @s firework.uuid_1 run data get storage firework:data tag.UUID[1]
execute store result score @s firework.uuid_2 run data get storage firework:data tag.UUID[2]
execute store result score @s firework.uuid_3 run data get storage firework:data tag.UUID[3]