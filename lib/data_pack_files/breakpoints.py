# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

import os
import shutil
import json
from pathlib import Path
from lib.log import log
from lib import defaults



# Define functions

def apply_breakpoints(world: Path):
    if not world.exists():
        log("ERROR: World does not exist!")
        return
    if not (world / "datapacks").exists():
        log("ERROR: World has no data packs!")
        return
    
    # Get name of data pack
    data_pack_name = input("Data pack to apply breakpoints to: ")
    data_pack_path = world / "datapacks" / data_pack_name
    if not (data_pack_path / "data").exists():
        log("ERROR: Data pack does not exist!")
        return
    log("Applying breakpoints")

    log("Copying data pack")
    new_data_pack_path = world / "datapacks" / f'{data_pack_name} - Breakpoints'
    if new_data_pack_path.exists():
        shutil.rmtree(new_data_pack_path)
    shutil.copytree(data_pack_path, new_data_pack_path)
    
    log("Generating function database")
    data_pack_dict = get_function_names(new_data_pack_path / "data")
    
    log("Hooking up function inheritance")
    apply_function_inheritance(data_pack_dict)

    log("Marking functions with breakpoints")
    mark_breakable_functions(data_pack_dict)
    
    log("Applying breakpoints to functions")
    modify_functions(data_pack_dict, new_data_pack_path)

    log("Breakpoints applied")
    


def get_function_names(data_pack_path: Path) -> dict[str, dict[str]]:
    data_pack_dict: dict[str, dict[str]] = {}
    for namespace_path in data_pack_path.iterdir():
        functions_path = namespace_path / "functions"
        if not functions_path.exists():
            continue
        for function_path in functions_path.glob("**/*.mcfunction"):
            data_pack_dict[get_namespaced_id(data_pack_path, function_path)] = {"path": function_path, "breakable": False, "parents": {}, "children": {}}
    return data_pack_dict

def get_namespaced_id(data_pack_path: Path, function_path: Path) -> str | None:
    function_list = function_path.as_posix()[len(data_pack_path.as_posix()) + 1:].split("/")
    if len(function_list) < 3:
        return None
    namespaced_id = f'{function_list[0]}:{"/".join(function_list[2:])}'
    if namespaced_id.endswith(".mcfunction"):
        namespaced_id = namespaced_id[:-11]
    return namespaced_id



def apply_function_inheritance(data_pack_dict: dict[str, dict[str]]):
    for function_id in data_pack_dict:
        function_path: Path = data_pack_dict[function_id]["path"]
        with function_path.open("r", encoding="utf-8") as file:
            commands = file.read().split("\n")
        for command in commands:
            command = command.strip()
            command_parts = command.split(" ")
            child_function_id = command_parts[-1]
            if (
                not command.startswith("#") and
                len(command_parts) >= 2 and
                command_parts[-2] == "function" and
                child_function_id in data_pack_dict
            ):
                data_pack_dict[function_id]["children"][child_function_id] = data_pack_dict[child_function_id]
                data_pack_dict[child_function_id]["parents"][function_id] = data_pack_dict[function_id]



def mark_breakable_functions(data_pack_dict: dict[str, dict[str]]):
    for function_id in data_pack_dict:
        mark_breakable_function(data_pack_dict[function_id])

def mark_breakable_function(function_dict: dict[str, bool, dict[str]]):
    if function_dict["breakable"]:
        return
    function_path: Path = function_dict["path"]
    with function_path.open("r", encoding="utf-8") as file:
        contents = file.read()
    
    if defaults.BREAKPOINT_MODE in contents:
        function_dict["breakable"] = True
    for child_function_id in function_dict["children"]:
        if function_dict["children"][child_function_id]["breakable"]:
            function_dict["breakable"] = True

    if function_dict["breakable"]:
        for function_id in function_dict["parents"]:
            mark_breakable_function(function_dict["parents"][function_id])



def modify_functions(data_pack_dict: dict[str, dict[str]], data_pack_path: Path):
    forceloads: list[tuple[str, str]] = []
    for function_id in data_pack_dict:
        function_dict = data_pack_dict[function_id]
        if not function_dict["breakable"]:
            continue
        function_path: Path = function_dict["path"]
        with function_path.open("r", encoding="utf-8") as file:
            commands = file.read().split("\n")
        
        commands.append( "EXTRA" )
        new_commands: list[str] = [f'data modify storage break:data history append value "{function_id}"']
        section = 0
        condition = ""
        coordinates: list[tuple[str, str]] = []
        chunk_load = False
        for command in commands:
            command = command.strip()
            if not command or command.startswith("#"):
                new_commands.append(command)
                continue
            command_parts = command.split(" ")

            if (
                chunk_load and
                (
                    defaults.BREAKPOINT_MODE not in command_parts or
                    condition != " ".join(command_parts[:command_parts.index(defaults.BREAKPOINT_MODE)])
                )
            ):
                if condition:
                    new_commands.append( f'execute if score #section break.value matches {section} run scoreboard players set #forceload_bool break.value 0' )
                    new_commands.append( f'execute if score #section break.value matches {section} run {condition} scoreboard players set #forceload_bool break.value 1'.replace(" run execute", "") )
                    for coordinate in coordinates:
                        new_commands.append( f'execute if score #section break.value matches {section} if score #forceload_bool break.value matches 1 run forceload add {coordinate[0]} {coordinate[1]}' )
                        new_commands.append( f'execute if score #section break.value matches {section} if score #forceload_bool break.value matches 1 run scoreboard players set #break.chunk.{coordinate[0]}_{coordinate[1]} break.value 5' )
                    new_commands.append( f'execute if score #section break.value matches {section} if score #forceload_bool break.value matches 0 run function break:modify_section {{modifier:2}}' )
                else:
                    for coordinate in coordinates:
                        new_commands.append( f'execute if score #section break.value matches {section} run forceload add {coordinate[0]} {coordinate[1]}' )
                        new_commands.append( f'execute if score #section break.value matches {section} run scoreboard players set #break.chunk.{coordinate[0]}_{coordinate[1]} break.value 5' )
                
                new_commands.append( f'execute if score #section break.value matches {section} run function break:modify_section {{modifier:1}}' )
                section += 1
                chunk_checks = [ f'if loaded {coordinate[0]} 0 {coordinate[1]}' for coordinate in coordinates ]
                new_commands.append( f'execute if score #section break.value matches {section} {" ".join(chunk_checks)} run function break:modify_section {{modifier:1}}' )
                new_commands.append( f'execute if score #section break.value matches {section} run function break:modify_section {{modifier:-1}}' )
                section += 1
                chunk_load = False
                condition = ""
                coordinates = []


            if defaults.BREAKPOINT_MODE in command_parts:
                chunk_load = True
                i = command_parts.index(defaults.BREAKPOINT_MODE)
                condition = " ".join(command_parts[:i])
                coordinate = ("0","0")
                if defaults.BREAKPOINT_MODE == "spreadplayers":
                    coordinate = (command_parts[i+1], command_parts[i+2])
                coordinates.append(coordinate)
                if coordinate not in forceloads:
                    forceloads.append(coordinate)
                continue

            if (
                len(command_parts) >= 2 and
                command_parts[-2] == "function" and
                command_parts[-1] in data_pack_dict and
                data_pack_dict[command_parts[-1]]["breakable"]
            ):
                new_commands.append( f'execute if score #section break.value matches {section} run {" ".join(command_parts[:-1])} break:add_call {{function: "{command_parts[-1]}"}}'.replace(" run execute", "") )
                new_commands.append( f'execute if score #section break.value matches {section} run function break:run_stack' )
                section += 1
                continue

            if command == "EXTRA":
                continue
            if "kill" in command_parts:
                command_parts[-2] = "tag"
                command_parts.append("add break.kill")
            new_commands.append( f'execute if score #section break.value matches {section} run {" ".join(command_parts)}'.replace(" run execute", "") )

        new_commands.append(
            "scoreboard players set #function_bool break.value 1\n" +
            "scoreboard players set #function_end_bool break.value 0\n" +
            f'execute if score #section break.value matches {section} run function break:child_end'
        )

        with function_path.open("w", encoding="utf-8", newline="\n") as file:
            file.write("\n".join(new_commands).replace("@e", "@e[tag=!break.kill]").replace("tag=!break.kill][", "tag=!break.kill,"))


    function_path = data_pack_path / "data" / "break" / "functions" / "load.mcfunction"
    function_path.parent.mkdir(exist_ok=True, parents=True)
    commands: list[str] = []
    for coordinate in forceloads:
        commands.append( f'execute unless score #break.chunk.{coordinate[0]}_{coordinate[1]} break.value = #break.chunk.{coordinate[0]}_{coordinate[1]} break.value run scoreboard players set #break.chunk.{coordinate[0]}_{coordinate[1]} break.value -1' )
    with function_path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(
            "scoreboard objectives add break.value dummy\n" + 
            "scoreboard objectives add break.id dummy\n" + 
            "scoreboard players set #zero break.value 0\n" + 
            "\n".join(commands)
        )

    file_path = data_pack_path / "data" / "minecraft" / "tags" / "functions" / "load.json"
    file_path.parent.mkdir(exist_ok=True, parents=True)
    if file_path.exists():
        with file_path.open("r", encoding="utf-8") as file:
            contents: dict[str, list[str]] = json.load(file)
        if "values" not in contents:
            contents["values"] = []
        contents["values"].append("break:load")
        with file_path.open("w", encoding="utf-8", newline="\n") as file:
            json.dump(contents, file, indent=4)
    else:
        with file_path.open("w", encoding="utf-8", newline="\n") as file:
            json.dump({ "values": [ "break:load" ] }, file, indent=4)

    
    function_path = data_pack_path / "data" / "break" / "functions" / "timer.mcfunction"
    function_path.parent.mkdir(exist_ok=True, parents=True)
    commands: list[str] = ["kill @e[tag=break.kill]"]
    for coordinate in forceloads:
        commands.append( f'execute if score #break.chunk.{coordinate[0]}_{coordinate[1]} break.value matches 0.. run scoreboard players remove #break.chunk.{coordinate[0]}_{coordinate[1]} break.value 1' )
    for coordinate in forceloads:
        commands.append( f'execute if score #break.chunk.{coordinate[0]}_{coordinate[1]} break.value matches 0 run forceload remove {coordinate[0]} {coordinate[1]}' )
    with function_path.open("w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(commands))


    file_path = data_pack_path / "data" / "minecraft" / "tags" / "functions" / "tick.json"
    file_path.parent.mkdir(exist_ok=True, parents=True)
    tick_function = "namespace:tick"
    if file_path.exists():
        with file_path.open("r", encoding="utf-8") as file:
            contents: dict[str, list[str]] = json.load(file)
        if "values" not in contents:
            contents["values"] = []
        else:
            tick_function = contents["values"][-1]
            contents["values"].pop(-1)
        contents["values"].append("break:tick")
        with file_path.open("w", encoding="utf-8", newline="\n") as file:
            json.dump(contents, file, indent=4)
    else:
        with file_path.open("w", encoding="utf-8", newline="\n") as file:
            json.dump({ "values": [ "break:tick" ] }, file, indent=4)

    function_path = data_pack_path / "data" / "break" / "functions" / "tick.mcfunction"
    function_path.parent.mkdir(exist_ok=True, parents=True)
    with function_path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(
            'data modify storage break:data history set value []\n' +
            'scoreboard players add #ticks break.value 1\n' +
            'execute unless data storage break:data stack run data modify storage break:data stack set value []\n' +
            f'execute unless data storage break:data stack[0] run data modify storage break:data stack append value {{executor:0, context:0, function:"{tick_function}", section:-1, tick:0, calls:[]}}\n' +
            'function break:run_stack\n' +
            'execute unless data storage break:data stack[0] run function break:timer'
        )

    with (data_pack_path / "data" / "break" / "functions" / "run_stack.mcfunction").open("w", encoding="utf-8", newline="\n") as file:
        file.write(
"""execute store result score #calls_bool break.value if data storage break:data stack[-1].calls[0]

execute if score #calls_bool break.value matches 1 run data modify storage break:data stack append from storage break:data stack[-1].calls[0]
execute if score #calls_bool break.value matches 1 run data remove storage break:data stack[-2].calls[0]
execute if score #calls_bool break.value matches 1 run function break:run_stack

execute if score #calls_bool break.value matches 0 store result score #section break.value run data get storage break:data stack[-1].section
execute if score #calls_bool break.value matches 0 run scoreboard players add #section break.value 1
execute if score #calls_bool break.value matches 0 store result storage break:data stack[-1].section int 1 run scoreboard players get #section break.value
execute if score #calls_bool break.value matches 0 store result score #tick break.value run data get storage break:data stack[-1].tick
execute if score #calls_bool break.value matches 0 store result storage break:data stack[-1].tick int 1 run scoreboard players get #ticks break.value
execute if score #calls_bool break.value matches 0 unless score #tick break.value = #ticks break.value run function break:run_function with storage break:data stack[-1]

scoreboard players set #calls_bool break.value -1"""
        )

    with (data_pack_path / "data" / "break" / "functions" / "run_function.mcfunction").open("w", encoding="utf-8", newline="\n") as file:
        file.write(
"""scoreboard players set #function_bool break.value 0

$execute if score #zero break.value matches $(executor) if score #zero break.value matches $(context) run function $(function)
$execute unless score #zero break.value matches $(executor) if score #zero break.value matches $(context) as @e[scores={break.id=$(executor)}] run function $(function)
$execute if score #zero break.value matches $(executor) unless score #zero break.value matches $(context) at @e[type=marker,tag=break.context,scores={break.id=$(context)}] run function $(function)
$execute unless score #zero break.value matches $(executor) unless score #zero break.value matches $(context) as @e[scores={break.id=$(executor)}] at @e[type=marker,tag=break.context,scores={break.id=$(context)}] run function $(function)

execute if score #function_bool break.value matches 0 run function break:child_end
execute if score #function_end_bool break.value matches 0 run scoreboard players set #section break.value -1
$execute if score #function_end_bool break.value matches 1 run kill @e[type=marker,tag=break.context,scores={break.id=$(context)}]"""
        )

    with (data_pack_path / "data" / "break" / "functions" / "add_call.mcfunction").open("w", encoding="utf-8", newline="\n") as file:
        file.write(
"""execute unless score @s break.id = @s break.id store result score @s break.id run scoreboard players add #global break.id 1
execute summon marker run function break:add_context
$data modify storage break:data stack[-1].calls append value {executor:0, context:0, function:"$(function)", section:-1, tick:0, calls:[]}
execute store result storage break:data stack[-1].calls[-1].executor int 1 run scoreboard players get @s break.id
execute store result storage break:data stack[-1].calls[-1].context int 1 run scoreboard players get #context_id break.value"""
        )

    with (data_pack_path / "data" / "break" / "functions" / "add_context.mcfunction").open("w", encoding="utf-8", newline="\n") as file:
        file.write(
"""execute store result score @s break.id run scoreboard players add #global break.id 1
tag @s add break.context
tp @s ~ ~ ~ ~ ~
scoreboard players operation #context_id break.value = @s break.id"""
        )

    with (data_pack_path / "data" / "break" / "functions" / "child_end.mcfunction").open("w", encoding="utf-8", newline="\n") as file:
        file.write(
"""data remove storage break:data stack[-1]
execute if data storage break:data stack[0] run function break:run_stack
scoreboard players set #function_end_bool break.value 1"""
        )

    with (data_pack_path / "data" / "break" / "functions" / "modify_section.mcfunction").open("w", encoding="utf-8", newline="\n") as file:
        file.write(
"""$scoreboard players set #modifier break.value $(modifier)
scoreboard players operation #section break.value += #modifier break.value
execute store result storage break:data stack[-1].section int 1 run scoreboard players get #section break.value"""
        )


    file_path = data_pack_path / "pack.mcmeta_old"
    if file_path.exists():
        os.rename(file_path, data_pack_path / "pack.mcmeta")