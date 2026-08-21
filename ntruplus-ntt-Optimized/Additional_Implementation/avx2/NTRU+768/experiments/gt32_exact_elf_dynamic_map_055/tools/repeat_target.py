#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("binary", type=Path)
parser.add_argument("repetitions", type=int)
args = parser.parse_args()
for _ in range(args.repetitions):
    subprocess.run([str(args.binary.resolve())], stdout=subprocess.DEVNULL, check=True)

