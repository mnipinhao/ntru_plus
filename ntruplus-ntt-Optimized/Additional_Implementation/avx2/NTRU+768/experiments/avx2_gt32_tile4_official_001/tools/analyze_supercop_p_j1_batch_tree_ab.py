#!/usr/bin/env python3
"""Analyze alternating ABBA/BAAB SUPERcop P-J1 batch-tree launches."""

from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path

from analyze_supercop_matrix import OPS, parse_result, stabilized_quartiles


def variant(path: Path) -> str:
    if "ntruplus768-avx2-20" in path.name:
        return "control"
    for name in ("control", "candidate"):
        if f"batch-tree-{name}" in path.name:
            return name
    raise ValueError(f"unrecognized result: {path}")


def bootstrap_ci(values: list[float], seed: int, samples: int = 100000) -> list[float]:
    rng = random.Random(seed)
    estimates = sorted(statistics.median(rng.choices(values, k=len(values)))
                       for _ in range(samples))
    return [estimates[int(samples * .025)], estimates[int(samples * .975)]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dirs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    paths = sorted(args.result_dirs, key=lambda item: item.stat().st_mtime_ns)
    if not paths or len(paths) % 4:
        raise ValueError("launch count must be a nonzero multiple of four")
    launches = []
    for path in paths:
        parsed = parse_result(path)
        launches.append({"result_dir": str(path), "variant": variant(path),
                         "operations": {op: {
                             "observations": len(parsed["measurements"][op]),
                             "q2_cycles": stabilized_quartiles(
                                 parsed["measurements"][op])[1]}
                             for op in OPS}})
    blocks = []
    for start in range(0, len(launches), 4):
        group = launches[start:start + 4]
        block_id = start // 4 + 1
        expected = (["control", "candidate", "candidate", "control"]
                    if block_id % 2 else
                    ["candidate", "control", "control", "candidate"])
        if [item["variant"] for item in group] != expected:
            raise ValueError(f"bad sequence block {block_id}")
        operations = {}
        for op in OPS:
            control = statistics.mean(item["operations"][op]["q2_cycles"]
                                      for item in group
                                      if item["variant"] == "control")
            candidate = statistics.mean(item["operations"][op]["q2_cycles"]
                                        for item in group
                                        if item["variant"] == "candidate")
            operations[op] = {"control_q2_cycles": control,
                              "candidate_q2_cycles": candidate,
                              "candidate_minus_control": candidate - control}
        blocks.append({"block": block_id, "sequence": expected,
                       "operations": operations})
    summary = {}
    for index, op in enumerate(OPS):
        deltas = [item["operations"][op]["candidate_minus_control"]
                  for item in blocks]
        control = [item["operations"][op]["control_q2_cycles"]
                   for item in blocks]
        candidate = [item["operations"][op]["candidate_q2_cycles"]
                     for item in blocks]
        median_delta = statistics.median(deltas)
        summary[op] = {
            "blocks": len(blocks),
            "control_block_median_q2_cycles": statistics.median(control),
            "candidate_block_median_q2_cycles": statistics.median(candidate),
            "median_block_delta_cycles": median_delta,
            "median_block_delta_percent": (100 * median_delta /
                                             statistics.median(control)),
            "block_delta_mad_cycles": statistics.median(
                abs(value - median_delta) for value in deltas),
            "bootstrap_median_95ci_cycles": bootstrap_ci(
                deltas, 0xB471 + index),
            "candidate_favorable_blocks": sum(value < 0 for value in deltas),
            "block_deltas_cycles": deltas,
            "abba_median_delta_cycles": statistics.median(deltas[0::2]),
            "baab_median_delta_cycles": statistics.median(deltas[1::2]),
        }
    result = {"schema": "ntruplus768-p-j1-batch-tree-supercop-ab-v1",
              "cycle_backend": "default-perfevent",
              "statistics_unit": "launch stabilized Q2; paired block delta",
              "launches": launches, "blocks": blocks, "summary": summary}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
