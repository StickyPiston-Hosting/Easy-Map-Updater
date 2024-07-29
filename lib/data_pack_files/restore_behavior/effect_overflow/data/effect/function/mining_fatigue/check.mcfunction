# Get effect data

data modify storage effect:data tag.effect set from entity @s active_effects[{id:"minecraft:mining_fatigue"}]

execute store result score #duration effect.value run data get storage effect:data tag.effect.duration
execute store result score #amplifier effect.value run data get storage effect:data tag.effect.amplifier
scoreboard players operation #amplifier effect.value %= #256 effect.value

scoreboard players add @s effect.mining_fatigue_amplifier 0
execute if score #amplifier effect.value >= @s effect.mining_fatigue_amplifier run function effect:mining_fatigue/apply

effect clear @s minecraft:mining_fatigue