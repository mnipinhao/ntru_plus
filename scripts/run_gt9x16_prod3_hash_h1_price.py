#!/usr/bin/env python3
"""Price current PROD3 hash recovery against direct H1 serialization."""

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

PREFIX = "gt9x16_prod3_hash_h1_price"
VARIANTS = ("h0", "h1")
LABELS = tuple(f"{PREFIX}_{variant}_pos{position}_cycles"
               for variant in VARIANTS for position in range(1, 5))


def run_checked(command: list[str]) -> None:
    completed = subprocess.run(command, text=True)
    if completed.returncode:
        raise SystemExit(
            f"command failed ({completed.returncode}): {' '.join(command)}")


def short_stq2(result_dir: Path, variant: str) -> float:
    summary = json.loads(
        (result_dir / "stq-summary.json").read_text(encoding="utf-8"))
    return float(summary["balanced_combined_operations"]
                        [f"{PREFIX}_{variant}_cycles"]["stq2"])


def launch(binary: Path, cpu: int, aslr_off: bool) -> tuple[
        str, dict[str, list[int]], list[int]]:
    command = ["taskset", "-c", str(cpu)]
    if aslr_off:
        command.extend(["setarch", platform.machine(), "-R"])
    command.append(str(binary.resolve()))
    completed = subprocess.run(
        command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if completed.returncode:
        raise SystemExit(
            f"H1 replay failed ({completed.returncode}): "
            f"{' '.join(command)}\n{completed.stdout}")
    observed = {name: decode_observations(completed.stdout, name)
                for name in LABELS}
    bad = {name: len(values) for name, values in observed.items()
           if len(values) != 96}
    if bad:
        raise SystemExit(f"H1 observation counts are wrong: {bad}")
    match = re.search(
        rf"^{PREFIX}_runtime_addresses"
        r"((?:\s+0x[0-9a-fA-F]+){4})$", completed.stdout, re.MULTILINE)
    if not match:
        raise SystemExit("H1 replay lacks four runtime addresses")
    return (completed.stdout, observed,
            [int(word, 16) for word in match.group(1).split()])


def variant_stq2(observed: dict[str, list[int]], variant: str) -> float:
    values = sum((observed[f"{PREFIX}_{variant}_pos{position}_cycles"]
                  for position in range(1, 5)), [])
    return stabilized_quartiles(values)[1]


def analyze(records: list[dict[str, object]]) -> dict[str, object]:
    pooled = {name: [] for name in LABELS}
    launches = []
    for record in records:
        observed = record["observed"]
        assert isinstance(observed, dict)
        for name in LABELS:
            pooled[name].extend(observed[name])
        stq2 = {variant: variant_stq2(observed, variant)
                for variant in VARIANTS}
        launches.append({
            "launch": record["launch"],
            "h0_stq2": stq2["h0"],
            "h1_stq2": stq2["h1"],
            "h1_minus_h0_cycles": stq2["h1"] - stq2["h0"],
        })
    combined = {}
    for variant in VARIANTS:
        values = sum((pooled[f"{PREFIX}_{variant}_pos{position}_cycles"]
                      for position in range(1, 5)), [])
        quartiles = stabilized_quartiles(values)
        combined[variant] = {
            "observations": len(values), "stq1": quartiles[0],
            "stq2": quartiles[1], "stq3": quartiles[2],
        }
    deltas = [float(entry["h1_minus_h0_cycles"]) for entry in launches]
    addresses = [record["addresses"] for record in records]
    return {
        "combined": combined,
        "launches": launches,
        "median_h1_minus_h0_cycles": statistics.median(deltas),
        "bootstrap_95pct_ci_median_h1_minus_h0_cycles":
            bootstrap_median_ci(deltas, seed=0x4831),
        "h1_faster_launches": sum(value < 0 for value in deltas),
        "h1_slower_launches": sum(value > 0 for value in deltas),
        "runtime_addresses": addresses,
        "unique_runtime_address_tuples":
            len({tuple(row) for row in addresses}),
    }


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
        raise SystemExit("SUPERCOP-like headline requires host ASLR enabled")
    args.output.mkdir(parents=True)
    selection_root = args.output / "selection"
    selection_root.mkdir()
    implementations = {
        "normal": args.normal_implementation,
        "reversed": args.reversed_implementation,
    }
    run_script = Path(__file__).with_name("run_supercop_benchmark.py")
    selection = {}
    for placement, implementation in implementations.items():
        result = selection_root / placement
        run_checked([
            "python3", str(run_script), "--campaign-root",
            str(args.campaign_root), "--parameter", "1152",
            "--implementation", implementation, "--cpu", str(args.cpu),
            "--mode", "derived-gt9x16-prod3-hash-h1-price",
            "--fresh-launches", "9", "--result-dir", str(result),
            "--compiler-wrapper", str(args.compiler_wrapper),
            "--require-frequency-control",
        ])
        selection[placement] = {
            "implementation": implementation,
            "h1_stq2": short_stq2(result, "h1"),
            "measure_sha256": sha256_file(result / "measure"),
        }
    selected = min(selection, key=lambda placement: (
        selection[placement]["h1_stq2"], placement != "normal"))
    alternate = "reversed" if selected == "normal" else "normal"
    settings_root = args.output / "settings"
    settings_root.mkdir()
    settings = {}
    for placement in (selected, alternate):
        binary = selection_root / placement / "measure"
        for aslr_off in (False, True):
            name = f"{placement}-aslr-{'off' if aslr_off else 'on'}"
            directory = settings_root / name
            directory.mkdir()
            records = []
            for number in range(1, 10):
                output, observed, addresses = launch(binary, args.cpu, aslr_off)
                filename = f"launch-{number:02d}.out"
                (directory / filename).write_text(output, encoding="utf-8")
                records.append({"launch": number, "file": filename,
                                "observed": observed, "addresses": addresses})
            result = analyze(records)
            unique = int(result["unique_runtime_address_tuples"])
            if aslr_off and unique != 1:
                raise SystemExit(f"ASLR-off addresses varied in {name}")
            if not aslr_off and unique < 2:
                raise SystemExit(f"ASLR-on addresses did not vary in {name}")
            settings[name] = result
    headline = f"{selected}-aslr-on"
    summary = {
        **read_lock(),
        "benchmark_class": "supercop-derived-gt9x16-prod3-hash-h1-price",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": args.cpu,
        "compiler_policy": "fixed-common-O3GC",
        "compiler_wrapper": str(args.compiler_wrapper.resolve()),
        "compiler_wrapper_sha256": sha256_file(args.compiler_wrapper),
        "selection_policy": "minimum absolute H1 StQ2 under independent ASLR-on selection",
        "selection": selection,
        "selected_placement": selected,
        "alternate_placement": alternate,
        "headline_setting": headline,
        "headline_estimator": "median per-launch H1-H0",
        "serious_launches_per_setting": 9,
        "observations_per_label_per_launch": 96,
        "positions_per_variant": 4,
        "boundary": "materialized scale-4 MA2 planes to exact 1728 bytes",
        "settings": settings,
    }
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    shutil.copy2(LOCK_PATH, args.output / "supercop.lock")
    print(f"selected {selected}; headline {headline}")
    print(json.dumps(settings[headline], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
