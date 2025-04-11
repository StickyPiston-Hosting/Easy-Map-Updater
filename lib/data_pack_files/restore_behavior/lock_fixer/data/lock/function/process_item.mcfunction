# Add tag

tag @s add lock.processed







# Modify item

tag @s add lock.target
execute positioned ~ ~1000 ~ summon minecraft:item_display run function lock:entity_process_item
tag @s remove lock.target