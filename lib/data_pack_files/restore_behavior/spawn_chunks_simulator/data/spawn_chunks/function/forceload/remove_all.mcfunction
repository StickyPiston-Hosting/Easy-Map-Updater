# Clear the forceloaded chunk list
data modify storage spawn_chunks:data forceloaded_chunks set value []

# Refresh spawn chunks
schedule function spawn_chunks:spawn/refresh 1t replace