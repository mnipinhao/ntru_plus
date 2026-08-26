#!/usr/bin/env python3
"""Price Official and PROD3 hash fanout with a four-way same-ELF design."""

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

PREFIX = "gt9x16_prod3_hash_fanout"
VARIANTS = ("o0", "o1", "c0", "c1")
LABELS = tuple(
    f"{PREFIX}_{variant}_pos{position}_cycles"
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
            f"hash-fanout replay failed ({completed.returncode}): "
            f"{' '.join(command)}\n{completed.stdout}")
    observed = {name: decode_observations(completed.stdout, name)
                for name in LABELS}
    bad = {name: len(values) for name, values in observed.items()
           if len(values) != 96}
    if bad:
        raise SystemExit(f"hash-fanout observation counts are wrong: {bad}")
    match = re.search(
        rf"^{PREFIX}_runtime_addresses"
        r"((?:\s+0x[0-9a-fA-F]+){5})$", completed.stdout, re.MULTILINE)
    if not match:
        raise SystemExit("hash-fanout replay lacks five runtime addresses")
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
        official_fanout = stq2["o1"] - stq2["o0"]
        candidate_fanout = stq2["c1"] - stq2["c0"]
        producer_delta = stq2["c0"] - stq2["o0"]
        launches.append({
            "launch": record["launch"],
            **{f"{variant}_stq2": value for variant, value in stq2.items()},
            "official_hash_fanout_cycles": official_fanout,
            "candidate_hash_fanout_cycles": candidate_fanout,
            "excess_hash_fanout_tax_cycles": candidate_fanout - official_fanout,
            "producer_candidate_minus_official_cycles": producer_delta,
            "complete_dual_output_candidate_minus_official_cycles":
                stq2["c1"] - stq2["o1"],
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
    excess = [float(entry["excess_hash_fanout_tax_cycles"])
              for entry in launches]
    producer = [float(entry["producer_candidate_minus_official_cycles"])
                for entry in launches]
    complete = [float(entry[
        "complete_dual_output_candidate_minus_official_cycles"])
                for entry in launches]
    addresses = [record["addresses"] for record in records]
    return {
        "combined": combined,
        "launches": launches,
        "median_excess_hash_fanout_tax_cycles": statistics.median(excess),
        "bootstrap_95pct_ci_median_excess_tax":
            bootstrap_median_ci(excess, seed=0xFA110),
        "positive_excess_tax_launches": sum(value > 0 for value in excess),
        "negative_excess_tax_launches": sum(value < 0 for value in excess),
        "median_producer_candidate_minus_official_cycles":
            statistics.median(producer),
        "bootstrap_95pct_ci_median_producer_delta":
            bootstrap_median_ci(producer, seed=0xC0D0),
        "candidate_producer_faster_launches":
            sum(value < 0 for value in producer),
        "candidate_producer_slower_launches":
            sum(value > 0 for value in producer),
        "median_complete_dual_output_candidate_minus_official_cycles":
            statistics.median(complete),
        "bootstrap_95pct_ci_median_complete_delta":
            bootstrap_median_ci(complete, seed=0xD0A1),
        "candidate_complete_faster_launches":
            sum(value < 0 for value in complete),
        "candidate_complete_slower_launches":
            sum(value > 0 for value in complete),
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
    parser.add_argument("--selection-launches", type=int, default=9)
    parser.add_argument("--serious-launches", type=int, default=9)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    if args.selection_launches != 9 or args.serious_launches != 9:
        raise SystemExit("hash-fanout checkpoint requires 9+9 launches")
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
            "--mode", "derived-gt9x16-prod3-hash-fanout",
            "--fresh-launches", "9", "--result-dir", str(result),
            "--compiler-wrapper", str(args.compiler_wrapper),
            "--require-frequency-control",
        ])
        selection[placement] = {
            "implementation": implementation,
            "c1_stq2": short_stq2(result, "c1"),
            "measure_sha256": sha256_file(result / "measure"),
        }
    selected = min(selection, key=lambda placement: (
        selection[placement]["c1_stq2"], placement != "normal"))
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
        "benchmark_class": "supercop-derived-gt9x16-prod3-hash-fanout",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": args.cpu,
        "compiler_policy": "fixed-common-O3GC",
        "compiler_wrapper": str(args.compiler_wrapper.resolve()),
        "compiler_wrapper_sha256": sha256_file(args.compiler_wrapper),
        "selection_policy": "minimum absolute C1 StQ2 under independent ASLR-on selection",
        "selection": selection,
        "selected_placement": selected,
        "alternate_placement": alternate,
        "headline_setting": headline,
        "headline_estimator": "median per-launch (C1-C0)-(O1-O0)",
        "serious_launches_per_setting": 9,
        "observations_per_label_per_launch": 96,
        "positions_per_variant": 4,
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
