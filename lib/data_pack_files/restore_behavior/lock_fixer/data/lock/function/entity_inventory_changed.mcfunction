# Modify items from every slot

execute positioned ~ ~-1000 ~ run item replace entity @s contents from entity @a[distance=..1,tag=lock.target,limit=1] hotbar.0
function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=lock.target,limit=1] hotbar.0 from entity @s contents

execute positioned ~ ~-1000 ~ run item replace entity @s contents from entity @a[distance=..1,tag=lock.target,limit=1] hotbar.1
function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=lock.target,limit=1] hotbar.1 from entity @s contents

execute positioned ~ ~-1000 ~ run item replace entity @s contents from entity @a[distance=..1,tag=lock.target,limit=1] hotbar.2
function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=lock.target,limit=1] hotbar.2 from entity @s contents

execute positioned ~ ~-1000 ~ run item replace entity @s contents from entity @a[distance=..1,tag=lock.target,limit=1] hotbar.3
function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=lock.target,limit=1] hotbar.3 from entity @s contents

execute positioned ~ ~-1000 ~ run item replace entity @s contents from entity @a[distance=..1,tag=lock.target,limit=1] hotbar.4
function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=lock.target,limit=1] hotbar.4 from entity @s contents

execute positioned ~ ~-1000 ~ run item replace entity @s contents from entity @a[distance=..1,tag=lock.target,limit=1] hotbar.5
function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=lock.target,limit=1] hotbar.5 from entity @s contents

execute positioned ~ ~-1000 ~ run item replace entity @s contents from entity @a[distance=..1,tag=lock.target,limit=1] hotbar.6
function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=lock.target,limit=1] hotbar.6 from entity @s contents

execute positioned ~ ~-1000 ~ run item replace entity @s contents from entity @a[distance=..1,tag=lock.target,limit=1] hotbar.7
function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=lock.target,limit=1] hotbar.7 from entity @s contents

execute positioned ~ ~-1000 ~ run item replace entity @s contents from entity @a[distance=..1,tag=lock.target,limit=1] hotbar.8
function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=lock.target,limit=1] hotbar.8 from entity @s contents

execute positioned ~ ~-1000 ~ run item replace entity @s contents from entity @a[distance=..1,tag=lock.target,limit=1] weapon.offhand
function lock:modify_item
execute if score #modified_boolean lock.value matches 1 positioned ~ ~-1000 ~ run item replace entity @a[distance=..1,tag=lock.target,limit=1] weapon.offhand from entity @s contents



kill @s