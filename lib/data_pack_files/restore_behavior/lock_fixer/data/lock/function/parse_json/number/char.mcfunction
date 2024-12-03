# Add character to character array

data modify storage lock:data char set string storage lock:data string 0 1

scoreboard players set #is_number lock.value 0
execute if data storage lock:data {char:"0"} run scoreboard players set #is_number lock.value 1
execute if data storage lock:data {char:"1"} run scoreboard players set #is_number lock.value 1
execute if data storage lock:data {char:"2"} run scoreboard players set #is_number lock.value 1
execute if data storage lock:data {char:"3"} run scoreboard players set #is_number lock.value 1
execute if data storage lock:data {char:"4"} run scoreboard players set #is_number lock.value 1
execute if data storage lock:data {char:"5"} run scoreboard players set #is_number lock.value 1
execute if data storage lock:data {char:"6"} run scoreboard players set #is_number lock.value 1
execute if data storage lock:data {char:"7"} run scoreboard players set #is_number lock.value 1
execute if data storage lock:data {char:"8"} run scoreboard players set #is_number lock.value 1
execute if data storage lock:data {char:"9"} run scoreboard players set #is_number lock.value 1
execute if data storage lock:data {char:"-"} run scoreboard players set #is_number lock.value 1
execute if data storage lock:data {char:"."} run scoreboard players set #is_number lock.value 1

execute if score #is_number lock.value matches 1 run data modify storage lock:data segments append from storage lock:data char



# Close loop if character is not a numeric character

execute if score #is_number lock.value matches 0 run return 1



# Recurse string

data modify storage lock:data string set string storage lock:data string 1
function lock:parse_json/number/char