#!/usr/bin/env python3
"""Select PROD3 placement and price the unchanged MA2 consumer island."""

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

PREFIX = "gt9x16_prod3_consumer"
LABELS = (
    f"{PREFIX}_control_first_cycles",
    f"{PREFIX}_candidate_second_cycles",
    f"{PREFIX}_candidate_first_cycles",
    f"{PREFIX}_control_second_cycles",
)


def run_checked(command: list[str]) -> None:
    completed = subprocess.run(command, text=True)
    if completed.returncode:
        raise SystemExit(f"command failed ({completed.returncode}): {' '.join(command)}")


def short_stq2(result_dir: Path, variant: str) -> float:
    summary = json.loads((result_dir / "stq-summary.json").read_text(encoding="utf-8"))
    return float(summary["balanced_combined_operations"]
                        [f"{PREFIX}_{variant}_cycles"]["stq2"])


def launch(binary: Path, cpu: int, aslr_off: bool) -> tuple[str, dict[str, list[int]], list[int]]:
    command = ["taskset", "-c", str(cpu)]
    if aslr_off:
        command.extend(["setarch", platform.machine(), "-R"])
    command.append(str(binary.resolve()))
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    if completed.returncode:
        raise SystemExit(
            f"consumer replay failed ({completed.returncode}): {' '.join(command)}\n"
            f"{completed.stdout}")
    observed = {name: decode_observations(completed.stdout, name) for name in LABELS}
    bad = {name: len(values) for name, values in observed.items() if len(values) != 96}
    if bad:
        raise SystemExit(f"consumer replay observation counts are wrong: {bad}")
    match = re.search(
        r"^gt9x16_prod3_consumer_runtime_addresses"
        r"((?:\s+0x[0-9a-fA-F]+){5})$", completed.stdout, re.MULTILINE)
    if not match:
        raise SystemExit("consumer replay lacks five runtime symbol addresses")
    return completed.stdout, observed, [int(word, 16) for word in match.group(1).split()]


def launch_stq2(observed: dict[str, list[int]], variant: str) -> float:
    values = (observed[f"{PREFIX}_{variant}_first_cycles"] +
              observed[f"{PREFIX}_{variant}_second_cycles"])
    return stabilized_quartiles(values)[1]


def analyze(records: list[dict[str, object]]) -> dict[str, object]:
    pooled = {name: [] for name in LABELS}
    launches = []
    for record in records:
        observed = record["observed"]
        assert isinstance(observed, dict)
        for name in LABELS:
            pooled[name].extend(observed[name])
        control = launch_stq2(observed, "control")
        candidate = launch_stq2(observed, "candidate")
        launches.append({
            "launch": record["launch"],
            "control_stq2": control,
            "candidate_stq2": candidate,
            "candidate_minus_control_cycles": candidate - control,
        })
    combined = {}
    for variant in ("control", "candidate"):
        values = (pooled[f"{PREFIX}_{variant}_first_cycles"] +
                  pooled[f"{PREFIX}_{variant}_second_cycles"])
        quartiles = stabilized_quartiles(values)
        combined[variant] = {
            "observations": len(values), "stq1": quartiles[0],
            "stq2": quartiles[1], "stq3": quartiles[2],
        }
    deltas = [float(entry["candidate_minus_control_cycles"]) for entry in launches]
    addresses = [record["addresses"] for record in records]
    return {
        "combined": combined,
        "launches": launches,
        "candidate_faster_launches": sum(delta < 0 for delta in deltas),
        "candidate_slower_launches": sum(delta > 0 for delta in deltas),
        "median_candidate_minus_control_cycles": statistics.median(deltas),
        "bootstrap_95pct_ci_median_delta": bootstrap_median_ci(deltas, seed=0x5033),
        "runtime_addresses": addresses,
        "unique_runtime_address_tuples": len({tuple(row) for row in addresses}),
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
        raise SystemExit("consumer checkpoint requires 9 selection and 9 serious launches")
    if Path("/proc/sys/kernel/randomize_va_space").read_text().strip() == "0":
        raise SystemExit("SUPERCOP-like ASLR-on headline requires randomize_va_space != 0")
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
            "python3", str(run_script), "--campaign-root", str(args.campaign_root),
            "--parameter", "1152", "--implementation", implementation,
            "--cpu", str(args.cpu), "--mode", "derived-gt9x16-prod3-consumer",
            "--fresh-launches", "9", "--result-dir", str(result),
            "--compiler-wrapper", str(args.compiler_wrapper),
        ])
        selection[placement] = {
            "implementation": implementation,
            "candidate_stq2": short_stq2(result, "candidate"),
            "control_stq2": short_stq2(result, "control"),
            "measure_sha256": sha256_file(result / "measure"),
        }
    selected = min(selection, key=lambda placement: (
        selection[placement]["candidate_stq2"], placement != "reversed"))
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
    primary = f"{selected}-aslr-on"
    summary = {
        **read_lock(),
        "benchmark_class": "supercop-derived-gt9x16-prod3-consumer",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": args.cpu,
        "compiler_policy": "fixed-common-O3GC",
        "compiler_wrapper": str(args.compiler_wrapper.resolve()),
        "compiler_wrapper_sha256": sha256_file(args.compiler_wrapper),
        "selection_policy": "minimum absolute candidate StQ2 under independent ASLR-on selection",
        "selection": selection,
        "selected_placement": selected,
        "alternate_placement": alternate,
        "headline_setting": primary,
        "headline_rationale": (
            "SUPERCOP executes PIE with host ASLR enabled; alternate placement and "
            "ASLR-off results are diagnostics"),
        "serious_launches_per_setting": 9,
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
