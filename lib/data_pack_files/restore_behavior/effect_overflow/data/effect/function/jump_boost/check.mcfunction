# Get effect data

data modify storage effect:data tag.effect set from entity @s active_effects[{id:"minecraft:jump_boost"}]

execute store result score #duration effect.value run data get storage effect:data tag.effect.duration
execute store result score #amplifier effect.value run data get storage effect:data tag.effect.amplifier
scoreboard players operation #amplifier effect.value %= #256 effect.value

scoreboard players add @s effect.jump_boost_amplifier 0
execute if score #amplifier effect.value >= @s effect.jump_boost_amplifier run function effect:jump_boost/apply

effect clear @s minecraft:jump_boost