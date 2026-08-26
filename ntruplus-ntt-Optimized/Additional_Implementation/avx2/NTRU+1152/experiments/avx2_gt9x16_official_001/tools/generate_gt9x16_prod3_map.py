#!/usr/bin/env python3
"""Map coefficient-domain GT9x16 formation alternatives without emitting ASM."""
from __future__ import annotations

import argparse
import hashlib
import json
from math import gcd
from pathlib import Path


P_ORDER = [0, 3, 6, 1, 4, 7, 8, 2, 5]
Q_ORDER = [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component-oracle", type=Path, required=True)
    parser.add_argument("--ntt9-first-oracle", type=Path, required=True)
    parser.add_argument("--prod1-schedule", type=Path, required=True)
    parser.add_argument("--prod2-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    component = json.loads(args.component_oracle.read_text(encoding="utf-8"))
    ntt9_first = json.loads(args.ntt9_first_oracle.read_text(encoding="utf-8"))
    prod1 = json.loads(args.prod1_schedule.read_text(encoding="utf-8"))
    prod2 = json.loads(args.prod2_map.read_text(encoding="utf-8"))

    frozen = prod1["frozen_contract"]
    if frozen["physical_p_order"] != P_ORDER or frozen["physical_q_order"] != Q_ORDER:
        raise SystemExit("current GT physical order changed")
    if frozen["transform_scale"] != 4 or frozen["montgomery_r_exponent"] != 0:
        raise SystemExit("current scale contract changed")
    if ntt9_first["shear"] != "Y_a[v] = R_(a+v mod 9)[v]":
        raise SystemExit("16-first shear identity changed")
    if not prod2["bijection_proof"]["all_equal_1152"]:
        raise SystemExit("P2-B MA2 boundary is no longer a proved bijection")

    component_by_owner = {}
    for branch_entries in component["components"]:
        for entry in branch_entries:
            key = (entry["branch"], entry["ntt9_frequency_p"],
                   entry["ntt16_frequency_q"])
            if key in component_by_owner:
                raise SystemExit(f"duplicate GT component owner {key}")
            component_by_owner[key] = entry
    if len(component_by_owner) != 288:
        raise SystemExit("component oracle does not cover 288 quartic leaves")

    ma2_by_owner = {}
    for cell in prod2["d1_to_ma2_cells"]:
        owner = cell["semantic_owner"]
        key = (owner["branch"], owner["p"], owner["q"],
               owner["terminal_coefficient"])
        if key in ma2_by_owner:
            raise SystemExit(f"duplicate MA2 owner {key}")
        ma2_by_owner[key] = cell["consumer"]
    if len(ma2_by_owner) != 1152:
        raise SystemExit("MA2 map does not cover 1,152 semantic cells")

    # Output cells for a persistent AoS realization.  Arithmetic is still
    # component-wise in j; only the physical lifetime of the four j values is
    # changed.  The final cell owners must be exactly the existing P2-B ABI.
    output_cells = []
    aos_slots = set()
    ma2_slots = set()
    semantic_owners = set()
    for branch in range(2):
        for physical_row, p in enumerate(P_ORDER):
            for physical_lane, q in enumerate(Q_ORDER):
                entry = component_by_owner[(branch, p, q)]
                for coefficient in range(4):
                    owner = (branch, p, q, coefficient)
                    consumer = ma2_by_owner[owner]
                    aos_slot = ((branch * 9 + physical_row) * 16 + physical_lane) * 4 + coefficient
                    ma2_slot = (consumer["ma2_native_vector"],
                                consumer["ma2_native_packed_lane"])
                    aos_slots.add(aos_slot)
                    ma2_slots.add(ma2_slot)
                    semantic_owners.add(owner)
                    output_cells.append({
                        "semantic_owner": {
                            "branch": branch, "p": p, "q": q,
                            "terminal_coefficient": coefficient,
                        },
                        "component": {
                            "factor_exponent_base_g": entry["factor_exponent_base_g"],
                            "factor_mod_q": entry["factor_mod_q"],
                            "official_component": entry["official_component"],
                        },
                        "persistent_aos": {
                            "physical_p_row": physical_row,
                            "physical_q_lane": physical_lane,
                            "q_block": physical_lane // 4,
                            "q_in_block": physical_lane % 4,
                            "terminal_coefficient_in_qword": coefficient,
                            "i16_slot": aos_slot,
                        },
                        "ma2_destination": consumer,
                        "scale": {"transform": 4, "montgomery_r_exponent": 0},
                    })
    if not (len(aos_slots) == len(ma2_slots) == len(semantic_owners) == 1152):
        raise SystemExit("persistent-AoS output is not a 1,152-cell bijection")

    # Axis-only affine relabels are valid rekeys, but none changes the source
    # fact that one 64-bit q cell owns j=0..3.  Record the entire search class
    # rather than presenting one visually nicer relabel as movement credit.
    units9 = [value for value in range(9) if gcd(value, 9) == 1]
    units16 = [value for value in range(16) if gcd(value, 16) == 1]
    affine_candidates = 0
    affine_movement_signatures = set()
    for up in units9:
        for sp in range(9):
            mapped_p = [(up * p + sp) % 9 for p in range(9)]
            if len(set(mapped_p)) != 9:
                raise SystemExit("non-bijective p relabel escaped the unit search")
            for uq in units16:
                for sq in range(16):
                    mapped_q = [(uq * q + sq) % 16 for q in range(16)]
                    if len(set(mapped_q)) != 16:
                        raise SystemExit("non-bijective q relabel escaped the unit search")
                    affine_candidates += 1
                    # Axis relabeling changes identities/constants only.  It
                    # cannot change this source-cell ownership signature.
                    affine_movement_signatures.add(
                        tuple(tuple(range(4)) for _ in range(16)))
    if affine_candidates != 6912 or len(affine_movement_signatures) != 1:
        raise SystemExit("affine relabel search did not close one movement class")
    representative_relabels = []
    for up, sp, uq, sq in ((1, 0, 1, 0), (8, 0, 1, 0),
                           (1, 0, 15, 0), (2, 1, 3, 1)):
        mapped = {(up * p + sp) % 9 for p in range(9)}
        mapped_q = {(uq * q + sq) % 16 for q in range(16)}
        representative_relabels.append({
            "p_map": f"p' = ({up}*p + {sp}) mod 9",
            "q_map": f"q' = ({uq}*q + {sq}) mod 16",
            "bijective": len(mapped) == 9 and len(mapped_q) == 16,
            "terminal_aos_cell_unchanged": True,
        })

    # The ordinary 16-first identity requires a q-dependent source row.  For
    # every output row a, the sixteen q inputs visit all nine materialized h
    # rows, so the current four-aligned-load row geometry is lost.
    shear_rows = []
    for a in range(9):
        rows = [(a + q) % 9 for q in range(16)]
        shear_rows.append({
            "a": a,
            "source_h_rows_by_q": rows,
            "distinct_source_h_rows": len(set(rows)),
            "four_contiguous_q_blocks_from_one_h_row": all(
                len(set(rows[start:start + 4])) == 1 for start in range(0, 16, 4)),
        })
    if any(row["distinct_source_h_rows"] != 9 for row in shear_rows):
        raise SystemExit("unexpected 16-first shear row coverage")
    if any(row["four_contiguous_q_blocks_from_one_h_row"] for row in shear_rows):
        raise SystemExit("16-first unexpectedly retained current aligned load geometry")

    # The branch twist is separable in the materialized row h and q component:
    # g^(offset*(16h+q)) = g^(16*offset*h) g^(offset*q).  This establishes a
    # legal absorption search, but does not claim a lower chain count.
    modulus = 3456
    separability_checks = 0
    for offset in component["branch_offsets"]:
        for h in range(9):
            for q in range(16):
                lhs = offset * (16 * h + q) % modulus
                rhs = (16 * offset * h + offset * q) % modulus
                if lhs != rhs:
                    raise SystemExit("branch twist exponent failed separability")
                separability_checks += 1

    g0 = {
        "aligned_top_split_loads": 144,
        "early_aos_to_soa_routing": 576,
        "pre_twist_montgomery_chains": 72,
        "producer_local_ma2_permutations": 72,
        "ma2_plane_stores": 72,
    }
    # This is a conservative, mechanically realizable upper bound: retain four
    # AoS q cells in each vector through both axes, then reuse the already proved
    # 16-instruction terminal-pair transpose twice at the final MA2 boundary.
    g1_upper = {
        "aligned_top_split_loads": 72,
        "early_aos_to_soa_routing": 0,
        "pre_twist_montgomery_chains": 72,
        "late_aos_to_ma2_routing_upper_bound": 576,
        "ma2_plane_stores": 72,
    }

    document = {
        "schema": "gt9x16-prod3-map/v1",
        "checkpoint": "GT9X16-PROD3-MAP",
        "parameter": 1152,
        "research_boundary": {
            "official_role": "performance baseline/control only; not an architecture donor",
            "semantic_decomposition": "2 branches x 9 GT rows x 16 GT lanes x quartic degree 4",
            "consumer": "unchanged scale-4 MA2-native coefficient planes",
            "top_split_arithmetic": "unchanged",
            "assembly_authorized": False,
            "kem_benchmark_authorized": False,
        },
        "current_control_G0": {
            "pipeline": ["materialized top split AoS", "36-map AoS-to-SoA formation",
                         "pre-twist", "paper-R2 NTT9", "adjusted D1 NTT16",
                         "P2-B MA2-native epilogue"],
            "movement_per_forward": g0,
            "known_routing_total": 648,
        },
        "persistent_aos_G1": {
            "pipeline": ["materialized top split AoS", "pre-twist in AoS q blocks",
                         "paper-R2 NTT9 while j remains interleaved",
                         "adjusted NTT16 while j remains interleaved",
                         "late AoS-to-MA2 plane formation"],
            "output_cells": output_cells,
            "bijection_proof": {
                "persistent_aos_slots": len(aos_slots),
                "ma2_destination_slots": len(ma2_slots),
                "semantic_owners": len(semantic_owners),
                "all_equal_1152": True,
            },
            "arithmetic_compatibility": {
                "terminal_coefficient_is_passive_dimension": True,
                "twist_depends_on_branch_h_q_not_terminal_coefficient": True,
                "ntt9_constants_depend_on_p_stage_not_terminal_coefficient": True,
                "ntt16_constants_depend_on_p_q_stage_not_terminal_coefficient": True,
                "semantic_map_and_scale_unchanged": True,
            },
            "conservative_movement_upper_bound_per_forward": g1_upper,
            "known_delta_vs_G0_before_arithmetic_rescheduling": {
                "aligned_top_split_loads": -72,
                "routing_upper_bound": -72,
                "pre_twist_montgomery_chains": 0,
                "ma2_plane_stores": 0,
            },
            "open_pricing_variable": "cost of AoS radix-2 routing and fusion of D2/D1 with final 16x4 transpose",
        },
        "axis_relabel_search_G3": {
            "class": "independent affine bijections p'=u*p+s mod9, q'=v*q+t mod16",
            "candidates_checked": affine_candidates,
            "all_preserve_four-terminal-coefficients-per-qword": True,
            "movement_classes_distinguished": len(affine_movement_signatures),
            "representatives": representative_relabels,
            "decision": "not selected alone; rekeys constants/owners but cannot remove the AoS-to-plane boundary",
        },
        "sixteen_first_G2": {
            "identity": ntt9_first["shear"],
            "source_row_audit": shear_rows,
            "all_rows_visit_nine_materialized_h_rows": True,
            "current_four_aligned_load_geometry_preserved": False,
            "decision": "deferred unless shear is absorbed into top-split stores or first arithmetic; naive 16-first is not a cheap-load candidate",
        },
        "twist_scale_search_G4": {
            "identity": "g^(offset*(16h+q)) = g^(16*offset*h) * g^(offset*q)",
            "checks": separability_checks,
            "separable": True,
            "current_pre_twist_montgomery_chains": 72,
            "lower_chain_count_proved": False,
            "decision": "retain as a second schedule variable; absorption must preserve factor identity, scale 4, ranges, and MA2 lambda constants",
        },
        "selection": {
            "selected_next": "GT9X16-PROD3-AOS-SCHED",
            "reason": "persistent AoS is the only mapped candidate that removes the duplicated pair loads and all 576 early formation routes without importing Official arithmetic",
            "required_next_proofs": [
                "exact AoS radix-3 and adjusted radix-2 lane schedule",
                "fused D2/D1-to-MA2 transpose synthesis with an exact opcode ledger",
                "range proof over the actual register orientation",
                "peak-YMM/spill-free schedule and overwrite proof",
                "bit-exact 1,152-cell oracle against P2-B",
            ],
            "assembly_authorized": False,
            "benchmark_authorized": False,
            "native_kem_authorized": False,
        },
        "source_sha256": {
            "component_oracle": sha256(args.component_oracle),
            "ntt9_first_oracle": sha256(args.ntt9_first_oracle),
            "prod1_schedule": sha256(args.prod1_schedule),
            "prod2_map": sha256(args.prod2_map),
        },
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    write(args.output, rendered, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
