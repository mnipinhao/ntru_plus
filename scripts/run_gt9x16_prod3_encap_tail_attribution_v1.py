#!/usr/bin/env python3
"""Run serious fixed-ELF ENCAP-TAIL-ATTRIBUTION-V1 pricing."""
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

PREFIX = "gt9x16_prod3_encap_tail_attribution_v1"
BOUNDARIES = ("t0", "t1", "t2")
COMPONENTS = ("resident_h_projection", "ma2_arithmetic", "ciphertext_serialization")
LABELS = tuple(
    f"{PREFIX}_{boundary}_{variant}_{position}_cycles"
    for boundary in BOUNDARIES
    for variant, position in (("official", "first"), ("gt", "second"),
                              ("gt", "first"), ("official", "second"))
)
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLACEMENT_REFERENCE = (
    REPO_ROOT / "ntruplus-ntt-Optimized/Additional_Implementation/avx2/"
    "NTRU+1152/experiments/avx2_gt9x16_official_001/results/"
    "gt9x16-prod3-encap-attribution-v2-intel155h-20260827-001/summary.json"
)


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
        raise SystemExit(f"tail V1 replay failed: {' '.join(command)}\n{result.stdout}")
    observed = {name: decode_observations(result.stdout, name) for name in LABELS}
    bad = {name: len(values) for name, values in observed.items() if len(values) != 96}
    if bad:
        raise SystemExit(f"tail V1 observation counts changed: {bad}")
    match = re.search(r"^gt9x16_prod3_encap_tail_attribution_v1_runtime_addresses"
                      r"((?:\s+0x[0-9a-fA-F]+){10})$", result.stdout, re.M)
    if not match:
        raise SystemExit("tail V1 replay lacks ten runtime addresses")
    return {"output": result.stdout, "observed": observed,
            "addresses": [int(x, 16) for x in match.group(1).split()]}


def stq2(observed: dict[str, list[int]], boundary: str, variant: str) -> float:
    values = (observed[f"{PREFIX}_{boundary}_{variant}_first_cycles"] +
              observed[f"{PREFIX}_{boundary}_{variant}_second_cycles"])
    return stabilized_quartiles(values)[1]


def summarize_values(values: list[float], seed: int) -> dict:
    return {
        "median_cycles": statistics.median(values),
        "bootstrap_95pct_ci_median": bootstrap_median_ci(values, seed=seed),
        "negative_launches": sum(value < 0 for value in values),
        "positive_launches": sum(value > 0 for value in values),
        "zero_launches": sum(value == 0 for value in values),
    }


def analyze(records: list[dict]) -> dict:
    pooled = {name: [] for name in LABELS}
    launches = []
    for number, record in enumerate(records, 1):
        for name in LABELS:
            pooled[name] += record["observed"][name]
        deltas = {}
        row: dict[str, object] = {"launch": number}
        for boundary in BOUNDARIES:
            official = stq2(record["observed"], boundary, "official")
            gt = stq2(record["observed"], boundary, "gt")
            delta = gt - official
            deltas[boundary] = delta
            row.update({f"{boundary}_official_stq2": official,
                        f"{boundary}_gt_stq2": gt,
                        f"{boundary}_gt_minus_official_cycles": delta})
        components = {
            "resident_h_projection": deltas["t0"],
            "ma2_arithmetic": deltas["t1"] - deltas["t0"],
            "ciphertext_serialization": deltas["t2"] - deltas["t1"],
        }
        reconstructed = sum(components.values())
        row.update({f"component_{name}_cycles": value
                    for name, value in components.items()})
        row["component_reconstructed_t2_cycles"] = reconstructed
        row["telescoping_residual_cycles"] = reconstructed - deltas["t2"]
        launches.append(row)

    combined = {}
    for boundary in BOUNDARIES:
        for variant in ("official", "gt"):
            values = (pooled[f"{PREFIX}_{boundary}_{variant}_first_cycles"] +
                      pooled[f"{PREFIX}_{boundary}_{variant}_second_cycles"])
            q = stabilized_quartiles(values)
            combined[f"{boundary}_{variant}"] = {
                "observations": len(values), "stq1": q[0], "stq2": q[1],
                "stq3": q[2]}

    boundary_evidence = {}
    for index, boundary in enumerate(BOUNDARIES):
        values = [float(row[f"{boundary}_gt_minus_official_cycles"])
                  for row in launches]
        boundary_evidence[boundary] = summarize_values(values, 0x7A110 + index)
    component_evidence = {}
    for index, component in enumerate(COMPONENTS):
        values = [float(row[f"component_{component}_cycles"])
                  for row in launches]
        component_evidence[component] = summarize_values(values, 0x7A120 + index)
    reconstructed = [float(row["component_reconstructed_t2_cycles"])
                     for row in launches]
    t2 = [float(row["t2_gt_minus_official_cycles"]) for row in launches]
    residuals = [abs(float(row["telescoping_residual_cycles"])) for row in launches]
    if max(residuals, default=0.0) > 1e-9 or reconstructed != t2:
        raise SystemExit("tail V1 launch-level telescoping identity failed")

    addresses = [record["addresses"] for record in records]
    return {
        "combined": combined,
        "launches": launches,
        "boundary_evidence": boundary_evidence,
        "component_evidence": component_evidence,
        "estimator_contract": {
            "boundary": "per-launch balanced Official/GT StQ2 difference",
            "components": "differences of nested boundary deltas within the same launch",
            "headline": "median across nine launch-level estimates",
            "warning": "component medians are for ranking and are not summed; telescoping is checked per launch",
        },
        "telescoping": {
            "identity": "H + M + S = delta(T2)",
            "launches_checked": len(launches),
            "max_absolute_residual_cycles": max(residuals, default=0.0),
            "median_reconstructed_t2_cycles": statistics.median(reconstructed),
            "median_direct_t2_cycles": statistics.median(t2),
        },
        "runtime_addresses": addresses,
        "unique_runtime_address_tuples": len({tuple(x) for x in addresses}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--normal-implementation", required=True)
    parser.add_argument("--reversed-implementation", required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--compiler-wrapper", type=Path, required=True)
    parser.add_argument("--placement-reference", type=Path,
                        default=DEFAULT_PLACEMENT_REFERENCE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    if Path("/proc/sys/kernel/randomize_va_space").read_text().strip() == "0":
        raise SystemExit("ASLR-on controls require randomize_va_space != 0")
    placement_reference = json.loads(args.placement_reference.read_text())
    headline_placement = placement_reference["selected_placement"]
    if headline_placement not in ("normal", "reversed"):
        raise SystemExit("placement reference has an invalid selected_placement")

    args.output.mkdir(parents=True)
    builds = args.output / "builds"
    builds.mkdir()
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
                 "derived-gt9x16-prod3-encap-tail-attribution-v1",
                 "--fresh-launches", "9", "--result-dir", str(result),
                 "--compiler-wrapper", str(args.compiler_wrapper),
                 "--require-frequency-control"])
        binaries[placement] = result / "measure"
        build_records[placement] = {
            "implementation": implementation,
            "measure_sha256": sha256_file(result / "measure"),
            "metadata_sha256": sha256_file(result / "metadata.json"),
        }

    settings_root = args.output / "settings"
    settings_root.mkdir()
    settings = {}
    for placement in ("normal", "reversed"):
        for aslr_off in (False, True):
            name = f"{placement}-aslr-{'off' if aslr_off else 'on'}"
            directory = settings_root / name
            directory.mkdir()
            records = []
            for number in range(1, 10):
                record = launch(binaries[placement], args.cpu, aslr_off)
                (directory / f"launch-{number:02d}.out").write_text(record.pop("output"))
                records.append(record)
            settings[name] = analyze(records)
            unique = settings[name]["unique_runtime_address_tuples"]
            if (aslr_off and unique != 1) or (not aslr_off and unique < 2):
                raise SystemExit(f"ASLR address control failed for {name}: {unique}")

    headline_name = f"{headline_placement}-aslr-on"
    headline = settings[headline_name]
    component_medians = {
        name: headline["component_evidence"][name]["median_cycles"]
        for name in COMPONENTS
    }
    largest = max(component_medians, key=lambda name: abs(component_medians[name]))
    summary = {
        **read_lock(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_class": "supercop-derived-gt9x16-prod3-encap-tail-attribution-v1",
        "candidate": "persistent-AoS + Natural-Q + T0-beta + scale4 MA2 + Direct H1",
        "cpu": args.cpu,
        "compiler_policy": "fixed-common-O3GC",
        "compiler_wrapper": str(args.compiler_wrapper.resolve()),
        "compiler_wrapper_sha256": sha256_file(args.compiler_wrapper),
        "placement_policy": "predeclared from completed ENCAP-CALLER-ATTRIBUTION-V2; current Tail V1 observations are not used for selection",
        "placement_reference": str(args.placement_reference.resolve()),
        "placement_reference_sha256": sha256_file(args.placement_reference),
        "headline_placement": headline_placement,
        "headline_setting": headline_name,
        "serious_launches_per_setting": 9,
        "observations_per_label_per_launch": 96,
        "boundaries": {
            "T0": "resident h projection",
            "T1": "resident h projection + MA2 arithmetic",
            "T2": "resident h projection + MA2 arithmetic + ciphertext serialization",
        },
        "starting_residency": "every balanced T0/T1/T2 entry independently resets coefficients and prepares identical semantic r/m/h states outside timing",
        "single_inv4_contract": "GT T2 uses scale-4 MA2 and exactly one Direct H1 inv4",
        "preflight": "resident-h raw map exact; T1 semantic bytes exact; GT T2 equals cumulative production path equals Official bytes",
        "builds": build_records,
        "settings": settings,
        "headline_component_medians_cycles": component_medians,
        "headline_t2_delta_cycles": headline["boundary_evidence"]["t2"]["median_cycles"],
        "largest_component_by_absolute_launch_median": largest,
        "decision": f"attack-largest-tail-component:{largest}",
        "forward_lazy_reduction_status": "ready-for-serious-pricing; not included in this cumulative tail baseline",
        "new_asm": False,
        "native_kem_result": False,
    }
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    shutil.copy2(LOCK_PATH, args.output / "supercop.lock")
    print(json.dumps({"headline_setting": headline_name,
                      "t2_delta_cycles": summary["headline_t2_delta_cycles"],
                      "components": component_medians,
                      "largest": largest}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
