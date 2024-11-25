# Check if character is a child object

function lock:parse_json/type
data modify storage lock:data child set from storage lock:data stack[-1].child



# Append returned data to list if it was a child object

execute if data storage lock:data {child:1b} run data modify storage lock:data stack[-1].list append from storage lock:data stack[-1].return



# Close loop if it wasn't a child object and the list has ended

execute if data storage lock:data {child:0b,char:"]"} run return 1



# Recurse list

function lock:parse_json/list/char