# Revoke advancement

advancement revoke @s only adventure:inventory_changed







# Apply item modifiers to every hotbar item and offhand

tag @s add adventure.target
execute positioned ~ ~1000 ~ summon minecraft:armor_stand run function adventure:entity_inventory_changed
tag @s remove adventure.target