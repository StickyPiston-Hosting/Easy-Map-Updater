# Remove characters from string

data modify storage lock:data string set string storage lock:data string 4



# Return boolean

data modify storage lock:data stack[-1].return set value {type:"boolean",value:"false"}