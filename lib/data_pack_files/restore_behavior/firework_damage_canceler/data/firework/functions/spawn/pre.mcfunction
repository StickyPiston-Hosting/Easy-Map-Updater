# Run function as players

execute positioned ~-5 ~-5 ~-5 as @a[gamemode=!creative,gamemode=!spectator,dx=9,dy=63,dz=9] at @s run function firework:spawn/main







# Manage bat tags

tag @e[type=bat,tag=firework.target] add firework.entity.pre
tag @e[type=bat,tag=firework.target] remove firework.target