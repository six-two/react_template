#!/usr/bin/env python3
import sys
import os
import yaml
from liquid import Liquid
import shutil
from munch import munchify, DefaultMunch

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
LIQUID_FILE_EXTENSION = ".liquid"
CODEC = "utf-8"
# Debugging switches
DONT_WRITE_FILES = False
CONFIRM_FORCE_OPTION = False

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
        self.templateFolder = os.path.join(SCRIPT_DIR, "template")
        self.ask = ask
        self.overwrite = overwrite

    def run(self):
        # TODO test if react folder exists

        # clean the tmp folder
        try:
            shutil.rmtree(self.tmpFolder)
        except:
            pass
        os.makedirs(self.tmpFolder)

        if self.overwrite and CONFIRM_FORCE_OPTION:
            print("You are using the '{}' option, which might result in data loss")
            print("Backup or commit your code before executing this action!");
            print("Do you really want to force overwrites on all existing files? [y/N]")
            a = input();
            if not a.lower().startswith("y"):
                print("Aborted")
                return

        # step one: process all files into a tmp directory
        yamlPath = os.path.join(self.reactFolder, "react-template.yaml")
        Preprocessor(yamlPath).processFolder(self.templateFolder, self.tmpFolder)
        # step 2: compare files in tmp dir and react dir
        changes = self.getChangedFileList()
        # step 3: replace files that have changed
        self.replaceFiles(changes)

    def getChangedFileList(self):
        changes = FolderCompare.compareFolders(self.tmpFolder, self.reactFolder)

        statusList = [FolderCompare.ADD]
        if self.overwrite:
            statusList.append(FolderCompare.CHANGED)

        filteredChanges = FolderCompare.filterByStatus(changes, statusList)
        return filteredChanges

    def replaceFiles(self, changedFileList):
        if self.ask:
            self.confirmChanges(changedFileList)

        for relPath in changedFileList:
            inputFile = os.path.join(self.tmpFolder, relPath)
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


class FolderCompare:
    SAME = "SAME"
    ADD = "ADD"
    CHANGED = "OVERWRITE"

    @staticmethod
    def filterByStatus(changedFileList, allowedStatusList):
        filtered = {}
        for relPath, status in changedFileList.items():
            if status in allowedStatusList:
                filtered[relPath] = status
        return filtered

    @staticmethod
    def compareFolders(sourceFolder, destFolder):
        diff = {}
        for root, dirs, files in os.walk(sourceFolder):
           for name in files:
              sourceFile = os.path.join(root, name)
              relPath = removePathPrefix(sourceFile, sourceFolder)
              destFile = os.path.join(destFolder, relPath)

              status = FolderCompare.compareFileContents(sourceFile, destFile)
              diff[relPath] = status
        return diff

    @staticmethod
    def compareFileContents(sourceFile, destFile):
        if not os.path.exists(destFile):
            return FolderCompare.ADD

        sourceBytes = readFileBytes(sourceFile)
        destBytes = readFileBytes(destFile)
        if sourceBytes == destBytes:
            return FolderCompare.SAME
        else:
            return FolderCompare.CHANGED


class Preprocessor:
    def __init__(self, yamlPath):
        yamlText = readFileBytes(yamlPath).decode(CODEC)
        # use munchify so that keys can be accessed using the dot notation
        self.yamlData = DefaultMunch.fromDict(munchify(yaml.safe_load(yamlText)), "")

    def processFolder(self, inputFolder, outputFolder):
        for root, dirs, files in os.walk(inputFolder):
           for name in files:
              inputFile = os.path.join(root, name)
              relPath = removePathPrefix(inputFile, inputFolder)
              outputFile = os.path.join(outputFolder, relPath)
              self.processFile(inputFile, outputFile)

    def processFile(self, inputFile, outputFile):
        fileBytes = readFileBytes(inputFile)

        if inputFile.endswith(LIQUID_FILE_EXTENSION):
            print("Processing '{}'".format(inputFile))
            # remove liquid extension
            outputFile = outputFile[:-len(LIQUID_FILE_EXTENSION)]
            # process with liquid
            fileAsString = fileBytes.decode(CODEC)
            processedString = Liquid(fileAsString).render(site=self.yamlData)
            fileBytes = processedString.encode(CODEC)

        writeFileBytes(outputFile, fileBytes)


def removePathPrefix(path, prefixToRemove):
    # remove prefix
    path = path[len(prefixToRemove):]
    # remove leading slashes
    while os.path.isabs(path):
        path = path[1:]
    return path


def writeFileBytes(path, content):
    # create the parent folder if it did not exist
    if (DONT_WRITE_FILES):
        print("Write prevented: '{}'".format(path))
        return

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
        print("Usage: {} <react_project_folder> [{}] [{}]".format(sys.argv[0], ASK_OPTION, OVERWRITE_OPTION))
        sys.exit(1);

    reactFolder = sys.argv[1]
    ask = ASK_OPTION in sys.argv
    overwrite = OVERWRITE_OPTION in sys.argv

    TemplateBuilder(reactFolder, ask, overwrite).run()
