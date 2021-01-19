#!/usr/bin/env python3
import sys
import os
import shutil
import subprocess
# External library
import yaml
from liquid import Liquid
from munch import munchify, DefaultMunch
# Local files
# pylint: disable=wildcard-import, unused-wildcard-import
from utils import *
import compare as FolderCompare

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PRE_BUILD_COMMANDS = "pre_build"
POST_BUILD_COMMANDS = "post_build"
LIQUID_FILE_EXTENSION = ".liquid"
# Debugging switches
CONFIRM_FORCE_OPTION = False

# Overwrite files, which might result in changes made by the user being lost
OVERWRITE_OPTION = "--force"
# Before executing the changes, print a summary and ask the user for confirmation
ASK_OPTION = "--ask"
# The dir to temporarily store the processed template files in
TMP_DIR_RUN_FIRST_OUTPUT = "/tmp/react_template_run_first_output"
TMP_DIR = "/tmp/react_template"
# Compress html files
COMPRESS_HTML = True

if COMPRESS_HTML:
    import htmlmin


class TemplateBuilder:
    def __init__(self, reactFolder, ask, overwrite):
        self.reactFolder = reactFolder
        self.ask = ask
        self.overwrite = overwrite

    def run(self):
        # TODO test if react folder exists

        empty_folder(TMP_DIR)

        if self.overwrite and CONFIRM_FORCE_OPTION:
            print("You are using the '{}' option, which might result in data loss")
            print("Backup or commit your code before executing this action!")
            print(
                "Do you really want to force overwrites on all existing files? [y/N]")
            a = input()
            if not a.lower().startswith("y"):
                print("Aborted")
                return

        # step 1: build the template
        templateFolder = os.path.join(SCRIPT_DIR, "template")
        # Run pre build commands
        templateFolder = run_pre_build_commands(
            templateFolder, self.reactFolder)
        # process template files
        Preprocessor(self.reactFolder).processFolder(templateFolder, TMP_DIR)
        # Run post build commands
        run_post_build_commands(TMP_DIR, self.reactFolder)

        # step 2: compare files in tmp dir and react dir
        changes = self.getChangedFileList()
        # step 3: replace files that have changed
        self.replaceFiles(changes)

    def getChangedFileList(self):
        changes = FolderCompare.compareFolders(TMP_DIR, self.reactFolder)

        statusList = [FolderCompare.ADD]
        if self.overwrite:
            statusList.append(FolderCompare.CHANGED)

        filteredChanges = FolderCompare.filterByStatus(changes, statusList)
        return filteredChanges

    def replaceFiles(self, changedFileList):
        if self.ask:
            self.confirmChanges(changedFileList)

        for relPath in changedFileList:
            inputFile = os.path.join(TMP_DIR, relPath)
            outputFile = os.path.join(self.reactFolder, relPath)
            data = readFileBytes(inputFile)
            writeFileBytes(outputFile, data)

    def confirmChanges(self, changedFileList):
        if changedFileList:
            print("The following changes will be made")
            for relPath, status in changedFileList.items():
                if status != FolderCompare.SAME:
                    if (self.overwrite or status != FolderCompare.CHANGED):
                        print(" '{}': {}".format(relPath, status))

            choice = input("Do you want to continue? [y/N]\n")
            if not choice.lower().startswith("y"):
                print("Aborted")
                sys.exit(0)
        else:
            print("No files will be changed")



def run_post_build_commands(template_dir, project_dir):
    config = parse_config_file(project_dir)
    build_commands = config.get(POST_BUILD_COMMANDS)

    if build_commands:
        run_commands(template_dir, project_dir, build_commands)


def parse_config_file(project_dir):
    yamlPath = os.path.join(project_dir, CONFIG_FILE_NAME)
    yamlText = readFileBytes(yamlPath).decode(CODEC)
    return yaml.safe_load(yamlText)


class Preprocessor:
    def __init__(self, project_dir):
        config = parse_config_file(project_dir)
        # use munchify so that keys can be accessed using the dot notation
        self.yamlData = DefaultMunch.fromDict(munchify(config), "")

    def processFolder(self, inputFolder, outputFolder):
        for root, _dirs, files in os.walk(inputFolder):
            for name in files:
                inputFile = os.path.join(root, name)
                relPath = removePathPrefix(inputFile, inputFolder)
                outputFile = os.path.join(outputFolder, relPath)
                self.processFile(inputFile, outputFile)

    def processFile(self, inputFile, outputFile):
        if inputFile.endswith(LIQUID_FILE_EXTENSION):
            print("Processing '{}'".format(inputFile))
            # remove liquid extension
            outputFile = outputFile[:-len(LIQUID_FILE_EXTENSION)]
            # Copy the file, should keep permissions
            my_copy(inputFile, outputFile)
            # process with liquid
            process_liquid = lambda file_contents: Liquid(file_contents).render(site=self.yamlData)
            replace_file_contents(outputFile, process_liquid)
        elif inputFile.endswith(".scss") or inputFile.endswith(".sass"):
            inputFolder, inputFileName = os.path.split(inputFile)
            if inputFileName.startswith("_"):
                print("Ignoring '{}'".format(inputFile))
                return  # do not process the file
            print("Processing '{}'".format(inputFile))
            outputFile = outputFile[:-5] + ".css"
            importFolder = inputFolder  # Maybe change this?
            subprocess.run(["sassc",
                            "--style", "compressed",
                            "--load-path", importFolder,
                            inputFile, outputFile
                            ])
            return
        else:
            # Copy the file, should keep permissions
            my_copy(inputFile, outputFile)

            # TODO what about css, js, etc
            if COMPRESS_HTML and (outputFile.endswith(".htm") or outputFile.endswith(".html")):
                # Minify
                minify_html = lambda file_contents: htmlmin.minify(file_contents,
                                                remove_comments=True, remove_empty_space=True) + "\n"
                replace_file_contents(outputFile, minify_html)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {} <react_project_folder> [{}] [{}]".format(
            sys.argv[0], ASK_OPTION, OVERWRITE_OPTION))
        sys.exit(1)

    reactFolder = sys.argv[1]
    ask = ASK_OPTION in sys.argv
    overwrite = OVERWRITE_OPTION in sys.argv

    TemplateBuilder(reactFolder, ask, overwrite).run()
