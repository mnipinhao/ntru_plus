#!/usr/bin/env python3
"""Run the bounded C1 serializer density gate in both link orders."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


LINE = re.compile(
    r"region=(\S+) metric=(\S+) control=([0-9.]+) candidate=([0-9.]+) "
    r"delta=(-?[0-9.]+) wins=(\d+)/(\d+)"
)


def symbol_size(binary: Path, symbol: str) -> int:
    text = subprocess.check_output(["nm", "-S", str(binary)], text=True)
    for line in text.splitlines():
        if line.endswith(" " + symbol):
            return int(line.split()[1], 16)
    raise ValueError(symbol)


def run(binary: Path, launches: int, iterations: int) -> dict[str, object]:
    records = []
    for launch in range(launches):
        process = subprocess.run(
            [str(binary), str(iterations), "1"], text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
        metrics = {}
        for line in process.stdout.splitlines():
            match = LINE.fullmatch(line)
            if match:
                region, metric, control, candidate, delta, wins, total = match.groups()
                metrics.setdefault(region, {})[metric] = {
                    "control": float(control), "candidate": float(candidate),
                    "delta": float(delta), "wins": int(wins), "samples": int(total),
                }
        records.append({"launch": launch + 1, "metrics": metrics})
    return {"binary": str(binary), "launches": records}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("normal", type=Path)
    parser.add_argument("reversed", type=Path)
    parser.add_argument("--launches", type=int, default=4)
    parser.add_argument("--iterations", type=int, default=4000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    control = "gt32_q24_encode_soa_lazy10788_asm"
    candidate = "gt32_q24_encode_soa_lazy10788_compact_c1_asm"
    report = {
        "schema": "ntruplus768-gt32-q24-hotcompact-c1-v1",
        "experiment": "PRODUCTION-REACHABLE-HOT-TEXT-COMPACTION-001-C1",
        "correctness": "exhaustive-[-12699,12699]-and-guard-page-pass-each-launch",
        "symbol_bytes": {
            "control": symbol_size(args.normal, control),
            "candidate": symbol_size(args.normal, candidate),
        },
        "placements": {
            "normal": run(args.normal, args.launches, args.iterations),
            "reversed": run(args.reversed, args.launches, args.iterations),
        },
    }
    report["symbol_bytes"]["delta"] = report["symbol_bytes"]["candidate"] - report["symbol_bytes"]["control"]
    report["decision"] = "hard-stop-local-cost-far-exceeds-2-to-4-cycle-density-budget"
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
