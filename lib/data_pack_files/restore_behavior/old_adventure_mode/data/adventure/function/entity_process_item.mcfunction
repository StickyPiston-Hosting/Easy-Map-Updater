# Modify item

execute positioned ~ ~-1000 ~ run data modify entity @s equipment.head set from entity @e[type=minecraft:item,distance=..1,tag=adventure.target,limit=1] Item
function adventure:modify_item
execute if score #modified_boolean adventure.value matches 1 positioned ~ ~-1000 ~ run data modify entity @e[type=minecraft:item,distance=..1,tag=adventure.target,limit=1] Item set from entity @s equipment.head

kill @s