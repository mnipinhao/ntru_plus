#!/usr/bin/env python3
"""Executable-resource gate for a direct degree-8 packet schedule."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
EXPERIMENTS = EXPERIMENT.parent
PARENT = EXPERIMENTS / "gt32_degree8_incomplete_ntt_018"
GT16 = EXPERIMENTS / "avx2_gt16_quadratic_official_001"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict[str, str]:
    return {"path": str(path.resolve()), "sha256": sha256(path)}


def build() -> dict:
    qbm_path = GT16 / "generated/qbm-static-schedules.json"
    floor_path = GT16 / "results/round4c-chain-floor.json"
    decision_path = GT16 / "results/round4c-decision.json"
    status_path = GT16 / "STATUS.yml"
    qbm = json.loads(qbm_path.read_text())
    floor = json.loads(floor_path.read_text())
    decision = json.loads(decision_path.read_text())
    status_text = status_path.read_text()

    selected = qbm["qbm_candidates"][qbm["selected"]]
    assert qbm["selected"] == "QBM-PREWEIGHT"
    assert selected["peak_live_ymm"] == 11
    assert selected["instructions"] == 1056
    assert qbm["split"]["instructions_per_forward"] == 336
    assert qbm["merge"]["instructions_per_inverse"] == 432
    assert floor["executable_local_cycles"]["terminal_saving"] == 48.84
    assert floor["executable_local_cycles"]["inverse_regression"] == 214.364
    assert "181.486 TSC" in status_text

    factor_vectors_per_operand_block = 8
    qbm_peak = selected["peak_live_ymm"]
    persistent_both = 2 * factor_vectors_per_operand_block + 1
    one_side_live = qbm_peak + factor_vectors_per_operand_block - 1
    # A direct root stream begins from eight pre-S5 planes.  The selected QBM
    # needs ten additional live values besides its B input.  Even if the newly
    # formed B input overwrites one source, the first factor remains over 16.
    root_stream = factor_vectors_per_operand_block + qbm_peak - 1
    assert persistent_both == 17
    assert one_side_live == 18
    assert root_stream == 18

    materialized = floor["round4b_hypothetical_terminal_boundary"]
    assert materialized["new_total"] == 2160
    assert materialized["old_total"] == 2387.549

    return {
        "schema": "ntruplus768-gt32-degree8-packet-schedule-019-v1",
        "experiment": "GT32-DEGREE8-PACKET-SCHEDULE-019",
        "production_modified": False,
        "assembly_emitted": False,
        "parent": artifact(PARENT / "generated/degree8_incomplete_ntt_gate.json"),
        "evidence": [artifact(qbm_path), artifact(floor_path),
                     artifact(decision_path), artifact(status_path),
                     artifact(GT16 / "README.md")],
        "coverage_reconciliation": {
            "GT16_persistent_degree8_ABI": False,
            "GT16_same_four_quadratic_factor_algebra": True,
            "GT16_complete_executable_regions": [
                "NTT16 Forward plus fused quadratic split",
                "QBM-PREWEIGHT",
                "scale-2 quadratic merge",
                "lazy CT16 inverse",
            ],
            "remaining_question": (
                "can a direct packet remove one of those regions rather than "
                "only changing where it materializes?"
            ),
        },
        "selected_executable_control": {
            "split_instructions_two_Forwards": 672,
            "QBM_instructions": selected["instructions"],
            "merge_instructions": qbm["merge"]["instructions_per_inverse"],
            "boundary_total_instructions": 2160,
            "terminal_measured_saving_TSC": 48.84,
            "inverse_measured_regression_TSC": 214.364,
            "legacy_best_chain_regression_TSC": 181.486,
            "fused_first_inverse_load_was_slower_percent": 0.78248,
        },
        "packet_capacity": {
            "degree8_leaves_per_block": 16,
            "quadratic_factor_vectors_per_operand": factor_vectors_per_operand_block,
            "architectural_YMM": 16,
            "persistent_A_and_B_minimum_YMM": persistent_both,
            "persistent_A_and_B_pass": False,
            "one_materialized_A_plus_live_B_during_QBM_peak_YMM": one_side_live,
            "one_materialized_A_plus_live_B_pass": False,
            "direct_root_stream_first_factor_peak_YMM": root_stream,
            "direct_root_stream_pass": False,
            "reason": (
                "all four factors occupy eight vectors per operand; selected "
                "QBM peaks at 11 including one A/B pair, so seven unconsumed "
                "factor vectors push a one-sided live schedule to 18"
            ),
        },
        "schedule_candidates": {
            "D8_PERSISTENT_AB": {
                "peak_YMM_lower_bound": persistent_both,
                "status": "capacity-hard-stop",
            },
            "D8_ONE_SIDE_MATERIALIZED": {
                "peak_YMM_lower_bound": one_side_live,
                "status": "must spill or materialize remaining live factor vectors",
            },
            "D8_ROOT_STREAM": {
                "peak_YMM_lower_bound": root_stream,
                "status": "must reread/recompute sources or spill",
            },
            "D8_FULL_MATERIALIZATION": {
                "instructions": materialized["new_total"],
                "status": "already executable and measured as GT16 quadratic control",
            },
        },
        "decision": {
            "status": "static_hard_stop_direct_degree8_packet_current_QBM",
            "emit_ASM": False,
            "reason": [
                "the algebraic rank-12 path is already executable in GT16",
                "the only zero-spill schedule uses the already measured materialized boundary",
                "persistent and one-side-live direct packets exceed 16 YMM",
                "fusing the inverse first load was already slower",
                "no complete split/merge or multiply class is deleted by the direct ABI alone",
            ],
            "scope_closed": [
                "direct degree8 packet with selected QBM-PREWEIGHT",
                "persistent two-operand factor packet",
                "one-side-materialized while all other-side factors remain live",
                "root-by-root stream while all eight pre-S5 planes remain live",
            ],
            "reopen_only_if": [
                "a QBM schedule peaks at 9 YMM or less",
                "a dynamic stage packet kills source planes before the first QBM factor",
                "LHS/RHS interleaving produces and consumes one factor without retaining eight planes",
                "a new bilinear realization deletes a complete split or merge transform",
            ],
            "next_priority": "streamed evaluation plus LHS/RHS-coupled producer schedule",
        },
    }


def main() -> None:
    output = EXPERIMENT / "generated/degree8_packet_schedule_gate.json"
    output.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
