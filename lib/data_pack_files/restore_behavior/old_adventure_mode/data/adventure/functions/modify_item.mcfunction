# Check if item is suitable for modification

scoreboard players set #modified_boolean adventure.value 0

execute store result score #boolean adventure.value if predicate adventure:placeable
execute if score #boolean adventure.value matches 1 run item modify entity @s armor.head adventure:placeable
execute if score #boolean adventure.value matches 1 run scoreboard players set #modified_boolean adventure.value 1

execute store result score #boolean adventure.value if predicate adventure:pickaxe
execute if score #boolean adventure.value matches 1 run item modify entity @s armor.head adventure:pickaxe
execute if score #boolean adventure.value matches 1 run scoreboard players set #modified_boolean adventure.value 1

execute store result score #boolean adventure.value if predicate adventure:shovel
execute if score #boolean adventure.value matches 1 run item modify entity @s armor.head adventure:shovel
execute if score #boolean adventure.value matches 1 run scoreboard players set #modified_boolean adventure.value 1

execute store result score #boolean adventure.value if predicate adventure:axe
execute if score #boolean adventure.value matches 1 run item modify entity @s armor.head adventure:axe
execute if score #boolean adventure.value matches 1 run scoreboard players set #modified_boolean adventure.value 1

execute store result score #boolean adventure.value if predicate adventure:hoe
execute if score #boolean adventure.value matches 1 run item modify entity @s armor.head adventure:hoe
execute if score #boolean adventure.value matches 1 run scoreboard players set #modified_boolean adventure.value 1

execute store result score #boolean adventure.value if predicate adventure:sword
execute if score #boolean adventure.value matches 1 run item modify entity @s armor.head adventure:sword
execute if score #boolean adventure.value matches 1 run scoreboard players set #modified_boolean adventure.value 1

execute store result score #boolean adventure.value if predicate adventure:shears
execute if score #boolean adventure.value matches 1 run item modify entity @s armor.head adventure:shears
execute if score #boolean adventure.value matches 1 run scoreboard players set #modified_boolean adventure.value 1

execute store result score #boolean adventure.value if predicate adventure:unprocessed
execute if score #boolean adventure.value matches 1 run item modify entity @s armor.head adventure:universal
execute if score #boolean adventure.value matches 1 run scoreboard players set #modified_boolean adventure.value 1