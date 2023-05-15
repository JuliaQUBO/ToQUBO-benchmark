import sys
import platform
import json
import re
import datetime as dt
import uuid
import subprocess
import cpuinfo
from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent
DATA_PATH = ROOT_PATH.joinpath("data")

def python_version():
    return f"{platform.python_implementation()} version {platform.python_version()}"

def julia_version(julia_exe: str):
    proc = subprocess.run(
        args = [julia_exe, "--version"],
        text = True,
        stdout = subprocess.PIPE,
        stderr = subprocess.DEVNULL,
    )

    m = re.match(r"julia version ([0-9]+\.[0-9]+\.[0-9]+)", proc.stdout)

    return str(m.group(0))

def main():
    JULIA_EXE = sys.argv[1]

    path = DATA_PATH.joinpath("report.json")
    data = {}

    # Indentify Report
    data["id"] = str(uuid.uuid4())

    # Track start time
    data["time"] = str(dt.datetime.now())

    # Collect system info
    data["os"]      = platform.platform()
    data["python"]  = python_version()
    data["julia"]   = julia_version(JULIA_EXE)
    data["cpuinfo"] = cpuinfo.get_cpu_info()

    with open(path, "w") as fp:
        json.dump(data, fp, indent=2)

    return None

if __name__ == '__main__':
    main()