# Close loop if list is empty

execute unless data storage lock:data stack[-1][0] run return 1



# Extract contents of first entry

data modify storage lock:data stack append from storage lock:data stack[-1][0]
function lock:extract_string/type
data remove storage lock:data stack[-1][0]



# Recurse list

function lock:extract_string/list/iterate