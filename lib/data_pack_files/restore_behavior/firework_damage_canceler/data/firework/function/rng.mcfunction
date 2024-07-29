# Generate random number

scoreboard players operation #rng firework.value *= #rng_multiplier firework.value
scoreboard players operation #rng firework.value += #rng_increment firework.value







# Swap bits

scoreboard players operation #rng_bit_swap firework.value = #rng firework.value
scoreboard players operation #rng_bit_swap firework.value /= #65536 firework.value
scoreboard players operation #rng firework.value *= #65536 firework.value
scoreboard players operation #rng firework.value += #rng_bit_swap firework.value







# Return output

scoreboard players operation #output firework.value = #rng firework.value
execute if score #input firework.value matches 1.. run scoreboard players operation #output firework.value %= #input firework.value