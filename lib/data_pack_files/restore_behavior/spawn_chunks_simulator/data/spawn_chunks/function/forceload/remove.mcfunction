# Prepare iterator
scoreboard players set #action spawn_chunks.value 0
scoreboard players operation #x spawn_chunks.value = #start_x spawn_chunks.value
function spawn_chunks:iter/x

# Refresh spawn chunks
schedule function spawn_chunks:spawn/refresh 1t replace