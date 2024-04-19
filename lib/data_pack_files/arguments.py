# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Define functions

def parse(string: str, separator: str, allow_single_quotes: bool) -> list[str]:
    # Process string based on the presence of quotes
    if '"' in string:
        return parse_with_quotes(string, separator, allow_single_quotes, "")
    if allow_single_quotes and "'" in string:
        return parse_with_quotes(string, separator, allow_single_quotes, "")
    return parse_without_quotes(string, separator)

def parse_with_quotes(string: str, separator: str, allow_single_quotes: bool, spare_separator: str = "") -> list[str]:
    # Initialize variables
    arguments: list[str] = []
    argument = ""
    prev_char = ""
    bracket_count = 0
    in_string = False
    char_escaped = False
    string_type = ""

    # Iterate through string
    for char in string:
        # Push previous character
        prev_char_test = prev_char
        prev_char = char

        # Manage end separator
        if char == spare_separator and bracket_count == 0 and not in_string:
            if argument:
                arguments.append(argument)
            argument = ""

        # Check separator conditions
        if char == separator and bracket_count == 0 and not in_string:
            if argument:
                arguments.append(argument)
            argument = ""
            continue

        # Count brackets
        char_list = ["[", "]", "{", "}", "(", ")"]
        if not in_string and char in char_list:
            bracket_count += [1, -1][char_list.index(char) % 2]

        # Add character to argument
        if bracket_count >= 0:
            argument += char

        # Manage string state
        if in_string:
            if char_escaped:
                char_escaped = False
            else:
                if char == "\\":
                    char_escaped = True
                elif string_type == "single" and char == "'":
                    in_string = False
                    string_type = ""
                elif string_type == "double" and char == '"':
                    in_string = False
                    string_type = ""
            continue

        if allow_single_quotes and char == "'":
            in_string = True
            string_type = "single"
        if char == '"':
            in_string = True
            string_type = "double"

    # Append last argument to arguments
    arguments.append(argument)
    return arguments

def parse_without_quotes(string: str, separator: str) -> list[str]:
    # Initialize variables
    arguments: list[str] = []
    argument = ""

    # Iterate through string
    for piece in string.split(separator):
        # Append argument
        argument += piece

        # Perform action
        if (
            argument.count("[") == argument.count("]") and
            argument.count("{") == argument.count("}") and
            argument.count("(") == argument.count(")")
        ):
            if argument:
                arguments.append(argument)
            argument = ""
            continue
        if (
            argument.count("[") > argument.count("]") or
            argument.count("{") > argument.count("}") or
            argument.count("(") > argument.count(")")
        ):
            argument += separator

    if argument:
        if argument[-1] == separator:
            argument = argument[:-1]
        arguments.append(argument)

    return arguments