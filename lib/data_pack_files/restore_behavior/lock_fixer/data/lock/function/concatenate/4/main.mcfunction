# Prepare macro parameters

data modify storage lock:data macro.c0 set from storage lock:data chars[0]
data modify storage lock:data macro.c1 set from storage lock:data chars[1]
data modify storage lock:data macro.c2 set from storage lock:data chars[2]
data modify storage lock:data macro.c3 set from storage lock:data chars[3]

data remove storage lock:data chars[0]
data remove storage lock:data chars[0]
data remove storage lock:data chars[0]
data remove storage lock:data chars[0]

scoreboard players remove #length lock.value 4

function lock:concatenate/4/insert with storage lock:data macro
function lock:concatenate/fetch