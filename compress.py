#!/bin/env python3

import os
from datetime import datetime, timedelta
import re
import subprocess

HOME_PATH = "/data/data/com.termux/files/home/"
STORAGE_PATH = HOME_PATH+"storage/"
CONFIG_SCAN_PATH = "dcim/Camera"
FFMPEG_ARGS = ["-map_metadata", "0", "-vcodec", "libx264", "-crf", "28", "-preset",
               "fast", "-acodec", "aac", "-b:a", "128k", "-movflags", "use_metadata_tags"]

CONFIG_MAX_COMPRESSABLE_COUNT = 20
CONFIG_REPLACE_FILE = "n"

CMD_PHONE = 0
CMD_TEST = 1
CMD_BOTH = 2
CMD_NONE = 3

processId = None
allSize = 0.0
timestamps = []

allCompressableCounter = 0
compressableCounter = 0
compressableFilePath = []

sizeOfOriginals = 0
sizeOfCompressed = 0

try:
    count = int(input('How many video?:'))
    CONFIG_MAX_COMPRESSABLE_COUNT = count
except ValueError:
    pass

CONFIG_REPLACE_FILE = input('Replace original?:')
CONFIG_SCAN_PATH = input('Path to scan:')


def replace_non_alphanumeric(text):
    return ''.join(char if char.isalnum() else '_' for char in text)


def extract_duration(exif_output: str) -> float:
    match = re.search(r'^Media Duration\s+:\s+(.+)', exif_output, re.MULTILINE)
    if match:
        return str(match.group(1)).strip()
    else:
        return "0:00:00"


def extract_author(exif_output: str) -> str:
    match = re.search(r'^Author\s+:\s+(.+)', exif_output, re.MULTILINE)
    if match:
        return replace_non_alphanumeric(match.group(1).strip())
    else:
        return ""


def parse_duration(duration_str):
    if 's' in duration_str:
        # Format: "18.52 s"
        seconds = float(duration_str.strip().replace('s', ''))
        return timedelta(seconds=seconds)
    else:
        # Format: "H:MM:SS" or "MM:SS"
        parts = list(map(int, duration_str.strip().split(':')))
        if len(parts) == 3:
            h, m, s = parts
        elif len(parts) == 2:
            h = 0
            m, s = parts
        else:
            raise ValueError("Invalid duration format")
        return timedelta(hours=h, minutes=m, seconds=s)


def human_readable_size(size_bytes):
    """
    Convert bytes into a human-readable string (e.g., '1.5K', '12M', '3.4G').
    """
    if size_bytes < 1024:
        return f"{size_bytes}B"

    units = ['K', 'M', 'G', 'T', 'P', 'E']
    size = size_bytes / 1024.0
    for unit in units:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}Z"  # In case the number is extremely large


def add_duration_to_now(duration_str):
    now = datetime.now()
    delta = parse_duration(duration_str)
    future_time = now + delta
    return future_time.strftime("%Y-%m-%d %H:%M:%S")


def contineRun():
    yes = input('Contine?(Y/n)')
    if len(yes) == 0 or yes == "y":
        print("Let's continue...")
    else:
        exit(1)


# List of timestamps to add
# timestamps = ["0:02:26", "29.31 s", "0:01:04", "15.5 s"]

# Convert various timestamp formats to timedelta
def parse_timestamp(ts):
    ts = ts.strip()
    if re.match(r"^\d+:\d+:\d+$", ts):  # Format: H:M:S
        h, m, s = map(int, ts.split(":"))
        return timedelta(hours=h, minutes=m, seconds=s)
    elif re.match(r"^\d+(\.\d+)?\s?s$", ts):  # Format: S.s s
        seconds = float(ts.replace("s", "").strip())
        return timedelta(seconds=seconds)
    else:
        raise ValueError(f"Unrecognized format: {ts}")


def run(cmd_type=False, *popenargs, **kwargs):
    global processId
    isTest = os.environ.get('CODESPACE_VSCODE_FOLDER')
    if cmd_type == CMD_PHONE and isTest is None:
        processId = subprocess.run(*popenargs, **kwargs)
    if cmd_type == CMD_TEST and isTest is not None:
        processId = subprocess.run(*popenargs, **kwargs)
    if cmd_type == CMD_BOTH:
        processId = subprocess.run(*popenargs, **kwargs)


def compressor(src_path: str, duration, model, size, counter):
    global sizeOfOriginals
    global sizeOfCompressed
    out = src_path.replace(".mp4", f"__{model}__.mp4")
    print(f"----------")
    print(f"compress start: ({counter}/{allCompressableCounter})")
    print(f"  src: {src_path.replace(HOME_PATH, "~/")}")
    print(f"  dest: {out.replace(HOME_PATH, "~/")}")
    print(f"  src size: {human_readable_size(int(size))}")
    print(f"  duration: {duration}")
    print(f"  start at: {add_duration_to_now("1 s")}")
    print(f"  stop at: {add_duration_to_now(duration)}")
    run(CMD_PHONE, ["ls", "-l", src_path], capture_output=True, text=True)
    print(f"  ls(src)[code]: {processId.returncode}")
    run(CMD_PHONE, ["ffmpeg", "-i", src_path, *FFMPEG_ARGS, out],
        capture_output=True, text=True)
    print(f"  ffmpeg[code]: {processId.returncode}")
    run(CMD_PHONE, ["exiftool", "-TagsFromFile", src_path, "-gps*", "-samsung*",
        "-author", "-overwrite_original", out], capture_output=True, text=True)
    print(f"  exiftool[code]: {processId.returncode}")
    run(CMD_PHONE, ["ls", "-l", out], capture_output=True, text=True)
    run(CMD_TEST, ["cat", f"{CONFIG_SCAN_PATH}/log.log"],
        capture_output=True, text=True)
    print(f"  ls(out)[code]: {processId.returncode}")
    compressedSizeNum = int(str(processId.stdout).split("\n")[0].split(" ")[4])
    print(f"  out size: {human_readable_size(compressedSizeNum)}")
    sizeOfOriginals += int(size)
    sizeOfCompressed += compressedSizeNum
    print(
        f"  compressed sizes: {human_readable_size(sizeOfCompressed)}/{human_readable_size(sizeOfOriginals)}")
    if CONFIG_REPLACE_FILE == "y":
        print(f"  replace: true")
        run(CMD_PHONE, ["mv", out, src_path], capture_output=True, text=True)
        print(f"  mv(out)[code]: {processId.returncode}")
    else:
        print(f"  replace: false")


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
            sizeNum = int(sizeStr)
            if x.endswith("__.mp4") is False:
                allCompressableCounter += 1
                if compressableCounter < CONFIG_MAX_COMPRESSABLE_COUNT:
                    compressableCounter += 1
                    allSize += sizeNum
                    run(CMD_PHONE, [
                        "bash", "-c", f"exiftool {filePath}"], capture_output=True, text=True)
                    run(CMD_TEST, ["bash", "-c", f"cat {CONFIG_SCAN_PATH}/duration.log"],
                        capture_output=True, text=True)
                    out = str(processId.stdout)
                    dur = extract_duration(out).split(": ")[-1].strip()
                    model = extract_author(out)
                    print(f"[ok] {sizeStr} [{dur}][{model}] {filePath}")
                    compressableFilePath.append(
                        f"{filePath},{dur},{model},{sizeStr}")
                    timestamps.append(dur)
                else:
                    print(f"[skip] {sizeStr} {filePath}")
            else:
                print(f"[ignore] {sizeStr} {filePath}")

# print(f"All video size is {allSize} and list is {compressableFilePath}, timestamps list is {timestamps}")
print(
    f"All video size is {human_readable_size(allSize)} [{compressableCounter}/{allCompressableCounter}]")
# Sum all the durations
total_time = sum((parse_timestamp(ts) for ts in timestamps), timedelta())
# Print the result
print("Total time:", str(total_time))
contineRun()

position = 0
for p in compressableFilePath:
    position += 1
    info = str(p).split(",")
    compressor(info[0], info[1], info[2], info[3], position)
print(f"----------")

contineRun()
print(f"trigger termux-media-scan")
run(CMD_PHONE, ["termux-media-scan", STORAGE_PATH+CONFIG_SCAN_PATH])
contineRun()
