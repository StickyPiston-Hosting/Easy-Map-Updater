# Extract characters from the string and construct the list

data modify storage lock:data stack append value {list:[]}
function lock:parse_json/list/char



# Push list to return stack

data modify storage lock:data stack[-2].return set value {type:"list"}
data modify storage lock:data stack[-2].return.value set from storage lock:data stack[-1].list
data remove storage lock:data stack[-1]