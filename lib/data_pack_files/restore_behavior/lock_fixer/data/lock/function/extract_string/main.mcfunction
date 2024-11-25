# Parse JSON

function lock:parse_json/main



# Extract segments

data modify storage lock:data stack set value []
data modify storage lock:data stack append from storage lock:data json

data modify storage lock:data segments set value ['{"extra":["']
function lock:extract_string/type
data modify storage lock:data segments append value '"],"text":"EMU"}'



# Concatenate segments

function lock:concatenate/main
data modify storage lock:data string set from storage lock:data concatenated_string