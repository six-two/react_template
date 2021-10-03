#!/usr/bin/env python3

import argparse
import subprocess
import os
import sys
from typing import List

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIRM_ACTIONS = True
CONFIG_FILE_NAME = "react-template.yaml"

def search_for_configs(path: str) -> List[str]:
    project_dirs = []
    for root, _dirs, files in os.walk(path):
        if CONFIG_FILE_NAME in files:
            # If the folder contains a config file, it is one of the projects
            if os.path.realpath(root) != os.path.realpath(SCRIPT_DIR):
                # Do not interpret this as one of the projects
                project_dirs.append(root)
    return project_dirs

def cd(path = ""):
    os.chdir(SCRIPT_DIR) # to allow relative paths
    if path:
        os.chdir(path)


def is_git_repo_clean() -> bool:
    gitStatusOutput = subprocess.check_output(["git", "status"])
    CLEAN_STRING = b"\nnothing to commit, working tree clean\n"
    return CLEAN_STRING in gitStatusOutput


def ask_user_to_confirm(message: str) -> bool:
    if CONFIRM_ACTIONS:
        print("Next step:", message)
        return not input(" >> Continue? [Y/n] << ").lower().startswith("n")
    else:
        return True

def exec(*args):
    print("[Command]", " ".join(args))
    subprocess.call(args)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("project_search_root", help="this folder and its subfolders will be searched")
    ap.add_argument("-c", "--commit-message", help="commit the changes with the following message")
    ap.add_argument("-f", "--force", action="store_true", help="force update, even if the git working tree not clean")
    args = ap.parse_args()

    search_root_dir = args.project_search_root
    commit_message = sys.argv[2]

    print(f"[INFO] Searching for projects in '{search_root_dir}'")
    project_folders = search_for_configs(search_root_dir)
    if project_folders:
        for project_dir in project_folders:
            print(f"[INFO] Found project folder: '{project_dir}'")

        for repo in project_folders:
            cd(repo)
            is_clean = is_git_repo_clean()
            if is_clean or args.force:
                if not is_clean:
                    print("[WARN] Your working tree is not clean. Please chommit your changes before running this")
                if ask_user_to_confirm(f"Updating '{repo}'"):
                    cd()
                    exec("src/main.py", repo)

                    cd(repo)
                    if is_git_repo_clean():
                        print("[INFO] No files were changed")
                    else:
                        exec("git", "status")
                        if args.commit_message and ask_user_to_confirm("Commit and push the changes"):
                            exec("git", "add", ".")
                            exec("git", "commit", "-m", commit_message)
                            exec("git", "push")
            else:
                ask_user_to_confirm(f"[WARN] Skipping '{repo}'. Reason: Working tree not clean")
    else:
        print("[WARN] Found no project folders")
