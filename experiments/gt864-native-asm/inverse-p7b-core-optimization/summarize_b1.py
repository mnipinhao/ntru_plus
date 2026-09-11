#!/usr/bin/env python3
"""Summarize balanced paired P7-B1 Pi 5 measurements."""

from collections import defaultdict
from pathlib import Path
import csv
import glob
import json
import statistics


P = Path(__file__).resolve().parent
COUNTERS = ("cycles", "instructions", "branches")
CAMPAIGNS = {
    "baseline_to_scheduled": "p7b1-r[01]-*.csv",
    "baseline_to_raw": "p7b1-raw-r[01]-*.csv",
    "raw_to_scheduled": "p7b1-sched-r[01]-*.csv",
}


def summarize(pattern: str) -> dict:
    paths = sorted(glob.glob(str(P / "build/pi5" / pattern)))
    assert paths, pattern
    absolute = defaultdict(list)
    paired = defaultdict(list)
    correctness = []
    for name in paths:
        rows = defaultdict(list)
        with open(name, newline="") as handle:
            first = handle.readline().strip()
            assert first == "correctness=pass valid=24 tampered=24 inverse_exact=256 alias=256"
            correctness.append(first)
            for row in csv.reader(handle):
                kind, boundary, variant, *values = row
                values = tuple(map(float, values))
                rows[kind, boundary, variant].append(values)
                for counter, value in zip(COUNTERS, values):
                    absolute[kind, boundary, variant, counter].append(value)
        for kind, boundary, variant in list(rows):
            if variant != "p3a":
                continue
            a = rows[kind, boundary, "p3a"]
            b = rows[kind, boundary, "p3b"]
            assert len(a) == len(b)
            for av, bv in zip(a, b):
                for index, counter in enumerate(COUNTERS):
                    paired[kind, boundary, counter].append(bv[index] - av[index])

    result = {"files": len(paths), "correctness_runs": len(correctness), "boundaries": {}}
    for kind, boundary in (("component", "inverse"), ("full", "keygen"),
                           ("full", "encaps"), ("full", "decaps")):
        key = f"{kind}:{boundary}"
        result["boundaries"][key] = {"absolute_median": {}, "paired_delta_b_minus_a": {}}
        for counter in COUNTERS:
            av = absolute[kind, boundary, "p3a", counter]
            bv = absolute[kind, boundary, "p3b", counter]
            delta = paired[kind, boundary, counter]
            result["boundaries"][key]["absolute_median"][counter] = {
                "a": statistics.median(av), "b": statistics.median(bv)
            }
            result["boundaries"][key]["paired_delta_b_minus_a"][counter] = {
                "samples": len(delta),
                "median": statistics.median(delta),
                "mean": statistics.mean(delta),
                "q1": statistics.quantiles(delta, n=4)[0],
                "q3": statistics.quantiles(delta, n=4)[2],
            }
    return result


report = {
    "date": "2026-09-11",
    "host": "pi@100.99.191.9",
    "core": 3,
    "governor": "ondemand",
    "temperature_c": [57.6, 59.3],
    "throttled": "0x0",
    "baseline_revision": "ffee627b",
    "kat_sha256": "0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c",
    "baseline_inverse9_object_bytes": 1220,
    "candidate_inverse9_object_bytes": 1140,
    "candidate": {
        "static_instruction_saving_per_inverse9": 20,
        "static_instruction_saving_per_complete_inverse": 240,
        "slothy_expected_cycles_per_inverse9": 71,
        "spill": 0,
        "new_memory_boundary": 0,
        "tested_scheduled_source_sha256": "70187de309907e157fce6c69083f51397359562f5647a1d1a06c32437e50c04a",
        "production_clean_source_sha256": "29be0511f5908964bb79720385c092c54bebefcbb82a08961599735e9c46180a",
        "tested_object_sha256": "b88e0408e3144cba29031e2e06a25fd51b89ea15bc5fc8f344c8beeab201373f",
    },
    "campaigns": {name: summarize(pattern) for name, pattern in CAMPAIGNS.items()},
}
(P / "p7b1-results.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
