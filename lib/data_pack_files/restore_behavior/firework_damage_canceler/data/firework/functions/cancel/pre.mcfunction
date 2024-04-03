# Revoke advancement

advancement revoke @s only firework:pre







# Manage gamemode

execute unless score @s firework.gamemode = @s firework.gamemode run scoreboard players set @s[gamemode=survival ] firework.gamemode 0
execute unless score @s firework.gamemode = @s firework.gamemode run scoreboard players set @s[gamemode=creative ] firework.gamemode 1
execute unless score @s firework.gamemode = @s firework.gamemode run scoreboard players set @s[gamemode=adventure] firework.gamemode 2
execute unless score @s firework.gamemode = @s firework.gamemode run scoreboard players set @s[gamemode=spectator] firework.gamemode 3

gamemode creative @s