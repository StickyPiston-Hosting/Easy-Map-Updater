# Extract characters from the string and put them into an array

data modify storage lock:data segments set value []
data modify storage lock:data segments append from storage lock:data char
function lock:parse_json/number/char



# Concatenate characters into single string and return

function lock:concatenate/main
data modify storage lock:data stack[-1].return set value {type:"number"}
data modify storage lock:data stack[-1].return.value set from storage lock:data concatenated_string