# Run function based on object type at top of stack

data modify storage lock:data type set from storage lock:data stack[-1].type

execute if data storage lock:data {type:"string"} run return run function lock:extract_string/string
execute if data storage lock:data {type:"compound"} run return run function lock:extract_string/compound
execute if data storage lock:data {type:"list"} run return run function lock:extract_string/list/main