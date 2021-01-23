#!/usr/bin/env python3

# ================== i18n.py =====================
# It localizes website elements.
# Hook type: pre_build (modifies config file)
# Configuration:
#  Create a i18n.yaml file in your project root. Look at i18n.yaml and i18n.example.yaml
#  to get a feel for the structure.
#  Add the correct id to every element (via react-template.yaml)

import json
import os
import sys
import shutil
# External libs
# pip install pyyaml
import yaml

CODEC = "utf-8"
DATA_PATH = "i18n.yaml"
DATA_PLACEHOLDER = "__I18N_JSON__"
JS_OUTPUT_NAME = "i18n.js"
JS_INPUT_PATH = "template-tools/i18n/i18n_temlate.js"
CONFIG_PATH = "react-template.yaml"
CUSTOM_HTML_HEAD_FIELD = "customHtmlHead"
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
LANGUAGE_CHOOSER_DOM_FIELD = "language_chooser_dom"


def load_config(project_dir: str) -> dict:
    # Load the project data file (if it exists)
    try:
        project_data_path = os.path.join(project_dir, DATA_PATH)
        project_data = parse_yaml_file(project_data_path) or {}
    except Exception:
        project_data = {}

    # Check if the project should be merged with the defaults
    ignore_defaults = project_data.get("ignore_defaults", False)

    if ignore_defaults:
        # Just use the project data, ignore the defaults
        return project_data
    else:
        # Load the template data file (defaults)
        template_data_path = os.path.join(SCRIPT_DIR, DATA_PATH)
        template_data = parse_yaml_file(template_data_path)

        # Merge the two data files
        merged_data = template_data

        if project_data:
            # Merge the individual config items
            for [key, data] in project_data.items():
                if key == "ignore_defaults":
                    # Already processed
                    pass
                elif key == "languages":
                    # Overwrite language list
                    merged_data[key] = data
                elif key == "translations":
                    # Merge translations dict
                    translations = template_data.get(key, {})
                    translations.update(data)
                    template_data[key] = translations
                else:
                    raise Exception(f"Unsupported config key: '{key}'")

            text = yaml.safe_dump(merged_data)
            write_file_bytes(
                "template-tools/debug/i18n.merged.yaml", text.encode(CODEC))

        return merged_data


def create_i18n_js(i18n_config: dict, project_dir: str):
    translations = i18n_config.get("translations", {})

    # Inject the data into the file
    js_output_path = "public/"+JS_OUTPUT_NAME
    inject_data_into_js_file(translations, JS_INPUT_PATH, js_output_path)


def inject_data_into_js_file(data, js_input_file: str, js_output_file: str):
    text = read_file_bytes(js_input_file).decode(CODEC)
    # Sorting them forces them in a deterministic order. Same input -> same output
    json_string = json.dumps(data, sort_keys=True)
    new_text = text.replace(DATA_PLACEHOLDER, json_string)
    if new_text == text:
        raise Exception("JS input template has no placeholder for the data")
    write_file_bytes(js_output_file, new_text.encode(CODEC))


def inject_script_url_into_config(i18n_config: dict, project_dir: str):
    yaml_path = os.path.join(project_dir, CONFIG_PATH)
    config = parse_yaml_file(yaml_path)

    # Inject script tag to load i18n.js
    script_tag = f'<script src="%PUBLIC_URL%/{JS_OUTPUT_NAME}"></script>'
    custom_html_head = config.get(CUSTOM_HTML_HEAD_FIELD, "")
    custom_html_head += script_tag

    # Inject dom for language chooser

    languages = i18n_config.get("languages", [])
    if languages:
        lang_select = ""
        lang_select += '<select id="page-language-chooser">'
        lang_select += '<option selected disabled hidden>Select a language</option>'
        for lang_obj in languages:
            code = lang_obj["code"]
            title = lang_obj["title"]
            lang_select += f'<option value="{code}">{title}</option>'
        lang_select += "</select>"
        lang_select += '<label for="page-language-chooser"><div class="page-language-chooser-label">Test</div></label>'

        config[LANGUAGE_CHOOSER_DOM_FIELD] = lang_select

        # Append the css link or language selector
        custom_html_head += "<link rel=stylesheet href=%PUBLIC_URL%/i18n.css>"
        shutil.move("template-tools/i18n/i18n.scss", "public/i18n.scss")


    config[CUSTOM_HTML_HEAD_FIELD] = custom_html_head

    text = yaml.safe_dump(config)
    write_file_bytes(CONFIG_PATH, text.encode(CODEC))


def parse_yaml_file(yamlPath: str):
    yamlText = read_file_bytes(yamlPath).decode(CODEC)
    return yaml.safe_load(yamlText)


def write_file_bytes(path: str, content: bytes):
    try:
        os.makedirs(os.path.dirname(path))
    except Exception:
        pass

    with open(path, "wb") as f:
        f.write(content)


def read_file_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <react_project_folder>")
        sys.exit(1)
    project_dir = sys.argv[1]
    print("Project dir:", project_dir)
    i18n_config = load_config(project_dir)

    # Do the important parts here
    create_i18n_js(i18n_config, project_dir)
    inject_script_url_into_config(i18n_config, project_dir)


if __name__ == "__main__":
    main()
