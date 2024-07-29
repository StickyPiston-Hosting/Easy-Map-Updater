# Create scoreboard objectives

scoreboard objectives add bossbar.value dummy

scoreboard objectives add bossbar.uuid_0 dummy
scoreboard objectives add bossbar.uuid_1 dummy
scoreboard objectives add bossbar.uuid_2 dummy
scoreboard objectives add bossbar.uuid_3 dummy







# Initialize storage if it doesn't exist

execute unless data storage bossbar:data spawner_list run data modify storage bossbar:data spawner_list set value []
execute unless data storage bossbar:data spawner run data modify storage bossbar:data spawner set value {}
execute unless data storage bossbar:data tag run data modify storage bossbar:data tag set value {}