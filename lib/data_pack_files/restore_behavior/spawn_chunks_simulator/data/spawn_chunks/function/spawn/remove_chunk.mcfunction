# Unforceload chunk if it's not marked for forceloading otherwise
function spawn_chunks:forceload/test_chunk with storage spawn_chunks:data macro
execute if score #is_forceloaded spawn_chunks.value matches 0 run forceload remove ~ ~ ~ ~