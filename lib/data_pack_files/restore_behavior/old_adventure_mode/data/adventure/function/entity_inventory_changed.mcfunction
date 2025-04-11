# Modify items from every slot

execute positioned ~ ~-1000 ~ run item replace entity @s armor.head from entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.0
function adventure:modify_item
execute if score #modified_boolean adventure.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.0 from entity @s armor.head

execute positioned ~ ~-1000 ~ run item replace entity @s armor.head from entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.1
function adventure:modify_item
execute if score #modified_boolean adventure.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.1 from entity @s armor.head

execute positioned ~ ~-1000 ~ run item replace entity @s armor.head from entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.2
function adventure:modify_item
execute if score #modified_boolean adventure.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.2 from entity @s armor.head

execute positioned ~ ~-1000 ~ run item replace entity @s armor.head from entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.3
function adventure:modify_item
execute if score #modified_boolean adventure.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.3 from entity @s armor.head

execute positioned ~ ~-1000 ~ run item replace entity @s armor.head from entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.4
function adventure:modify_item
execute if score #modified_boolean adventure.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.4 from entity @s armor.head

execute positioned ~ ~-1000 ~ run item replace entity @s armor.head from entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.5
function adventure:modify_item
execute if score #modified_boolean adventure.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.5 from entity @s armor.head

execute positioned ~ ~-1000 ~ run item replace entity @s armor.head from entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.6
function adventure:modify_item
execute if score #modified_boolean adventure.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.6 from entity @s armor.head

execute positioned ~ ~-1000 ~ run item replace entity @s armor.head from entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.7
function adventure:modify_item
execute if score #modified_boolean adventure.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.7 from entity @s armor.head

execute positioned ~ ~-1000 ~ run item replace entity @s armor.head from entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.8
function adventure:modify_item
execute if score #modified_boolean adventure.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=adventure.target,limit=1] hotbar.8 from entity @s armor.head

execute positioned ~ ~-1000 ~ run item replace entity @s armor.head from entity @a[distance=..1,tag=adventure.target,limit=1] weapon.offhand
function adventure:modify_item
execute if score #modified_boolean adventure.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=adventure.target,limit=1] weapon.offhand from entity @s armor.head



kill @s