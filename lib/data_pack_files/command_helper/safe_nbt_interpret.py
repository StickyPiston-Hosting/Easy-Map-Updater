# Import things

from lib.data_pack_files import command_block_helper



# Define functions

def handle_interpret(command: list[str], issues: list[dict[str, str]]) -> str:
    commands = ["data modify storage help:data safe_nbt_interpret set value {}\n"]

    for issue in issues:
        index = issue["index"]
        nbt_source = issue["source"]
        nbt_object = issue["object"]
        nbt_path = issue["path"]
        commands.append(
            f'data modify storage help:data safe_nbt_interpret.v{index} set value "null"\n'
            f'data modify storage help:data safe_nbt_interpret.v{index} set from {nbt_source} {nbt_object} {nbt_path}\n'
            f'execute if data storage help:data {{safe_nbt_interpret:{{v{index}:"null"}}}} run data modify storage help:data safe_nbt_interpret.v{index} set value \'{{"type":"text","text":""}}\'\n'
            f'execute if data storage help:data {{safe_nbt_interpret:{{v{index}:[]}}}} run data modify storage help:data safe_nbt_interpret.v{index} set value \'{{"type":"text","text":""}}\'\n'
            f'execute if data storage help:data {{safe_nbt_interpret:{{v{index}:"[]"}}}} run data modify storage help:data safe_nbt_interpret.v{index} set value \'{{"type":"text","text":""}}\'\n'
        )

    return command_block_helper.create_function(
        "\n".join(commands) + "\n" +
        f'return run {" ".join(command)}'
    )