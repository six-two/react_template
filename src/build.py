# pylint: disable=wildcard-import, unused-wildcard-import
from utils import *
import os
import subprocess
from typing import List
# External libs
from liquid import Liquid
from munch import munchify, DefaultMunch

LIQUID_FILE_EXTENSION = ".liquid"
COMPRESS_HTML = True

if COMPRESS_HTML:
    # External lib
    import htmlmin


def build(settings: Settings):
    config_path = os.path.join(BUILD_DIR, CONFIG_FILE_NAME)
    config = parse_yaml_file(config_path)
    # Make the fields accessible from liquid
    config = DefaultMunch.fromDict(munchify(config), "")

    # Scan all files, then process them.
    # This prevents processing a file, that was created by processing another file
    for file_path in list_files(BUILD_DIR):
        process_file(config, file_path)


def process_file(config, file_path: str):
    if file_path.endswith(LIQUID_FILE_EXTENSION):
        # Compile liquid files

        # Remove liquid extension
        new_file_path = file_path[:-len(LIQUID_FILE_EXTENSION)]
        os.rename(file_path, new_file_path)

        # process with liquid
        def process_liquid(file_contents): return Liquid(
            file_contents).render(site=config)
        replace_file_contents(file_path, process_liquid)
    elif file_path.endswith(".scss") or file_path.endswith(".sass"):
        # Compile SASS files

        file_dir, file_name = os.path.split(file_path)
        if file_name.startswith("_"):
            # This file will probably be included by another liquid file
            return  # do not process the file
            # TODO remove all sass files in post_build
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
            return
    elif COMPRESS_HTML and (file_path.endswith(".htm") or file_path.endswith(".html")):
        # Minify the html file
        def minify_html(file_contents):
            return htmlmin.minify(file_contents,
                                  remove_comments=True,
                                  remove_empty_space=True) + "\n"
        replace_file_contents(file_path, minify_html)

    else:
        # Keep all other files as they are
        pass
