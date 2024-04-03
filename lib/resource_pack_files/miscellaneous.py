# Import things

from pathlib import Path



# Initialize variables

LEGAL_CHARS = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","0","1","2","3","4","5","6","7","8","9","/",".","_","-",":"]



# Define functions

def is_resource_legal(resource: str) -> bool:
    for char in resource:
        if char not in LEGAL_CHARS:
            return False
    return True

def namespace(resource: str) -> str:
    if resource == "":
        return resource
    if ":" in resource:
        return resource
    return "minecraft:" + resource

def resource_exists(pack: Path, resource: str, resource_type: str, file_type: str = "") -> bool:
    if not is_resource_legal(resource):
        return False

    resource_path = pack / "assets" / resource.split(":")[0] / resource_type / (resource.split(":")[1] + file_type)
    if resource_path.exists():
        return True
    
    vanilla_pack = pack.parent / "vanilla_resources"
    if not vanilla_pack.exists():
        return True
    
    resource_path = vanilla_pack / "assets" / resource.split(":")[0] / resource_type / resource.split(":")[1]
    if resource_path.exists():
        return True
    
    return False