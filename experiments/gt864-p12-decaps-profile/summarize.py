#!/usr/bin/env python3
"""Summarize the raw clean and call-site profile observations."""

from __future__ import annotations

import csv
import json
import pathlib
import statistics


ROOT = pathlib.Path(__file__).resolve().parent
RAW = ROOT / "raw"
BUILD = ROOT / "build"
OPERATIONS = ("keygen", "encaps", "decaps")
IMPLEMENTATIONS = ("official", "gt")


def distribution(values: list[float]) -> dict[str, float | int]:
    ordered = sorted(values)
    return {
        "n": len(values),
        "median": statistics.median(values),
        "p25": ordered[len(ordered) // 4],
        "p75": ordered[(3 * len(ordered)) // 4],
        "min": ordered[0],
        "max": ordered[-1],
    }


def main() -> None:
    clean: list[tuple[str, str, float, float, float]] = []
    correctness: list[str] = []
    for path in sorted(RAW.glob("clean-*.csv")):
        for line in path.read_text().splitlines():
            if line.startswith("correctness="):
                correctness.append(line)
                continue
            row = next(csv.reader([line]))
            if row and row[0] == "clean":
                clean.append((row[1], row[2], float(row[3]), float(row[4]), float(row[5])))
    if len(correctness) != 6 or any(x != "correctness=pass exact=100 tampered=100" for x in correctness):
        raise RuntimeError(f"clean correctness records are incomplete: {correctness}")

    clean_summary: dict[str, object] = {}
    for operation in OPERATIONS:
        clean_summary[operation] = {}
        for implementation in IMPLEMENTATIONS:
            values = [row[2:] for row in clean if row[:2] == (operation, implementation)]
            if len(values) != 252:
                raise RuntimeError(f"expected 252 clean rows for {operation}/{implementation}, got {len(values)}")
            clean_summary[operation][implementation] = {
                metric: distribution([row[index] for row in values])
                for index, metric in enumerate(("cycles", "instructions", "branches"))
            }
        official = clean_summary[operation]["official"]["cycles"]["median"]
        gt = clean_summary[operation]["gt"]["cycles"]["median"]
        clean_summary[operation]["gt_cycle_delta"] = gt - official
        clean_summary[operation]["gt_cycle_delta_percent"] = 100.0 * (gt / official - 1.0)

    profiles: list[tuple[str, str, str, float, float, float]] = []
    equivalence: list[str] = []
    for path in sorted(RAW.glob("profile-*.csv")):
        for line in path.read_text().splitlines():
            if line.startswith("instrumentation_equivalence="):
                equivalence.append(line)
                continue
            row = next(csv.reader([line]))
            if row and row[0] == "profile":
                profiles.append((row[1], row[2], row[3], float(row[4]), float(row[5]), float(row[6])))
    if len(equivalence) != 12 or any("pass" not in x for x in equivalence):
        raise RuntimeError(f"profile equivalence records are incomplete: {equivalence}")

    profile_summary: dict[str, object] = {}
    for operation in OPERATIONS:
        profile_summary[operation] = {}
        groups = sorted({row[2] for row in profiles if row[0] == operation})
        for implementation in IMPLEMENTATIONS:
            profile_summary[operation][implementation] = {}
            for group in groups:
                rows = [row[3:] for row in profiles if row[:3] == (operation, implementation, group)]
                if not rows:
                    continue
                if len(rows) != 126:
                    raise RuntimeError(f"expected 126 profile rows for {operation}/{implementation}/{group}, got {len(rows)}")
                profile_summary[operation][implementation][group] = {
                    "raw_cycles": distribution([row[0] for row in rows]),
                    "net_cycles": distribution([row[1] for row in rows]),
                    "calls": distribution([row[2] for row in rows]),
                }

    environment = json.loads((BUILD / "environment.json").read_text())
    result = {
        "experiment": "GT864-P12-DECAPS-PROFILE-20260912",
        "correctness": {
            "fresh_gt_test_kem": "pass",
            "fresh_gt_kat": "pass",
            "cross_implementation_processes": 6,
            "exact_transcripts_per_process": 100,
            "tampered_ciphertexts_per_process": 100,
            "instrumentation_equivalence_processes": 12,
        },
        "environment": environment,
        "clean_full_kem": clean_summary,
        "call_site_profile": profile_summary,
        "interpretation_note": "Clean full-KEM PMU values are authoritative. Call-site profile values subtract the measured perf read-pair cost per call and are diagnostic; instrumentation changes execution and component medians are not assumed to add exactly to clean totals.",
    }
    (ROOT / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
