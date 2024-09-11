# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import traceback
from nbt import nbt as NBT
import random
random.seed()
from lib import defaults
from lib.log import log, get_log_path



# Define functions

def is_num(string: str) -> bool:
    # Check that at least one character is a number (to rule out NaN and infinity)
    for char in string:
        if char.isnumeric():
            break
    else:
        return False

    # Check if the input is a number
    try:
        int(string)
    except:
        pass
    else:
        return True

    try:
        float(string)
    except:
        pass
    else:
        return True

    return False

def is_int(string: str) -> bool:
    # Check if the input is a number
    try:
        int(string)
    except:
        pass
    else:
        return True

    return False

def is_uuid(string: str) -> bool:
    if len(string) != 36 or string.count("-") != 4:
        return False

    split_string = string.split("-")
    if (
        len(split_string[0]) != 8 or
        len(split_string[1]) != 4 or
        len(split_string[2]) != 4 or
        len(split_string[3]) != 4 or
        len(split_string[4]) != 12
    ):
        return False

    legal_chars = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f","-"]
    for char in string:
        if char not in legal_chars:
            return False

    return True

def is_partial_uuid(string: str) -> bool:
    if len(string) != 16 or string.count("-") != 2:
        return False

    split_string = string.split("-")
    if (
        len(split_string[0]) != 8 or
        len(split_string[1]) != 4 or
        len(split_string[2]) != 2
    ):
        return False

    legal_chars = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f","-"]
    for char in string:
        if char not in legal_chars:
            return False

    return True

def uuid_from_int_array(int_array: list[int]) -> str:
    chars = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]
    output = ""
    for int_entry in int_array:
        int_entry %= 4294967296
        for power in [268435456,16777216,1048576,65536,4096,256,16,1]:
            output += chars[(int_entry//power) % 16]
    output += "0"*(32-len(output))
    return f"{output[0:8]}-{output[8:12]}-{output[12:16]}-{output[16:20]}-{output[20:32]}"

def uuid_from_string(uuid: str) -> list[int]:
    uuid_int = 0
    hex_digit = 1
    chars = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]
    hyphen_count = 0
    for i in range(len(uuid)-1, -1, -1):
        char = uuid[i]
        if char == "-":
            hyphen_count += 1
            hex_digit = int(16**(8+4*hyphen_count))
            continue
        uuid_int += chars.index(char)*hex_digit
        hex_digit *= 16
    return [
        int_range(uuid_int//(4294967296*4294967296*4294967296)),
        int_range(uuid_int//(4294967296*4294967296)),
        int_range(uuid_int//(4294967296)),
        int_range(uuid_int)
    ]

def new_uuid() -> list[int]:
    return [
        random.randint(-2147483648,2147483647),
        random.randint(-2147483648,2147483647),
        random.randint(-2147483648,2147483647),
        random.randint(-2147483648,2147483647)
    ]



def unpack_string_check(string: str) -> str:
    # Unpack the string only if it is quoted
    if string.startswith('"') or string.startswith("'"):
        return unpack_string(string)
    return string

def unpack_string(string: str) -> str:
    # Return unescaped string
    if len(string) == 0:
        return ""
    else:
        if string.startswith("'"):
            return unquote(string).replace("\\\\", "__DOUBLE_BACKSLASH_INDICATOR__").replace("\\'", "'").replace("\\n", "\n").replace("\\u", "__UNICODE_INDICATOR__").replace("__UNICODE_INDICATOR__003d", "=").replace("__UNICODE_INDICATOR__0027", "'").replace("__DOUBLE_BACKSLASH_INDICATOR__", "\\")
        else:
            return unquote(string).replace("\\\\", "__DOUBLE_BACKSLASH_INDICATOR__").replace('\\"', '"').replace("\\n", "\n").replace("\\u", "__UNICODE_INDICATOR__").replace("__UNICODE_INDICATOR__003d", "=").replace("__UNICODE_INDICATOR__0027", "'").replace("__DOUBLE_BACKSLASH_INDICATOR__", "\\")

def pack_string(string: str, force_double: bool = False) -> str:
    # Return escaped string
    if '"' in string and not force_double:
        return "'" + string.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("__UNICODE_INDICATOR__", "\\u") + "'"
    return '"' + string.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("__UNICODE_INDICATOR__", "\\u") + '"'



def unquote(string: str) -> str:
    # Remove quotes from string
    if len(string) == 0:
        return ""
    elif string[0] in ['"', "'"]:
        return string[1:-1]
    else:
        return string
    


def nbt_list_contains(nbt_list: NBT.TAG_List, value) -> bool:
    for entry in nbt_list:
        if entry.value == value:
            return True
    return False

def nbt_num_array_contains(nbt_list: NBT.TAG_List, value) -> bool:
    for entry in nbt_list:
        if entry == value:
            return True
    return False

def nbt_list_remove(nbt_list: NBT.TAG_List, value):
    length = len(nbt_list)
    for i in range(length):
        i = length-i-1
        if nbt_list[i].value == value:
            nbt_list.pop(i)



def int_range(x: int):
    return (x + 2147483648)%4294967296 - 2147483648



def deduplicate_list(array: list) -> list:
    output_array = []
    for entry in array:
        if entry not in output_array:
            output_array.append(entry)
    return output_array



def get_version_from_user(message: str, skippable: bool) -> tuple[str, int]:
    while True:
        version_input = input(message)
        if skippable and not version_input:
            return version_input, 0
        parts = version_input.split(".")
        if len(parts) < 2 or len(parts) > 3:
            log("Invalid version!")
            continue
        if len(parts) == 2:
            parts.append("0")
        try:
            if int(parts[0]) != 1 or int(parts[1]) >= 100 or int(parts[2]) >= 100:
                log("Invalid version!")
                continue
            version = int(parts[1])*100 + int(parts[2])
        except:
            log("Invalid version!")
            continue
        return version_input, version

def get_version_string(version: int) -> str:
    if version%100 == 0:
        return f'1.{version//100%100}'
    return f'1.{version//100%100}.{version%100}'



def log_error():
    print("")
    log(f'ERROR:\n{traceback.format_exc()}')
    log(f'Error logged to: {get_log_path().as_posix()}')
    log(f'Please report the issue on the E.M.U. Discord server: {defaults.DISCORD_INVITE}', True)