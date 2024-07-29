# Create scoreboard objectives

scoreboard objectives add firework.value dummy
scoreboard objectives add firework.gamemode dummy

scoreboard objectives add firework.uuid_0 dummy
scoreboard objectives add firework.uuid_1 dummy
scoreboard objectives add firework.uuid_2 dummy
scoreboard objectives add firework.uuid_3 dummy







# Set constants

scoreboard players set #65536 firework.value 65536







# Prepare RNG

scoreboard players set #rng_multiplier firework.value 1664525
scoreboard players set #rng_increment firework.value 1013904223
scoreboard players add #rng firework.value 0







# Prepare storage

data modify storage firework:data tag set value {}