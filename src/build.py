# pylint: disable=wildcard-import, unused-wildcard-import
from utils import *
import os
import subprocess
from typing import List, Any
# External libs
from liquid import Environment
from munch import munchify, DefaultMunch

LIQUID_FILE_EXTENSION = ".liquid"


def process_liquid(config, file_path: str) -> str:
    log(f"Rendering liquid file: {file_path}")

    # Remove liquid extension
    new_file_path = file_path[:-len(LIQUID_FILE_EXTENSION)]
    os.rename(file_path, new_file_path)

    # process with liquid
    def process_liquid_file_contents(file_contents):
        liquid_vars = {"site":config}
        liquid_env = Environment(globals=liquid_vars)
        bound_template = liquid_env.from_string(file_contents)
        return bound_template.render()

    replace_file_contents(new_file_path, process_liquid_file_contents)

    return new_file_path


def process_scss(config, file_path: str) -> str:
    file_dir, file_name = os.path.split(file_path)
    if file_name.startswith("_"):
        # This file will probably be included by another liquid file
        return ""  # do not process the file
    else:
        print(f"Compiling SASS file: {file_name}")
        # Change file extension to .css
        output_file_path = file_path[:-5] + ".css"
        import_folder = file_dir
        subprocess.run(["sassc",
                        "--style", "compressed",
                        "--load-path", import_folder,
                        file_path, output_file_path
                        ])
        return output_file_path


def process_file(config, file_path: str) -> str:
    if file_path.endswith(LIQUID_FILE_EXTENSION):
        return process_liquid(config, file_path)
    elif file_path.endswith(".scss") or file_path.endswith(".sass"):
        return process_scss(config, file_path)
    else:
        return ""


FILE_EXTENSION_PRIORITIES = [
    {
        "extensions": [".liquid"],
        "fn": process_liquid,
    },
    {
        "extensions": [".scss", ".sass"],
        "fn": process_scss,
    },
]


def process_files_by_prioritizing_extensions(config, dir_path: str):
    # Advantages: has easier to understand processing of files
    #             Enables complicated stuff like a.liquid.scss.liquid
    # Disadvantages: Harder to understand and debug code
    processed_files: List[str] = []
    while process_next_batch_of_files(config, dir_path, processed_files):
        pass


def process_next_batch_of_files(config, dir_path: str, processed_files: List[str]) -> bool:
    # Finds the first (ie hightest priority) processor that can process files and lets it run
    # Returns False it no more files can be processed
    files = list_files(dir_path)
    for processor in FILE_EXTENSION_PRIORITIES:
        extensions: Any = processor["extensions"]  # actually List[str]
        matching_files = get_files_with_matching_extensions(files, extensions)
        # Remove files that were already processed
        matching_files = [f for f in matching_files if f not in processed_files]
        if matching_files:
            print("Processing next batch:", matching_files)
            # Mark this batch of files as processed
            processed_files.extend(matching_files)
            # actually Callable[[type(config),str], str]
            process_files: Any = processor["fn"]
            for file_name in matching_files:
                process_files(config, file_name)
            return True
    return False


def get_files_with_matching_extensions(files: List[str], extension_list: List[str]) -> List[str]:
    matching_files = []
    for file_path in files:
        for extension in extension_list:
            if file_path.endswith(extension):
                matching_files.append(file_path)
    # Remove potential duplicates
    matching_files = list(set(matching_files))
    return matching_files


def build(settings: Settings):
    log("Loading config")
    config_path = os.path.join(BUILD_DIR, CONFIG_FILE_NAME)
    config = parse_yaml_file(config_path)
    # Make the fields accessible from liquid
    config = DefaultMunch.fromDict(munchify(config), "")
    log("Config file loaded")

    process_files_by_prioritizing_extensions(config, BUILD_DIR)
    # process_files_sequentially(config, ".")
    log("Build step done")


def process_files_sequentially(config, dir_path: str):
    # Advantage: simple
    # Disadvantage: files depending on other files being processed first are hard to handle
    files = list_files(dir_path)
    log(f"{len(files)} file(s) will be processed")
    for file_path in files:
        process_file_recursive(config, file_path)


def process_file_recursive(config, file_path: str):
    new_file_path = process_file(config, file_path)
    log(f"Processing file {file_path}")

    if new_file_path and new_file_path != file_path:
        process_file(config, new_file_path)
