# Determine data type

data modify storage lock:data string_test set value "__EMU_STRING_TEST__"
execute store success score #is_string lock.value run data modify storage lock:data string_test set string storage lock:data stack[-1]
execute store success score #is_list lock.value if data storage lock:data stack[-1][]



# Run function based on object type at top of stack

execute if score #is_string lock.value matches 1 run return run function lock:extract_string/string
execute if score #is_list lock.value matches 1 run return run function lock:extract_string/list/main
return run function lock:extract_string/compound