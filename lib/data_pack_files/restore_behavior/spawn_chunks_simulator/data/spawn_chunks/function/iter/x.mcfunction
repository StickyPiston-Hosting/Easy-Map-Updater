# Run z branch
scoreboard players operation #z spawn_chunks.value = #start_z spawn_chunks.value
function spawn_chunks:iter/z

# Iterate over the x coordinates
scoreboard players add #x spawn_chunks.value 1
execute if score #x spawn_chunks.value <= #end_x spawn_chunks.value positioned ~16 ~ ~ run function spawn_chunks:iter/x