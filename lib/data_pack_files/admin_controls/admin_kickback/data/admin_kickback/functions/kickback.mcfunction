# Kickback player

execute facing entity @s feet rotated ~ 0 positioned as @s run tp @s ^ ^ ^1
tellraw @s {"text":"Hey! You aren't allowed to touch that!","color":"red"}
execute at @s run playsound minecraft:entity.item.break master @s