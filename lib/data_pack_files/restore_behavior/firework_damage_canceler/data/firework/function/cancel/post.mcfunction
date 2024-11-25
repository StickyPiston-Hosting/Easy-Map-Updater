# Revoke advancement

advancement revoke @s only firework:post







# Manage gamemode

gamemode survival @s[scores={firework.gamemode=0}]
gamemode creative @s[scores={firework.gamemode=1}]
gamemode adventure @s[scores={firework.gamemode=2}]
gamemode spectator @s[scores={firework.gamemode=3}]

scoreboard players reset @s firework.gamemode