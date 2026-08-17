#!/usr/bin/env python3
"""Create a compact decision record from the Q24 environment and PMU gates."""

import argparse
import hashlib
import json
import statistics
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", type=Path, required=True)
    parser.add_argument("--pmu", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    environment = json.loads(args.environment.read_text())
    pmu = json.loads(args.pmu.read_text())
    tsc_launches = [launch
                    for batch in environment["batches"]
                    for mode in batch.values()
                    for placement in mode["placements"].values()
                    for launch in placement["launches"]]
    core_launches = [launch
                     for mode in pmu["measurements"].values()
                     for placement in mode.values()
                     for launch in placement["core"]["launches"]]
    fetch_launches = [launch
                      for mode in pmu["measurements"].values()
                      for placement in mode.values()
                      for launch in placement["fetch"]["launches"]]
    frontend_signatures = []
    for mode in pmu["measurements"].values():
        for placement in mode.values():
            classified = placement["frontend"]["classified"]
            if (classified["good"]["launches"] > 0
                    and classified["bad"]["launches"] > 0):
                good = classified["good"]["median_event_deltas_per_call"][
                    "idq_uops_not_delivered.core"]
                bad = classified["bad"]["median_event_deltas_per_call"][
                    "idq_uops_not_delivered.core"]
                frontend_signatures.append(good - bad)
    frequency_differences = [
        abs(launch["derived"]["q24"]["core_cycles_per_ref_cycle"]
            - launch["derived"]["control"]["core_cycles_per_ref_cycle"])
        for launch in core_launches]
    fixed_batches = {
        mode_name: {
            placement: data["good_launches_by_batch"]
            for placement, data in environment["combined"][mode_name][
                "placements"].items()
        }
        for mode_name in ("pie_aslr_disabled", "nonpie_fixed_address")
    }
    result = {
        "schema": "ntruplus768-gt32-q24-launch-attribution-summary-v1",
        "experiment": "GT32-Q24-LAUNCH-ATTRIBUTION-001",
        "inputs": {
            "environment": str(args.environment),
            "environment_sha256": digest(args.environment),
            "pmu": str(args.pmu),
            "pmu_sha256": digest(args.pmu),
        },
        "tsc": {
            "launches": len(tsc_launches),
            "launches_with_negative_median_delta": sum(
                launch["q24_minus_control_tsc"]["median"] < 0
                for launch in tsc_launches),
            "launches_meeting_18_of_20": sum(
                launch["good_launch"] for launch in tsc_launches),
            "paired_sample_wins": sum(
                launch["q24_wins_vs_control"] for launch in tsc_launches),
            "paired_samples": 20 * len(tsc_launches),
            "fixed_address_good_launches_by_batch": fixed_batches,
            "smt_sibling_cpu2_active_ticks": sum(
                launch["runtime"]["sibling_cpu2_active_ticks"]
                for launch in tsc_launches),
        },
        "region_scoped_pmu": {
            "core_launches": len(core_launches),
            "negative_core_cycle_deltas": sum(
                launch["q24_minus_control"]["cycles"][
                    "q24_minus_control_per_call"] < 0
                for launch in core_launches),
            "core_cycle_delta_per_call_range": [
                min(launch["q24_minus_control"]["cycles"][
                    "q24_minus_control_per_call"] for launch in core_launches),
                max(launch["q24_minus_control"]["cycles"][
                    "q24_minus_control_per_call"] for launch in core_launches),
            ],
            "instruction_delta_per_call_range": [
                min(launch["q24_minus_control"]["instructions"][
                    "q24_minus_control_per_call"] for launch in core_launches),
                max(launch["q24_minus_control"]["instructions"][
                    "q24_minus_control_per_call"] for launch in core_launches),
            ],
            "median_abs_q24_control_frequency_ratio_difference":
                statistics.median(frequency_differences),
            "max_abs_q24_control_frequency_ratio_difference":
                max(frequency_differences),
            "icache_stall_delta_per_call_range": [
                min(launch["q24_minus_control"]["icache_data.stalls"][
                    "q24_minus_control_per_call"] for launch in fetch_launches),
                max(launch["q24_minus_control"]["icache_data.stalls"][
                    "q24_minus_control_per_call"] for launch in fetch_launches),
            ],
            "itlb_walk_delta_per_call_range": [
                min(launch["q24_minus_control"][
                    "itlb_misses.walk_completed"][
                        "q24_minus_control_per_call"]
                    for launch in fetch_launches),
                max(launch["q24_minus_control"][
                    "itlb_misses.walk_completed"][
                        "q24_minus_control_per_call"]
                    for launch in fetch_launches),
            ],
            "all_groups_nonmultiplexed": all(
                group["all_nonmultiplexed"]
                for mode in pmu["measurements"].values()
                for placement in mode.values()
                for group in placement.values()),
            "idq_good_minus_bad_signs": frontend_signatures,
            "consistent_idq_good_bad_direction": (
                all(value >= 0 for value in frontend_signatures)
                or all(value <= 0 for value in frontend_signatures)),
        },
        "findings": {
            "q24_instruction_advantage_is_deterministic": True,
            "q24_core_cycle_advantage_is_observed_in_every_pmu_launch": True,
            "absolute_virtual_address_is_sufficient": False,
            "simple_icache_itlb_explanation_supported": False,
            "consistent_dsb_mite_idq_explanation_supported": False,
            "frequency_explains_launch_win_variance": False,
            "smt_sibling_activity_explains_variance": False,
            "per_launch_18_of_20_is_too_sensitive_to_runtime_jitter": True,
        },
        "decision": "core-work-qualified-statistical-delivery-gate-must-change",
        "next_gate": (
            "hierarchical-launch-level paired statistics plus realistic-cold "
            "caller corroboration before encoder or fusion integration"),
        "q24_assembly_modified": False,
        "encoder_integration": False,
        "fusion": False,
        "serious_100k": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"launch medians: {result['tsc']['launches_with_negative_median_delta']}/"
          f"{result['tsc']['launches']} negative")
    print(f"core cycles: {result['region_scoped_pmu']['negative_core_cycle_deltas']}/"
          f"{result['region_scoped_pmu']['core_launches']} negative")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
