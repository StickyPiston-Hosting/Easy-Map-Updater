# Add entry to storage

data modify storage bossbar:data spawner set value {x:0,y:0,z:0,Dimension:"minecraft:overworld",UUID:[I;0,0,0,0]}
data modify storage bossbar:data spawner.x set from block ~ ~ ~ x
data modify storage bossbar:data spawner.y set from block ~ ~ ~ y
data modify storage bossbar:data spawner.z set from block ~ ~ ~ z
execute if dimension minecraft:overworld run data modify storage bossbar:data spawner.Dimension set value "minecraft:overworld"
execute if dimension minecraft:the_nether run data modify storage bossbar:data spawner.Dimension set value "minecraft:the_nether"
execute if dimension minecraft:the_end run data modify storage bossbar:data spawner.Dimension set value "minecraft:the_end"
execute if block ~ ~ ~ spawner run data modify storage bossbar:data spawner_list prepend from storage bossbar:data spawner