# Get effect data

data modify storage effect:data tag.effect set from entity @s active_effects[{id:"minecraft:levitation"}]

execute store result score #duration effect.value run data get storage effect:data tag.effect.duration
execute store result score #amplifier effect.value run data get storage effect:data tag.effect.amplifier
scoreboard players operation #amplifier effect.value %= #256 effect.value

scoreboard players add @s effect.levitation_amplifier 0
execute if score #amplifier effect.value >= @s effect.levitation_amplifier run function effect:levitation/apply

effect clear @s minecraft:levitation