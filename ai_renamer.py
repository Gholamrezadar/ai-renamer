import os
import argparse
import pathlib

from colorama import Fore, Style, init
# This is needed on Windows for colorama to work
init()

def rename_files(old_names, new_names):
    '''Rename old_names to new_names
    Both lists must have the same length
    Both lists contain the full paths to the files (not just the file names)
    '''
    for old_name, new_name in zip(old_names, new_names):
        old_path = pathlib.Path(old_name)
        new_path = pathlib.Path(new_name)

        # Add a number suffix if the target file already exists
        counter = 1
        temp_path = new_path
        while new_path.exists() and new_path.name != old_path.name:
            new_path = new_path.with_name(f"{temp_path.stem}_{counter}{temp_path.suffix}")
            counter += 1

        os.rename(old_path, new_path)

def generate_name_based_on_content(file: pathlib.Path):
    '''Generate a name based on the content of the file using AI
    Returns None if the file is not text-based
    '''

    # try to read the file content
    content = ""
    try:
        with open(file, "r") as f:
            content = f.read()
    except:
        print(f"Could not read file {file}")
        return None
    
    # TODO: Generate a name based on the content
    return content[:10]

def get_ai_name(file: pathlib.Path):
    '''Returns the full path to the file with the new name'''
    parent_folder = file.parent
    extension = file.suffix
    name = file.stem

    # In case we can't generate a name, return the original name
    new_name = name

    # If the file is not text-based, returns None
    generated_name = generate_name_based_on_content(file)
    if generated_name is not None:
        new_name = generated_name

    return f"{parent_folder}/{new_name}{extension}"

if __name__ == "__main__":

    # Get the arguments
    parser = argparse.ArgumentParser(description="Rename files in a folder using AI")
    parser.add_argument("folder", help="Folder containing the files to rename")
    args = parser.parse_args()

    print(">> Generating names for files in", args.folder, "...")

    # Get the list of files in the folder
    folder = pathlib.Path(args.folder)
    files = [f for f in folder.iterdir() if f.is_file()]

    # Generate new names using using AI
    new_names = []
    for file in files:
        new_name = get_ai_name(file)
        new_names.append(new_name)
        print(f"{Fore.RED}{file.name}{Style.RESET_ALL} -> {Fore.GREEN}{new_name}{Style.RESET_ALL}")

    # Rename the files
    print(">> Renaming files in", args.folder, "...")
    rename_files(files, new_names)
    print(">> Done") 