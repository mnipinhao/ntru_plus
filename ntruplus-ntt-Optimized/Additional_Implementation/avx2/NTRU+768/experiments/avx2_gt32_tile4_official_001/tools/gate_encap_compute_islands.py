#!/usr/bin/env python3
"""Fail-closed source-level gate for GT768 Encap compute-island seams.

This proves ownership and tests retention against the *current* register
schedule. It does not claim a lower bound over alternative schedules or cycles.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from vector_mapping_source_ledger import Source, replay_loop, stats

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parents[5]
CLEAN = ROOT.parent.parent / "clean" / "avx2-gt32-clean"
OUT = ROOT / "generated/tile4_encap_compute_island_gate.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_loop(path: Path, name: str, label: str) -> list[str]:
    function = Source(path.read_text()).function(name)
    return replay_loop(function, 1, label)


def positions(trace: list[dict], pattern: str) -> list[int]:
    return [i for i, row in enumerate(trace)
            if re.fullmatch(pattern, row["instruction"])]


def build() -> dict:
    bm_path = CLEAN / "basemul.s"
    forward_path = CLEAN / "ntt_m.s"
    pack_path = CLEAN / "pack.s"
    encap_path = CLEAN / "encap.c"
    sum_path = ROOT / "src/tile4_q24_codec_asm.S"
    status_path = ROOT / "STATUS.yml"
    range_path = ROOT / "generated/tile4_encap_range_refined.json"
    files = (bm_path, forward_path, pack_path, encap_path, sum_path,
             range_path, ROOT / "generated/tile4_gt_vector_mapping.json")
    assert all(p.is_file() for p in files)

    bm = stats(source_loop(bm_path, "ntruplus768_basemul_general_m_avx2",
                           ".Ltile4_bm_b3_loop"), ("r8", "r9"))
    trace = bm["def_use"]
    partial = positions(trace, r"vmovdqu %ymm15, (0|32|64)\(%rdi\)")
    assert len(partial) == 3 and bm["peak_live_YMM"] == 16
    final = positions(trace, r"vmovdqu %ymm[5-8], (0|32|64|96)\(%rdi\)")
    assert len(final) == 4 and min(final) > max(partial)
    retention = []
    for kept in (1, 2, 3):
        first = partial[kept - 1] + 1
        last = partial[kept] if kept < 3 else final[0]
        max_original = max(len(x["live_before"]) for x in trace[first:last])
        retention.append(dict(results_retained=kept,
                              original_peak_in_interval=max_original,
                              counterfactual_peak=max_original + kept,
                              fit_without_rescheduling=max_original + kept <= 16))
    assert retention[0]["counterfactual_peak"] == 17
    assert retention[1]["counterfactual_peak"] == 18

    forward = stats(source_loop(forward_path, "ntruplus768_ntt_m_avx2",
                                ".Lfr_core_loop"))
    ftrace = forward["def_use"]
    first_planes = positions(ftrace, r"vmovdqu %ymm[0-3], 0\+(0|32|64|96)\(%rdi\)")
    second_planes = positions(ftrace, r"vmovdqu %ymm[4-7], 128\+(0|32|64|96)\(%rdi\)")
    assert len(first_planes) == len(second_planes) == 4
    assert max(first_planes) < min(second_planes)
    assert forward["peak_live_YMM"] <= 16

    source = encap_path.read_text()
    required = ("forward_m(scratch.r, scratch.c, scratch.work)",
                "forward_m(scratch.m, scratch.c, scratch.work)",
                "ntruplus768_basemul_general_m_avx2(scratch.c, scratch.h, scratch.r)",
                "ntruplus768_pack_m_highrange12699_avx2(ct, scratch.c)")
    assert all(item in source for item in required)
    assert source.index(required[0]) < source.index(required[1]) < source.index(required[2]) < source.index(required[3])
    assert "poly_add((poly *)(void *)scratch.c" in source
    assert "hash_g(ct, ct)" in source
    assert "ntruplus768_unpack_m_avx2(scratch.h, pk)" in source

    status = status_path.read_text()
    old = status.split("gt32_encap_q24_sum_m_20260817:", 1)[1].split("\ngt32_", 1)[0]
    assert "status: local-qualified-full-caller-hard-stop" in old
    assert "removed_vector_loads: 48" in old and "removed_vector_stores: 48" in old
    assert "reversed: {delta_tsc: 14.2585" in old

    range_report = json.loads(range_path.read_text())
    terminal_max = max(max(row) for row in range_report["terminal_bounds"])
    assert terminal_max == 15592
    assert range_report["post_add_bound"] == 17448
    assert range_report["serializer"]["exact_mod_q"] is True

    return {
        "schema": "gt768-encap-compute-islands-source-gate-v1",
        "evidence_level": "expanded reachable source and historical benchmark; not linked allocation or new timing",
        "source_sha256": {str(p.relative_to(REPO)): sha(p) for p in files},
        "range_contract": {
            "input": "CBD1 r and SOTP m are ternary; validated h is [0,3456]",
            "refined_forward_abs_bound": terminal_max,
            "refined_post_add_abs_bound": range_report["post_add_bound"],
            "serializer_signed_domain_checked": range_report["serializer"]["inputs"],
            "applies_to": "unchanged arithmetic and representatives only; rescheduling requires pre-operation replay",
        },
        "control": {
            "r": "materialized M; two consumers: hash packing and BaseMul",
            "h": "early PK decode/validate to materialized M",
            "m": "materialized M; one arithmetic consumer",
            "c": "B3 raw results, late R^2 finalizer, add-m, Q24 serializer",
            "per_encap": {
                "m_terminal_stores": 48,
                "m_basemul_reloads": 48,
                "B3_partial_raw_stores": 3 * 12,
                "B3_late_finalizer_reloads": 3 * 12,
                "c_final_stores": 48,
                "c_serializer_reloads": 48,
                "separate_add_c_reloads": 48,
                "separate_add_c_stores": 48,
            },
        },
        "historical_controls": {
            "serializer_side_sum_m": {
                "mechanism": "add m inside existing Q24 serializer",
                "removed_c_loads_and_stores_each": 48,
                "correctness": "100 complete Encap vectors, byte exact",
                "normal_full_encap_tsc_delta": -52.246,
                "reversed_full_encap_tsc_delta": 14.2585,
                "decision": "placement-sensitive rejection; not a new prototype",
            },
            "wire_packet_montgomery": {
                "complete_island_cycle_delta_single_packet": 345.67,
                "decision": "reject old realization; aggregated-lambda model is separate and unpriced",
            },
        },
        "A_live_B3_to_ciphertext": {
            "question": "can raw partial results and final c be consumed without the existing materializations?",
            "source_loop_peak_YMM": bm["peak_live_YMM"],
            "first_three_output_store_instruction_indices": partial,
            "finalizer_output_store_instruction_indices": final,
            "retain_results_with_identical_instruction_schedule": retention,
            "decision": "current-schedule-hard-stop",
            "needed_new_mechanism": "exact reallocation/interleave or explicitly priced h/r operand reload; then a compact block Q24 consumer",
            "not_proved": "an alternative B3 schedule is impossible or slower",
        },
        "B_live_m_terminal_to_MulAdd": {
            "question": "can m's single-consumer planes flow directly into h*r+m?",
            "forward_loop_iterations": 6,
            "M_blocks_per_iteration": 2,
            "planes_per_block": 4,
            "source_loop_peak_YMM": forward["peak_live_YMM"],
            "first_block_store_instruction_indices": first_planes,
            "second_block_store_instruction_indices": second_planes,
            "source_basemul_peak_YMM": bm["peak_live_YMM"],
            "decision": "direct-unchanged-helper-link-not-allocated",
            "needed_new_mechanism": "consume m planes one at a time or reload h/r on a bounded block schedule; protect unread frontend scratch before writing c",
            "not_proved": "a bounded alternative allocation is impossible or slower",
        },
        "C_asymmetric_ingress": {
            "r": "M remains materialized because both hash and arithmetic use it",
            "h": "decoder-natural packet only qualifies if quartic arithmetic consumes it without recreating full M",
            "prior_D01": "routing moved to consumer; no new mechanism in unchanged schedule",
            "decision": "mapping-only until a new consumer schedule removes a full pass",
        },
        "prototype_decision": "zero authorized: A/B require exact 16-YMM machine schedules; C has no distinct mechanism yet",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = json.dumps(build(), sort_keys=True, indent=2) + "\n"
    if args.check:
        assert OUT.read_text() == report, "stale compute-island gate"
    else:
        OUT.write_text(report)
    print("compute-island gate:", "verified" if args.check else "written")


if __name__ == "__main__":
    main()
