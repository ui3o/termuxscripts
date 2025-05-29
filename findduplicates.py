#!/bin/env python3

import os
from datetime import datetime, timedelta
import re
import subprocess

HOME_PATH = "/data/data/com.termux/files/home/"
STORAGE_PATH = HOME_PATH+"storage/"
CONFIG_SCAN_PATH = "dcim/Camera"


CMD_PHONE = 0
CMD_TEST = 1
CMD_BOTH = 2
CMD_NONE = 3

processId = None
allSize = 0.0
timestamps = []

inp = input(f"Path to scan({CONFIG_SCAN_PATH}):")
if len(inp.strip()):
    CONFIG_SCAN_PATH = inp.strip()


allCompressableCounter = 0
compressableCounter = 0
compressableFilePath = []
allTimeStartAt = ""
allTimeStopAt = ""
allTimeDuration = ""

sizeOfOriginals = 0
sizeOfCompressed = 0


def extract_filePath(filePath: str) -> str:
    match = re.search(r'.*/(.+)', filePath, re.MULTILINE)
    if match:
        return match.group(1).strip()
    else:
        return ""


def contineRun():
    yes = input('Contine?(Y/n)')
    if len(yes) == 0 or yes == "y":
        print("Let's continue...")
    else:
        exit(1)


def run(cmd_type=False, *popenargs, **kwargs):
    global processId
    isTest = os.environ.get('CODESPACE_VSCODE_FOLDER')
    if cmd_type == CMD_PHONE and isTest is None:
        processId = subprocess.run(*popenargs, **kwargs)
    if cmd_type == CMD_TEST and isTest is not None:
        processId = subprocess.run(*popenargs, **kwargs)
    if cmd_type == CMD_BOTH:
        processId = subprocess.run(*popenargs, **kwargs)


run(CMD_TEST, ["cat", f"{CONFIG_SCAN_PATH}/duplicate.log"],
    capture_output=True, text=True)
run(CMD_PHONE, ["find", STORAGE_PATH+CONFIG_SCAN_PATH, "-size", "+1M", "-type",
    "f", "-name", "*.mp4", "-exec", "ls", "-l", "{}", ";"], capture_output=True, text=True)
out = str(processId.stdout).split("\n")
files = list(map(lambda x: extract_filePath(x).replace(".mp4", ""), out))

for x in files:
    for y in files:
        if len(y) and len(x) and x != y and x in y:
            print(f"duplicate found: {x},{y}")

contineRun()
