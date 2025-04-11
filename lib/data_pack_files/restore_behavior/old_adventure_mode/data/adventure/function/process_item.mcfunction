# Add tag

tag @s add adventure.processed







# Modify item

tag @s add adventure.target
execute positioned ~ ~1000 ~ summon minecraft:armor_stand run function adventure:entity_process_item
tag @s remove adventure.target