# Check if coordinates are in the list
$execute store result score #is_forceloaded spawn_chunks.value if data storage spawn_chunks:data forceloaded_chunks[{x:$(x),z:$(z)}]