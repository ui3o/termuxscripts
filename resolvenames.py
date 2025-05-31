#!/bin/env python3

import os
from datetime import datetime, timedelta
import re
import subprocess

HOME_PATH = "/data/data/com.termux/files/home/"
STORAGE_PATH = HOME_PATH+"storage/"
CONFIG_SCAN_PATH = "dcim/Camera"

isTest = os.environ.get('CODESPACE')
if isTest is not None:
    CONFIG_SCAN_PATH = "tests"

# ffmpeg -i ~/storage/dcim/Camera/20250530_020912.mp4 -map_metadata 0 -vcodec libx264 -crf 28 -preset fast -acodec aac -b:a 128k  -metadata "Encoded_Hardware_Name"="Galaxy S24" -metadata "Encoded_Hardware_CompanyName"="..::" -movflags use_metadata_tags -c copy ~/storage/dcim/Camera/20250530_020912.mod.mp4

CONFIG_MAX_COMPRESSABLE_COUNT = 20
CONFIG_DELETE_ORIGINAL_FILE = "n"

CMD_PHONE = 0
CMD_TEST = 1
CMD_BOTH = 2
CMD_NONE = 3

processId = None
nonReplacable = []

compressableCounter = 0

try:
    count = int(input(f"How many video({CONFIG_MAX_COMPRESSABLE_COUNT})?:"))
    CONFIG_MAX_COMPRESSABLE_COUNT = count
except ValueError:
    pass


def extract_date(exif_output: str) -> str:
    match = re.search(r'^Create Date\s+:\s+(.+)', exif_output, re.MULTILINE)
    if match:
        return match.group(1).strip()
    else:
        return ""


def repleceVideo(videoPath: str, outPath: str, model: str, counter):
    expanded_path = os.path.expanduser(videoPath)
    dir = os.path.dirname(expanded_path).replace(HOME_PATH, "~/")
    print(f"----------")
    print(f"replece start: ({counter}/{CONFIG_MAX_COMPRESSABLE_COUNT})")
    print(f"  dir: {dir}")
    print(f"  src: {videoPath.replace(STORAGE_PATH+CONFIG_SCAN_PATH+'/', "")}")
    print(f"  dest: {outPath.replace(STORAGE_PATH+CONFIG_SCAN_PATH+'/', "")}")
    run(CMD_PHONE, [
        "bash", "-c", f"exiftool {filePath}"], capture_output=True, text=True)
    run(CMD_TEST, ["bash", "-c", f"cat {CONFIG_SCAN_PATH}/duration.log"],
        capture_output=True, text=True)
    print(f"  exiftool[code]: {colorize_returncode()}")
    out = str(processId.stdout)
    createDate = extract_date(out)
    print(f"  create date: {createDate}")
    run(CMD_PHONE, ["ffmpeg", "-i", videoPath, "-map_metadata", "0", "-metadata", f"Encoded_Hardware_Name={model}", "-metadata", "Encoded_Hardware_CompanyName=..::", "-movflags", "use_metadata_tags", "-c", "copy",  outPath],
        capture_output=True, text=True)
    run(CMD_TEST, ["ls", "-l"],
        capture_output=True, text=True)
    print(f"  ffmpeg[code]: {colorize_returncode()}")
    if processId.returncode == 0:
        run(CMD_PHONE, ["exiftool", "-TagsFromFile", videoPath, "-createdate",  createDate, "-gps*", "-samsung*",
            "-author", "-overwrite_original", outPath], capture_output=True, text=True)
        print(f"  exiftool[code]: {colorize_returncode()}")
        run(CMD_PHONE, ["rm", "-f", videoPath], capture_output=True, text=True)
        print(f"  rm[code]: {colorize_returncode()}")


def colorize_returncode(code: int):
    if processId.returncode == 0:
        return f"\033[32m{processId.returncode}\033[0m"
    return f"\033[31m{processId.returncode}\033[0m\n{processId.stdout}"


def contineRun():
    yes = input('Contine?(Y/n)')
    if len(yes) == 0 or yes == "y":
        print("Let's continue...")
    else:
        exit(1)


def run(cmd_type=False, *popenargs, **kwargs):
    global processId
    isTest = os.environ.get('CODESPACE')
    if cmd_type == CMD_PHONE and isTest is None:
        processId = subprocess.run(*popenargs, **kwargs)
    if cmd_type == CMD_TEST and isTest is not None:
        processId = subprocess.run(*popenargs, **kwargs)
    if cmd_type == CMD_BOTH:
        processId = subprocess.run(*popenargs, **kwargs)


run(CMD_TEST, ["cat", f"{CONFIG_SCAN_PATH}/log.log"],
    capture_output=True, text=True)
run(CMD_PHONE, ["find", STORAGE_PATH+CONFIG_SCAN_PATH, "-size", "+1M", "-type",
    "f", "-name", "*.mp4", "-exec", "ls", "-l", "{}", ";"], capture_output=True, text=True)
out = str(processId.stdout).split("\n")
# print(out)
for x in out:
    if x.__len__:
        l = x.split(" ")
        if len(l) > 1:
            filePath = l[-1]
            sizeStr = l[4]
            shortFilePathToPrint = f" >> {filePath.replace(STORAGE_PATH, "~/s/")}"
            sizeNum = int(sizeStr)
            if compressableCounter < CONFIG_MAX_COMPRESSABLE_COUNT:
                compressableCounter += 1
                if x.endswith("_Galaxy_S23_.mp4") is True:
                    repleceVideo(filePath, filePath.replace(
                        "_Galaxy_S23_.mp4", ".mp4"), "Galaxy S23", compressableCounter)
                elif x.endswith("__.mp4") is True:
                    repleceVideo(filePath, filePath.replace(
                        "__.mp4", ".mp4"), "none", compressableCounter)
            if x.endswith("_Galaxy_S23_.mp4") is False and x.endswith("__.mp4") is False:
                nonReplacable.append(shortFilePathToPrint)

print(f"----------")

for p in nonReplacable:
    print(f"\033[33m[unresolved]\033[0m {p}")

contineRun()
print(f"trigger termux-media-scan")
run(CMD_PHONE, ["termux-media-scan", STORAGE_PATH+CONFIG_SCAN_PATH])
contineRun()
