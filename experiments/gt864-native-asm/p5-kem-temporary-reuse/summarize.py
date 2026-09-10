#!/usr/bin/env python3
import csv
import glob
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parent
rows = defaultdict(list)
correctness = 0
for filename in glob.glob(str(P / "pi-results/paired-*.csv")):
    with open(filename, newline="") as stream:
        for row in csv.reader(stream):
            if row and row[0] == "correctness=pass valid_kem_exact=24":
                correctness += 1
            elif row and row[0] == "full":
                rows[(row[1], row[2])].append(tuple(map(float, row[3:])))

summary = {}
for operation in ("keygen", "encaps", "decaps"):
    summary[operation] = {}
    for implementation in ("p4", "p5"):
        values = rows[(operation, implementation)]
        summary[operation][implementation] = {
            metric: statistics.median(value[index] for value in values)
            for index, metric in enumerate(("cycles", "instructions", "branches"))
        }
    summary[operation]["delta"] = {
        metric: summary[operation]["p5"][metric] - summary[operation]["p4"][metric]
        for metric in ("cycles", "instructions", "branches")
    }
    summary[operation]["cycle_delta_percent"] = 100 * (
        summary[operation]["p5"]["cycles"] /
        summary[operation]["p4"]["cycles"] - 1
    )

malformed = (P / "pi-results/malformed-candidate.txt").read_bytes()
result = {
    "experiment": "gt864-p5-kem-temporary-reuse",
    "baseline": "GT864 production P4 at 60b74b05",
    "candidate": "P5 KEM lifetime reuse",
    "correctness_repetitions": correctness,
    "stack_frames_bytes": {
        "keygen": {"p4": 10720, "p5": 8992, "delta": -1728},
        "encaps_helper": {"p4": 8704, "p5": 7392, "delta": -1312},
        "decaps": {"p4": 16288, "p5": 11072, "delta": -5216},
    },
    "kat_sha256": "0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c",
    "malformed_transcript_sha256": hashlib.sha256(malformed).hexdigest(),
    "rejection_cases": 13824,
    "summary": summary,
    "environment": {
        "host": "pi@100.99.191.9",
        "kernel": "Linux 6.18.33+rpt-rpi-2712 aarch64",
        "compiler": "gcc 14.2.0",
        "core": 3,
        "governor": "ondemand",
        "temperature_after": "59.8'C",
        "supercop_reference_root": "/home/pi/supercop-20260831",
    },
}
(P / "pi-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
