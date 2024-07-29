# Start raycast

scoreboard players set @s leaves.use_bucket 0
scoreboard players set #iterations leaves.value 300
execute at @s anchored eyes positioned ^ ^ ^ run function leaves:raycast