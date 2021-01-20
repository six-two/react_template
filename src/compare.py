# pylint: disable=wildcard-import, unused-wildcard-import
from utils import *
from typing import List

SAME = "SAME"
ADD = "ADD"
CHANGED = "OVERWRITE"


def filter_by_status(changedFileList: dict, allowedStatusList: List[str]) -> dict:
    filtered = {}
    for rel_path, status in changedFileList.items():
        if status in allowedStatusList:
            filtered[rel_path] = status
    return filtered


def compare_folders(src_dir: str, dst_dir: str) -> dict:
    diff = {}
    for root, _dirs, files in os.walk(src_dir):
        for name in files:
            src = os.path.join(root, name)
            rel_path = remove_path_prefix(src, src_dir)
            dst = os.path.join(dst_dir, rel_path)

            status = check_file_status(src, dst)
            diff[rel_path] = status
    return diff


def check_file_status(src: str, dst: str) -> str:
    if not os.path.exists(dst):
        return ADD

    src_bytes = read_file_bytes(src)
    dst_bytes = read_file_bytes(dst)
    if src_bytes == dst_bytes:
        return SAME
    else:
        return CHANGED
