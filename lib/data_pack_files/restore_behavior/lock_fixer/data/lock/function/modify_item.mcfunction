# Modify item name if custom name is defined and is different from the stored value

data modify storage lock:data item set from entity @s ArmorItems[3]

execute store result score #custom_name_exists lock.value if data storage lock:data item.components."minecraft:custom_name"

execute if score #custom_name_exists lock.value matches 1 run data modify storage lock:data string set value ""
execute if score #custom_name_exists lock.value matches 1 run data modify storage lock:data string set from storage lock:data item.components."minecraft:custom_data".emu_lock_name
execute if score #custom_name_exists lock.value matches 1 store success score #different lock.value run data modify storage lock:data string set from storage lock:data item.components."minecraft:custom_name"

scoreboard players set #modified_boolean lock.value 0
execute if score #custom_name_exists lock.value matches 1 if score #different lock.value matches 1 run scoreboard players set #modified_boolean lock.value 1
execute if score #modified_boolean lock.value matches 1 unless data storage lock:data item.components."minecraft:custom_data" run data modify storage lock:data item.components."minecraft:custom_data" set value {}
execute if score #modified_boolean lock.value matches 1 run data modify storage lock:data item.components."minecraft:custom_data".emu_lock_name set from storage lock:data item.components."minecraft:custom_name"
execute if score #modified_boolean lock.value matches 1 run function lock:extract_string/main
execute if score #modified_boolean lock.value matches 1 run data modify storage lock:data item.components."minecraft:item_name" set from storage lock:data string
execute if score #modified_boolean lock.value matches 1 run data modify entity @s ArmorItems[3] set from storage lock:data item