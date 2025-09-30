# Perform action
data modify storage spawn_chunks:data macro set value {x:0,z:0}
execute store result storage spawn_chunks:data macro.x int 1 run scoreboard players get #x spawn_chunks.value
execute store result storage spawn_chunks:data macro.z int 1 run scoreboard players get #z spawn_chunks.value
execute if score #action spawn_chunks.value matches 0 run function spawn_chunks:forceload/remove_chunk with storage spawn_chunks:data macro
execute if score #action spawn_chunks.value matches 1 run function spawn_chunks:forceload/add_chunk with storage spawn_chunks:data macro
execute if score #action spawn_chunks.value matches 2 run function spawn_chunks:spawn/remove_chunk
execute if score #action spawn_chunks.value matches 3 run function spawn_chunks:spawn/add_chunk

# Iterate over the z coordinates
scoreboard players add #z spawn_chunks.value 1
execute if score #z spawn_chunks.value <= #end_z spawn_chunks.value positioned ~ ~ ~16 run function spawn_chunks:iter/z