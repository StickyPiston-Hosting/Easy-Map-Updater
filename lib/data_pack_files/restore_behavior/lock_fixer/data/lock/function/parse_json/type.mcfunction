# Run function based on data type of proceeding character

data modify storage lock:data char set string storage lock:data string 0 1
data modify storage lock:data string set string storage lock:data string 1

data modify storage lock:data stack[-1].child set value 1b

execute if data storage lock:data {char:'"'} run return run function lock:parse_json/string/main
execute if data storage lock:data {char:"{"} run return run function lock:parse_json/compound/main
execute if data storage lock:data {char:"["} run return run function lock:parse_json/list/main
execute if data storage lock:data {char:"t"} run return run function lock:parse_json/boolean/true
execute if data storage lock:data {char:"f"} run return run function lock:parse_json/boolean/false

execute if data storage lock:data {char:"0"} run return run function lock:parse_json/number/main
execute if data storage lock:data {char:"1"} run return run function lock:parse_json/number/main
execute if data storage lock:data {char:"2"} run return run function lock:parse_json/number/main
execute if data storage lock:data {char:"3"} run return run function lock:parse_json/number/main
execute if data storage lock:data {char:"4"} run return run function lock:parse_json/number/main
execute if data storage lock:data {char:"5"} run return run function lock:parse_json/number/main
execute if data storage lock:data {char:"6"} run return run function lock:parse_json/number/main
execute if data storage lock:data {char:"7"} run return run function lock:parse_json/number/main
execute if data storage lock:data {char:"8"} run return run function lock:parse_json/number/main
execute if data storage lock:data {char:"9"} run return run function lock:parse_json/number/main
execute if data storage lock:data {char:"-"} run return run function lock:parse_json/number/main
execute if data storage lock:data {char:"."} run return run function lock:parse_json/number/main

data modify storage lock:data stack[-1].child set value 0b