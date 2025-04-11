# Append content strings to segment list

execute if data storage lock:data stack[-1].text run data modify storage lock:data segments append from storage lock:data stack[-1].text
execute if data storage lock:data stack[-1].selector run data modify storage lock:data segments append from storage lock:data stack[-1].selector
execute if data storage lock:data stack[-1].translate run data modify storage lock:data segments append from storage lock:data stack[-1].translate
execute if data storage lock:data stack[-1].keybind run data modify storage lock:data segments append from storage lock:data stack[-1].keybind



# Iterate through extra list

execute store result score #extra lock.value if data storage lock:data stack[-1].extra
execute if score #extra lock.value matches 1 run data modify storage lock:data stack append from storage lock:data stack[-1].extra
execute if score #extra lock.value matches 1 run function lock:extract_string/list/main



# Pop top of stack

data remove storage lock:data stack[-1]