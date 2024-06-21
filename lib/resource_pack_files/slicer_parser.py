# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



import json
from typing import cast, Any
from pathlib import Path
from slicer_input import DATA



PROGRAM_PATH = Path(__file__).parent
OUTPUT = {}



def program():
    for entry in DATA:
        data_type: str = entry[0]

        if data_type == "input":
            handle_input(entry)

        if data_type == "moveRealmsToMinecraft":
            handle_move_realms(entry)

        if data_type == "clip":
            handle_clip(entry)

    with (PROGRAM_PATH / "slicer_output.json").open("w", encoding="utf-8", newline="\n") as file:
        file.write(
            json.dumps(deep_sort(OUTPUT), indent=4).replace('"{', "{").replace('}"', "}").replace('\\"', '"')
        )



def handle_input(entry: tuple[str, str, tuple]):
    input_path = entry[1].split("/")[1:]
    data = cast(list, get_branch(OUTPUT, input_path, True))

    output: tuple[str, tuple[int], str]
    for output in entry[2:]:
        output_path = output[0].split("/")[1:]
        i = 0
        for i in range(min(len(input_path), len(output_path))):
            if input_path[i] != output_path[i]:
                break
        else:
            i += 1
        data_entry = {
            "path": (len(input_path) - i - 1)*"./" + "/".join(output_path[i:]),
            "slice": list(output[1])
        }
        if len(output) >= 3:
            data_entry["metadata"] = json.loads(output[2])
        data.append(json.dumps(data_entry))



def handle_move_realms(entry: tuple[str, str]):
    input_path = f'realms/textures/gui/{entry[1]}.png'.split("/")
    data = cast(list, get_branch(OUTPUT, input_path, True))

    output_path = ["minecraft", *(input_path[1:])]
    i = 0
    for i in range(min(len(input_path), len(output_path))):
        if input_path[i] != output_path[i]:
            break
    else:
        i += 1
    data.append((len(input_path) - i - 1)*"./" + "/".join(output_path[i:]))



def handle_clip(entry: tuple[str, str, tuple[int]]):
    input_path = f'minecraft/textures/gui/{entry[1]}.png'.split("/")
    data: list = cast(list, get_branch(OUTPUT, input_path, True))
    data.append(json.dumps({
        "path": input_path[-1],
        "clip": list(entry[2])
    }))



def get_branch(data: dict, path: list[str], end: bool) -> dict | list:
    for folder in path[:-1]:
        if folder not in data:
            data[folder] = {}
        data = data[folder]
    if not end:
        return data
    if path[-1] not in data:
        data[path[-1]] = []
    return data[path[-1]]



def deep_sort(data: dict[str, Any] | str) -> dict[str, Any] | str:
    if not isinstance(data, dict):
        return data

    keys = list(data.keys())
    keys.sort()
    output_data = {}
    for key in keys:
        output_data[key] = deep_sort(data[key])
    
    return output_data



# copy() - This just moves the file, doesn't modify it.
# clip() - Crops the image in place without changing the location.
# moveRealmsToMinecraft() - Moves file from the realms namespace to the minecraft namespace, nested inside textures/gui.

program()