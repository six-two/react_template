import shutil
import os
import sys
from typing import NamedTuple, List
# External library
import yaml


# Constants that may be used in multiple places
CODEC = "utf-8"
BUILD_DIR = "/tmp/react-template"
CONFIG_FILE_NAME = "react-template.yaml"
VERBOSE = True


# Debugging switches
DONT_WRITE_FILES = False


class Settings(NamedTuple):
    project_dir: str
    template_dir: str


def log(msg: str):
    if VERBOSE:
        print(msg)


def rm_folder(path):
    try:
        shutil.rmtree(path)
    except:
        pass


def empty_folder(path):
    rm_folder(path)
    os.makedirs(path)


def mk_parent_dir(path):
    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass


def my_copy(src, dst):
    mk_parent_dir(dst)
    shutil.copy(src, dst)


def removePathPrefix(path, prefixToRemove):
    # remove prefix
    path = path[len(prefixToRemove):]
    # remove leading slashes
    while os.path.isabs(path):
        path = path[1:]
    return path


def replace_file_contents(path, fn):
    # read
    fileBytes = readFileBytes(path)
    fileAsString = fileBytes.decode(CODEC)
    # modify
    fileAsString = str(fn(fileAsString))
    # write
    fileBytes = fileAsString.encode(CODEC)
    writeFileBytes(path, fileBytes)


def writeFileBytes(path, content):
    # create the parent folder if it did not exist
    if (DONT_WRITE_FILES):
        print("Write prevented: '{}'".format(path))
        return

    mk_parent_dir(path)

    with open(path, "wb") as f:
        f.write(content)


def readFileBytes(path):
    with open(path, "rb") as f:
        fileBytes = f.read()
    return fileBytes


def confirm_or_exit():
    choice = input("Do you want to continue? [y/N]\n")
    if not choice.lower().startswith("y"):
        print("Aborted")
        sys.exit(0)


def parse_yaml_file(path):
    yamlText = readFileBytes(path).decode(CODEC)
    return yaml.safe_load(yamlText)


def list_files(dir_path: str) -> List[str]:
    file_list: List[str] = []
    for root, _dirs, files in os.walk(dir_path):
        for name in files:
            file_path = os.path.join(root, name)
            file_list.append(file_path)
    return file_list
