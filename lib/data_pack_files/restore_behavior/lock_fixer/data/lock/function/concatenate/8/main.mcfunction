# Prepare macro parameters

data modify storage lock:data macro.c0 set from storage lock:data chars[0]
data modify storage lock:data macro.c1 set from storage lock:data chars[1]
data modify storage lock:data macro.c2 set from storage lock:data chars[2]
data modify storage lock:data macro.c3 set from storage lock:data chars[3]
data modify storage lock:data macro.c4 set from storage lock:data chars[4]
data modify storage lock:data macro.c5 set from storage lock:data chars[5]
data modify storage lock:data macro.c6 set from storage lock:data chars[6]
data modify storage lock:data macro.c7 set from storage lock:data chars[7]

data remove storage lock:data chars[0]
data remove storage lock:data chars[0]
data remove storage lock:data chars[0]
data remove storage lock:data chars[0]
data remove storage lock:data chars[0]
data remove storage lock:data chars[0]
data remove storage lock:data chars[0]
data remove storage lock:data chars[0]

scoreboard players remove #length lock.value 8

function lock:concatenate/8/insert with storage lock:data macro
function lock:concatenate/fetch