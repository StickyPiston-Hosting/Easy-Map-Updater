# Remove all effects

execute unless score @s effect.levitation_duration matches 0 run function effect:levitation/remove
execute unless score @s effect.jump_boost_duration matches 0 run function effect:jump_boost/remove
execute unless score @s effect.mining_fatigue_duration matches 0 run function effect:mining_fatigue/remove







# Reset scores

scoreboard players set @s effect.deaths 0
scoreboard players set @s effect.milk_bucket 0