# Prepare macro to test if given coordinates are in the list
data modify storage spawn_chunks:data macro set value {x:0,z:0}
execute store result storage spawn_chunks:data macro.x int 1 run scoreboard players get #x spawn_chunks.value
execute store result storage spawn_chunks:data macro.z int 1 run scoreboard players get #z spawn_chunks.value
function spawn_chunks:forceload/test_chunk with storage spawn_chunks:data macro