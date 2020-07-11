#!/usr/bin/env python3

import subprocess
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
REPOS = ["../react_payload_builder", "../react_did_someone_touch_this", "../react_fake_kali_login", "../react_redirect"]
CONFIRM_ACTIONS = True

def cd(path = ""):
    os.chdir(SCRIPT_DIR) # to allow relative paths
    if path:
        os.chdir(path)


def isGitRepoClean():
    gitStatusOutput = subprocess.check_output(["git", "status"])
    CLEAN_STRING = b"\nnothing to commit, working tree clean\n";
    return CLEAN_STRING in gitStatusOutput


def letUserConfirm(message):
    if CONFIRM_ACTIONS:
        print("Next step: " + message)
        return not input(" >> Continue? [Y/n] << ").lower().startswith("n")
    else:
        return True

def exec(*args):
    print("[Command]", " ".join(args))
    subprocess.call(args)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[USAGE] <commitMessage>")
        sys.exit(1)

    commitMessage = sys.argv[1]
    for repo in REPOS:
        cd(repo)
        if isGitRepoClean():
            if letUserConfirm("Updating '{}'".format(repo)):
                cd()
                exec("./main.py", repo, "--force")

                cd(repo)
                exec("git", "status")
                if letUserConfirm("Deploy the app"):
                    exec("./run.sh", "deploy")
                if letUserConfirm("Commit and push the changes"):
                    exec("git", "add", ".")
                    exec("git", "commit", "-m", commitMessage)
                    exec("git", "push")
        else:
            letUserConfirm("[WARN] Skipping '{}'. Reason: Working tree not clean".format(repo))
