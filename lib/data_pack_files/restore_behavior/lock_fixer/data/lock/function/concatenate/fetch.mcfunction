# Run function based on length

execute if score #length lock.value matches 16.. run return run function lock:concatenate/16/main
execute if score #length lock.value matches 08.. run return run function lock:concatenate/8/main
execute if score #length lock.value matches 04.. run return run function lock:concatenate/4/main
execute if score #length lock.value matches 02.. run return run function lock:concatenate/2/main
execute if score #length lock.value matches 01.. run return run function lock:concatenate/1/main