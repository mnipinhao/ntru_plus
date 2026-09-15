#!/usr/bin/env python3
"""Summarize P32 paired PMU logs and emit the durable result ledger."""
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = []
for path in sorted((HERE / "pi-run").glob("paired-*.csv")):
    process = int(path.stem.split("-")[-1])
    for row in csv.reader(path.read_text().splitlines()):
        if row and row[0] in {"full", "component"}:
            rows.append((process, row[1], row[2], *map(float, row[3:6])))


def q(values, p):
    values = sorted(values)
    position = (len(values) - 1) * p
    lo = int(position)
    hi = min(lo + 1, len(values) - 1)
    frac = position - lo
    return values[lo] * (1 - frac) + values[hi] * frac


result = {"metric_order": ["cycles", "instructions", "branches"], "operations": {}}
for operation in ("inverse_to_ternary", "keygen", "encaps", "decaps"):
    by_process = defaultdict(lambda: defaultdict(list))
    for process, op, label, cycles, instructions, branches in rows:
        if op == operation:
            by_process[process][label].append((cycles, instructions, branches))
    pairs = []
    for process in sorted(by_process):
        baseline = by_process[process]["baseline"]
        candidate = by_process[process]["candidate"]
        assert len(baseline) == len(candidate)
        pairs += [(c[0]-b[0], c[1]-b[1], c[2]-b[2]) for b, c in zip(baseline, candidate)]
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
    summary["cycle_delta_iqr"] = [q(cycle_deltas, .25), q(cycle_deltas, .75)]
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
    "throttled": "0x0", "temperature_after": "58.2 C",
    "selected_official_root": "/home/pi/supercop-20260831",
}
result["artifact_sha256"] = {
    "production_libgt864_so": "7e71af800dbcf220977d0f6344bcf92542e279edf6d64ca66de2844d2125aff0",
    "p32_libgt864_so": "a153b23012ed2eb3579270964bafcde9c4c949f46ba1334781ce11216b5ee898",
    "p32_prefix_source": "f594d72a442efaebbe1e8ffb302af9cd254f6280374a38e07ad2019dbe896566",
    "p32_terminal_source": "d0caf97498063121403eacb7da6130c37362b12aac4ab09d56675ec912626059",
}
(HERE / "results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
