#!/usr/bin/env python3
"""Select the fastest PROD3 placement, then run serious ASLR controls."""

from __future__ import annotations

import argparse
import json
import platform
import random
import re
import shutil
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from run_supercop_benchmark import decode_observations, stabilized_quartiles
from supercop_workflow import LOCK_PATH, read_lock, sha256_file

PREFIX = "gt9x16_prod3_price"
LABELS = tuple(
    f"{PREFIX}_{width}_{variant}_{position}_cycles"
    for width in ("1x", "2x")
    for variant, position in (("control", "first"),
                              ("candidate", "second"),
                              ("candidate", "first"),
                              ("control", "second")))


def run_checked(command: list[str]) -> None:
    completed = subprocess.run(command, text=True)
    if completed.returncode:
        raise SystemExit(f"command failed ({completed.returncode}): {' '.join(command)}")


def read_short_stq2(result_dir: Path, width: str, variant: str) -> float:
    summary = json.loads((result_dir / "stq-summary.json").read_text(encoding="utf-8"))
    name = f"{PREFIX}_{width}_{variant}_cycles"
    return float(summary["balanced_combined_operations"][name]["stq2"])


def launch(binary: Path, cpu: int, aslr_off: bool) -> tuple[str, dict[str, list[int]], list[int]]:
    command = ["taskset", "-c", str(cpu)]
    if aslr_off:
        command.extend(["setarch", platform.machine(), "-R"])
    command.append(str(binary.resolve()))
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    if completed.returncode:
        raise SystemExit(
            f"PRICE replay failed ({completed.returncode}): {' '.join(command)}\n"
            f"{completed.stdout}")
    observed = {name: decode_observations(completed.stdout, name) for name in LABELS}
    bad = {name: len(values) for name, values in observed.items() if len(values) != 96}
    if bad:
        raise SystemExit(f"PRICE replay observation counts are wrong: {bad}")
    match = re.search(
        r"^gt9x16_prod3_price_runtime_addresses"
        r"((?:\s+0x[0-9a-fA-F]+){4})$", completed.stdout, re.MULTILINE)
    if not match:
        raise SystemExit("PRICE replay lacks the four runtime symbol addresses")
    addresses = [int(word, 16) for word in match.group(1).split()]
    return completed.stdout, observed, addresses


def launch_stq2(observed: dict[str, list[int]], width: str, variant: str) -> float:
    values = (observed[f"{PREFIX}_{width}_{variant}_first_cycles"] +
              observed[f"{PREFIX}_{width}_{variant}_second_cycles"])
    return stabilized_quartiles(values)[1]


def bootstrap_median_ci(values: list[float], seed: int = 1152,
                        repetitions: int = 20000) -> list[float]:
    generator = random.Random(seed)
    estimates = []
    for _ in range(repetitions):
        sample = [values[generator.randrange(len(values))] for _ in values]
        estimates.append(statistics.median(sample))
    estimates.sort()
    return [estimates[int(0.025 * repetitions)],
            estimates[int(0.975 * repetitions) - 1]]


def analyze_setting(records: list[dict[str, object]]) -> dict[str, object]:
    launches = []
    pooled = {name: [] for name in LABELS}
    for record in records:
        observed = record["observed"]
        assert isinstance(observed, dict)
        for name in LABELS:
            pooled[name].extend(observed[name])
        entry: dict[str, object] = {"launch": record["launch"]}
        for width in ("1x", "2x"):
            control = launch_stq2(observed, width, "control")
            candidate = launch_stq2(observed, width, "candidate")
            entry.update({
                f"{width}_control_stq2": control,
                f"{width}_candidate_stq2": candidate,
                f"{width}_candidate_minus_control_cycles": candidate - control,
            })
        launches.append(entry)
    combined = {}
    for width in ("1x", "2x"):
        for variant in ("control", "candidate"):
            values = (pooled[f"{PREFIX}_{width}_{variant}_first_cycles"] +
                      pooled[f"{PREFIX}_{width}_{variant}_second_cycles"])
            quartiles = stabilized_quartiles(values)
            combined[f"{width}_{variant}"] = {
                "observations": len(values), "stq1": quartiles[0],
                "stq2": quartiles[1], "stq3": quartiles[2],
            }
    deltas = [float(entry["2x_candidate_minus_control_cycles"])
              for entry in launches]
    address_rows = [record["addresses"] for record in records]
    return {
        "combined": combined,
        "launches": launches,
        "candidate_2x_faster_launches": sum(delta < 0 for delta in deltas),
        "candidate_2x_slower_launches": sum(delta > 0 for delta in deltas),
        "median_2x_candidate_minus_control_cycles": statistics.median(deltas),
        "bootstrap_95pct_ci_median_2x_delta": bootstrap_median_ci(deltas),
        "runtime_addresses": address_rows,
        "unique_runtime_address_tuples": len({tuple(row) for row in address_rows}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--normal-implementation", required=True)
    parser.add_argument("--reversed-implementation", required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--compiler-wrapper", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--selection-launches", type=int, default=3)
    parser.add_argument("--serious-launches", type=int, default=9)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    if args.selection_launches < 2 or args.serious_launches != 9:
        raise SystemExit("PRICE requires >=2 selection launches and exactly 9 serious launches")
    if Path("/proc/sys/kernel/randomize_va_space").read_text().strip() == "0":
        raise SystemExit("SUPERCOP-like ASLR-on headline requires randomize_va_space != 0")
    args.output.mkdir(parents=True)
    short_root = args.output / "selection"
    short_root.mkdir()
    implementations = {
        "normal": args.normal_implementation,
        "reversed": args.reversed_implementation,
    }
    run_script = Path(__file__).with_name("run_supercop_benchmark.py")
    short = {}
    for placement, implementation in implementations.items():
        result = short_root / placement
        run_checked([
            "python3", str(run_script), "--campaign-root", str(args.campaign_root),
            "--parameter", "1152", "--implementation", implementation,
            "--cpu", str(args.cpu), "--mode", "derived-gt9x16-prod3-price",
            "--fresh-launches", str(args.selection_launches),
            "--result-dir", str(result), "--compiler-wrapper",
            str(args.compiler_wrapper),
        ])
        short[placement] = {
            "implementation": implementation,
            "candidate_2x_stq2": read_short_stq2(result, "2x", "candidate"),
            "control_2x_stq2": read_short_stq2(result, "2x", "control"),
            "measure_sha256": sha256_file(result / "measure"),
        }
    selected = min(short, key=lambda placement: (short[placement]["candidate_2x_stq2"],
                                                  placement != "normal"))
    alternate = "reversed" if selected == "normal" else "normal"
    settings_root = args.output / "settings"
    settings_root.mkdir()
    settings = {}
    for placement in (selected, alternate):
        binary = short_root / placement / "measure"
        for aslr_off in (False, True):
            setting_name = f"{placement}-aslr-{'off' if aslr_off else 'on'}"
            setting_dir = settings_root / setting_name
            setting_dir.mkdir()
            records = []
            for launch_number in range(1, args.serious_launches + 1):
                output, observed, addresses = launch(binary, args.cpu, aslr_off)
                output_name = f"launch-{launch_number:02d}.out"
                (setting_dir / output_name).write_text(output, encoding="utf-8")
                records.append({"launch": launch_number, "file": output_name,
                                "observed": observed, "addresses": addresses})
            analysis = analyze_setting(records)
            unique = int(analysis["unique_runtime_address_tuples"])
            if aslr_off and unique != 1:
                raise SystemExit(f"ASLR-off addresses varied in {setting_name}")
            if not aslr_off and unique < 2:
                raise SystemExit(f"ASLR-on addresses did not vary in {setting_name}")
            settings[setting_name] = analysis
    primary = f"{selected}-aslr-on"
    summary = {
        **read_lock(),
        "benchmark_class": "supercop-derived-gt9x16-prod3-price",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": args.cpu,
        "compiler_policy": "fixed-common-O3GC",
        "compiler_wrapper": str(args.compiler_wrapper.resolve()),
        "compiler_wrapper_sha256": sha256_file(args.compiler_wrapper),
        "selection_policy": (
            "minimum absolute candidate 2x StQ2 under ASLR-on short runs"),
        "selection": short,
        "selected_placement": selected,
        "alternate_placement": alternate,
        "headline_setting": primary,
        "headline_rationale": (
            "SUPERCOP executes PIE with host ASLR enabled; alternate placement and "
            "ASLR-off results are diagnostics, not equal promotion gates"),
        "serious_launches_per_setting": args.serious_launches,
        "observations_per_label_per_launch": 96,
        "settings": settings,
    }
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    shutil.copy2(LOCK_PATH, args.output / "supercop.lock")
    print(f"selected {selected}; headline {primary}")
    print(json.dumps(settings[primary], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
