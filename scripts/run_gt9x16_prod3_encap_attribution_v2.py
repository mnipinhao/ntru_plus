#!/usr/bin/env python3
"""Run serious fixed-ELF ENCAP-CALLER-ATTRIBUTION-V2 pricing."""
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

PREFIX = "gt9x16_prod3_encap_attribution_v2"
BOUNDARIES = ("producer_r", "producer_m", "dual_r", "tail")
LABELS = tuple(
    f"{PREFIX}_{boundary}_{variant}_{position}_cycles"
    for boundary in BOUNDARIES
    for variant, position in (("official", "first"), ("gt", "second"),
                              ("gt", "first"), ("official", "second"))
)
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_NATIVE_SUMMARY = (
    REPO_ROOT / "ntruplus-ntt-Optimized/Additional_Implementation/avx2/"
    "NTRU+1152/experiments/avx2_gt9x16_official_001/results/"
    "gt9x16-prod3-cumulative-native-rebase-intel155h-20260827-001/summary.json"
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
        raise SystemExit(f"attribution V2 replay failed: {' '.join(command)}\n{result.stdout}")
    observed = {name: decode_observations(result.stdout, name) for name in LABELS}
    bad = {name: len(values) for name, values in observed.items() if len(values) != 96}
    if bad:
        raise SystemExit(f"attribution V2 observation counts changed: {bad}")
    match = re.search(r"^gt9x16_prod3_encap_attribution_v2_runtime_addresses"
                      r"((?:\s+0x[0-9a-fA-F]+){10})$", result.stdout, re.M)
    if not match:
        raise SystemExit("attribution V2 replay lacks ten runtime addresses")
    return {"output": result.stdout, "observed": observed,
            "addresses": [int(x, 16) for x in match.group(1).split()]}


def stq2(observed: dict[str, list[int]], boundary: str, variant: str) -> float:
    values = (observed[f"{PREFIX}_{boundary}_{variant}_first_cycles"] +
              observed[f"{PREFIX}_{boundary}_{variant}_second_cycles"])
    return stabilized_quartiles(values)[1]


def analyze(records: list[dict]) -> dict:
    pooled = {name: [] for name in LABELS}
    launches = []
    for number, record in enumerate(records, 1):
        for name in LABELS:
            pooled[name] += record["observed"][name]
        row: dict[str, object] = {"launch": number}
        deltas = {}
        for boundary in BOUNDARIES:
            official = stq2(record["observed"], boundary, "official")
            gt = stq2(record["observed"], boundary, "gt")
            deltas[boundary] = gt - official
            row.update({f"{boundary}_official_stq2": official,
                        f"{boundary}_gt_stq2": gt,
                        f"{boundary}_gt_minus_official_cycles": gt - official})
        row["hash_fanout_excess_cycles"] = (
            deltas["dual_r"] - deltas["producer_r"])
        row["rough_modeled_debt_cycles"] = (
            deltas["producer_m"] + deltas["dual_r"] + deltas["tail"])
        launches.append(row)
    combined = {}
    evidence = {}
    for boundary in BOUNDARIES:
        for variant in ("official", "gt"):
            values = (pooled[f"{PREFIX}_{boundary}_{variant}_first_cycles"] +
                      pooled[f"{PREFIX}_{boundary}_{variant}_second_cycles"])
            q = stabilized_quartiles(values)
            combined[f"{boundary}_{variant}"] = {
                "observations": len(values), "stq1": q[0], "stq2": q[1],
                "stq3": q[2]}
        deltas = [float(row[f"{boundary}_gt_minus_official_cycles"])
                  for row in launches]
        evidence[boundary] = {
            "gt_faster_launches": sum(x < 0 for x in deltas),
            "gt_slower_launches": sum(x > 0 for x in deltas),
            "median_gt_minus_official_cycles": statistics.median(deltas),
            "bootstrap_95pct_ci_median_delta":
                bootstrap_median_ci(deltas, seed=0xA772 + len(boundary)),
        }
    for metric in ("hash_fanout_excess_cycles", "rough_modeled_debt_cycles"):
        values = [float(row[metric]) for row in launches]
        evidence[metric] = {
            "median_cycles": statistics.median(values),
            "bootstrap_95pct_ci_median":
                bootstrap_median_ci(values, seed=0xA772 + len(metric)),
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
    parser.add_argument("--native-summary", type=Path,
                        default=DEFAULT_NATIVE_SUMMARY)
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
                 "derived-gt9x16-prod3-encap-attribution-v2",
                 "--fresh-launches", "9", "--result-dir", str(result),
                 "--compiler-wrapper", str(args.compiler_wrapper),
                 "--require-frequency-control"])
        binaries[placement] = result / "measure"
        generic = json.loads((result / "stq-summary.json").read_text())
        ops = generic["balanced_combined_operations"]
        selection[placement] = sum(
            ops[f"{PREFIX}_{boundary}_gt_cycles"]["stq2"]
            for boundary in ("dual_r", "producer_m", "tail")
        )
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
    headline = settings[f"{selected}-aslr-on"]
    native_report = json.loads(args.native_summary.read_text())
    native_gap = native_report["operations"]["enc_cycles"]["delta_cycles"]
    modeled = headline["evidence"]["rough_modeled_debt_cycles"]["median_cycles"]
    debts = {
        boundary: headline["evidence"][boundary]["median_gt_minus_official_cycles"]
        for boundary in BOUNDARIES
    }
    hash_excess = headline["evidence"]["hash_fanout_excess_cycles"]["median_cycles"]
    components = {"r_producer": debts["producer_r"],
                  "m_producer": debts["producer_m"],
                  "r_excess_hash_fanout": hash_excess,
                  "h_ma2_ciphertext_tail": debts["tail"]}
    largest = max(components, key=lambda key: abs(components[key]))
    residual = native_gap - modeled
    decision = ("measure-caller-dependency-chain" if abs(residual) > 300 else
                f"attack-largest-component:{largest}")
    summary = {
        **read_lock(), "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_class": "supercop-derived-gt9x16-prod3-encap-attribution-v2",
        "candidate": "persistent-AoS + Natural-Q + T0-beta + scale4 MA2 + Direct H1",
        "cpu": args.cpu, "compiler_policy": "fixed-common-O3GC",
        "compiler_wrapper": str(args.compiler_wrapper.resolve()),
        "compiler_wrapper_sha256": sha256_file(args.compiler_wrapper),
        "selection_policy": "minimum absolute GT StQ2 sum for dual-r + m producer + tail from independent SUPERCOP builds",
        "selection_gt_modeled_path_stq2": selection,
        "selected_placement": selected,
        "headline_setting": f"{selected}-aslr-on",
        "serious_launches_per_setting": 9,
        "observations_per_label_per_launch": 96,
        "builds": build_records, "settings": settings,
        "headline_component_balance": components,
        "headline_rough_modeled_debt_cycles": modeled,
        "reference_native_enc_gap_cycles": native_gap,
        "reference_native_result": "gt9x16-prod3-cumulative-native-rebase-intel155h-20260827-001",
        "reference_native_summary_sha256": sha256_file(args.native_summary),
        "cross_campaign_residual_cycles": residual,
        "additivity_warning": "island debts and native gap are not expected to add exactly because cache, placement, dependency overlap, and hash_g/SOTP are cut out",
        "corrected_single_inv4_qorder_sidecar": "not-run: would require a new current-Q scale4 machine object, outside the no-new-ASM cheap-sidecar boundary",
        "largest_component_by_absolute_median": largest,
        "decision": decision,
        "native_kem_result": False,
    }
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    shutil.copy2(LOCK_PATH, args.output / "supercop.lock")
    print(json.dumps({"selected": selected, "components": components,
                      "modeled": modeled, "native_gap": native_gap,
                      "residual": residual, "decision": decision}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
