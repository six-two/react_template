#!/usr/bin/env python3
import sys
import os
import yaml
from liquid import Liquid
import shutil

# Overwrite files, which might result in changes made by the user being lost
OVERWRITE_OPTION = "--force"
# Before executing the changes, print a summary and ask the user for confirmation
ASK_OPTION = "--ask"
# The dir to temporarily store the processed template files in
TMP_DIR = "/tmp/react_template"

class TemplateBuilder:
    def __init__(self, reactFolder, ask, overwrite):
        self.tmpFolder = TMP_DIR
        self.reactFolder = reactFolder
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.templateFolder = os.path.join(scriptDir, "template")
        self.ask = ask
        self.overwrite = overwrite

    def run(self):
        # TODO test if react folder exists

        # clean the tmp folder
        shutil.rmtree(self.tmpFolder)
        os.makedirs(self.tmpFolder)

        if self.overwrite:
            print("You are using the '{}' option, which might result in data loss")
            print("Backup or commit your code before executing this action!");
            print("Do you really want to force overwrites on all existing files? [yes/NO]")
            a = input();
            if not a.toLower().startsWith("y"):
                print("Aborted")
                return

        print("TODO implement!")
        # step one: process all files into a tmp directory
        self.processTemplateFiles()
        # step 2: compare files in tmp dir and react dir
        changes = self.getChangedFileList()
        # step 3: replace files that have changed
        self.replaceFiles(changes)

    def processTemplateFiles(self):
        yamlPath = os.path.join(self.reactFolder, "react-template.yaml")
        with open(yamlPath, "r") as f:
            yamlData = yaml.safe_load(f.read())

        print(yamlData)

        pass

    def processFile(self, relPath, yamlData):
        inputFile = os.path.join(self.templateFolder, relPath)
        outputFile = os.path.join(self.tmpFolder, relPath)
        liq = Liquid(path, liquid_from_file=True)
        ret = liq.render(site=yamlData)
        print(ret)
        with open(outputFile, "w") as f:
            f.write(ret)

    def getChangedFileList(self):#returns [(relPath, change)]
        pass

    def replaceFiles(self, changedFileList):
        if self.ask:
            self.confirmChanges(changes)
        pass

    def confirmChanges(self, changedFileList):
        pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {} <react_project_folder> [{}] [{}]".format(sys.argv[0], ASK_OPTION, OVERWRITE_OPTION))
        sys.exit(1);

    reactFolder = sys.argv[1]
    ask = ASK_OPTION in sys.argv
    overwrite = OVERWRITE_OPTION in sys.argv

    TemplateBuilder(reactFolder, ask, overwrite).run()
