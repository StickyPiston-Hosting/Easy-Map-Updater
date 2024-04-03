# Set owner tag

data modify storage firework:data tag set value {Owner:[I;0,0,0,0]}
execute store result storage firework:data tag.Owner[0] int 1 run scoreboard players get @s firework.uuid_0
execute store result storage firework:data tag.Owner[1] int 1 run scoreboard players get @s firework.uuid_1
execute store result storage firework:data tag.Owner[2] int 1 run scoreboard players get @s firework.uuid_2
execute store result storage firework:data tag.Owner[3] int 1 run scoreboard players get @s firework.uuid_3