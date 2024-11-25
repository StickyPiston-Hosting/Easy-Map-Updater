# Prepare macro parameters

data modify storage lock:data macro.c0 set from storage lock:data segments[0]
data modify storage lock:data macro.c1 set from storage lock:data segments[1]
data modify storage lock:data macro.c2 set from storage lock:data segments[2]
data modify storage lock:data macro.c3 set from storage lock:data segments[3]
data modify storage lock:data macro.c4 set from storage lock:data segments[4]
data modify storage lock:data macro.c5 set from storage lock:data segments[5]
data modify storage lock:data macro.c6 set from storage lock:data segments[6]
data modify storage lock:data macro.c7 set from storage lock:data segments[7]
data modify storage lock:data macro.c8 set from storage lock:data segments[8]
data modify storage lock:data macro.c9 set from storage lock:data segments[9]
data modify storage lock:data macro.ca set from storage lock:data segments[10]
data modify storage lock:data macro.cb set from storage lock:data segments[11]
data modify storage lock:data macro.cc set from storage lock:data segments[12]
data modify storage lock:data macro.cd set from storage lock:data segments[13]
data modify storage lock:data macro.ce set from storage lock:data segments[14]
data modify storage lock:data macro.cf set from storage lock:data segments[15]

data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]
data remove storage lock:data segments[0]

scoreboard players remove #length lock.value 16

function lock:concatenate/16/insert with storage lock:data macro
function lock:concatenate/fetch