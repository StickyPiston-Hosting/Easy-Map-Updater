# Import things

from pathlib import Path



# Initialize variables

PROGRAM_PATH = Path(__file__).parent.parent



# Define functions

def log(text: str | list, halt = False):
    # Convert list to string
    if isinstance(text, list):
        text = "\n".join(text)

    # Add string to file
    with (PROGRAM_PATH / "log.txt").open("a", encoding="utf-8", newline="\n") as file:
        file.write("\n" + text)

    # Wait for input if halt is true
    if halt:
        input(text)
    else:
        print(text)