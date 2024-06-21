# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from typing import cast, Any
from lib import defaults
from lib import json_manager
from lib.data_pack_files import predicate
from lib.data_pack_files import miscellaneous



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


def advancement(contents: dict[str, Any]) -> dict[str, Any]:
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



def update_criterion(criterion: dict[str, Any]):

    if "trigger" in criterion:
        criterion["trigger"] = miscellaneous.namespace(criterion["trigger"])

    # Update conditions
    if "conditions" in criterion:

        # Update all variations of the entity predicate
        for key in ["bystander", "entity", "lightning", "player", "projectile", "source", "villager"]:
            if key in criterion["conditions"]:
                if isinstance(criterion["conditions"][key], dict):
                    predicate.predicate_entity(criterion["conditions"][key], pack_version)
                if isinstance(criterion["conditions"][key], list):
                    for entity in criterion["conditions"][key]:
                        predicate.predicate(entity, pack_version)


        # Update damage objects

        if "killing_blow" in criterion["conditions"]:
            if "direct_entity" in criterion["conditions"]["killing_blow"]:
                predicate.predicate_entity(criterion["conditions"]["killing_blow"]["direct_entity"], pack_version)
            if "source_entity" in criterion["conditions"]["killing_blow"]:
                predicate.predicate_entity(criterion["conditions"]["killing_blow"]["source_entity"], pack_version)

        if "damage" in criterion["conditions"]:
            if "source_entity" in criterion["conditions"]["damage"]:
                predicate.predicate_entity(criterion["conditions"]["damage"]["source_entity"], pack_version)


        # Update item predicates
        if "item" in criterion["conditions"]:
            if isinstance(criterion["conditions"]["item"], dict):
                predicate.predicate_item(criterion["conditions"]["item"], pack_version)

        if "items" in criterion["conditions"]:
            if isinstance(criterion["conditions"]["items"], list):
                for item in criterion["conditions"]["items"]:
                    predicate.predicate_item(item, pack_version)

        if "rod" in criterion["conditions"]:
            if isinstance(criterion["conditions"]["rod"], dict):
                predicate.predicate_item(criterion["conditions"]["rod"], pack_version)