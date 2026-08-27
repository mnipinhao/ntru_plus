#!/usr/bin/env python3
"""Run serious producer and frozen-caller Natural-Q T0-beta pricing."""
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

PREFIX = "gt9x16_prod3_t0_beta_price"
WIDTHS = ("1x", "2x", "caller")
LABELS = tuple(
    f"{PREFIX}_{width}_{variant}_{position}_cycles"
    for width in WIDTHS
    for variant, position in (("control", "first"),
                              ("candidate", "second"),
                              ("candidate", "first"),
                              ("control", "second")))


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
        raise SystemExit(f"T0-beta replay failed: {' '.join(command)}\n{result.stdout}")
    observed = {name: decode_observations(result.stdout, name) for name in LABELS}
    bad = {name: len(values) for name, values in observed.items() if len(values) != 96}
    if bad:
        raise SystemExit(f"T0-beta observation counts changed: {bad}")
    match = re.search(r"^gt9x16_prod3_t0_beta_price_runtime_addresses"
                      r"((?:\s+0x[0-9a-fA-F]+){8})$", result.stdout, re.M)
    if not match:
        raise SystemExit("T0-beta replay lacks eight runtime addresses")
    return {"output": result.stdout, "observed": observed,
            "addresses": [int(x, 16) for x in match.group(1).split()]}


def stq2(observed: dict[str, list[int]], width: str, variant: str) -> float:
    values = (observed[f"{PREFIX}_{width}_{variant}_first_cycles"] +
              observed[f"{PREFIX}_{width}_{variant}_second_cycles"])
    return stabilized_quartiles(values)[1]


def analyze(records: list[dict]) -> dict:
    pooled = {name: [] for name in LABELS}
    launches = []
    for number, record in enumerate(records, 1):
        for name in LABELS:
            pooled[name] += record["observed"][name]
        row: dict[str, object] = {"launch": number}
        for width in WIDTHS:
            control = stq2(record["observed"], width, "control")
            candidate = stq2(record["observed"], width, "candidate")
            row.update({f"{width}_control_stq2": control,
                        f"{width}_candidate_stq2": candidate,
                        f"{width}_candidate_minus_control_cycles":
                            candidate - control})
        launches.append(row)
    combined = {}
    evidence = {}
    for width in WIDTHS:
        for variant in ("control", "candidate"):
            values = (pooled[f"{PREFIX}_{width}_{variant}_first_cycles"] +
                      pooled[f"{PREFIX}_{width}_{variant}_second_cycles"])
            q = stabilized_quartiles(values)
            combined[f"{width}_{variant}"] = {
                "observations": len(values), "stq1": q[0], "stq2": q[1],
                "stq3": q[2]}
        deltas = [float(row[f"{width}_candidate_minus_control_cycles"])
                  for row in launches]
        evidence[width] = {
            "candidate_faster_launches": sum(x < 0 for x in deltas),
            "candidate_slower_launches": sum(x > 0 for x in deltas),
            "median_candidate_minus_control_cycles": statistics.median(deltas),
            "bootstrap_95pct_ci_median_delta":
                bootstrap_median_ci(deltas, seed=0x70B0 + len(width)),
        }
    addresses = [record["addresses"] for record in records]
    return {"combined": combined, "launches": launches, "evidence": evidence,
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
    selection = {}
    for placement, implementation in implementations.items():
        result = builds / placement
        checked(["python3", str(runner), "--campaign-root", str(args.campaign_root),
                 "--parameter", "1152", "--implementation", implementation,
                 "--cpu", str(args.cpu), "--mode",
                 "derived-gt9x16-prod3-t0-beta-price", "--fresh-launches", "9",
                 "--result-dir", str(result), "--compiler-wrapper",
                 str(args.compiler_wrapper), "--require-frequency-control"])
        binaries[placement] = result / "measure"
        generic = json.loads((result / "stq-summary.json").read_text())
        caller = generic["balanced_combined_operations"][
            f"{PREFIX}_caller_candidate_cycles"]["stq2"]
        selection[placement] = caller
        build_records[placement] = {
            "implementation": implementation,
            "measure_sha256": sha256_file(result / "measure"),
            "metadata_sha256": sha256_file(result / "metadata.json"),
        }
    selected = min(selection, key=lambda x: (selection[x], x != "normal"))
    settings_root = args.output / "settings"; settings_root.mkdir()
    settings = {}
    for placement in ("normal", "reversed"):
        for aslr_off in (False, True):
            name = f"{placement}-aslr-{'off' if aslr_off else 'on'}"
            directory = settings_root / name; directory.mkdir()
            records = []
            for number in range(1, 10):
                record = launch(binaries[placement], args.cpu, aslr_off)
                (directory / f"launch-{number:02d}.out").write_text(
                    record.pop("output"))
                records.append(record)
            settings[name] = analyze(records)
            unique = settings[name]["unique_runtime_address_tuples"]
            if (aslr_off and unique != 1) or (not aslr_off and unique < 2):
                raise SystemExit(f"ASLR address control failed for {name}: {unique}")
    producer_stable = all(value["evidence"]["2x"][
        "median_candidate_minus_control_cycles"] < 0 for value in settings.values())
    caller_stable = all(value["evidence"]["caller"][
        "median_candidate_minus_control_cycles"] < 0 for value in settings.values())
    decision = ("promote-to-natural-q-prod3-research-baseline"
                if producer_stable and caller_stable else
                "retain-local-only" if producer_stable else "reject")
    summary = {
        **read_lock(), "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_class": "supercop-derived-gt9x16-prod3-t0-beta-price",
        "boundary": "producer 1x/2x and frozen Natural-Q resident-h/MA2/H1 caller",
        "semantic_contract": "Natural-Q scale-4 equality modulo q; raw representative may differ",
        "caller_contract": "exact ciphertext and hash bytes",
        "cpu": args.cpu, "compiler_policy": "fixed-common-O3GC",
        "compiler_wrapper": str(args.compiler_wrapper.resolve()),
        "compiler_wrapper_sha256": sha256_file(args.compiler_wrapper),
        "selection_policy": "minimum absolute candidate caller StQ2 from independent SUPERCOP builds",
        "selection_candidate_caller_stq2": selection,
        "selected_placement": selected,
        "headline_setting": f"{selected}-aslr-on",
        "serious_launches_per_setting": 9,
        "observations_per_label_per_launch": 96,
        "builds": build_records, "settings": settings,
        "schedule_vs_linked_accounting": {
            "schedule_constant_operands": [666, 650],
            "linked_natural_q_constant_operands": [594, 578],
            "schedule_rodata_delta_bytes": 448,
            "linked_rodata_delta_bytes": 416,
            "explanation": "absolute baseline taxonomy and linked retained set differ; -16 operand direction agrees",
        },
        "producer_2x_direction_stable": producer_stable,
        "caller_direction_stable": caller_stable,
        "decision": decision, "native_kem_result": False,
    }
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    shutil.copy2(LOCK_PATH, args.output / "supercop.lock")
    print(json.dumps({"selected": selected, "decision": decision,
                      "deltas": {name: {width: data["evidence"][width][
                          "median_candidate_minus_control_cycles"]
                          for width in WIDTHS}
                          for name, data in settings.items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
