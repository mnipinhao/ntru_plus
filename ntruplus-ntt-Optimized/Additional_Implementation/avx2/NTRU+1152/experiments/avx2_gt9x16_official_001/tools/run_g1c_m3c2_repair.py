#!/usr/bin/env python3
"""Record the fixed-corpus M3C2 repair-action observation."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import subprocess
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--common-header", type=Path, required=True)
    parser.add_argument("--m3-oracle", type=Path, required=True)
    parser.add_argument("--m3c0-oracle", type=Path, required=True)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--cflags", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    probe = json.loads(subprocess.check_output([str(args.binary)], text=True))
    if probe["pre_d8_failures"] != 0:
        raise SystemExit("M3C2 corpus unexpectedly fails before D8")
    if len(probe["nodes"]) != 576:
        raise SystemExit("M3C2 probe must emit all 576 logical D8 nodes")
    unsafe = [node for node in probe["nodes"] if node["unsafe_count"][0] > 0]
    if not unsafe:
        raise SystemExit("M3C2 lost the permanent D8 counterexample")
    if any(node["unsafe_count"][1] or node["unsafe_count"][2]
           for node in unsafe):
        raise SystemExit("fixed corpus contains a node not repaired one-sided")
    permanent = next(
        node for node in probe["nodes"]
        if (node["branch"], node["row"], node["coefficient"], node["pair"]) ==
        (0, 3, 3, 0))
    if permanent["unsafe_count"][0] == 0:
        raise SystemExit("permanent M3B regression node no longer fails")

    document = {
        "schema": "gt-g1c-m3c2-repair-observation/v1",
        "benchmark_class": (
            "repository-local-deterministic-repair-search-not-performance"),
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "hostname": platform.node(),
        "kernel": platform.release(),
        "compiler": args.compiler,
        "cflags": args.cflags,
        "binary_sha256": digest(args.binary),
        "source_sha256": digest(args.source),
        "common_header_sha256": digest(args.common_header),
        "m3_oracle_sha256": digest(args.m3_oracle),
        "m3c0_oracle_sha256": digest(args.m3c0_oracle),
        "probe": probe,
        "summary": {
            "logical_nodes": len(probe["nodes"]),
            "nodes_unsafe_without_repair": len(unsafe),
            "unsafe_pair_indices": sorted({node["pair"] for node in unsafe}),
            "unsafe_nodes_safe_with_left_only": sum(
                node["unsafe_count"][1] == 0 for node in unsafe),
            "unsafe_nodes_safe_with_right_only": sum(
                node["unsafe_count"][2] == 0 for node in unsafe),
            "unsafe_nodes_requiring_both": sum(
                node["unsafe_count"][1] > 0 and node["unsafe_count"][2] > 0
                for node in unsafe),
            "global_maximum_abs_sum_or_difference_by_action": [
                max(node["maximum_abs_sum_or_difference"][action]
                    for node in probe["nodes"])
                for action in range(4)],
        },
        "conclusions": {
            "candidate_selection": (
                "fixed corpus selects one-sided repair for 37 pair-0 nodes"),
            "exact_safety": (
                "open; clean corpus actions are not a proof for all producer inputs"),
            "assembly": "not-authorized",
            "performance": "not-measured",
        },
        "promotion_eligible": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
