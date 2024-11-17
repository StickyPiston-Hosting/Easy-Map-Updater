# Get array length

execute store result score #length lock.value if data storage lock:data chars[]
data modify storage lock:data macro.string set value ""
function lock:concatenate/fetch