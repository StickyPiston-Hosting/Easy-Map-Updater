# Process item in list every 10 ticks

scoreboard players add #timer bossbar.value 1
execute if score #timer bossbar.value matches 10.. run scoreboard players set #timer bossbar.value 0
execute if score #timer bossbar.value matches 0 if data storage bossbar:data spawner_list[0] run function bossbar:iterate







# Have withers check if their list entry still exists

execute if score #timer bossbar.value matches 0 as @e[type=minecraft:wither,tag=bossbar.bossbar,tag=!bossbar.activated,sort=random,limit=1] run function bossbar:check_list
execute if score #timer bossbar.value matches 0 unless entity @e[type=minecraft:wither,tag=bossbar.bossbar,tag=!bossbar.activated] run tag @e[type=minecraft:wither,tag=bossbar.bossbar] remove bossbar.activated