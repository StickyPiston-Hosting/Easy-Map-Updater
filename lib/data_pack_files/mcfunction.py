# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from pathlib import Path
from lib.log import log
from lib.data_pack_files import command
from lib import defaults
from lib import utils



# Initialize variables

pack_version = defaults.PACK_VERSION
namespaced_id = ""



# Define functions

def update(file_path: Path, source_file_path: Path, version: int, function_id: str):
    # Set pack version
    global pack_version
    pack_version = version
    global namespaced_id
    namespaced_id = function_id

    # Log namespaced ID
    if defaults.DEBUG_MODE:
        log(f"Function: {namespaced_id}")

    # Read file
    contents = utils.safe_file_read(source_file_path)

    # Write to new location
    file_path.parent.mkdir(parents=True, exist_ok=True)
    utils.safe_file_write(file_path, mcfunction(contents, version))

def mcfunction(contents: str, version: int) -> str:
    global pack_version
    pack_version = version

    # Split up the lines
    lines = contents.split("\n")

    # Condense lines which are split up
    lines: list[str] = []
    line_break = False
    for line in contents.split("\n"):
        line = line.strip()
        if not line_break:
            lines.append(line)
        else:
            lines[-1] += line
        if line.endswith("\\"):
            if not line_break and not line.startswith("#"):
                line_break = True
        else:
            line_break = False
        if line_break:
            lines[-1] = lines[-1][:-1]

    # Iterate and convert the lines
    for line_index in range(len(lines)):
        line = lines[line_index]

        # Skip line if it is blank or a comment
        if not line:
            continue
        if line.startswith("#"):
            continue

        # Convert command
        line = command.update(line, pack_version, namespaced_id)

        # Write line to list
        lines[line_index] = line

    # Add return command for pre-1.20.3
    if pack_version <= 2002:
        if lines[-1].split(" ")[0] != "return":
            lines.append("return 1")

    # Return contents
    return "\n".join(lines)