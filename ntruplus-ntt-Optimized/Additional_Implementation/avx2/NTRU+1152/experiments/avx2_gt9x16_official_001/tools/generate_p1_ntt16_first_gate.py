#!/usr/bin/env python3
"""Gate the single shrunk-P1 NTT16-first/blocked 1152 challenger."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(schedule_path: Path) -> str:
    schedule = json.loads(schedule_path.read_text(encoding="utf-8"))
    ledger = schedule["apples_to_apples_ledger"]
    networks = schedule["step_C_networks"]
    control = ledger["AOS_C1"]
    c1 = networks["C1_live_d1_to_transpose"]
    c2 = networks["C2_early_plane_orientation"]
    if control["routing_total"] != 576 or c2["full_forward_routing"] != 792:
        raise SystemExit("selected 1152 baseline ledger changed")
    if control["data_loads_after_top_split"] != 144 or control["data_stores_after_top_split"] != 144:
        raise SystemExit("selected 1152 movement ledger changed")

    report = {
        "schema": "ntruplus1152-p1-ntt16-first-gate/v1",
        "checkpoint": "P1-1152-NTT16-FIRST-GATE",
        "scope": "one and only NTT16-first/blocked challenger against current persistent-AoS NTT9-first",
        "control": {
            "name": "current NTT9-first persistent-AoS C1",
            "data_loads_after_top_split": control["data_loads_after_top_split"],
            "data_stores_after_top_split": control["data_stores_after_top_split"],
            "routing": control["routing_total"],
            "peak_ymm": control["peak_ymm"],
            "ntt9_to_ntt16_materialization": {
                "stores": schedule["step_A_aos_ntt9"]["data_stores"],
                "reloads": schedule["step_B_aos_d8_d4"]["data_loads"],
            },
            "late_live_boundary": c1["per_tile"]["fusion"],
        },
        "challenger": {
            "name": "NTT16-first, coefficient-plane blocked",
            "required_entry": "transpose each top-split 4q-by-4j AoS tile to four q-lane planes",
            "known_early_plane_control": {
                "routing": c2["full_forward_routing"],
                "delta_vs_selected": c2["full_forward_routing"] - c1["full_forward_routing"],
                "meaning": "exact existing early-plane network cost; evidence, not an asserted lower bound for every NTT16-first schedule",
            },
            "only_plausible_credit": "delete some or all of the 72-store plus 72-reload axis boundary",
            "blocking_obligation": "retain nine row results for one j while forming later rows, or materialize/recompute the other coefficient planes",
            "exact_two_axis_schedule": None,
            "proved_peak_ymm": None,
            "proved_removed_stores": None,
            "proved_removed_reloads": None,
            "new_constant_operands": None,
        },
        "decision": {
            "linked_asm_authorized": False,
            "paired_benchmark_authorized": False,
            "reason": "the challenger has not exhibited a <=16-YMM full-branch schedule that removes a complete boundary; the only exact early-plane evidence is 216 additional routes",
            "not_rejected_mathematically": True,
            "reopen_condition": "provide exact def/use liveness and full-branch movement showing net boundary deletion after entry transpose",
            "p2_opened": False,
        },
        "source_sha256": {"current_schedule": sha256(schedule_path)},
    }
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(args.schedule)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"generated file is stale: {args.output}")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(expected, encoding="utf-8")
    print("P1 1152 NTT16-first gate stopped before ASM: no feasible boundary-deleting schedule")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
