# Extract characters from the string and construct the compound

data modify storage lock:data stack append value {compound:{},key_value:[]}
function lock:parse_json/compound/char



# Push compound to return stack

data modify storage lock:data stack[-2].return set value {type:"compound"}
data modify storage lock:data stack[-2].return.value set from storage lock:data stack[-1].compound
data remove storage lock:data stack[-1]