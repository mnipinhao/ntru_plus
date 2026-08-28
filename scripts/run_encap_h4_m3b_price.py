#!/usr/bin/env python3
"""Run fixed-ELF paired H4-M3B exact-egress pricing."""
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


PREFIX = "encap_h4_m3b_price"
LABELS = tuple(
    f"{PREFIX}_{variant}_{position}_cycles"
    for variant, position in (("control", "first"), ("candidate", "second"),
                              ("candidate", "first"), ("control", "second"))
)
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLACEMENT_REFERENCE = (
    REPO_ROOT / "ntruplus-ntt-Optimized/Additional_Implementation/avx2/"
    "NTRU+1152/experiments/avx2_gt9x16_official_001/results/"
    "encap-h-ingress-ma2-h3-price-intel155h-20260827-001/summary.json"
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
        raise SystemExit(f"H4-M3B price replay failed: {' '.join(command)}\n{result.stdout}")
    observed = {name: decode_observations(result.stdout, name) for name in LABELS}
    bad = {name: len(values) for name, values in observed.items() if len(values) != 96}
    if bad:
        raise SystemExit(f"H4-M3B price observation counts changed: {bad}")
    match = re.search(r"^encap_h4_m3b_price_runtime_addresses"
                      r"((?:\s+0x[0-9a-fA-F]+){2})$", result.stdout, re.M)
    if not match:
        raise SystemExit("H4-M3B price replay lacks two runtime addresses")
    return {"output": result.stdout, "observed": observed,
            "addresses": [int(x, 16) for x in match.group(1).split()]}


def stq2(observed: dict[str, list[int]], variant: str) -> float:
    values = (observed[f"{PREFIX}_{variant}_first_cycles"] +
              observed[f"{PREFIX}_{variant}_second_cycles"])
    return stabilized_quartiles(values)[1]


def analyze(records: list[dict]) -> dict:
    pooled = {name: [] for name in LABELS}
    launches = []
    for number, record in enumerate(records, 1):
        for name in LABELS:
            pooled[name] += record["observed"][name]
        control = stq2(record["observed"], "control")
        candidate = stq2(record["observed"], "candidate")
        launches.append({
            "launch": number,
            "control_stq2": control,
            "candidate_stq2": candidate,
            "candidate_minus_control_cycles": candidate - control,
        })

    combined = {}
    for variant in ("control", "candidate"):
        values = (pooled[f"{PREFIX}_{variant}_first_cycles"] +
                  pooled[f"{PREFIX}_{variant}_second_cycles"])
        q = stabilized_quartiles(values)
        combined[variant] = {"observations": len(values), "stq1": q[0],
                             "stq2": q[1], "stq3": q[2]}
    deltas = [float(row["candidate_minus_control_cycles"])
              for row in launches]
    addresses = [record["addresses"] for record in records]
    return {
        "combined": combined,
        "launches": launches,
        "evidence": {
            "median_cycles": statistics.median(deltas),
            "bootstrap_95pct_ci_median": bootstrap_median_ci(
                deltas, seed=0x48344D3342),
            "negative_launches": sum(value < 0 for value in deltas),
            "positive_launches": sum(value > 0 for value in deltas),
            "zero_launches": sum(value == 0 for value in deltas),
        },
        "runtime_addresses": addresses,
        "unique_runtime_address_tuples": len({tuple(value) for value in addresses}),
        "estimator_contract": {
            "operation": "balanced first/second StQ2 within each fresh launch",
            "delta": "H4-M3B candidate minus H4-M3 control",
            "headline": "median of nine launch-level deltas",
        },
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
    parser.add_argument("--launches", type=int, default=9)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    if args.launches < 1:
        raise SystemExit("--launches must be positive")
    if Path("/proc/sys/kernel/randomize_va_space").read_text().strip() == "0":
        raise SystemExit("ASLR-on controls require randomize_va_space != 0")
    placement_reference = json.loads(args.placement_reference.read_text())
    headline_placement = placement_reference["headline_setting"].split("-aslr-", 1)[0]
    if headline_placement not in ("normal", "reversed"):
        raise SystemExit("placement reference has an invalid headline setting")

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
                 "--cpu", str(args.cpu), "--mode", "derived-encap-h4-m3b-price",
                 "--fresh-launches", "1", "--result-dir", str(result),
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
            for number in range(1, args.launches + 1):
                record = launch(binaries[placement], args.cpu, aslr_off)
                (directory / f"launch-{number:02d}.out").write_text(record.pop("output"))
                records.append(record)
            (directory / "raw-observations.json").write_text(json.dumps(
                [{"launch": number, "addresses": record["addresses"],
                  "observed": record["observed"]}
                 for number, record in enumerate(records, 1)],
                indent=2, sort_keys=True) + "\n")
            settings[name] = analyze(records)
            unique = settings[name]["unique_runtime_address_tuples"]
            if (aslr_off and unique != 1) or (not aslr_off and unique < 2):
                raise SystemExit(f"ASLR address control failed for {name}: {unique}")

    headline_name = f"{headline_placement}-aslr-on"
    headline = settings[headline_name]["evidence"]
    summary = {
        **read_lock(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_class": "supercop-derived-encap-h4-m3b-price",
        "cpu": args.cpu,
        "compiler_policy": "fixed-common-O3GC",
        "compiler_wrapper": str(args.compiler_wrapper.resolve()),
        "compiler_wrapper_sha256": sha256_file(args.compiler_wrapper),
        "placement_policy": "predeclared from H3-price campaign",
        "placement_reference": str(args.placement_reference.resolve()),
        "placement_reference_sha256": sha256_file(args.placement_reference),
        "headline_setting": headline_name,
        "serious_launches_per_setting": args.launches,
        "observations_per_label_per_launch": 96,
        "boundary": "valid PK plus resident scale-1 r/m to exact ciphertext",
        "control": "H4-M3 canonical scratch plus Natural-Q H1 fallback",
        "candidate": "H4-M3B canonical scratch plus exact direct egress",
        "builds": build_records,
        "settings": settings,
        "headline_candidate_minus_control_cycles": headline["median_cycles"],
        "decision": "price exact egress only; no native KEM or automatic promotion",
        "native_kem_result": False,
    }
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    shutil.copy2(LOCK_PATH, args.output / "supercop.lock")
    print(json.dumps({"headline_setting": headline_name,
                      "candidate_minus_control":
                          summary["headline_candidate_minus_control_cycles"]},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
