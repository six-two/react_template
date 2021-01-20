# pylint: disable=wildcard-import, unused-wildcard-import
from utils import *
import compare as FolderCompare
from typing import List


ASK = True


def apply_template(settings: Settings):
    changed_files = get_changed_files(settings)
    if ASK:
        confirm_changes(changed_files)

    print("Applying the changes...")
    for rel_path in changed_files:
        src = os.path.join(BUILD_DIR, rel_path)
        dst = os.path.join(settings.project_dir, rel_path)
        my_copy(src, dst)


def get_changed_files(settings: Settings) -> dict:
    changes = FolderCompare.compare_folders(BUILD_DIR, settings.project_dir)
    statusList = [FolderCompare.ADD, FolderCompare.CHANGED]
    return FolderCompare.filter_by_status(changes, statusList)


def confirm_changes(changed_files: dict):
    if changed_files:
        print("The following changes will be made")
        for relPath, status in changed_files.items():
            if status != FolderCompare.SAME:
                print(" '{}': {}".format(relPath, status))

        confirm_or_exit()
    else:
        print("No files will be changed")
