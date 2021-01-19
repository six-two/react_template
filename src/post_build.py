# pylint: disable=wildcard-import, unused-wildcard-import
from utils import *
from pre_build import run_commands, remove_cache_files
import os

POST_BUILD_COMMANDS = "post_build"


def post_build(settings: Settings):
    # remove the template tools
    tool_folder = os.path.join(BUILD_DIR, "template-tools")
    rm_folder(tool_folder)

    # Remove the config we copied over in pre_build, but keep it in memory
    config_path = os.path.join(BUILD_DIR, CONFIG_FILE_NAME)
    config = parse_yaml_file(config_path)
    os.remove(config_path)

    # Remove all SASS files (no longer needed, since they were compiled to CSS)
    for file_path in list_files(BUILD_DIR):
        if file_path.endswith(".scss") or file_path.endswith(".sass"):
            os.remove(file_path)

    # Run the command from the config file (if specified)
    build_commands = config.get(POST_BUILD_COMMANDS)

    if build_commands:
        run_commands(settings.project_dir, build_commands)

    # Final clean up
    remove_cache_files(BUILD_DIR)

