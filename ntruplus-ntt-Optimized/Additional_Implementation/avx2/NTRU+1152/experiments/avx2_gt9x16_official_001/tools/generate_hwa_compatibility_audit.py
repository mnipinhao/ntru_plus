#!/usr/bin/env python3
"""Audit Hwa-style coefficient-plane compatibility across the current GT path."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layout", type=Path, required=True)
    parser.add_argument("--views", type=Path, required=True)
    parser.add_argument("--g1b-result", type=Path, required=True)
    parser.add_argument("--m3-result", type=Path, required=True)
    parser.add_argument("--m3-audit", type=Path, required=True)
    parser.add_argument("--producer-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    layout = json.loads(args.layout.read_text())
    views = json.loads(args.views.read_text())
    g1b = json.loads(args.g1b_result.read_text())
    m3 = json.loads(args.m3_result.read_text())
    audit = json.loads(args.m3_audit.read_text())
    producer_source = args.producer_source.read_text()

    p_order = layout["physical_row_to_mathematical_p"]
    q_order = layout["physical_lane_to_mathematical_q"]
    if len(p_order) != 9 or len(q_order) != 16:
        raise SystemExit("Hwa audit requires the fixed GT9x16 physical orders")
    checks = 0
    for cell in layout["cells"]:
        branch = cell["branch"]
        row = cell["gt_row_physical_trit_reversed"]
        lane = cell["ntt16_lane_physical_bit_reversed"]
        if cell["ntt9_frequency_p"] != p_order[row]:
            raise SystemExit("physical row no longer maps through P")
        if cell["ntt16_frequency_q"] != q_order[lane]:
            raise SystemExit("physical lane no longer maps through Q")
        for position in cell["positions"]:
            terminal = position["terminal_coefficient"]
            expected = ((branch * 9 + row) * 4 + terminal) * 16 + lane
            if position["gt_row_terminal_lane"]["position_i16"] != expected:
                raise SystemExit("terminal-major plane formula changed")
            checks += 1
    if checks != 1152:
        raise SystemExit(f"expected 1152 plane checks, found {checks}")

    view_by_id = {item["id"]: item for item in views["views"]}
    f0 = view_by_id["F0-d1-persistent-sd-control"]
    f1 = view_by_id["F1-terminal-major-consumer-natural"]
    if "persistent" not in f0["representation"]["B"]:
        raise SystemExit("F0 is no longer the persistent control")
    if "terminal-major" not in f1["representation"]["B"]:
        raise SystemExit("F1 is no longer terminal-major")
    if "forward_f1_b1" not in producer_source:
        raise SystemExit("M3 producer no longer names F1-B1 explicitly")

    c0 = audit["functions"]["C0"]
    c1 = audit["functions"]["C1"]
    c2 = audit["functions"]["C2"]
    document = {
        "schema": "gt9x16-hwa-compatibility-audit/v1",
        "checkpoint": "HWA-A0-current-representation-compatibility",
        "parameter": 1152,
        "semantic_plane_contract": {
            "formula": "V[b,physical_p_row,j][lane] = A[b,P[row],Q[lane],j]",
            "P": p_order,
            "Q": q_order,
            "address_i16": "((b*9 + physical_p_row)*4 + j)*16 + lane",
            "vectors": 72,
            "component_checks": checks,
            "classification": "Hwa-style coefficient-plane SIMD over 16 homogeneous q leaves",
        },
        "critical_distinction": {
            "F0_fastest_forward": {
                "basis": f0["representation"]["B"],
                "cycles": views["control_result"]["combined_cycles"],
                "exact_terminal_major_plane": False,
            },
            "F1_B1_M3_producer": {
                "basis": f1["representation"]["B"],
                "exact_terminal_major_plane": True,
                "producer_debt_cycles": 58.5,
                "source_call": "ntruplus1152_exp001_gt9x16_r2_adjusted_forward_f1_b1",
            },
            "interpretation": (
                "The M3 72-YMM state is exactly coefficient-plane SIMD, but the "
                "current fastest F0 forward is a persistent terminal-pair S/D "
                "view. M3 timing excludes the F1 producer debt and is not yet a "
                "complete F0-to-consumer path."
            ),
        },
        "boundary_audit": [
            {
                "edge": "paper R2 NTT9 -> adjusted NTT16",
                "status": "materialized",
                "detail": "36-YMM R2 output seam retained by F-R3D1",
            },
            {
                "edge": "adjusted NTT16 -> BMScale operands",
                "status": "exact-plane-only-through-F1-B1",
                "detail": "F1-B1 pays 58.5 cycles versus F0; consumer-native F0 BMScale remains open",
            },
            {
                "edge": "BMScale -> repaired inverse D1",
                "status": "live-direct",
                "paired_cycles": m3["paired"]["C1_minus_C0"]["median_cycles"],
            },
            {
                "edge": "repaired D1 -> persistent D2/D4/D8",
                "status": "one-D1-boundary-then-register-persistent",
                "removed_memory_instructions_vs_C1": (
                    c1["output_loads"] + c1["output_stores"] -
                    c2["output_loads"] - c2["output_stores"]),
                "paired_cycles": m3["paired"]["C2_minus_C1"]["median_cycles"],
            },
            {
                "edge": "inverse16 -> inverse scaled NTT9",
                "status": "not-built-interface-not-frozen",
                "required_next_audit": (
                    "derive inverse NTT9 loads directly from the C2 physical "
                    "P/Q/j output; reject standalone natural-q or full-array repack"
                ),
            },
        ],
        "m3_price": {
            "C0": m3["median_cycles"]["M3-C0-materialized"],
            "C1": m3["median_cycles"]["M3-C1-linked-D1"],
            "C2": m3["median_cycles"]["M3-C2-persistent"],
            "C1_minus_C0": m3["paired"]["C1_minus_C0"]["median_cycles"],
            "C2_minus_C1": m3["paired"]["C2_minus_C1"]["median_cycles"],
            "C2_minus_C0": m3["paired"]["C2_minus_C0"]["median_cycles"],
        },
        "shared_864_projection": {
            "semantic_coordinates": "(b,p,q,j) with identical P/Q plane rule",
            "1152_terminal_degree_and_vectors": [4, 72],
            "864_terminal_degree_and_vectors": [3, 54],
            "shareable": ["P/Q component map", "NTT9/NTT16 routing", "plane address rule", "generator skeleton"],
            "parameter_specific": ["terminal BaseMul/BaseInv", "producer bounds", "inverse repair policy"],
        },
        "decision": {
            "fork_new_Hwa_candidate_now": False,
            "freeze_complete_physical_ABI_now": False,
            "freeze_shared_semantic_plane_contract": True,
            "next_checkpoint": "inverse16-to-inverse-NTT9 direct-consumer map before writing inverse NTT9 assembly",
            "parallel_open_question": "can BMScale consume F0 persistent S/D without paying F1's 58.5-cycle producer debt?",
        },
        "benchmark_policy": "repository-local diagnostic only; no production or SUPERCOP claim",
        "source_sha256": {
            "layout": digest(args.layout),
            "views": digest(args.views),
            "g1b_result": digest(args.g1b_result),
            "m3_result": digest(args.m3_result),
            "m3_audit": digest(args.m3_audit),
            "producer_source": digest(args.producer_source),
        },
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated Hwa compatibility audit is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
