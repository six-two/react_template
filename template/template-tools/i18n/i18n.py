#!/usr/bin/env python3
# TODO
# Hook for pre_build (modifies config file)
# Read <project>/i18n.yaml, convert to json and inline into the i18n.js file
# copy modified js file to public folder
# Append script location to `customHtmlHead` in react-templaye.yaml

import json
import os
import sys
# External libs
# pip install pyyaml
import yaml

CODEC = "utf-8"
DATA_PATH = "i18n.yaml"
JS_OUTPUT_PATH = "public/i18n.js"
JS_INPUT_PATH = "template-tools/i18n/i18n_temlate.js"
CONFIG_PATH = "react-template.yaml"
CUSTOM_HTML_HEAD_FIELD = "customHtmlHead"


def create_i18n_js(project_dir):
    yaml_path = os.path.join(project_dir, DATA_PATH)
    data = parse_yaml_file(yaml_path)
    inject_data_into_js_file(data, JS_INPUT_PATH, JS_OUTPUT_PATH)


def inject_data_into_js_file(data, js_input_file, js_output_file):
    text = readFileBytes(js_input_file).decode(CODEC)
    text.replace("__I18N_JSON__", json.dumps(data))
    writeFileBytes(js_output_file, text.encode(CODEC))


def inject_script_url_into_config():
    yaml_path = os.path.join(project_dir, DATA_PATH)
    config = parse_yaml_file(yaml_path)
    custom_html_head = config.get(CUSTOM_HTML_HEAD_FIELD, "")
    custom_html_head += f'<script src="/{JS_OUTPUT_PATH}"></srcipt>'
    config[CUSTOM_HTML_HEAD_FIELD] = custom_html_head
    text = yaml.safe_dump(config)
    writeFileBytes(CONFIG_PATH, text.encode(CODEC))


def parse_yaml_file(yamlPath):
    yamlText = readFileBytes(yamlPath).decode(CODEC)
    return yaml.safe_load(yamlText)


def writeFileBytes(path, content):
    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass

    with open(path, "wb") as f:
        f.write(content)


def readFileBytes(path):
    with open(path, "rb") as f:
        fileBytes = f.read()
    return fileBytes


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <react_project_folder>")
        sys.exit(1)
    project_dir = sys.argv[1]
    print("Project dir:", project_dir)
    create_i18n_js(project_dir)
    inject_script_url_into_config()
