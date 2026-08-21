#!/usr/bin/env python3
"""Re-run the exact D-B oracle proofs and reject stale generated evidence."""

import subprocess
from pathlib import Path

experiment = Path(__file__).resolve().parents[1]
subprocess.run([
    "python3", str(experiment / "tools/generate_ntt9_first_oracle.py"),
    "--component-oracle", str(experiment / "generated/gt9x16-component-oracle.json"),
    "--output", str(experiment / "generated/gt9x16-ntt9-first-oracle.json"),
    "--check",
], check=True)
print("D-B NTT9-first shear phase and adjusted-twiddle basis proofs passed")
