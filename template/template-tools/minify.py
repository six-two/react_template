#!/usr/bin/env python3

# ================== i18n.py =====================
# Minifies HTML files (and in the future maybe css and js too).
# Hook type: post_build
# Configuration: You need to do nothing :)

import os
# External dependencies
import htmlmin

CODEC = "utf-8"


def replace_file_contents(path, fn):
    # read
    with open(path, "rb") as f:
        file_contents = f.read().decode(CODEC)
    # modify
    file_contents = str(fn(file_contents))
    # write
    with open(path, "wb") as f:
        f.write(file_contents.encode(CODEC))


def minify_html(file_contents):
            return htmlmin.minify(file_contents,
                                  remove_comments=True,
                                  remove_empty_space=True) + "\n"

def process_file(file_path):
    if file_path.endswith(".htm") or file_path.endswith(".html"):
        # Minify the html file
        print(f"Minifying {file_path}")

        replace_file_contents(file_path, minify_html)

def process_recursive(dir_path: str):
    for root, _dirs, files in os.walk(dir_path):
        for name in files:
            file_path = os.path.join(root, name)
            process_file(file_path)                

if __name__ == "__main__":
    process_recursive(".")