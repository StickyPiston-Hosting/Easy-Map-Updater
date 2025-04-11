# Modify item

execute positioned ~ ~-1000 ~ run data modify entity @s item set from entity @e[type=minecraft:item,distance=..1,tag=lock.target,limit=1] Item
function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ ~-1000 ~ run data modify entity @e[type=minecraft:item,distance=..1,tag=lock.target,limit=1] Item set from entity @s item

kill @s