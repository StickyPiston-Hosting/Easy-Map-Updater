# Run function based on data type of proceeding character

data modify storage lock:data char set string storage lock:data string 0 1
data modify storage lock:data string set string storage lock:data string 1

data modify storage lock:data stack[-1].child set value 1b

execute if data storage lock:data {char:'"'} run return run function lock:convert_string/string/main
execute if data storage lock:data {char:'{'} run return run function lock:convert_string/compound/main
execute if data storage lock:data {char:'['} run return run function lock:convert_string/list/main

data modify storage lock:data stack[-1].child set value 0b