# Setup effect simulation

scoreboard players operation @s effect.jump_boost_duration = #duration effect.value
scoreboard players operation @s effect.jump_boost_amplifier = #amplifier effect.value

# Attribute formula: https://www.desmos.com/calculator/mr3lmwqspl

execute if score #amplifier effect.value matches 128..251 run attribute @s minecraft:jump_strength base set 0.0
execute if score #amplifier effect.value matches 252 run attribute @s minecraft:jump_strength base set 0.04761725531183117
execute if score #amplifier effect.value matches 253 run attribute @s minecraft:jump_strength base set 0.19932824772240407
execute if score #amplifier effect.value matches 254 run attribute @s minecraft:jump_strength base set 0.3136974813109145
execute if score #amplifier effect.value matches 255 run attribute @s minecraft:jump_strength base set 0.41833081188907467

execute if score #amplifier effect.value matches 128.. run attribute @s minecraft:fall_damage_multiplier base set 0