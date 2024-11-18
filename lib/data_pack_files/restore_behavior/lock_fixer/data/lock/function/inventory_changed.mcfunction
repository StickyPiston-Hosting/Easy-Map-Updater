# Revoke advancement

advancement revoke @s only lock:inventory_changed







# Apply item modifiers to every hotbar item and offhand

summon minecraft:armor_stand ~ 1000 ~ {Tags:["lock.armor_stand"],Invisible:1b,NoGravity:1b}

execute positioned ~ 1000 ~ run item replace entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head from entity @s hotbar.0
execute positioned ~ 1000 ~ as @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] run function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ 1000 ~ run item replace entity @s hotbar.0 from entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head

execute positioned ~ 1000 ~ run item replace entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head from entity @s hotbar.1
execute positioned ~ 1000 ~ as @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] run function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ 1000 ~ run item replace entity @s hotbar.1 from entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head

execute positioned ~ 1000 ~ run item replace entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head from entity @s hotbar.2
execute positioned ~ 1000 ~ as @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] run function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ 1000 ~ run item replace entity @s hotbar.2 from entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head

execute positioned ~ 1000 ~ run item replace entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head from entity @s hotbar.3
execute positioned ~ 1000 ~ as @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] run function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ 1000 ~ run item replace entity @s hotbar.3 from entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head

execute positioned ~ 1000 ~ run item replace entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head from entity @s hotbar.4
execute positioned ~ 1000 ~ as @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] run function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ 1000 ~ run item replace entity @s hotbar.4 from entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head

execute positioned ~ 1000 ~ run item replace entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head from entity @s hotbar.5
execute positioned ~ 1000 ~ as @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] run function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ 1000 ~ run item replace entity @s hotbar.5 from entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head

execute positioned ~ 1000 ~ run item replace entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head from entity @s hotbar.6
execute positioned ~ 1000 ~ as @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] run function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ 1000 ~ run item replace entity @s hotbar.6 from entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head

execute positioned ~ 1000 ~ run item replace entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head from entity @s hotbar.7
execute positioned ~ 1000 ~ as @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] run function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ 1000 ~ run item replace entity @s hotbar.7 from entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head

execute positioned ~ 1000 ~ run item replace entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head from entity @s hotbar.8
execute positioned ~ 1000 ~ as @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] run function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ 1000 ~ run item replace entity @s hotbar.8 from entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head

execute positioned ~ 1000 ~ run item replace entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head from entity @s weapon.offhand
execute positioned ~ 1000 ~ as @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] run function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ 1000 ~ run item replace entity @s weapon.offhand from entity @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1] armor.head



execute positioned ~ 1000 ~ run kill @e[type=minecraft:armor_stand,tag=lock.armor_stand,distance=..1,limit=1]