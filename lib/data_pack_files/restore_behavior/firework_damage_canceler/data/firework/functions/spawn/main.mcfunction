# Get UUID

execute unless score @s firework.uuid_0 = @s firework.uuid_0 run function firework:spawn/uuid
function firework:spawn/owner







# Prepare recursive spawning

scoreboard players operation #entity_count firework.value = #wait_time firework.value
scoreboard players add #entity_count firework.value 1
function firework:spawn/loop