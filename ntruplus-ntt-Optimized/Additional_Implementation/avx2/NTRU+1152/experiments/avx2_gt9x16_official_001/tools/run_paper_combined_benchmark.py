#!/usr/bin/env python3
"""Run fresh pinned F-R3C Official-vs-paper combined-transform launches."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--launches", type=int, default=9)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--range", dest="range_path", type=Path, required=True)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--cflags", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    grouped = defaultdict(list)
    documents = []
    for _launch in range(1, args.launches + 1):
        result = subprocess.run(
            ["taskset", "-c", str(args.cpu), str(args.binary.resolve())],
            check=True, text=True, stdout=subprocess.PIPE)
        document = json.loads(result.stdout)
        documents.append(document)
        launch_groups = defaultdict(list)
        for record in document["records"]:
            if record["comparison"] == "sink":
                continue
            launch_groups[(record["comparison"], record["implementation"])].append(
                record["median_cycles"])
        for key, values in launch_groups.items():
            grouped[key].append(statistics.median(values))

    names = {
        "R2-cached": ("isolated-components", "R2-cached"),
        "adjusted-NTT16": ("isolated-components", "adjusted-NTT16"),
        "Official-T3x3+T2x4": ("transform-body", "Official-T3x3+T2x4"),
        "R2+adjusted-NTT16": ("transform-body", "R2+adjusted-NTT16"),
    }
    summary = {}
    for name, key in names.items():
        values = grouped[key]
        summary[name] = {
            "cycles_by_launch": values,
            "median_cycles": statistics.median(values),
            "minimum": min(values),
            "maximum": max(values),
        }
    r2 = summary["R2-cached"]["median_cycles"]
    adjusted = summary["adjusted-NTT16"]["median_cycles"]
    official = summary["Official-T3x3+T2x4"]["median_cycles"]
    combined = summary["R2+adjusted-NTT16"]["median_cycles"]
    isolated_sum = r2 + adjusted
    body_deltas = [candidate - baseline for baseline, candidate in zip(
        grouped[names["Official-T3x3+T2x4"]],
        grouped[names["R2+adjusted-NTT16"]])]
    if combined < 726:
        classification = "green"
    elif combined <= 740:
        classification = "near-parity"
    else:
        classification = "behind"
    audit = json.loads(args.audit.read_text())
    functions = audit["functions"]
    report = {
        "benchmark_class": "repository-local-f-r3c-combined-paired-not-for-promotion",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": args.cpu,
        "cpu_model": next((line.split(":", 1)[1].strip()
                           for line in Path("/proc/cpuinfo").read_text().splitlines()
                           if line.lower().startswith("model name")), "unknown"),
        "hostname": platform.node(),
        "kernel": platform.release(),
        "compiler": args.compiler,
        "cflags": args.cflags,
        "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
        "launches": args.launches,
        "blocks_per_launch": documents[0]["blocks"],
        "observations_per_slot": documents[0]["observations_per_slot"],
        "ntt9_instances_per_observation": documents[0]["ntt9_instances_per_observation"],
        "summary": summary,
        "derived": {
            "sum_of_isolated_medians": isolated_sum,
            "actual_combined_cycles": combined,
            "integration_delta_cycles": combined - isolated_sum,
            "adjusted_ntt16_budget_cycles": 452,
            "adjusted_ntt16_minus_budget_cycles": adjusted - 452,
            "official_pinned_isolated_sum_cycles": 726,
            "combined_minus_pinned_726_cycles": combined - 726,
            "measured_official_body_cycles": official,
            "combined_minus_measured_official_body_cycles": combined - official,
            "paired_body_delta_by_launch": body_deltas,
            "median_paired_body_delta_cycles": statistics.median(body_deltas),
            "gate_classification": classification,
        },
        "static": {
            "R2-cached": functions["ntruplus1152_exp001_gt9x16_ntt9_r2_cached"],
            "adjusted-NTT16": functions["ntruplus1152_exp001_gt9x16_paper_adjusted_ntt16"],
            "combined": functions["ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body"],
        },
        "range_proof": json.loads(args.range_path.read_text()),
        "upstream": json.loads((args.upstream / "UPSTREAM.json").read_text()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
