# Prepare macro parameters

data modify storage lock:data macro.c0 set from storage lock:data segments[0]
data modify storage lock:data macro.c1 set from storage lock:data segments[1]

data remove storage lock:data segments[0]
data remove storage lock:data segments[0]

scoreboard players remove #length lock.value 2

function lock:concatenate/2/insert with storage lock:data macro
function lock:concatenate/fetch