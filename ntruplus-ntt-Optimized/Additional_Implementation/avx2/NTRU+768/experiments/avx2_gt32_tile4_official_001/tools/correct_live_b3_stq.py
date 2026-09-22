#!/usr/bin/env python3
"""Recompute historical reports without replacing raw data or legacy summaries."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from run_encap_live_b3_short import stq

ROOT = Path(__file__).resolve().parent.parent

def main():
    for suffix in ("a", "b"):
        root = ROOT / "results" / ("encap-live-b3-q24-short-20260922-" + suffix)
        groups = defaultdict(list)
        per_launch = defaultdict(list)
        raw_hashes = {}
        for launch in range(3):
            path = root / f"launch-{launch}.csv"
            raw_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
            for row in csv.DictReader(path.open()):
                key = (int(row["region"]), int(row["variant"]))
                groups[key].append(int(row["cycles"]))
                per_launch[(launch, *key)].append(int(row["cycles"]))
        regions = json.loads((root / "metadata.json").read_text())["regions"]
        report = {"estimator": "SUPERCOP-20260831-stq.h",
                  "supersedes": "summary.json (incorrect quartile-slice estimator)",
                  "raw_sha256": raw_hashes, "regions": {}}
        for region, name in enumerate(regions):
            control, candidate = (stq(groups[region, v]) for v in (0, 1))
            delta = [stq(per_launch[k, region, 1])[1] -
                     stq(per_launch[k, region, 0])[1] for k in range(3)]
            report["regions"][name] = dict(control_stq=control, candidate_stq=candidate,
                delta_stq2=candidate[1]-control[1], launch_deltas=delta,
                favorable_launches=sum(x < 0 for x in delta))
        (root / "summary-corrected-stq.json").write_text(json.dumps(report, indent=2)+"\n")
        print(json.dumps(report))

if __name__ == "__main__":
    main()
