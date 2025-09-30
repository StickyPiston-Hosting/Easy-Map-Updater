# Prepare iterator
scoreboard players set #action spawn_chunks.value 1
scoreboard players operation #x spawn_chunks.value = #start_x spawn_chunks.value
function spawn_chunks:iter/x