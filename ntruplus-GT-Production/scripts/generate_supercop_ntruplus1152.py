#!/usr/bin/env python3
"""Generate or verify the checked-in NTRU+1152 SUPERCOP leaf."""

from pathlib import Path
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=("generate", "check"))
parser.add_argument("--source-root", type=Path, required=True)
parser.add_argument("--package-root", type=Path, required=True)
args = parser.parse_args()

script = args.source_root.resolve() / "scripts" / "export_supercop.py"
leaf = args.package_root.resolve() / "crypto_kem" / "ntruplus1152" / "aarch64"
command = ["python3", str(script), str(leaf)]
if args.mode == "check":
    command.append("--check")
subprocess.run(command, check=True)
