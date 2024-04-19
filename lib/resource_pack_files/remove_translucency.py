# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from pathlib import Path
from PIL import Image
from lib.log import log
from lib import json_manager
from lib import defaults



# Initialize variables

PRORAM_PATH = Path(__file__).parent

ITEM_TEXTURE_LEGEND = {
    "minecraft:item/white_stained_glass":           ["minecraft:block/white_stained_glass"],
    "minecraft:item/orange_stained_glass":          ["minecraft:block/orange_stained_glass"],
    "minecraft:item/magenta_stained_glass":         ["minecraft:block/magenta_stained_glass"],
    "minecraft:item/light_blue_stained_glass":      ["minecraft:block/light_blue_stained_glass"],
    "minecraft:item/yellow_stained_glass":          ["minecraft:block/yellow_stained_glass"],
    "minecraft:item/lime_stained_glass":            ["minecraft:block/lime_stained_glass"],
    "minecraft:item/pink_stained_glass":            ["minecraft:block/pink_stained_glass"],
    "minecraft:item/gray_stained_glass":            ["minecraft:block/gray_stained_glass"],
    "minecraft:item/light_gray_stained_glass":      ["minecraft:block/light_gray_stained_glass"],
    "minecraft:item/cyan_stained_glass":            ["minecraft:block/cyan_stained_glass"],
    "minecraft:item/purple_stained_glass":          ["minecraft:block/purple_stained_glass"],
    "minecraft:item/blue_stained_glass":            ["minecraft:block/blue_stained_glass"],
    "minecraft:item/brown_stained_glass":           ["minecraft:block/brown_stained_glass"],
    "minecraft:item/green_stained_glass":           ["minecraft:block/green_stained_glass"],
    "minecraft:item/red_stained_glass":             ["minecraft:block/red_stained_glass"],
    "minecraft:item/black_stained_glass":           ["minecraft:block/black_stained_glass"],

    "minecraft:item/white_stained_glass_pane":      ["minecraft:block/white_stained_glass"],
    "minecraft:item/orange_stained_glass_pane":     ["minecraft:block/orange_stained_glass"],
    "minecraft:item/magenta_stained_glass_pane":    ["minecraft:block/magenta_stained_glass"],
    "minecraft:item/light_blue_stained_glass_pane": ["minecraft:block/light_blue_stained_glass"],
    "minecraft:item/yellow_stained_glass_pane":     ["minecraft:block/yellow_stained_glass"],
    "minecraft:item/lime_stained_glass_pane":       ["minecraft:block/lime_stained_glass"],
    "minecraft:item/pink_stained_glass_pane":       ["minecraft:block/pink_stained_glass"],
    "minecraft:item/gray_stained_glass_pane":       ["minecraft:block/gray_stained_glass"],
    "minecraft:item/light_gray_stained_glass_pane": ["minecraft:block/light_gray_stained_glass"],
    "minecraft:item/cyan_stained_glass_pane":       ["minecraft:block/cyan_stained_glass"],
    "minecraft:item/purple_stained_glass_pane":     ["minecraft:block/purple_stained_glass"],
    "minecraft:item/blue_stained_glass_pane":       ["minecraft:block/blue_stained_glass"],
    "minecraft:item/brown_stained_glass_pane":      ["minecraft:block/brown_stained_glass"],
    "minecraft:item/green_stained_glass_pane":      ["minecraft:block/green_stained_glass"],
    "minecraft:item/red_stained_glass_pane":        ["minecraft:block/red_stained_glass"],
    "minecraft:item/black_stained_glass_pane":      ["minecraft:block/black_stained_glass"],

    "minecraft:item/ice":                           ["minecraft:block/ice"],
    "minecraft:item/slime_block":                   ["minecraft:block/slime_block"],
    "minecraft:item/honey_block":                   ["minecraft:block/honey_block_top", "minecraft:block/honey_block_bottom", "minecraft:block/honey_block_side"],
    "minecraft:item/tinted_glass":                  ["minecraft:block/tinted_glass"]
}

BLOCK_TEXTURE_LEGEND = {
    "minecraft:white_stained_glass":           {"minecraft:block/white_stained_glass":      ["minecraft:block/white_stained_glass"     ]},
    "minecraft:orange_stained_glass":          {"minecraft:block/orange_stained_glass":     ["minecraft:block/orange_stained_glass"    ]},
    "minecraft:magenta_stained_glass":         {"minecraft:block/magenta_stained_glass":    ["minecraft:block/magenta_stained_glass"   ]},
    "minecraft:light_blue_stained_glass":      {"minecraft:block/light_blue_stained_glass": ["minecraft:block/light_blue_stained_glass"]},
    "minecraft:yellow_stained_glass":          {"minecraft:block/yellow_stained_glass":     ["minecraft:block/yellow_stained_glass"    ]},
    "minecraft:lime_stained_glass":            {"minecraft:block/lime_stained_glass":       ["minecraft:block/lime_stained_glass"      ]},
    "minecraft:pink_stained_glass":            {"minecraft:block/pink_stained_glass":       ["minecraft:block/pink_stained_glass"      ]},
    "minecraft:gray_stained_glass":            {"minecraft:block/gray_stained_glass":       ["minecraft:block/gray_stained_glass"      ]},
    "minecraft:light_gray_stained_glass":      {"minecraft:block/light_gray_stained_glass": ["minecraft:block/light_gray_stained_glass"]},
    "minecraft:cyan_stained_glass":            {"minecraft:block/cyan_stained_glass":       ["minecraft:block/cyan_stained_glass"      ]},
    "minecraft:purple_stained_glass":          {"minecraft:block/purple_stained_glass":     ["minecraft:block/purple_stained_glass"    ]},
    "minecraft:blue_stained_glass":            {"minecraft:block/blue_stained_glass":       ["minecraft:block/blue_stained_glass"      ]},
    "minecraft:brown_stained_glass":           {"minecraft:block/brown_stained_glass":      ["minecraft:block/brown_stained_glass"     ]},
    "minecraft:green_stained_glass":           {"minecraft:block/green_stained_glass":      ["minecraft:block/green_stained_glass"     ]},
    "minecraft:red_stained_glass":             {"minecraft:block/red_stained_glass":        ["minecraft:block/red_stained_glass"       ]},
    "minecraft:black_stained_glass":           {"minecraft:block/black_stained_glass":      ["minecraft:block/black_stained_glass"     ]},

    "minecraft:white_stained_glass_pane":      {
        "minecraft:block/white_stained_glass_pane_post":       ["minecraft:block/white_stained_glass", "minecraft:block/white_stained_glass_pane_top"],
        "minecraft:block/white_stained_glass_pane_side":       ["minecraft:block/white_stained_glass", "minecraft:block/white_stained_glass_pane_top"],
        "minecraft:block/white_stained_glass_pane_side_alt":   ["minecraft:block/white_stained_glass", "minecraft:block/white_stained_glass_pane_top"],
        "minecraft:block/white_stained_glass_pane_noside":     ["minecraft:block/white_stained_glass"],
        "minecraft:block/white_stained_glass_pane_noside_alt": ["minecraft:block/white_stained_glass"]
    },
    "minecraft:orange_stained_glass_pane":     {
        "minecraft:block/orange_stained_glass_pane_post":       ["minecraft:block/orange_stained_glass", "minecraft:block/orange_stained_glass_pane_top"],
        "minecraft:block/orange_stained_glass_pane_side":       ["minecraft:block/orange_stained_glass", "minecraft:block/orange_stained_glass_pane_top"],
        "minecraft:block/orange_stained_glass_pane_side_alt":   ["minecraft:block/orange_stained_glass", "minecraft:block/orange_stained_glass_pane_top"],
        "minecraft:block/orange_stained_glass_pane_noside":     ["minecraft:block/orange_stained_glass"],
        "minecraft:block/orange_stained_glass_pane_noside_alt": ["minecraft:block/orange_stained_glass"]
    },
    "minecraft:magenta_stained_glass_pane":    {
        "minecraft:block/magenta_stained_glass_pane_post":       ["minecraft:block/magenta_stained_glass", "minecraft:block/magenta_stained_glass_pane_top"],
        "minecraft:block/magenta_stained_glass_pane_side":       ["minecraft:block/magenta_stained_glass", "minecraft:block/magenta_stained_glass_pane_top"],
        "minecraft:block/magenta_stained_glass_pane_side_alt":   ["minecraft:block/magenta_stained_glass", "minecraft:block/magenta_stained_glass_pane_top"],
        "minecraft:block/magenta_stained_glass_pane_noside":     ["minecraft:block/magenta_stained_glass"],
        "minecraft:block/magenta_stained_glass_pane_noside_alt": ["minecraft:block/magenta_stained_glass"]
    },
    "minecraft:light_blue_stained_glass_pane": {
        "minecraft:block/light_blue_stained_glass_pane_post":       ["minecraft:block/light_blue_stained_glass", "minecraft:block/light_blue_stained_glass_pane_top"],
        "minecraft:block/light_blue_stained_glass_pane_side":       ["minecraft:block/light_blue_stained_glass", "minecraft:block/light_blue_stained_glass_pane_top"],
        "minecraft:block/light_blue_stained_glass_pane_side_alt":   ["minecraft:block/light_blue_stained_glass", "minecraft:block/light_blue_stained_glass_pane_top"],
        "minecraft:block/light_blue_stained_glass_pane_noside":     ["minecraft:block/light_blue_stained_glass"],
        "minecraft:block/light_blue_stained_glass_pane_noside_alt": ["minecraft:block/light_blue_stained_glass"]
    },
    "minecraft:yellow_stained_glass_pane":     {
        "minecraft:block/yellow_stained_glass_pane_post":       ["minecraft:block/yellow_stained_glass", "minecraft:block/yellow_stained_glass_pane_top"],
        "minecraft:block/yellow_stained_glass_pane_side":       ["minecraft:block/yellow_stained_glass", "minecraft:block/yellow_stained_glass_pane_top"],
        "minecraft:block/yellow_stained_glass_pane_side_alt":   ["minecraft:block/yellow_stained_glass", "minecraft:block/yellow_stained_glass_pane_top"],
        "minecraft:block/yellow_stained_glass_pane_noside":     ["minecraft:block/yellow_stained_glass"],
        "minecraft:block/yellow_stained_glass_pane_noside_alt": ["minecraft:block/yellow_stained_glass"]
    },
    "minecraft:lime_stained_glass_pane":       {
        "minecraft:block/lime_stained_glass_pane_post":       ["minecraft:block/lime_stained_glass", "minecraft:block/lime_stained_glass_pane_top"],
        "minecraft:block/lime_stained_glass_pane_side":       ["minecraft:block/lime_stained_glass", "minecraft:block/lime_stained_glass_pane_top"],
        "minecraft:block/lime_stained_glass_pane_side_alt":   ["minecraft:block/lime_stained_glass", "minecraft:block/lime_stained_glass_pane_top"],
        "minecraft:block/lime_stained_glass_pane_noside":     ["minecraft:block/lime_stained_glass"],
        "minecraft:block/lime_stained_glass_pane_noside_alt": ["minecraft:block/lime_stained_glass"]
    },
    "minecraft:pink_stained_glass_pane":       {
        "minecraft:block/pink_stained_glass_pane_post":       ["minecraft:block/pink_stained_glass", "minecraft:block/pink_stained_glass_pane_top"],
        "minecraft:block/pink_stained_glass_pane_side":       ["minecraft:block/pink_stained_glass", "minecraft:block/pink_stained_glass_pane_top"],
        "minecraft:block/pink_stained_glass_pane_side_alt":   ["minecraft:block/pink_stained_glass", "minecraft:block/pink_stained_glass_pane_top"],
        "minecraft:block/pink_stained_glass_pane_noside":     ["minecraft:block/pink_stained_glass"],
        "minecraft:block/pink_stained_glass_pane_noside_alt": ["minecraft:block/pink_stained_glass"]
    },
    "minecraft:gray_stained_glass_pane":       {
        "minecraft:block/gray_stained_glass_pane_post":       ["minecraft:block/gray_stained_glass", "minecraft:block/gray_stained_glass_pane_top"],
        "minecraft:block/gray_stained_glass_pane_side":       ["minecraft:block/gray_stained_glass", "minecraft:block/gray_stained_glass_pane_top"],
        "minecraft:block/gray_stained_glass_pane_side_alt":   ["minecraft:block/gray_stained_glass", "minecraft:block/gray_stained_glass_pane_top"],
        "minecraft:block/gray_stained_glass_pane_noside":     ["minecraft:block/gray_stained_glass"],
        "minecraft:block/gray_stained_glass_pane_noside_alt": ["minecraft:block/gray_stained_glass"]
    },
    "minecraft:light_gray_stained_glass_pane": {
        "minecraft:block/light_gray_stained_glass_pane_post":       ["minecraft:block/light_gray_stained_glass", "minecraft:block/light_gray_stained_glass_pane_top"],
        "minecraft:block/light_gray_stained_glass_pane_side":       ["minecraft:block/light_gray_stained_glass", "minecraft:block/light_gray_stained_glass_pane_top"],
        "minecraft:block/light_gray_stained_glass_pane_side_alt":   ["minecraft:block/light_gray_stained_glass", "minecraft:block/light_gray_stained_glass_pane_top"],
        "minecraft:block/light_gray_stained_glass_pane_noside":     ["minecraft:block/light_gray_stained_glass"],
        "minecraft:block/light_gray_stained_glass_pane_noside_alt": ["minecraft:block/light_gray_stained_glass"]
    },
    "minecraft:cyan_stained_glass_pane":       {
        "minecraft:block/cyan_stained_glass_pane_post":       ["minecraft:block/cyan_stained_glass", "minecraft:block/cyan_stained_glass_pane_top"],
        "minecraft:block/cyan_stained_glass_pane_side":       ["minecraft:block/cyan_stained_glass", "minecraft:block/cyan_stained_glass_pane_top"],
        "minecraft:block/cyan_stained_glass_pane_side_alt":   ["minecraft:block/cyan_stained_glass", "minecraft:block/cyan_stained_glass_pane_top"],
        "minecraft:block/cyan_stained_glass_pane_noside":     ["minecraft:block/cyan_stained_glass"],
        "minecraft:block/cyan_stained_glass_pane_noside_alt": ["minecraft:block/cyan_stained_glass"]
    },
    "minecraft:purple_stained_glass_pane":     {
        "minecraft:block/purple_stained_glass_pane_post":       ["minecraft:block/purple_stained_glass", "minecraft:block/purple_stained_glass_pane_top"],
        "minecraft:block/purple_stained_glass_pane_side":       ["minecraft:block/purple_stained_glass", "minecraft:block/purple_stained_glass_pane_top"],
        "minecraft:block/purple_stained_glass_pane_side_alt":   ["minecraft:block/purple_stained_glass", "minecraft:block/purple_stained_glass_pane_top"],
        "minecraft:block/purple_stained_glass_pane_noside":     ["minecraft:block/purple_stained_glass"],
        "minecraft:block/purple_stained_glass_pane_noside_alt": ["minecraft:block/purple_stained_glass"]
    },
    "minecraft:blue_stained_glass_pane":       {
        "minecraft:block/blue_stained_glass_pane_post":       ["minecraft:block/blue_stained_glass", "minecraft:block/blue_stained_glass_pane_top"],
        "minecraft:block/blue_stained_glass_pane_side":       ["minecraft:block/blue_stained_glass", "minecraft:block/blue_stained_glass_pane_top"],
        "minecraft:block/blue_stained_glass_pane_side_alt":   ["minecraft:block/blue_stained_glass", "minecraft:block/blue_stained_glass_pane_top"],
        "minecraft:block/blue_stained_glass_pane_noside":     ["minecraft:block/blue_stained_glass"],
        "minecraft:block/blue_stained_glass_pane_noside_alt": ["minecraft:block/blue_stained_glass"]
    },
    "minecraft:brown_stained_glass_pane":      {
        "minecraft:block/brown_stained_glass_pane_post":       ["minecraft:block/brown_stained_glass", "minecraft:block/brown_stained_glass_pane_top"],
        "minecraft:block/brown_stained_glass_pane_side":       ["minecraft:block/brown_stained_glass", "minecraft:block/brown_stained_glass_pane_top"],
        "minecraft:block/brown_stained_glass_pane_side_alt":   ["minecraft:block/brown_stained_glass", "minecraft:block/brown_stained_glass_pane_top"],
        "minecraft:block/brown_stained_glass_pane_noside":     ["minecraft:block/brown_stained_glass"],
        "minecraft:block/brown_stained_glass_pane_noside_alt": ["minecraft:block/brown_stained_glass"]
    },
    "minecraft:green_stained_glass_pane":      {
        "minecraft:block/green_stained_glass_pane_post":       ["minecraft:block/green_stained_glass", "minecraft:block/green_stained_glass_pane_top"],
        "minecraft:block/green_stained_glass_pane_side":       ["minecraft:block/green_stained_glass", "minecraft:block/green_stained_glass_pane_top"],
        "minecraft:block/green_stained_glass_pane_side_alt":   ["minecraft:block/green_stained_glass", "minecraft:block/green_stained_glass_pane_top"],
        "minecraft:block/green_stained_glass_pane_noside":     ["minecraft:block/green_stained_glass"],
        "minecraft:block/green_stained_glass_pane_noside_alt": ["minecraft:block/green_stained_glass"]
    },
    "minecraft:red_stained_glass_pane":        {
        "minecraft:block/red_stained_glass_pane_post":       ["minecraft:block/red_stained_glass", "minecraft:block/red_stained_glass_pane_top"],
        "minecraft:block/red_stained_glass_pane_side":       ["minecraft:block/red_stained_glass", "minecraft:block/red_stained_glass_pane_top"],
        "minecraft:block/red_stained_glass_pane_side_alt":   ["minecraft:block/red_stained_glass", "minecraft:block/red_stained_glass_pane_top"],
        "minecraft:block/red_stained_glass_pane_noside":     ["minecraft:block/red_stained_glass"],
        "minecraft:block/red_stained_glass_pane_noside_alt": ["minecraft:block/red_stained_glass"]
    },
    "minecraft:black_stained_glass_pane":      {
        "minecraft:block/black_stained_glass_pane_post":       ["minecraft:block/black_stained_glass", "minecraft:block/black_stained_glass_pane_top"],
        "minecraft:block/black_stained_glass_pane_side":       ["minecraft:block/black_stained_glass", "minecraft:block/black_stained_glass_pane_top"],
        "minecraft:block/black_stained_glass_pane_side_alt":   ["minecraft:block/black_stained_glass", "minecraft:block/black_stained_glass_pane_top"],
        "minecraft:block/black_stained_glass_pane_noside":     ["minecraft:block/black_stained_glass"],
        "minecraft:block/black_stained_glass_pane_noside_alt": ["minecraft:block/black_stained_glass"]
    },

    "minecraft:ice":           {"minecraft:block/ice":          ["minecraft:block/ice"]},
    "minecraft:slime_block":   {"minecraft:block/slime_block":  ["minecraft:block/slime_block"]},
    "minecraft:honey_block":   {"minecraft:block/honey_block":  ["minecraft:block/honey_block_top", "minecraft:block/honey_block_bottom", "minecraft:block/honey_block_side"]},
    "minecraft:tinted_glass":  {"minecraft:block/tinted_glass": ["minecraft:block/tinted_glass"]},
    "minecraft:nether_portal": {
        "minecraft:block/nether_portal_ns": ["minecraft:block/nether_portal"],
        "minecraft:block/nether_portal_ew": ["minecraft:block/nether_portal"]
    },
    "minecraft:frosted_ice":   {
        "minecraft:block/frosted_ice_0": ["minecraft:block/frosted_ice_0"],
        "minecraft:block/frosted_ice_1": ["minecraft:block/frosted_ice_1"],
        "minecraft:block/frosted_ice_2": ["minecraft:block/frosted_ice_2"],
        "minecraft:block/frosted_ice_3": ["minecraft:block/frosted_ice_3"]
    }
}

FORCED_BLOCK_TEXTURES = ["minecraft:block/water_overlay", "minecraft:block/water_flow", "minecraft:block/water_still"]



# Define functions

def remove_translucency(pack: Path):
    log("Removing translucency")

    texture_list = extract_texture_list(pack)
    for texture in texture_list:
        remove_translucency_from_texture(pack, path_from_id(pack, texture, "textures", ".png"))

    log("Translucency removed")



def extract_texture_list(pack: Path) -> list[str]:
    # Initialize texture list
    minecraft_namespace = pack / "assets" / "minecraft"
    minecraft_texture_path = minecraft_namespace / "textures"
    texture_list: list[str] = []
    for texture_path in [
        minecraft_texture_path / "block",
        minecraft_texture_path / "item"
    ]:
        if texture_path.exists():
            for texture in texture_path.glob("**/*.png"):
                texture_list.append(f'minecraft:{texture.as_posix()[len(minecraft_texture_path.as_posix()) + 1:-4]}')

    # Add custom texture directories to list from block and item models
    minecraft_model_path = minecraft_namespace / "models"
    for model_path in [
        minecraft_model_path / "block",
        minecraft_model_path / "item"
    ]:
        if model_path.exists():
            for model in model_path.glob("**/*.json"):
                model_json, load_bool = json_manager.safe_load(model)
                if not load_bool:
                    continue
                if (
                    "textures" in model_json and
                    isinstance(model_json["textures"], dict)
                ):
                    for key, texture in model_json["textures"].items():
                        if (
                            not texture or
                            not isinstance(texture, str) or
                            texture[0] == "#"
                        ):
                            continue
                        if ":" not in texture:
                            texture = f'minecraft:{texture}'
                        if texture not in texture_list:
                            texture_list.append(texture)

    # Remove textures from the list if they are referenced by blocks and items which permit translucency
    textures_to_remove: list[str] = FORCED_BLOCK_TEXTURES.copy()

    textures_to_remove.extend(extract_textures_from_model_list(pack, ITEM_TEXTURE_LEGEND))

    for block_state_id in BLOCK_TEXTURE_LEGEND:
        block_state_path = path_from_id(pack, block_state_id, "blockstates", ".json")
        if block_state_path.exists():
            textures_to_remove.extend(extract_textures_from_block_state(pack, block_state_path))
        else:
            textures_to_remove.extend(extract_textures_from_model_list(pack, BLOCK_TEXTURE_LEGEND[block_state_id]))

    for texture in textures_to_remove:
        if texture in texture_list:
            texture_list.remove(texture)

    return texture_list

def path_from_id(pack: Path, model_id: str, folder: str, extension: str) -> Path:
    return pack / "assets" / model_id.split(":")[0] / folder / (model_id.split(":")[1] + extension)

def extract_textures_from_block_state(pack: Path, block_state: Path) -> list[str]:
    texture_list: list[str] = []
    block_state_json, load_bool = json_manager.safe_load(block_state)
    if not load_bool:
        return []
    if (
        "variants" in block_state_json and
        isinstance(block_state_json["variants"], dict)
    ):
        for key, variant in block_state_json["variants"].items():
            texture_list.extend(extract_textures_from_block_state_variant(pack, variant))
    if (
        "multipart" in block_state_json and
        isinstance(block_state_json["multipart"], list)
    ):
        for entry in block_state_json["multipart"]:
            if "apply" in entry:
                texture_list.extend(extract_textures_from_block_state_variant(pack, entry["apply"]))
    return texture_list

def extract_textures_from_block_state_variant(pack: Path, variant: dict[str, str] | list[dict[str, str]]) -> list[str]:
    texture_list: list[str] = []
    if (
        isinstance(variant, dict) and
        "model" in variant
    ):
        texture_list.extend(extract_textures_from_model(pack, variant["model"]))
    elif (isinstance(variant, list)):
        for entry in variant:
            if (
                isinstance(entry, dict) and
                "model" in entry
            ):
                texture_list.extend(extract_textures_from_model(pack, entry["model"]))
    return texture_list

def extract_textures_from_model_list(pack: Path, model_list: dict[str, list[str]]) -> list[str]:
    texture_list: list[str] = []
    for model_id in model_list:
        model_path = path_from_id(pack, model_id, "models", ".json")
        if model_path.exists():
            texture_list.extend(extract_textures_from_model(pack, model_path))
        else:
            texture_list.extend(model_list[model_id])
    return texture_list

def extract_textures_from_model(pack: Path, model: Path) -> list[str]:
    texture_list: list[str] = []
    model_json, load_bool = json_manager.safe_load(model)
    if not load_bool:
        return []
    if (
        "textures" in model_json and
        isinstance(model_json["textures"], dict)
    ):
        for key, texture in model_json["textures"].items():
            if (
                not texture or
                not isinstance(texture, str) or
                texture[0] == "#"
            ):
                continue
            if ":" not in texture:
                texture = f'minecraft:{texture}'
            if texture not in texture_list:
                texture_list.append(texture)

    if (
        "parent" in model_json and
        isinstance(model_json["parent"], str)
    ):
        texture_list.extend(extract_textures_from_model(pack, path_from_id(pack, model_json["parent"], "models", ".json")))
    if (
        "overrides" in model_json and
        isinstance(model_json["overrides"], list)
    ):
        for override in model_json["overrides"]:
            if (
                isinstance(override, dict) and
                "model" in override and
                isinstance(override["model"], str)
            ):
                texture_list.extend(extract_textures_from_model(pack, path_from_id(pack, override["model"], "models", ".json")))

    return texture_list



def remove_translucency_from_texture(pack: Path, image_path: Path):
    if not image_path.exists():
        return
    if defaults.DEBUG_MODE:
        log(image_path.as_posix()[len(pack.as_posix()):])
    image = Image.open(image_path, "r", ["png"])
    if image.mode == "P":
        log(f'WARNING: Indexed color image found: {image_path.as_posix()[len(pack.as_posix()):]}')
        return
    if image.mode != "RGBA":
        return
    pixels = image.load()
    modified = False
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            pixel = pixels[x,y]
            if (
                pixel[3] != 0 or
                pixel[3] != 255
            ):
                pixels[x,y] = (
                    pixel[0],
                    pixel[1],
                    pixel[2],
                    0 if pixel[3] < 128 else 255
                )
                modified = True
    if modified:
        image.save(image_path, "png")