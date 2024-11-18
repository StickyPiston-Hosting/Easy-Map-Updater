# Run function based on data type of proceeding character

data modify storage lock:data char set string storage lock:data string 0 1
data modify storage lock:data string set string storage lock:data string 1

data modify storage lock:data stack[-1].child set value 1b

execute if data storage lock:data {char:'"'} run return run function lock:parse_json/string/main
execute if data storage lock:data {char:'{'} run return run function lock:parse_json/compound/main
execute if data storage lock:data {char:'['} run return run function lock:parse_json/list/main
execute if data storage lock:data {char:'t'} run return run function lock:parse_json/boolean/true
execute if data storage lock:data {char:'f'} run return run function lock:parse_json/boolean/false

data modify storage lock:data stack[-1].child set value 0b