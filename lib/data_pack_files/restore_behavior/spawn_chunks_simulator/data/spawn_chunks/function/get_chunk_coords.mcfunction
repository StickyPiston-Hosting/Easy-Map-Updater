# This function is run as a marker spawned with /execute summon minecraft:marker
data modify storage spawn_chunks:data tag set from entity @s {}
execute store result score #x spawn_chunks.value run data get storage spawn_chunks:data tag.Pos[0]
execute store result score #z spawn_chunks.value run data get storage spawn_chunks:data tag.Pos[2]
scoreboard players operation #x spawn_chunks.value /= #16 spawn_chunks.value
scoreboard players operation #z spawn_chunks.value /= #16 spawn_chunks.value
execute in minecraft:overworld store result score #in_overworld spawn_chunks.value if entity @s[distance=0..]
kill @s