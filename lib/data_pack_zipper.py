# Easy Map Updater
# Copyright (C) 2024  Jesse Spicer, and StickyPiston Hosting



# Import things

from pathlib import Path
import shutil
import sys



# Check that correct Python version is running

if not (
    (sys.version_info[0] == 3 and sys.version_info[1] >= 9)
    or
    (sys.version_info[0] > 3)
):
    print("\n\nERROR: Data Pack Zipper requires Python 3.9 or newer!")
    input()
    exit()



# Initialize variables

PROGRAM_PATH = Path(__file__).parent



def program():

    # Iterate through select folders
    for containing_folder in [
        PROGRAM_PATH / "data_pack_files" / "restore_behavior",
        PROGRAM_PATH / "region_files"
    ]:

        # Iterate through packs
        for data_pack_path in containing_folder.iterdir():

            # Skip if not a data pack
            if not data_pack_path.is_dir():
                continue
            if not (data_pack_path / "pack.mcmeta").exists():
                continue

            # Zip data pack
            print(f'Zipping {data_pack_path.name}')
            shutil.make_archive(data_pack_path, "zip", data_pack_path)

    print("Data packs zipped")



program()
input()