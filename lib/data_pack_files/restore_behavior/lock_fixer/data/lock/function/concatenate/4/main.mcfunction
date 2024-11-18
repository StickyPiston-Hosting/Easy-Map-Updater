# Prepare macro parameters

data modify storage lock:data macro.c0 set from storage lock:data segments[0]
data modify storage lock:data macro.c1 set from storage lock:data segments[1]
data modify storage lock:data macro.c2 set from storage lock:data segments[2]
data modify storage lock:data macro.c3 set from storage lock:data segments[3]

data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]

scoreboard players remove #length lock.value 4

function lock:concatenate/4/insert with storage lock:data macro
function lock:concatenate/fetch