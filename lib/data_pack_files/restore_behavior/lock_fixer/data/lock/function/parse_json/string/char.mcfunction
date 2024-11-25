# Add character to character array

data modify storage lock:data char set string storage lock:data string 0 1
data modify storage lock:data string set string storage lock:data string 1

scoreboard players set #char_type lock.value 0
execute if data storage lock:data {char:"'"} run scoreboard players set #char_type lock.value 1
execute if data storage lock:data {char:'"'} run scoreboard players set #char_type lock.value 2
execute if data storage lock:data {char:"\\"} run scoreboard players set #char_type lock.value 3

execute if score #char_type lock.value matches 0 run data modify storage lock:data segments append from storage lock:data char
execute if score #char_type lock.value matches 1 run data modify storage lock:data segments append value "_SQ_"
execute if score #char_type lock.value matches 2 if score #is_escaped lock.value matches 1 run data modify storage lock:data segments append value "_DQ_"
execute if score #char_type lock.value matches 3 if score #is_escaped lock.value matches 1 run data modify storage lock:data segments append value "_BS_"



# Close loop if character is an unescaped quote

execute if score #char_type lock.value matches 2 if score #is_escaped lock.value matches 0 run return 1



# Toggle escaped flag if character is a backslash
execute if score #char_type lock.value matches 3 run scoreboard players add #is_escaped lock.value 1
execute if score #char_type lock.value matches 3 run scoreboard players operation #is_escaped lock.value %= #2 lock.value

# Set escaped flag to false if character is not a backslash
execute unless score #char_type lock.value matches 3 run scoreboard players set #is_escaped lock.value 0



# Recurse string

function lock:parse_json/string/char