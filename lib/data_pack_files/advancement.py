# Import things

import json
from pathlib import Path
from lib import defaults
from lib import json_manager
from lib.data_pack_files import predicate



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def update(file_path: Path, og_file_path: Path, version: int):
    global pack_version
    pack_version = version

    # Read file
    contents, load_bool = json_manager.safe_load(og_file_path)
    if not load_bool:
        return

    # Write to new location
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(advancement(contents), file, indent=4)


def advancement(contents: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    # Update criteria
    for criterion_name in contents["criteria"]:
        update_criterion(contents["criteria"][criterion_name])

    # Enforce booleans
    if "display" in contents:
        display = contents["display"]
        for key in ["show_toast", "announce_to_chat", "hidden"]:
            if key in display:
                if display[key] in ["true", "True"]:
                    display[key] = True
                if display[key] in ["false", "False"]:
                    display[key] = False
    if "sends_telemetry_event" in contents:
        if contents["sends_telemetry_event"] in ["true", "True"]:
            contents["sends_telemetry_event"] = True
        if contents["sends_telemetry_event"] in ["false", "False"]:
            contents["sends_telemetry_event"] = False


    return contents



def update_criterion(criterion: dict[str, str | dict[str, str]]) -> dict[str, str | dict[str, str]]:
    # Update player conditions
    if "conditions" in criterion:
        if "player" in criterion["conditions"]:
            if isinstance(criterion["conditions"]["player"], dict):
                predicate.predicate_entity(criterion["conditions"]["player"])
            elif isinstance(criterion["conditions"]["player"], list):
                for player_predicate in criterion["conditions"]["player"]:
                    predicate.predicate(player_predicate)