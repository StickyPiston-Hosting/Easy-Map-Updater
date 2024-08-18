# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from pathlib import Path
from datetime import datetime



# Initialize variables

PROGRAM_PATH = Path(__file__).parent.parent



# Define functions

def log(text: str | list, halt = False):
    # Convert list to string
    if isinstance(text, list):
        text = "\n".join(text)

    # Add string to file
    current_time = datetime.now()
    with get_log_path(current_time).open("a", encoding="utf-8", newline="\n") as file:
        file.write(f'{current_time.strftime("[%H:%M:%S]")} {text}\n')

    # Wait for input if halt is true
    if halt:
        input(f'{text}\nPress ENTER to continue')
    else:
        print(text)



def get_log_path(current_time: datetime = datetime.now()) -> Path:
    logs_folder = PROGRAM_PATH / "logs"
    logs_folder.mkdir(exist_ok=True, parents=True)
    return logs_folder / current_time.strftime("%Y-%m-%d.log")