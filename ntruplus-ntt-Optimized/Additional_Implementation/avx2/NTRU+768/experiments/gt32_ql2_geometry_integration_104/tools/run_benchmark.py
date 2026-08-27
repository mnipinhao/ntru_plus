#!/usr/bin/env python3
"""Run the formal fixed-ELF SUPERcop-style 104 qualification."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
RUNNER = ROOT / "experiments/gt32_compact_q24_037/tools/run_fixed_elf_campaign.py"


def main() -> None:
    destination = EXP / "results/formal"
    subprocess.run(["python3", str(RUNNER),
                    "--control", str(EXP / "build/measure-control"),
                    "--candidate", str(EXP / "build/measure-ql2"),
                    "--control-name", "b2a4bea geometry anchor + reserved QL2 tail",
                    "--candidate-name", "104 geometry-preserved QL2 Encap",
                    "--cpu", "1", "--blocks", "16", "--output", str(destination)],
                   check=True)
    summary = json.loads((destination / "manifest.json").read_text())["summary"]
    (EXP / "generated/benchmark-summary.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
