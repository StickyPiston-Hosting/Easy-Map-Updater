# Get current spawner

data modify storage bossbar:data spawner set from storage bossbar:data spawner_list[0]







# Execute at that position

execute if data storage bossbar:data {spawner:{Dimension:"minecraft:overworld"}} in minecraft:overworld summon minecraft:marker run function bossbar:position
execute if data storage bossbar:data {spawner:{Dimension:"minecraft:the_nether"}} in minecraft:the_nether summon minecraft:marker run function bossbar:position
execute if data storage bossbar:data {spawner:{Dimension:"minecraft:the_end"}} in minecraft:the_end summon minecraft:marker run function bossbar:position







# Iterate through list

execute if score #bossbar_boolean bossbar.value matches 1 run data modify storage bossbar:data spawner_list append from storage bossbar:data spawner
data remove storage bossbar:data spawner_list[0]