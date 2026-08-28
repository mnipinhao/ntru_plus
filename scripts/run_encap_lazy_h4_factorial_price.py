#!/usr/bin/env python3
"""Run same-ELF serious Lazy x H4 2x2 pricing."""
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


PREFIX = "encap_lazy_h4_factorial_price"
VARIANTS = ("c00", "c10", "c01", "c11")
LABELS = tuple(
    f"{PREFIX}_{variant}_pos{position}_cycles"
    for variant in VARIANTS for position in range(4)
)
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLACEMENT_REFERENCE = (
    REPO_ROOT / "ntruplus-ntt-Optimized/Additional_Implementation/avx2/"
    "NTRU+1152/experiments/avx2_gt9x16_official_001/results/"
    "encap-h4-m3b-price-intel155h-20260828-001/summary.json"
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
        raise SystemExit(f"factorial replay failed: {' '.join(command)}\n{result.stdout}")
    observed = {name: decode_observations(result.stdout, name) for name in LABELS}
    bad = {name: len(values) for name, values in observed.items()
           if len(values) != 96}
    if bad:
        raise SystemExit(f"factorial observation counts changed: {bad}")
    match = re.search(r"^encap_lazy_h4_factorial_price_runtime_addresses"
                      r"((?:\s+0x[0-9a-fA-F]+){4})$", result.stdout, re.M)
    if not match:
        raise SystemExit("factorial replay lacks four runtime addresses")
    return {"output": result.stdout, "observed": observed,
            "addresses": [int(x, 16) for x in match.group(1).split()]}


def variant_stq2(observed: dict[str, list[int]], variant: str) -> float:
    values: list[int] = []
    for position in range(4):
        values += observed[f"{PREFIX}_{variant}_pos{position}_cycles"]
    return stabilized_quartiles(values)[1]


def effects(cells: dict[str, float]) -> dict[str, float]:
    lazy_h0 = cells["c10"] - cells["c00"]
    h4_l0 = cells["c01"] - cells["c00"]
    lazy_h1 = cells["c11"] - cells["c01"]
    h4_l1 = cells["c11"] - cells["c10"]
    interaction = cells["c11"] - cells["c10"] - cells["c01"] + cells["c00"]
    return {
        "lazy_at_h4_off": lazy_h0,
        "h4_at_lazy_off": h4_l0,
        "lazy_at_h4_on": lazy_h1,
        "h4_at_lazy_on": h4_l1,
        "lazy_main_effect": (lazy_h0 + lazy_h1) / 2.0,
        "h4_main_effect": (h4_l0 + h4_l1) / 2.0,
        "interaction": interaction,
        "c11_minus_c00": cells["c11"] - cells["c00"],
    }


def analyze(records: list[dict]) -> dict:
    pooled = {name: [] for name in LABELS}
    launches = []
    for number, record in enumerate(records, 1):
        for name in LABELS:
            pooled[name] += record["observed"][name]
        cells = {variant: variant_stq2(record["observed"], variant)
                 for variant in VARIANTS}
        launches.append({"launch": number, "cells": cells,
                         "effects": effects(cells)})

    combined = {}
    for variant in VARIANTS:
        values: list[int] = []
        for position in range(4):
            values += pooled[f"{PREFIX}_{variant}_pos{position}_cycles"]
        quartiles = stabilized_quartiles(values)
        combined[variant] = {"observations": len(values),
                             "stq1": quartiles[0], "stq2": quartiles[1],
                             "stq3": quartiles[2]}

    evidence = {}
    for name in effects({variant: 0.0 for variant in VARIANTS}):
        values = [float(row["effects"][name]) for row in launches]
        evidence[name] = {
            "median_cycles": statistics.median(values),
            "bootstrap_95pct_ci_median": bootstrap_median_ci(
                values, seed=0x324C4834 + sum(map(ord, name))),
            "negative_launches": sum(value < 0 for value in values),
            "positive_launches": sum(value > 0 for value in values),
            "zero_launches": sum(value == 0 for value in values),
        }
    addresses = [record["addresses"] for record in records]
    return {
        "combined": combined,
        "launches": launches,
        "evidence": evidence,
        "runtime_addresses": addresses,
        "unique_runtime_address_tuples": len({tuple(value) for value in addresses}),
        "estimator_contract": {
            "cell": "StQ2 pooled over all four balanced positions within each fresh launch",
            "effects": "launch-local cell contrasts followed by median over launches",
            "interaction": "C11-C10-C01+C00",
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
                 "--cpu", str(args.cpu),
                 "--mode", "derived-encap-lazy-h4-factorial-price",
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
                (directory / f"launch-{number:02d}.out").write_text(
                    record.pop("output"))
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
        "benchmark_class": "supercop-derived-encap-lazy-h4-factorial-price",
        "cpu": args.cpu,
        "compiler_policy": "fixed-common-O3GC",
        "compiler_wrapper": str(args.compiler_wrapper.resolve()),
        "compiler_wrapper_sha256": sha256_file(args.compiler_wrapper),
        "placement_policy": "predeclared from H4-M3B serious campaign",
        "placement_reference": str(args.placement_reference.resolve()),
        "placement_reference_sha256": sha256_file(args.placement_reference),
        "headline_setting": headline_name,
        "serious_launches_per_setting": args.launches,
        "observations_per_cell_per_launch": 384,
        "boundary": "coefficient-domain small r/m plus valid PK bytes to exact ciphertext",
        "cells": {
            "C00": "current forward plus scale4 H3 plus H1",
            "C10": "lazy forward plus scale4 H3 plus H1",
            "C01": "current scale1 forward plus H4-M3B",
            "C11": "lazy scale1 forward plus H4-M3B",
        },
        "excluded": "r hash fanout, hash_g, SOTP, native KEM",
        "builds": build_records,
        "settings": settings,
        "headline_effects": headline,
        "decision": "select integrated cell before native KEM Rebase #2",
        "native_kem_result": False,
    }
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    shutil.copy2(LOCK_PATH, args.output / "supercop.lock")
    print(json.dumps({"headline_setting": headline_name,
                      "headline_effects": {
                          name: item["median_cycles"]
                          for name, item in headline.items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
