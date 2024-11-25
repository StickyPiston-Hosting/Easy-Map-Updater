# Add tag

tag @s add adventure.processed







# Modify item

summon minecraft:armor_stand ~ 1000 ~ {Tags:["adventure.armor_stand"],Invisible:1b,NoGravity:1b,ArmorItems:[{},{},{},{}]}

execute positioned ~ 1000 ~ run data modify entity @e[type=minecraft:armor_stand,distance=..1,tag=adventure.armor_stand,limit=1] ArmorItems[3] set from entity @s Item
execute positioned ~ 1000 ~ as @e[type=minecraft:armor_stand,distance=..1,tag=adventure.armor_stand,limit=1] run function adventure:modify_item
execute if score #modified_boolean adventure.value matches 1 positioned ~ 1000 ~ run data modify entity @s Item set from entity @e[type=minecraft:armor_stand,distance=..1,tag=adventure.armor_stand,limit=1] ArmorItems[3]

execute positioned ~ 1000 ~ run kill @e[type=minecraft:armor_stand,distance=..1,tag=adventure.armor_stand,limit=1]