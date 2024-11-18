# Prepare macro parameters

data modify storage lock:data macro.c0 set from storage lock:data segments[0]

data remove storage lock:data segments[0]

scoreboard players remove #length lock.value 1

function lock:concatenate/1/insert with storage lock:data macro
function lock:concatenate/fetch