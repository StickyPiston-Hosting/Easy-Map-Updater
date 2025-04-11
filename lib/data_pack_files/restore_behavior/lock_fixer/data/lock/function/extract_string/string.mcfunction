# Append string onto segment list

data modify storage lock:data segments append from storage lock:data stack[-1]



# Pop top of stack

data remove storage lock:data stack[-1]