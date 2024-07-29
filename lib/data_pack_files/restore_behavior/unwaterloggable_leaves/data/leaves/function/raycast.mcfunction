# Place water block

execute if block ^ ^ ^0.02 #minecraft:leaves[waterlogged=true] if block ~ ~ ~ #leaves:passable run setblock ~ ~ ~ minecraft:water
execute positioned ^ ^ ^0.02 if block ~ ~ ~ #minecraft:leaves[waterlogged=true] run function leaves:unwaterlog_leaves







# Run recursively

scoreboard players remove #iterations leaves.value 1
execute if score #iterations leaves.value matches 1.. positioned ^ ^ ^0.02 unless block ~ ~ ~ #minecraft:leaves run function leaves:raycast