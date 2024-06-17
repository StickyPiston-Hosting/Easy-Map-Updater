# Apply effects

execute as @a[predicate=effect:levitation] run function effect:levitation/check
execute as @a[predicate=effect:jump_boost] run function effect:jump_boost/check
execute as @a[predicate=effect:mining_fatigue] run function effect:mining_fatigue/check







# Tick effects

scoreboard players remove @a[scores={effect.levitation_duration=1..}] effect.levitation_duration 1
scoreboard players remove @a[scores={effect.jump_boost_duration=1..}] effect.jump_boost_duration 1
scoreboard players remove @a[scores={effect.mining_fatigue_duration=1..}] effect.mining_fatigue_duration 1

execute as @a[scores={effect.levitation_duration=0}] run function effect:levitation/remove
execute as @a[scores={effect.jump_boost_duration=0}] run function effect:jump_boost/remove
execute as @a[scores={effect.mining_fatigue_duration=0}] run function effect:mining_fatigue/remove







# Remove effects

execute as @a[scores={effect.deaths=1..}] run function effect:remove_all
execute as @a[scores={effect.milk_bucket=1..}] run function effect:remove_all