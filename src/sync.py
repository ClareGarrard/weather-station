# Syncs code on raspberry pi with rp2 directory that is linked into repo
# With thanks to @Rollcloud

"""Implement `mpremote fs cp -r src/rp2/ :/` in Python until mpremote release-1.24.0 (https://github.com/micropython/micropython/milestone/7) is available."""

import subprocess
import sys
from pathlib import Path

import mpremote
import yaml

SOURCE = Path("src/rp2/")
DEST = Path(":")
DEFAULT_SEARCH = "*"

SETTINGS = Path("src/setup/sync.yaml")

settings = {}
if SETTINGS.exists():
    with SETTINGS.open("r") as f:
        settings = yaml.safe_load(f)


search = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SEARCH

if mpremote.__version__ >= "1.24.0":
    print(
        "mpremote release-1.24.0 or later is available. Use `mpremote fs cp -r src/rp2/ :/` instead."
    )
    exit(1)


def mpremote_fs_cp(source: Path, dest: Path):
    """Copy source to dest using mpremote fs cp."""
    if source.is_dir():
        if source.parent != SOURCE:
            # Create the parent directory of the source file
            print(f"Creating directory {dest.parent}")
            subprocess.run(f"mpremote fs mkdir {dest.parent}", shell=True)
    else:
        # print(f"Copying {source_file} to {dest_file}")
        subprocess.run(f"mpremote fs cp {source} {dest}", check=True, shell=True)
        if "files" not in settings:
            settings["files"] = {}
        settings["files"][source.as_posix()] = int(source.stat().st_mtime)


# Recursively iterate over all files in the source directory
for source_file in SOURCE.rglob(search):
    # Calculate the relative path of the source file
    relative_path = source_file.relative_to(SOURCE)
    # Calculate the destination path of the source file
    dest_file = DEST / relative_path

    # if file is newer, copy it
    source_modified = int(source_file.stat().st_mtime)
    dest_modified = settings.get("files", {}).get(source_file.as_posix(), 0)
    if source_modified > dest_modified:
        mpremote_fs_cp(source_file, dest_file)
    else:
        print(f"Skipping {source_file}")

with SETTINGS.open("w") as f:
    yaml.dump(settings, f)

print("Done.")
