#!/usr/bin/env python3
# pylint: disable=wildcard-import, unused-wildcard-import
from utils import Settings
from pre_build import pre_build
from build import build
from post_build import post_build
from apply import apply_template
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def build_and_apply_template(settings: Settings):
    pre_build(settings)
    build(settings)
    post_build(settings)
    apply_template(settings)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <project_dir>")
        sys.exit(1)

    project_dir = sys.argv[1]
    template_dir = os.path.join(SCRIPT_DIR, "..", "template")
    settings = Settings(project_dir=project_dir, template_dir=template_dir)

    build_and_apply_template(settings)