# pylint: disable=wildcard-import, unused-wildcard-import
from utils import *

SAME = "SAME"
ADD = "ADD"
CHANGED = "OVERWRITE"


def filterByStatus(changedFileList, allowedStatusList):
    filtered = {}
    for relPath, status in changedFileList.items():
        if status in allowedStatusList:
            filtered[relPath] = status
    return filtered


def compareFolders(sourceFolder, destFolder):
    diff = {}
    for root, _dirs, files in os.walk(sourceFolder):
        for name in files:
            sourceFile = os.path.join(root, name)
            relPath = removePathPrefix(sourceFile, sourceFolder)
            destFile = os.path.join(destFolder, relPath)

            status = compareFileContents(sourceFile, destFile)
            diff[relPath] = status
    return diff


def compareFileContents(sourceFile, destFile):
    if not os.path.exists(destFile):
        return ADD

    sourceBytes = readFileBytes(sourceFile)
    destBytes = readFileBytes(destFile)
    if sourceBytes == destBytes:
        return SAME
    else:
        return CHANGED
