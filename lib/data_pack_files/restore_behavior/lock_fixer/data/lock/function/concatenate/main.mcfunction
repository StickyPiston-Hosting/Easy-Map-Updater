# Get array length

execute store result score #length lock.value if data storage lock:data segments[]
data modify storage lock:data macro.string set value ""
function lock:concatenate/fetch
data modify storage lock:data concatenated_string set from storage lock:data macro.string