# Append content strings to segment list

execute if data storage lock:data stack[-1].value.text run data modify storage lock:data segments append from storage lock:data stack[-1].value.text.value
execute if data storage lock:data stack[-1].value.selector run data modify storage lock:data segments append from storage lock:data stack[-1].value.selector.value
execute if data storage lock:data stack[-1].value.translate run data modify storage lock:data segments append from storage lock:data stack[-1].value.translate.value
execute if data storage lock:data stack[-1].value.keybind run data modify storage lock:data segments append from storage lock:data stack[-1].value.keybind.value



# Iterate through extra list

execute store result score #extra lock.value if data storage lock:data stack[-1].value.extra
execute if score #extra lock.value matches 1 run data modify storage lock:data stack append from storage lock:data stack[-1].value.extra
execute if score #extra lock.value matches 1 run function lock:extract_string/list/main



# Pop top of stack

data remove storage lock:data stack[-1]