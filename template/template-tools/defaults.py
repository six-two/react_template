#!/usr/bin/env python3

# ================== i18n.py =====================
# It invokes a list of default plugins. Specific plugins can be enabled / disabled with specific flags
# This should make it simple to add new backwards compatible plugins to projects, without touching their config files.
# Hook type: pre_build (since it may need to execute pre_build plugins and it needs to modify the config file)
# Configuration:
#  Call it with no arguments, to just use the defaults.
#  En-/Disable plugins by passing --<plugin_name> or --no-"plugin_name" (eg --i18n or --no-i18n) options

# Debugging tip: make the final pre build command print the config (like this:)
# pre_build:
# - template-tools/defaults.py <PROJECT>
# - cat react-template.yaml


import os
from typing import Callable, List, Tuple
import sys
import subprocess
# External libs
# pip install pyyaml
import yaml

CODEC = "utf-8"
PRE_BUILD = "PRE_BUILD"
POST_BUILD = "POST_BUILD"

# A list of all supported plugins
PLUGINS = {
    # The plugin name, used in the CLI flags
    "i18n": {
        # When the plugin should get executed
        "stage": PRE_BUILD,
        # The command that should be run
        "cmd": "template-tools/i18n/i18n.py <PROJECT>",
        # Whether it is enabled by default
        "enabled": True,
    },
    "minify": {
        "stage": POST_BUILD,
        "cmd": "template-tools/minify.py",
        "enabled": True,
    },
}


def modify_yaml_file(yaml_path: str, fn: Callable[[dict], dict]):
    # read
    text = read_file(yaml_path)
    data = yaml.safe_load(text)
    # modify
    data = fn(data)
    # write
    text = yaml.safe_dump(data)
    write_file(yaml_path, text)


def write_file(path: str, content: str):
    try:
        os.makedirs(os.path.dirname(path))
    except Exception:
        pass

    with open(path, "wb") as f:
        f.write(content.encode(CODEC))


def read_file(path: str) -> str:
    with open(path, "rb") as f:
        return f.read().decode(CODEC)


def parse_command_line_arguments() -> Tuple[str, dict]:
    if len(sys.argv) < 2:
        print(f" Usage error ".center(80, "!"))
        print(f"Usage: {sys.argv[0]} <project_dir>")
        sys.exit(1)
    project_dir = sys.argv[1]

    remaining_options = [x for x in sys.argv[2:]]
    plugin_status = {}
    for [name, data] in PLUGINS.items():
        plugin_status[name] = {
            "enabled": data["enabled"] or False,
            "args": "",
        }

    while remaining_options:
        option, remaining_options = remaining_options[0], remaining_options[1:]
        if not option.startswith("--"):
            raise Exception(
                f"Unsupported option '{open}', expected it to start with '--'")

        arg_str = ""
        while remaining_options and not remaining_options[0].startswith("--"):
            arg_str += f" {remaining_options[0]}"
            remaining_options = remaining_options[1:]

        if option.startswith("--no-"):
            plugin_name = option[len("--no-"):]
            plugin_status[plugin_name] = {
                "enabled": False,
                "args": arg_str,
            }
        else:
            plugin_name = option[len("--"):]
            plugin_status[plugin_name] = {
                "enabled": True,
                "args": arg_str,
            }

    return project_dir, plugin_status


def append_to_list_in_dict(the_dict: dict, dict_key: str, list_to_append: List):
    original_list = the_dict.get(dict_key, [])
    the_dict[dict_key] = original_list + list_to_append


if __name__ == "__main__":
    project_dir, plugin_status_map = parse_command_line_arguments()
    pre_build_commands = []
    post_build_commands = []

    for [plugin_name, plugin_status] in plugin_status_map.items():
        if plugin_status["enabled"]:
            print(f"Plugin {plugin_name}: enabled")
            plugin_data = PLUGINS[plugin_name]
            stage = plugin_data["stage"]
            cmd = plugin_data["cmd"] + plugin_status["args"]

            if stage == PRE_BUILD:
                # Run it now, since we are currently in th pre build stage
                pre_build_commands.append(cmd)
                # @SYNC from: ../src/pre_build.py fn=run_commands
                command = str(cmd).replace("<PROJECT>", project_dir)
                print(f" Executing: {command} ".center(80, "="))
                subprocess.call(command, shell=True)
            elif stage == POST_BUILD:
                # Store this plugin so that we can inject it into the config later
                post_build_commands.append(cmd)
            else:
                raise Exception(f"Invalid stage: '{stage}'")
        else:
            print(f"Plugin {plugin_name}: disabled")

    def inject_post_build_commands(config: dict):
        append_to_list_in_dict(config, "post_build", post_build_commands)
        # Not really needed, but nice for debugging
        append_to_list_in_dict(config, "pre_build", pre_build_commands)
        return config

    if post_build_commands:
        print(
            f"Injecting {len(post_build_commands)} post build command(s) into the config")
        modify_yaml_file("react-template.yaml", inject_post_build_commands)
