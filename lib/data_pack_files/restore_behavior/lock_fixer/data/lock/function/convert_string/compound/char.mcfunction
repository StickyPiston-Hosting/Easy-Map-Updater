# Check if character is a child object

function lock:convert_string/type
data modify storage lock:data child set from storage lock:data stack[-1].child



# Append returned data to key value pair list if it was a child object

execute if data storage lock:data {child:1b} run data modify storage lock:data stack[-1].key_value append from storage lock:data stack[-1].return



# Push data to compound if key value pair has been decided

execute store result score #length lock.value if data storage lock:data stack[-1].key_value[]
execute if score #length lock.value matches 2.. run data modify storage lock:data macro.key set from storage lock:data stack[-1].key_value[0].value
execute if score #length lock.value matches 2.. run function lock:convert_string/compound/insert with storage lock:data macro
execute if score #length lock.value matches 2.. run data modify storage lock:data stack[-1].key_value set value []



# Close loop if it wasn't a child object and the compound has ended

execute if data storage lock:data {child:0b,char:"}"} run return 1



# Recurse compound

function lock:convert_string/compound/char