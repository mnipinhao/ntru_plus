#!/usr/bin/env python3
"""Summarize P33 paired main-I16 and full-path PMU logs."""
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = []
for path in sorted((HERE / "pi-run").glob("main-*.csv")):
    process = int(path.stem.split("-")[-1])
    for row in csv.reader(path.read_text().splitlines()):
        if row and row[0] == "main_i16":
            rows.append((process, "main_i16", row[1], *map(float, row[2:5])))
for path in sorted((HERE / "pi-run").glob("full-*.csv")):
    process = int(path.stem.split("-")[-1])
    for row in csv.reader(path.read_text().splitlines()):
        if row and row[0] in {"full", "component"}:
            rows.append((process, row[1], row[2], *map(float, row[3:6])))


def quantile(values, p):
    values = sorted(values)
    position = (len(values) - 1) * p
    lo = int(position)
    hi = min(lo + 1, len(values) - 1)
    fraction = position - lo
    return values[lo] * (1 - fraction) + values[hi] * fraction


result = {"metric_order": ["cycles", "instructions", "branches"], "operations": {}}
for operation in ("main_i16", "inverse_to_ternary", "keygen", "encaps", "decaps"):
    by_process = defaultdict(lambda: defaultdict(list))
    for process, op, label, cycles, instructions, branches in rows:
        if op == operation:
            by_process[process][label].append((cycles, instructions, branches))
    pairs = []
    for process in sorted(by_process):
        baseline = by_process[process]["baseline"]
        candidate = by_process[process]["candidate"]
        assert len(baseline) == len(candidate)
        pairs += [tuple(c[i] - b[i] for i in range(3)) for b, c in zip(baseline, candidate)]
    flat = {
        label: [x[3:] for x in rows if x[1] == operation and x[2] == label]
        for label in ("baseline", "candidate")
    }
    summary = {"samples_per_side": len(flat["baseline"])}
    for label in ("baseline", "candidate"):
        summary[label] = dict(zip(
            result["metric_order"], map(statistics.median, zip(*flat[label]))
        ))
    summary["paired_delta_median"] = dict(zip(
        result["metric_order"], map(statistics.median, zip(*pairs))))
    cycle_deltas = [x[0] for x in pairs]
    summary["cycle_delta_iqr"] = [quantile(cycle_deltas, .25), quantile(cycle_deltas, .75)]
    summary["candidate_cycle_wins"] = sum(x < 0 for x in cycle_deltas)
    summary["baseline_ipc"] = summary["baseline"]["instructions"] / summary["baseline"]["cycles"]
    summary["candidate_ipc"] = summary["candidate"]["instructions"] / summary["candidate"]["cycles"]
    result["operations"][operation] = summary

inv = result["operations"]["inverse_to_ternary"]
dec = result["operations"]["decaps"]
result["status"] = "promote" if (
    inv["paired_delta_median"]["cycles"] < 0 and inv["cycle_delta_iqr"][1] < 0 and
    dec["paired_delta_median"]["cycles"] < 0 and dec["cycle_delta_iqr"][1] < 0
) else "reject"
result["environment"] = {
    "host": "pi@100.99.191.9", "core": 3,
    "kernel": "6.18.33+rpt-rpi-2712", "governor": "ondemand",
    "throttled": "0x0", "temperature_after": "57.6 C",
    "selected_official_root": "/home/pi/supercop-20260831",
}
result["artifact_sha256"] = {
    "production_libgt864_so": "7e71af800dbcf220977d0f6344bcf92542e279edf6d64ca66de2844d2125aff0",
    "p33_libgt864_so": "8a84e166a7639951db0e467b0c39c4ef7b254db3b8c3d732c05969566a5171ac",
    "p33_prefix_source": "f6164b2000ce2a861b5b9d964e40fd969c002bbe1a85832aa2aa2c7a993b0d1c",
    "p33_pair_source": "adc9f745239c02b8e9ff86ae2e04670edbd1b4a728744ad864f55720f402692b",
}
(HERE / "results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
