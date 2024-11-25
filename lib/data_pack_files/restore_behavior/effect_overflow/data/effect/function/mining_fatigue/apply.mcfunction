# Setup effect simulation

scoreboard players operation @s effect.mining_fatigue_duration = #duration effect.value
scoreboard players operation @s effect.mining_fatigue_amplifier = #amplifier effect.value

execute if score #amplifier effect.value matches 128.. run attribute @s minecraft:block_break_speed base set 0