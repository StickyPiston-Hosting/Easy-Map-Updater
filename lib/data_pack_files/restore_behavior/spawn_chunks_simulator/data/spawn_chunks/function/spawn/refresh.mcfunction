# Refresh forceloaded chunks in case some of them were removed
execute store result score #new_spawn_x spawn_chunks.value run data get storage spawn_chunks:data spawn.x
execute store result score #new_spawn_z spawn_chunks.value run data get storage spawn_chunks:data spawn.z
execute store result score #new_radius spawn_chunks.value run data get storage spawn_chunks:data spawn.radius

scoreboard players operation #start_x spawn_chunks.value = #new_spawn_x spawn_chunks.value
scoreboard players operation #start_z spawn_chunks.value = #new_spawn_z spawn_chunks.value
scoreboard players operation #end_x spawn_chunks.value = #new_spawn_x spawn_chunks.value
scoreboard players operation #end_z spawn_chunks.value = #new_spawn_z spawn_chunks.value
scoreboard players operation #start_x spawn_chunks.value -= #new_radius spawn_chunks.value
scoreboard players operation #start_z spawn_chunks.value -= #new_radius spawn_chunks.value
scoreboard players operation #end_x spawn_chunks.value += #new_radius spawn_chunks.value
scoreboard players operation #end_z spawn_chunks.value += #new_radius spawn_chunks.value
scoreboard players add #start_x spawn_chunks.value 1
scoreboard players add #start_z spawn_chunks.value 1
scoreboard players remove #end_x spawn_chunks.value 1
scoreboard players remove #end_z spawn_chunks.value 1

scoreboard players set #action spawn_chunks.value 3
data modify storage spawn_chunks:data macro set value {x:0,z:0}
scoreboard players operation #init_x spawn_chunks.value = #start_x spawn_chunks.value
scoreboard players operation #init_z spawn_chunks.value = #start_z spawn_chunks.value
scoreboard players operation #init_x spawn_chunks.value *= #16 spawn_chunks.value
scoreboard players operation #init_z spawn_chunks.value *= #16 spawn_chunks.value
execute store result storage spawn_chunks:data macro.x int 1 run scoreboard players get #init_x spawn_chunks.value
execute store result storage spawn_chunks:data macro.z int 1 run scoreboard players get #init_z spawn_chunks.value
scoreboard players operation #x spawn_chunks.value = #start_x spawn_chunks.value
execute if score #new_radius spawn_chunks.value matches 1.. run function spawn_chunks:iter/init with storage spawn_chunks:data macro