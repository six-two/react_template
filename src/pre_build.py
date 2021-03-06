# pylint: disable=wildcard-import, unused-wildcard-import
from utils import *
from typing import List
import os
import subprocess
from pathlib import Path

PRE_BUILD_COMMANDS = "pre_build"


def pre_build(settings: Settings):
    # Delete the build dir and make sure its parent exists
    empty_folder(BUILD_DIR)
    rm_folder(BUILD_DIR)

    # Copy the template to the build dir
    shutil.copytree(settings.template_dir, BUILD_DIR)

    # Copy the config file, so that it can be modified by (pre)build scripts
    src = os.path.join(settings.project_dir, CONFIG_FILE_NAME)
    config_path = os.path.join(BUILD_DIR, CONFIG_FILE_NAME)
    my_copy(src, config_path)

    # Clean up a bit
    remove_cache_files(BUILD_DIR)

    # Run the pre_build commands (if they are specified in the config file)
    config = parse_yaml_file(config_path)
    build_commands = config.get(PRE_BUILD_COMMANDS)

    if build_commands:
        run_commands(settings.project_dir, build_commands)

    

def run_commands(project_dir: str, commands: List[str]):
    # Change into the template directory
    old_cwd = os.getcwd()
    os.chdir(BUILD_DIR)

    # Run the build commands in the copy
    absolute_project_dir = os.path.join(old_cwd, project_dir)
    for command in commands:
        # @SYNC to: ../template-tools/defaults.py
        command = str(command).replace("<PROJECT>", absolute_project_dir)
        print(f" Executing: {command} ".center(80, "="))
        subprocess.call(command, shell=True)

    # Change back to the old working dir
    os.chdir(old_cwd)

def remove_cache_files(root_dir: str):
    for path in Path(root_dir).rglob('.mypy_cache'):
        log(f"Removing cache folder: {path}")
        rm_folder(str(path))
    for path in Path(root_dir).rglob('__pycache__'):
        log(f"Removing cache folder: {path}")
        rm_folder(str(path))