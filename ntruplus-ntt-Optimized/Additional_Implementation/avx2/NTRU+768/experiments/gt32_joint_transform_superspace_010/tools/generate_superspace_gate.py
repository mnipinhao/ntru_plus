#!/usr/bin/env python3
"""GT32 whole-transform superspace coverage and first open frontier.

This generator deliberately starts at Top/R3 rather than at the post-S1
layout.  It imports earlier closed regions, audits the two six-branch
materialization boundaries, and searches the one previously explicit reopen
condition of RAW160: a typed, nonuniform per-leaf diagonal scale carried
through BaseMul and discharged by the inverse.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
EXPERIMENTS = EXPERIMENT.parent
ROOT = EXPERIMENTS.parent
LEGACY = EXPERIMENTS / "avx2_gt32_tile4_official_001"
G = LEGACY / "generated"
S7 = EXPERIMENTS / "gt32_plane_n16_stockham_stages_007"
S8 = EXPERIMENTS / "gt32_plane_n16_radix4_route_elim_008"
S9 = EXPERIMENTS / "gt32_joint_transform_basis_009"

sys.path.insert(0, str(LEGACY / "tools"))
import generate_tile4 as gt  # noqa: E402
import generate_n32_branchlocal_scale_placement_gate as scale_gate  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def artifact(path: Path, decision: str | None = None) -> dict:
    record = {"path": str(path.resolve()), "sha256": sha256(path)}
    if decision is not None:
        value = load(path)
        for key in decision.split("."):
            value = value[key]
        record["recorded_decision"] = value
    return record


def coverage_registry() -> dict:
    """Import, do not silently rerun, the already covered families."""
    return {
        "global_R2_physical_trajectory": {
            "status": "covered_do_not_repeat",
            "artifact": artifact(G / "tile4_global_physical_layout_gate.json", "decision"),
            "scope": "5040 bit-axis states between Forward stages, BM entry, inverse stages and T9 entry",
            "not_covered": "Top/R3 persistence and mixed-radix packet ownership",
        },
        "current_M_frontend_seam": {
            "status": "covered_under_fixed_M_S2_S5",
            "artifact": artifact(G / "tile4_n5_m_frontend_seam_gate.json", "decision"),
            "result": "packet-pair S1 raises memory operations 96->144; keeping a partner packet needs 22 YMM",
            "reopen_used_here": "change the factorization/packet consumer rather than preserving current M S2-S5",
        },
        "NTT32_first_and_R3": {
            "status": "covered_narrow_families_imported",
            "artifacts": [
                artifact(G / "tile4_n32first_split_twist_gate.json", "decision"),
                artifact(G / "tile4_n32_gt_pfa_native_gate.json", "decision"),
                artifact(G / "tile4_n32_gt_pfa_joint_gate.json", "decision"),
                artifact(G / "tile4_n32_mr_s3local_gate.json", "decision"),
                artifact(G / "tile4_n32_branchlocal_raw160_gate.json", "decision"),
                artifact(G / "tile4_n32_branchlocal_scale_placement_gate.json", "decision"),
            ],
            "remaining": "a changed consumer scale/basis contract or a genuinely smaller R3 closure frontier",
        },
        "R3_persistent_packet_and_pebble_families": {
            "status": "covered_for_current_factorization",
            "artifacts": [
                artifact(G / "tile4_n32_physical_schedule_gate.json", "decision"),
                artifact(G / "tile4_n32_gt_wave_producer_gate.json", "decision"),
                artifact(G / "tile4_n32_stage_native_tile_gate.json", "decision"),
            ],
            "result": (
                "strict zero-spill has a 16-data-plus-one-Montgomery-temp cut; "
                "the best allocated remedy is one spill/reload per component, "
                "while 8/10/12-YMM stage-native packets lose to source replay or routing"
            ),
        },
        "persistent_full_plane_radix2": {
            "status": "covered_not_promoted",
            "artifact": artifact(S7 / "generated/plane_n16_stockham_gate.json"),
            "result": "progressive wins 8/8 launches",
        },
        "persistent_full_plane_radix4": {
            "status": "covered_static_hard_stop",
            "artifact": artifact(S8 / "generated/plane_n16_radix4_gate.json", "decision.status"),
            "result": "route saving is repaid by terminal/range repair",
        },
        "one_plane_Hybrid_L01": {
            "status": "covered_static_hard_stop",
            "artifact": artifact(S9 / "generated/joint_transform_basis_gate.json", "gate_decision.status"),
            "result": "optimistic whole-island floor is +36 instructions; 19->12 chains is only 63->61 multiply uops",
        },
        "pair_and_compact_basis_arithmetic": {
            "status": "covered_do_not_repeat",
            "artifacts": [
                artifact(G / "tile4_pair_native_bm_gate.json"),
                artifact(G / "tile4_terminal_karatsuba_basis_gate.json"),
                artifact(G / "tile4_pair02_exact_dag_tile_gate.json"),
            ],
            "remaining": "a basis generated by Top/Forward that deletes formation and inverse repair simultaneously",
        },
    }


def production_boundary_census() -> dict:
    ntt = ROOT / "ntt.s"
    ntt_m = ROOT / "ntt_m.s"
    inv = ROOT / "invntt.s"
    text = ntt.read_text()
    assert "DFT3_WIDE_STORE %ymm6,%ymm7,%ymm8,0,512,1024" in text
    assert "DFT3_WIDE_STORE %ymm9,%ymm10,%ymm11,256,768,1280" in text
    assert "movl $6, %ecx" in ntt_m.read_text()
    assert "LOAD_RAW_GROUP" in inv.read_text()
    per_boundary = {
        "YMM_stores": 48,
        "YMM_loads": 48,
        "memory_operations": 96,
        "bytes": 48 * 32 * 2,
    }
    return {
        "sources": [artifact(ntt), artifact(ntt_m), artifact(inv)],
        "Forward_Top_R3_to_N32": per_boundary,
        "Inverse_InvN32_to_tail": per_boundary,
        "whole_2F_plus_I": {
            "memory_operations": 3 * per_boundary["memory_operations"],
            "bytes": 3 * per_boundary["bytes"],
        },
        "classification": "implementation boundary, not an algebraic requirement",
    }


def mont_bound(bound: int, factor: int) -> int:
    """Safe cheap bound for the signed high-word Montgomery implementation."""
    return (bound * abs(gt.centered(factor)) + 65535) // 65536 + (gt.Q + 1) // 2


def initial_rows() -> tuple[list[list[list[int]]], list[int]]:
    rows_by_branch: list[list[list[int]]] = []
    for branch, scale in enumerate(gt.BRANCH_SCALE):
        initial = max(abs(v) for v in scale_gate.top_intervals()[branch])
        rows = []
        for row in range(3):
            values = []
            for q in range(32):
                n = (64 * row + 33 * q) % 96
                factor = gt.centered(pow(scale, -n, gt.Q) * gt.R)
                values.append(mont_bound(initial, factor))
            rows.append(values)
        # Qualified RAW S1.
        out = [r[:] for r in rows]
        for low, high in scale_gate.butterfly_pairs(1):
            for row in range(3):
                bound = max(rows[row][low], rows[row][high])
                out[row][low] = out[row][high] = 2 * bound
        rows_by_branch.append(out)
    return rows_by_branch, [1] * 32


def apply_stage(bounds, scales, stage: int, nibble: int):
    result = [[row[:] for row in branch] for branch in bounds]
    next_scales = scales[:]
    for low, high in scale_gate.butterfly_pairs(stage):
        slot = scale_gate.operation_slot(stage, low)
        arm = "L" if (nibble >> slot) & 1 else "H"
        dl, dh = scales[low], scales[high]
        w = scale_gate.ordinary_twiddle(stage, low)
        if arm == "H":
            p = dl
            factor = w * p * pow(dh, -1, gt.Q) % gt.Q
        else:
            p = dh * pow(w, -1, gt.Q) % gt.Q
            factor = p * pow(dl, -1, gt.Q) % gt.Q
        next_scales[low] = next_scales[high] = p
        for branch in range(2):
            for row in range(3):
                left = bounds[branch][row][low]
                right = bounds[branch][row][high]
                reduced = mont_bound(right if arm == "H" else left, factor)
                value = (left if arm == "H" else right) + reduced
                result[branch][row][low] = result[branch][row][high] = value
    return result, next_scales


def dft3(bounds):
    result = [[[0] * 32 for _ in range(3)] for _ in range(2)]
    for branch in range(2):
        for q in range(32):
            x0, x1, x2 = (bounds[branch][row][q] for row in range(3))
            omega = mont_bound(x1 + x2, -886)
            result[branch][0][q] = x0 + x1 + x2
            result[branch][1][q] = x0 + x2 + omega
            result[branch][2][q] = x0 + x1 + omega
    return result


def scale_history(mask: int):
    scales = [1] * 32
    records = []
    for stage in (2, 3):
        before = scales
        scales = scale_gate.scale_stage(scales, stage, mask)
        records.append((stage, before, scales))
    for stage in (4, 5):
        before = scales
        scales = scale_gate.scale_stage(scales, stage, mask)
        records.append((stage, before, scales))
    return records


def inverse_squared_scale_chains(mask: int) -> dict:
    """Count an exact reverse typed-scale implementation.

    BaseMul maps Forward scale D to D^2 without a repair.  Reversing one
    Forward butterfly can always recover the squared pre-stage scales.  The
    normal high/difference chain remains; a low/sum chain is additionally
    required exactly when the Forward chose the L-arm representation.
    Factors are allowed to vary by word lane.
    """
    per_stage = []
    total = 0
    for stage, before, after in reversed(scale_history(mask)):
        slot_records = []
        stage_chains_per_tile = 0
        for slot in range(4):
            pairs = [(lo, hi) for lo, hi in scale_gate.butterfly_pairs(stage)
                     if scale_gate.operation_slot(stage, lo) == slot]
            low_factors = []
            high_factors = []
            for low, high in pairs:
                p2 = after[low] * after[low] % gt.Q
                low_factors.append(before[low] * before[low] * pow(p2, -1, gt.Q) % gt.Q)
                w = scale_gate.ordinary_twiddle(stage, low)
                high_factors.append(pow(w, -1, gt.Q) * before[high] * before[high]
                                    * pow(p2, -1, gt.Q) % gt.Q)
            low_chain = any(value != 1 for value in low_factors)
            # The high operation is a chain unless the complete factor vector
            # is identity.  This includes the inverse twiddle.
            high_chain = any(value != 1 for value in high_factors)
            chains = int(low_chain) + int(high_chain)
            stage_chains_per_tile += chains
            slot_records.append({
                "slot": slot,
                "low_sum_chain": low_chain,
                "high_difference_chain": high_chain,
                "chains": chains,
            })
        # Six (u,r) tiles carry the same q-scale trajectory.
        full_stage = 6 * stage_chains_per_tile
        total += full_stage
        per_stage.append({"stage": stage, "slots": slot_records,
                          "chains_full_inverse": full_stage})
    baseline = 4 * 4 * 6
    return {
        "chains_S2_S5": total,
        "uniform_control_chains_S2_S5": baseline,
        "extra_chains": total - baseline,
        "per_stage": per_stage,
    }


def exact_interval_evaluate(mask: int) -> dict:
    """Refine a selected schedule with the legacy exact interval reducer."""
    branch_records = []
    terminal_scales = None
    for branch, branch_scale in enumerate(gt.BRANCH_SCALE):
        initial = scale_gate.top_intervals()[branch]
        rows = []
        for row in range(3):
            values = []
            for q in range(32):
                n = (64 * row + 33 * q) % 96
                factor = gt.centered(pow(branch_scale, -n, gt.Q) * gt.R)
                values.append(scale_gate.mont_interval(initial, factor))
            rows.append(values)
        scales = [1] * 32
        s1 = [row[:] for row in rows]
        for low, high in scale_gate.butterfly_pairs(1):
            for row in range(3):
                s1[row][low] = scale_gate.add(rows[row][low], rows[row][high])
                s1[row][high] = scale_gate.sub(rows[row][low], rows[row][high])
        rows = s1
        for stage in (2, 3):
            rows, scales, _ = scale_gate.apply_interval_stage(rows, scales, stage, mask)
        after_dft = [[(0, 0)] * 32 for _ in range(3)]
        for q in range(32):
            x0, x1, x2 = (rows[row][q] for row in range(3))
            omega = scale_gate.mont_interval(scale_gate.sub(x1, x2), -886)
            values = (
                scale_gate.add(scale_gate.add(x0, x1), x2),
                scale_gate.add(scale_gate.sub(x0, x2), omega),
                scale_gate.sub(scale_gate.sub(x0, x1), omega),
            )
            for k3, value in enumerate(values):
                after_dft[k3][q] = value
        rows = after_dft
        for stage in (4, 5):
            rows, scales, _ = scale_gate.apply_interval_stage(rows, scales, stage, mask)
        bounds = [max(scale_gate.peak(value) for value in row) for row in rows]
        branch_records.append({"branch": branch,
                               "bounds_by_k3": bounds,
                               "maximum": max(bounds)})
        if terminal_scales is None:
            terminal_scales = scales
        else:
            assert terminal_scales == scales
    return {
        "exact_interval_terminal_abs_bound": max(r["maximum"] for r in branch_records),
        "branch_records": branch_records,
        "terminal_scale_vector": terminal_scales,
        "distinct_terminal_scales": len(set(terminal_scales)),
    }


def raw_s1(rows):
    output = [row[:] for row in rows]
    for low, high in scale_gate.butterfly_pairs(1):
        for row in range(len(rows)):
            output[row][low] = scale_gate.add(rows[row][low], rows[row][high])
            output[row][high] = scale_gate.sub(rows[row][low], rows[row][high])
    return output


def exact_dft3_rows(rows):
    output = [[(0, 0)] * 32 for _ in range(3)]
    maximum = 0
    for q in range(32):
        x0, x1, x2 = (rows[row][q] for row in range(3))
        omega = scale_gate.mont_interval(scale_gate.sub(x1, x2), -886)
        values = (
            scale_gate.add(scale_gate.add(x0, x1), x2),
            scale_gate.add(scale_gate.sub(x0, x2), omega),
            scale_gate.sub(scale_gate.sub(x0, x1), omega),
        )
        for k3, value in enumerate(values):
            output[k3][q] = value
            maximum = max(maximum, scale_gate.peak(value))
    return output, maximum


def stage_relocation_selective_center_search() -> dict:
    """Move R3 across the R2 prefix and search three row-center choices."""
    schedules = []
    for after_stage in range(0, 6):
        for center_mask in range(8):
            branch_records = []
            all_precenter_safe = True
            all_terminal_safe = True
            for branch, branch_scale in enumerate(gt.BRANCH_SCALE):
                initial = scale_gate.top_intervals()[branch]
                rows = []
                for row in range(3):
                    values = []
                    for q in range(32):
                        n = (64 * row + 33 * q) % 96
                        factor = gt.centered(pow(branch_scale, -n, gt.Q) * gt.R)
                        values.append(scale_gate.mont_interval(initial, factor))
                    rows.append(values)
                scales = [1] * 32
                if after_stage >= 1:
                    rows = raw_s1(rows)
                for stage in range(2, after_stage + 1):
                    rows, scales, _ = scale_gate.apply_interval_stage(rows, scales, stage, 0)
                rows, dft_max = exact_dft3_rows(rows)
                precenter_safe = dft_max < 32768
                all_precenter_safe &= precenter_safe
                if precenter_safe:
                    for k3 in range(3):
                        if center_mask & (1 << k3):
                            rows[k3] = [scale_gate.centered_interval(value)
                                        for value in rows[k3]]
                    if after_stage == 0:
                        rows = raw_s1(rows)
                    for stage in range(max(2, after_stage + 1), 6):
                        rows, scales, bound = scale_gate.apply_interval_stage(
                            rows, scales, stage, 0)
                        if bound >= 32768:
                            all_terminal_safe = False
                    terminal = max(scale_gate.peak(value) for row in rows for value in row)
                else:
                    terminal = None
                    all_terminal_safe = False
                branch_records.append({"branch": branch,
                                       "pre_center_DFT3_abs_bound": dft_max,
                                       "terminal_abs_bound": terminal})
            center_rows = center_mask.bit_count()
            # One complete k3 row is eight YMM for each u branch.
            center_vectors = center_rows * 8 * 2
            center_instructions = center_vectors * 3
            closure_data = 3 * (1 << after_stage)
            closure_peak = closure_data + 1  # serial Montgomery temporary
            range_qualified = (all_precenter_safe and all_terminal_safe
                               and max(r["terminal_abs_bound"] for r in branch_records) <= 10788)
            schedules.append({
                "R3_after_stage": after_stage,
                "center_mask_hex": f"0x{center_mask:x}",
                "centered_k3_rows": [k for k in range(3) if center_mask & (1 << k)],
                "center_vectors_per_Forward": center_vectors,
                "center_instructions_per_Forward": center_instructions,
                "closure_data_YMM_per_u_component": closure_data,
                "closure_peak_with_one_temp": closure_peak,
                "fits_16YMM_closure": closure_peak <= 16,
                "branch_records": branch_records,
                "range_qualified_for_B3": range_qualified,
                "optimistic_boundary_instruction_delta": center_instructions - 96,
            })
    qualified = [r for r in schedules if r["range_qualified_for_B3"]]
    qualified.sort(key=lambda r: (not r["fits_16YMM_closure"],
                                  r["center_instructions_per_Forward"],
                                  r["R3_after_stage"], r["center_mask_hex"]))
    no_materialization = [r for r in qualified if r["fits_16YMM_closure"]]
    return {
        "stage_positions": 6,
        "center_policies_per_position": 8,
        "candidate_schedules": len(schedules),
        "closure_model": "3 radix-3 rows times 2^d R2-prefix values, plus one serial Montgomery temporary",
        "range_qualified_count": len(qualified),
        "range_and_register_qualified_count": len(no_materialization),
        "best_range_and_register_qualified": no_materialization[0] if no_materialization else None,
        "qualified_schedules": qualified,
        "all_schedules": schedules,
        "important_caveat": (
            "closure capacity is necessary, not a complete producer allocation; "
            "source traversal/replay and physical lane routing remain to be charged"
        ),
    }


def conservative_nonuniform_search() -> dict:
    initial_bounds, initial_scales = initial_rows()
    prefixes = [(0, initial_bounds, initial_scales)]
    for stage in (2, 3):
        following = []
        for mask, bounds, scales in prefixes:
            for nibble in range(16):
                shifted = mask | (nibble << (4 * (stage - 2)))
                nb, ns = apply_stage(bounds, scales, stage, nibble)
                following.append((shifted, nb, ns))
        prefixes = following
    prefixes = [(mask, dft3(bounds), scales) for mask, bounds, scales in prefixes]
    for stage in (4, 5):
        following = []
        for mask, bounds, scales in prefixes:
            for nibble in range(16):
                shifted = mask | (nibble << (4 * (stage - 2)))
                nb, ns = apply_stage(bounds, scales, stage, nibble)
                following.append((shifted, nb, ns))
        prefixes = following

    records = []
    for mask, bounds, scales in prefixes:
        maximum = max(value for branch in bounds for row in branch for value in row)
        inverse = inverse_squared_scale_chains(mask)
        records.append({
            "mask": mask,
            "mask_hex": f"0x{mask:04x}",
            "orientation_nibbles_S2_S5": [(mask >> (4 * i)) & 15 for i in range(4)],
            "conservative_terminal_abs_bound": maximum,
            "uniform_e0": scales == [1] * 32,
            "distinct_terminal_scales": len(set(scales)),
            "inverse_extra_chains": inverse["extra_chains"],
            "inverse_scale_chain_proof": inverse,
        })

    # Pareto on the only resources changed by this typed diagonal contract.
    pareto = []
    for record in sorted(records, key=lambda r: (
            r["conservative_terminal_abs_bound"], r["inverse_extra_chains"], r["mask"])):
        point = (record["conservative_terminal_abs_bound"], record["inverse_extra_chains"])
        if any(p["conservative_terminal_abs_bound"] <= point[0]
               and p["inverse_extra_chains"] <= point[1] for p in pareto):
            continue
        pareto = [p for p in pareto if not (
            point[0] <= p["conservative_terminal_abs_bound"]
            and point[1] <= p["inverse_extra_chains"])]
        pareto.append(record)
    pareto.sort(key=lambda r: (r["inverse_extra_chains"],
                               r["conservative_terminal_abs_bound"], r["mask"]))
    for record in pareto:
        record["exact_interval_refinement"] = exact_interval_evaluate(record["mask"])
    safe = [r for r in records if r["conservative_terminal_abs_bound"] <= 10788]
    best_bound = min(records, key=lambda r: (r["conservative_terminal_abs_bound"],
                                             r["inverse_extra_chains"], r["mask"]))
    best_zero_extra = min((r for r in records if r["inverse_extra_chains"] <= 0),
                          key=lambda r: (r["conservative_terminal_abs_bound"], r["mask"]))
    return {
        "candidate_schedules": len(records),
        "typed_contract": "Forward D(q); BaseMul D(q)^2; inverse discharges D(q)^2",
        "BaseMul_extra_chains": 0,
        "reason_BaseMul_is_free": "leaf scalar D commutes with quartic multiplication; output is intentionally typed D^2",
        "current_B3_input_bound": 10788,
        "safe_schedule_count_under_conservative_bound": len(safe),
        "qualification_note": (
            "zero means no schedule is range-qualified by the safe whole-space "
            "bound; exact interval refinement is additionally reported for "
            "every conservative Pareto point"
        ),
        "best_terminal_bound": best_bound,
        "best_with_no_inverse_chain_increase": best_zero_extra,
        "pareto": pareto,
    }


def materialization_frontier() -> dict:
    seam = load(G / "tile4_n5_m_frontend_seam_gate.json")
    physical = load(G / "tile4_n32_physical_schedule_gate.json")
    stage_native = load(G / "tile4_n32_stage_native_tile_gate.json")
    raw = load(G / "tile4_n32_branchlocal_raw160_gate.json")
    return {
        "current_R3_first": {
            "memory_operations_per_transform_boundary": 96,
            "bytes_per_transform_boundary": 3072,
            "executable_control": True,
        },
        "packet_pair_S1_preserving_current_M": {
            "memory_operations_per_Forward": seam["candidates"]["F1_packet_pair_S1"]["memory"]["total_vector_memory_operations"],
            "decision": "dominated_by_current",
        },
        "R3_wave_controlled_spill": {
            "spill_store_load_instructions_per_Forward": 6,
            "spill_bytes_per_Forward": physical["candidates"]["R3"]["spill_bytes_per_Forward"],
            "measured_net_tax_TSC_per_Forward": stage_native["measured_R3_reference"]["three_wave_plus_five_blend_net_TSC_per_Forward"],
            "status": "allocated local remedy; full source-to-terminal closure still needs changed range/consumer contract",
        },
        "stage_native_8_10_12YMM": {
            "status": stage_native["T_series_status"],
            "candidates": stage_native["candidates"],
        },
        "RAW160_branch_local": {
            "Montgomery_chains": raw["Montgomery_chain_accounting"]["candidate"]["total"],
            "peak_YMM": raw["register_and_materialization"]["peak_YMM"],
            "extra_branch_materialization_memory_instructions": raw["register_and_materialization"]["static_delta_vs_current_branch_at_time_168"]["extra_branch_materialization_memory_instructions"],
            "old_blocker": raw["range_and_consumer_contract"]["reason"],
            "typed_diagonal_reopen": "evaluated in this gate",
        },
        "strict_zero_materialization": {
            "status": "not proved executable for current factorization",
            "cut": "16 live data YMM plus one Montgomery temporary",
            "not_a_global_theorem": True,
            "reopen": "factorization that reduces the six-component closure frontier or deletes a complete producer wave",
        },
    }


def family_superspace(diagonal: dict) -> list[dict]:
    return [
        {"family": "current_progressive", "status": "benchmark_control",
         "R3_materialization": "full", "terminal_basis": "M monomial"},
        {"family": "producer_native_Hybrid", "status": "first L01 node closed; other bases open only with a new joint deletion",
         "R3_materialization": "unchanged in 009", "terminal_basis": "variable"},
        {"family": "R3_persistent_mixed_radix", "status": "current 8/10/12 packetizations closed; smaller closure factorization open",
         "R3_materialization": "primary variable", "terminal_basis": "mixed (u,r,k,p)"},
        {"family": "full_plane_or_Hybrid_R4", "status": "full-plane R4 closed; consumer-selected Hybrid R4 conditional",
         "R3_materialization": "not removed by 008", "terminal_basis": "variable"},
        {"family": "multiplication_selected_basis", "status": "general basis open; unit-coefficient L01 node closed",
         "R3_materialization": "must be scored jointly", "terminal_basis": "T(a)"},
        {"family": "RAW160_nonuniform_diagonal", "status": (
            "range-safe-candidate-found" if diagonal["safe_schedule_count_under_conservative_bound"] else
            "typed-scale-range-shaping-does-not-close-B3-contract"),
         "R3_materialization": "branch-local/controlled-spill trajectory", "terminal_basis": "D(q) monomial"},
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    diagonal = conservative_nonuniform_search()
    relocation = stage_relocation_selective_center_search()
    safe = diagonal["safe_schedule_count_under_conservative_bound"] > 0
    result = {
        "schema": "ntruplus768-gt32-joint-transform-superspace-010-v1",
        "experiment": "GT32-JOINT-TRANSFORM-SUPERSPACE-010",
        "production_modified": False,
        "decision_unit": "2*(Top+Forward_L)+BaseMul_(L->J)+(Inverse_J+TopJoin)",
        "semantic_coordinates": ["u", "r", "k4", "k3", "k2", "k1", "k0", "p1", "p0"],
        "coverage_registry": coverage_registry(),
        "production_boundary_census": production_boundary_census(),
        "architecture_families": family_superspace(diagonal),
        "materialization_frontier": materialization_frontier(),
        "new_RAW160_typed_diagonal_search": diagonal,
        "R3_stage_relocation_selective_center_search": relocation,
        "decision": {
            "wave_completed": "coverage plus six-branch materialization and typed-diagonal RAW160 reopen",
            "assembly_emitted": False,
            "reason": (
                "a conservative range-safe typed diagonal exists; continue to exact interval/BM/inverse proof"
                if safe else
                "all 65536 existing-chain diagonal schedules remain above the 10788 B3 contract; no RAW160 ASM"
            ),
            "superspace_closed": False,
            "why_not_closed": [
                "strict zero-materialization is not a theorem beyond the current six-component factorization",
                "arbitrary multiplication-selected linear bases are not enumerated by this diagonal wave",
                "Forward and BaseMul output layouts may still differ",
            ],
            "next": (["exact interval proof for range-safe diagonal schedules",
                      "construct inverse D^2 discharge and whole-island Pareto score"] if safe else (
                ["allocate and score the best after-S1/after-S2 R3 selective-center frontier",
                 "synthesize its BaseMul output and inverse-entry trajectory"]
                if relocation["range_and_register_qualified_count"] else [
                    "search only factorizations that reduce the six-component R3 closure frontier",
                    "search multiplication-selected bases only when they delete formation and inverse repair together",
                ])),
        },
        "hard_stop_rule": "only a complete 2F+B+I candidate dominated on every Pareto dimension may be pruned",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(args.output)
    print(result["decision"]["reason"])


if __name__ == "__main__":
    main()
