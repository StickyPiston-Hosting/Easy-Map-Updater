# Revoke advancement

advancement revoke @s only lock:inventory_changed







# Apply item modifiers to every hotbar item and offhand

tag @s add lock.target
execute positioned ~ ~1000 ~ summon minecraft:item_display run function lock:entity_inventory_changed
tag @s remove lock.target