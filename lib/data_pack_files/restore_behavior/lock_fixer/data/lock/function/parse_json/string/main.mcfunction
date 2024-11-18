# Extract characters from the string and put them into an array
# The string will be escaped by a single quote encapsulation for the future stage

data modify storage lock:data segments set value []
scoreboard players set #is_escaped lock.value 0
function lock:parse_json/string/char



# Concatenate characters into single string and return

function lock:concatenate/main
data modify storage lock:data stack[-1].return set value {type:"string"}
data modify storage lock:data stack[-1].return.value set from storage lock:data concatenated_string