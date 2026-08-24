#!/usr/bin/env python3
"""Summarize benchmark artifacts and evaluate the statistical promotion gates."""

from __future__ import annotations

import argparse
import json
import random
import re
import statistics
from pathlib import Path

OPERATIONS = ("keypair_cycles", "enc_cycles", "dec_cycles")


def decoded(text: str, operation: str) -> list[int]:
    result: list[int] = []
    for line in text.splitlines():
        if f" {operation} " not in f" {line} ":
            continue
        encoded = re.findall(r"[+-]?\d+", line.split(operation, 1)[1])
        if len(encoded) >= 2:
            center = int(encoded[0])
            result.extend(center + int(delta) for delta in encoded[1:])
    return result


def bootstrap_ci(samples: list[float], iterations: int = 20000) -> tuple[float, float]:
    generator = random.Random(0x4E545255)
    means = []
    for _ in range(iterations):
        means.append(statistics.fmean(generator.choice(samples) for _ in samples))
    means.sort()
    return means[int(iterations * 0.025)], means[int(iterations * 0.975)]


def stq2(samples: list[int]) -> float:
    expanded = sorted(value for value in samples for _ in range(8))
    count = len(samples)
    middle = expanded[3 * count:5 * count]
    return statistics.fmean(middle)


def setting_stats(root: Path, launches: list[dict], operation: str) -> dict[str, object]:
    by_block: dict[int, dict[str, list[float]]] = {}
    for launch in launches:
        values = decoded((root / launch["file"]).read_text(encoding="utf-8"), operation)
        if len(values) < 96:
            raise ValueError(f"{launch['file']} has only {len(values)} {operation} observations")
        block = by_block.setdefault(launch["block"], {"official": [], "candidate": []})
        block[launch["implementation"]].append(stq2(values))
    differences = []
    for block_number in sorted(by_block):
        block = by_block[block_number]
        differences.append(statistics.fmean(block["candidate"]) - statistics.fmean(block["official"]))
    low, high = bootstrap_ci(differences)
    return {"block_differences_cycles": differences, "mean_difference_cycles": statistics.fmean(differences),
            "bootstrap_95_ci_cycles": [low, high], "candidate_faster": high < 0}


def formal_summary(directory: Path, benchmark_class: str,
                   operations: tuple[str, ...]) -> dict[str, object]:
    metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
    summary = json.loads((directory / "stq-summary.json").read_text(encoding="utf-8"))
    if metadata.get("benchmark_class") != benchmark_class:
        raise ValueError(f"{directory} is not {benchmark_class}")
    if metadata.get("frequency_policy") != "required":
        raise ValueError(f"{directory} is not a serious frequency-controlled run")
    if not metadata.get("frequency_control", {}).get("formal_policy_passed"):
        raise ValueError(f"{directory} failed formal frequency controls")
    if summary.get("estimator") != "SUPERCOP-20260627-stabilized-quartiles":
        raise ValueError(f"{directory} uses the wrong estimator")
    if summary.get("fresh_process_launches", 0) < 9:
        raise ValueError(f"{directory} has fewer than 9 fresh measure processes")
    missing = [name for name in operations if name not in summary.get("operations", {})]
    if missing:
        raise ValueError(f"{directory} summary lacks {', '.join(missing)}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paired", type=Path, required=True)
    parser.add_argument("--native-official", type=Path, required=True)
    parser.add_argument("--native-candidate", type=Path, required=True)
    parser.add_argument("--poly-official", type=Path, required=True)
    parser.add_argument("--poly-candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.paired / "manifest.json").read_text(encoding="utf-8"))
    native_official_summary = formal_summary(
        args.native_official, "supercop-native-kem", OPERATIONS)
    native_candidate_summary = formal_summary(
        args.native_candidate, "supercop-native-kem", OPERATIONS)
    native_official = {operation: native_official_summary["operations"][operation]["stq2"]
                       for operation in OPERATIONS}
    native_candidate = {operation: native_candidate_summary["operations"][operation]["stq2"]
                        for operation in OPERATIONS}
    native_regressions = {operation: native_candidate[operation] > native_official[operation]
                          for operation in OPERATIONS}
    poly_operations = ("forward_small_cycles", "forward_general_cycles", "basemul_cycles",
                       "inverse_cycles", "baseinv_cycles", "poly_mul_small_cycles",
                       "poly_mul_general_cycles")
    poly_official = formal_summary(args.poly_official, "supercop-derived-poly", poly_operations)
    poly_candidate = formal_summary(args.poly_candidate, "supercop-derived-poly", poly_operations)
    paired = {}
    settings = sorted({launch["setting"] for launch in manifest["launches"]})
    for setting in settings:
        launches = [launch for launch in manifest["launches"] if launch["setting"] == setting]
        paired[setting] = {operation: setting_stats(args.paired, launches, operation)
                           for operation in OPERATIONS}
    direction_consistent = {}
    for operation in OPERATIONS:
        means = [paired[setting][operation]["mean_difference_cycles"] for setting in settings]
        direction_consistent[operation] = all(value < 0 for value in means)
    aslr_off_ci = {
        operation: all(paired[setting][operation]["bootstrap_95_ci_cycles"][1] < 0
                       for setting in settings if setting.endswith("aslr-off"))
        for operation in OPERATIONS
    }
    report = {
        "pinned_supercop": {key: manifest[key] for key in (
            "version", "url", "archive_sha256", "ntruplus864_avx2_tree_sha256",
            "ntruplus1152_avx2_tree_sha256")},
        "native": {"estimator": "StQ2", "official_stq2": native_official,
                   "candidate_stq2": native_candidate,
                   "candidate_slower": native_regressions},
        "paired": paired,
        "direction_consistent": direction_consistent,
        "aslr_off_ci_below_zero": aslr_off_ci,
        "poly": {"estimator": "StQ1/StQ2/StQ3",
                 "official": poly_official["operations"],
                 "candidate": poly_candidate["operations"]},
        "automatic_statistical_gate": all(direction_consistent.values()) and all(aslr_off_ci.values()),
        "manual_gates_required": ["correctness/KAT/range/ABI/constant-time",
                                  "native regression explanation", "caller-path attribution"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = args.output.with_suffix(".md")
    markdown.write_text(
        "# SUPERCOP promotion report\n\n"
        f"Pinned SUPERCOP: `{manifest['version']}`  \n"
        f"Archive SHA-256: `{manifest['archive_sha256']}`  \n"
        f"Automatic paired statistical gate: **{'PASS' if report['automatic_statistical_gate'] else 'FAIL'}**\n\n"
        "This report does not replace the correctness, ABI, constant-time, native-regression, "
        "or caller-path gates listed in the workflow. See the adjacent JSON for full statistics.\n",
        encoding="utf-8",
    )
    print(f"wrote {args.output} and {markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
