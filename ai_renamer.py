import os
import argparse
import pathlib
import time
from backend import generate_names 

from colorama import Fore, Style, init
# This is needed on Windows for colorama to work
init()

def rename_files(old_names, new_names):
    '''Rename old_names to new_names
    Both lists must have the same length
    Both lists contain the full paths to the files (not just the file names)
    '''
    if len(old_names) != len(new_names):
        raise ValueError("old_names and new_names must have the same length")

    for old_name, new_name in zip(old_names, new_names):
        old_path = pathlib.Path(old_name)
        new_path = pathlib.Path(new_name)

        # Add a number suffix if the target file already exists
        counter = 1
        temp_path = new_path
        while new_path.exists() and new_path.name != old_path.name:
            new_path = new_path.with_name(f"{temp_path.stem}_{counter}{temp_path.suffix}")
            counter += 1
        try:
            os.rename(old_path, new_path)
        except:
            print(f"Error renaming {old_path} to {new_path}")

if __name__ == "__main__":
    start_time = time.time()

    # Get the arguments
    parser = argparse.ArgumentParser(description="Rename files in a folder using AI")
    parser.add_argument("folder", help="Folder containing the files to rename")
    args = parser.parse_args()

    print(">> Generating names for files in", args.folder, "...")

    # Get the list of files in the folder
    folder = pathlib.Path(args.folder)
    files = [f for f in folder.iterdir() if f.is_file()]

    # Generate new names using using AI
    new_names = generate_names(files)
    for file, new_name in zip(files, new_names):
        print(f"{Fore.RED}{file.name}{Style.RESET_ALL} -> {Fore.GREEN}{pathlib.Path(new_name).name}{Style.RESET_ALL}")

    # Rename the files
    print(">> Renaming files in", args.folder, "...")
    rename_files(files, new_names)
    print(">> Done in", f"({time.time() - start_time} seconds)")