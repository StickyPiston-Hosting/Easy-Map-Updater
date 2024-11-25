# Convert a JSON text component in string form to NBT

data modify storage lock:data stack set value [{}]
function lock:parse_json/type
data modify storage lock:data json set from storage lock:data stack[0].return