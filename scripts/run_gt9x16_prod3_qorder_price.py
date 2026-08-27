#!/usr/bin/env python3
"""Run final caller-shaped current-Q versus natural-Q SUPERCOP arbitration."""
from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from run_gt9x16_prod3_price import bootstrap_median_ci
from run_supercop_benchmark import decode_observations, stabilized_quartiles
from supercop_workflow import LOCK_PATH, read_lock, sha256_file

PREFIX = "gt9x16_prod3_qorder_price"
LABELS = tuple(f"{PREFIX}_{variant}_{position}_cycles"
               for variant in ("current", "natural")
               for position in ("first", "second"))


def checked(command: list[str]) -> None:
    result = subprocess.run(command, text=True)
    if result.returncode:
        raise SystemExit(f"command failed ({result.returncode}): {' '.join(command)}")


def launch(binary: Path, cpu: int, aslr_off: bool) -> dict:
    command = ["taskset", "-c", str(cpu)]
    if aslr_off:
        command += ["setarch", platform.machine(), "-R"]
    command.append(str(binary.resolve()))
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    if result.returncode:
        raise SystemExit(f"Q-order replay failed: {' '.join(command)}\n{result.stdout}")
    observed = {name: decode_observations(result.stdout, name) for name in LABELS}
    bad = {name: len(values) for name, values in observed.items() if len(values) != 96}
    if bad:
        raise SystemExit(f"Q-order observation counts changed: {bad}")
    match = re.search(r"^gt9x16_prod3_qorder_price_runtime_addresses"
                      r"((?:\s+0x[0-9a-fA-F]+){6})$", result.stdout, re.M)
    if not match:
        raise SystemExit("Q-order replay lacks six runtime addresses")
    return {"output": result.stdout, "observed": observed,
            "addresses": [int(x, 16) for x in match.group(1).split()]}


def analyze(records: list[dict]) -> dict:
    launches = []
    pooled = {name: [] for name in LABELS}
    for number, record in enumerate(records, 1):
        for name in LABELS:
            pooled[name] += record["observed"][name]
        current = stabilized_quartiles(
            record["observed"][f"{PREFIX}_current_first_cycles"] +
            record["observed"][f"{PREFIX}_current_second_cycles"])[1]
        natural = stabilized_quartiles(
            record["observed"][f"{PREFIX}_natural_first_cycles"] +
            record["observed"][f"{PREFIX}_natural_second_cycles"])[1]
        launches.append({"launch": number, "current_stq2": current,
                         "natural_stq2": natural,
                         "natural_minus_current_cycles": natural-current})
    combined = {}
    for variant in ("current", "natural"):
        values = (pooled[f"{PREFIX}_{variant}_first_cycles"] +
                  pooled[f"{PREFIX}_{variant}_second_cycles"])
        q = stabilized_quartiles(values)
        combined[variant] = {"observations": len(values), "stq1": q[0],
                             "stq2": q[1], "stq3": q[2]}
    deltas = [float(row["natural_minus_current_cycles"]) for row in launches]
    addresses = [record["addresses"] for record in records]
    return {"combined": combined, "launches": launches,
            "median_natural_minus_current_cycles": statistics.median(deltas),
            "bootstrap_95pct_ci_median_delta": bootstrap_median_ci(deltas, seed=0x514f),
            "natural_faster_launches": sum(x < 0 for x in deltas),
            "natural_slower_launches": sum(x > 0 for x in deltas),
            "runtime_addresses": addresses,
            "unique_runtime_address_tuples": len({tuple(x) for x in addresses})}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--normal-implementation", required=True)
    parser.add_argument("--reversed-implementation", required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--compiler-wrapper", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    if Path("/proc/sys/kernel/randomize_va_space").read_text().strip() == "0":
        raise SystemExit("ASLR-on controls require randomize_va_space != 0")
    args.output.mkdir(parents=True)
    builds = args.output / "builds"; builds.mkdir()
    runner = Path(__file__).with_name("run_supercop_benchmark.py")
    implementations = {"normal": args.normal_implementation,
                       "reversed": args.reversed_implementation}
    binaries = {}
    build_records = {}
    for placement, implementation in implementations.items():
        result = builds / placement
        checked(["python3", str(runner), "--campaign-root", str(args.campaign_root),
                 "--parameter", "1152", "--implementation", implementation,
                 "--cpu", str(args.cpu), "--mode",
                 "derived-gt9x16-prod3-qorder-price", "--fresh-launches", "9",
                 "--result-dir", str(result), "--compiler-wrapper",
                 str(args.compiler_wrapper), "--require-frequency-control"])
        binaries[placement] = result / "measure"
        build_records[placement] = {
            "implementation": implementation,
            "measure_sha256": sha256_file(result / "measure"),
            "metadata_sha256": sha256_file(result / "metadata.json"),
        }
    settings_root = args.output / "settings"; settings_root.mkdir()
    settings = {}
    for placement in ("normal", "reversed"):
        for aslr_off in (False, True):
            name = f"{placement}-aslr-{'off' if aslr_off else 'on'}"
            directory = settings_root / name; directory.mkdir()
            records = []
            for number in range(1, 10):
                record = launch(binaries[placement], args.cpu, aslr_off)
                filename = f"launch-{number:02d}.out"
                (directory / filename).write_text(record.pop("output"))
                records.append(record)
            settings[name] = analyze(records)
            unique = settings[name]["unique_runtime_address_tuples"]
            if (aslr_off and unique != 1) or (not aslr_off and unique < 2):
                raise SystemExit(f"ASLR address control failed for {name}: {unique}")
    signs = {name: value["median_natural_minus_current_cycles"] < 0
             for name, value in settings.items()}
    winner = ("natural-Q" if all(signs.values()) else
              "current-Q" if not any(signs.values()) else "inconclusive")
    summary = {**read_lock(), "created_at": datetime.now(timezone.utc).isoformat(),
               "benchmark_class": "supercop-derived-gt9x16-prod3-qorder-price",
               "boundary": "two coefficient-domain producers plus resident h, lane-wise MA2, ciphertext H1, and r hash H1",
               "cpu": args.cpu, "compiler_policy": "fixed-common-O3GC",
               "compiler_wrapper": str(args.compiler_wrapper.resolve()),
               "compiler_wrapper_sha256": sha256_file(args.compiler_wrapper),
               "serious_launches_per_setting": 9,
               "observations_per_label_per_launch": 96,
               "placement_selection": "none; all four settings are co-equal ABI evidence",
               "builds": build_records, "settings": settings,
               "all_four_delta_signs_agree": len(set(signs.values())) == 1,
               "winner": winner,
               "freeze_policy": "freeze winner; do not search more Q-orders",
               "native_kem_result": False}
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    shutil.copy2(LOCK_PATH, args.output / "supercop.lock")
    print(json.dumps({"winner": winner,
                      "deltas": {k: v["median_natural_minus_current_cycles"]
                                 for k, v in settings.items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
