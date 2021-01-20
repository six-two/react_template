import shutil
import os
import sys
from typing import NamedTuple, List, Callable
# External library
import yaml


# Constants that may be used in multiple places
CODEC = "utf-8"
BUILD_DIR = "/tmp/react-template"
CONFIG_FILE_NAME = "react-template.yaml"
VERBOSE = True


class Settings(NamedTuple):
    project_dir: str
    template_dir: str


def log(msg: str):
    if VERBOSE:
        print(msg)


def rm_folder(path: str):
    try:
        shutil.rmtree(path)
    except:
        pass


def empty_folder(path: str):
    rm_folder(path)
    os.makedirs(path)


def mk_parent_dir(path: str):
    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass


def my_copy(src: str, dst: str):
    mk_parent_dir(dst)
    shutil.copy(src, dst)


def remove_path_prefix(path: str, prefix_to_remove: str) -> str:
    # remove prefix
    path = path[len(prefix_to_remove):]
    # remove leading slashes
    while os.path.isabs(path):
        path = path[1:]
    return path


def replace_file_contents(path: str, fn: Callable[[str], str]):
    # read
    with open(path, "rb") as f:
        file_contents = f.read().decode(CODEC)
    # modify
    file_contents = str(fn(file_contents))
    # write
    with open(path, "wb") as f:
        f.write(file_contents.encode(CODEC))


def write_file_bytes(path: str, content: bytes):
    # create the parent folder if it did not exist
    mk_parent_dir(path)

    with open(path, "wb") as f:
        f.write(content)


def read_file_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def confirm_or_exit():
    choice = input("Do you want to continue? [y/N]\n")
    if not choice.lower().startswith("y"):
        print("Aborted")
        sys.exit(0)


def parse_yaml_file(path: str):
    yamlText = read_file_bytes(path).decode(CODEC)
    return yaml.safe_load(yamlText)


def list_files(dir_path: str) -> List[str]:
    file_list: List[str] = []
    for root, _dirs, files in os.walk(dir_path):
        for name in files:
            file_path = os.path.join(root, name)
            file_list.append(file_path)
    return file_list
