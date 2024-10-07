# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import json
from pathlib import Path
from typing import Any
from lib import defaults
from lib import utils
from lib import json_manager
from lib.data_pack_files import predicate
from lib.data_pack_files import items
from lib.data_pack_files import miscellaneous



# Initialize variables

pack_version = defaults.PACK_VERSION



# Define functions

def update(file_path: Path, source_file_path: Path, version: int):
    global pack_version
    pack_version = version

    # Read file
    contents, load_bool = json_manager.safe_load(source_file_path)
    if not load_bool:
        return

    # Write to new location
    file_path.parent.mkdir(parents=True, exist_ok=True)
    utils.safe_file_write(file_path, json.dumps(advancement(contents, version), indent=4))


def advancement(contents: dict[str, Any], version: int) -> dict[str, Any]:
    global pack_version
    pack_version = version

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

    # Update display data
    if "display" in contents:
        display = contents["display"]

        if "icon" in display:
            icon = display["icon"]

            if version <= 2004:
                display["icon"] = items.update_from_json(
                    {
                        "id": icon["item"],
                        "nbt": icon["nbt"] if "nbt" in icon else None
                    },
                    version,
                    []
                )

            else:
                count = icon["count"] if "count" in icon else None
                display["icon"] = items.update_from_json(
                    display["icon"],
                    version,
                    []
                )
                if count:
                    display["icon"]["count"] = count


    return contents



def update_criterion(criterion: dict[str, Any]):

    if "trigger" in criterion:
        criterion["trigger"] = miscellaneous.namespace(criterion["trigger"])

    # Update conditions
    if "conditions" in criterion:

        # Update all variations of the entity predicate
        for key in ["bystander", "child", "entity", "lightning", "parent", "player", "projectile", "shooter", "source", "villager", "zombie"]:
            if key in criterion["conditions"]:
                if isinstance(criterion["conditions"][key], dict):
                    predicate.predicate_entity(criterion["conditions"][key], pack_version)
                if isinstance(criterion["conditions"][key], list):
                    for entity in criterion["conditions"][key]:
                        predicate.predicate(entity, pack_version)

        if "victims" in criterion["conditions"]:
            for victim in criterion["conditions"]["victims"]:
                if isinstance(victim, dict):
                    predicate.predicate_entity(victim, pack_version)
                if isinstance(victim, list):
                    for entity in victim:
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
        for key in ["item", "rod"]:
            if key in criterion["conditions"]:
                if isinstance(criterion["conditions"][key], dict):
                    predicate.predicate_item(criterion["conditions"][key], pack_version)

        for key in ["ingredients", "items"]:
            if key in criterion["conditions"]:
                if isinstance(criterion["conditions"][key], list):
                    for item in criterion["conditions"][key]:
                        predicate.predicate_item(item, pack_version)


        # Update location predicate
        if "start_position" in criterion["conditions"]:
            predicate.predicate_location(criterion["conditions"]["start_position"], pack_version)

        if "location" in criterion["conditions"]:
            if isinstance(criterion["conditions"]["location"], list):
                for location in criterion["conditions"]["location"]:
                    predicate.predicate(location, pack_version)