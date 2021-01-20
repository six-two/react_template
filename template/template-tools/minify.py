#!/usr/bin/env python3

# ================== i18n.py =====================
# Minifies HTML, CSS, and JS files
# Hook type: post_build
# Configuration: You need to do nothing :)

import os
from typing import Callable
# External dependencies
import htmlmin
import rcssmin
import rjsmin

CODEC = "utf-8"


def replace_file_contents(path: str, fn: Callable[[str], str]):
    # read
    with open(path, "rb") as f:
        file_contents = f.read().decode(CODEC)
    # modify
    file_contents = str(fn(file_contents))
    # write
    with open(path, "wb") as f:
        f.write(file_contents.encode(CODEC))


def minify_html(file_contents: str) -> str:
    return htmlmin.minify(file_contents,
                          remove_comments=True,
                          remove_empty_space=True) + "\n"


def minify_css(file_contents: str) -> str:
    return rcssmin.cssmin(file_contents)


def minify_js(file_contents: str) -> str:
    return rjsmin.jsmin(file_contents)


def process_file(file_path: str):
    if file_path.endswith(".htm") or file_path.endswith(".html"):
        print(f"Minifying {file_path}")
        replace_file_contents(file_path, minify_html)
    elif file_path.endswith(".css"):
        print(f"Minifying {file_path}")
        replace_file_contents(file_path, minify_css)
    elif file_path.endswith(".js"):
        print(f"Minifying {file_path}")
        replace_file_contents(file_path, minify_js)


def process_recursive(dir_path: str):
    for root, _dirs, files in os.walk(dir_path):
        for name in files:
            file_path = os.path.join(root, name)
            process_file(file_path)


if __name__ == "__main__":
    process_recursive(".")
