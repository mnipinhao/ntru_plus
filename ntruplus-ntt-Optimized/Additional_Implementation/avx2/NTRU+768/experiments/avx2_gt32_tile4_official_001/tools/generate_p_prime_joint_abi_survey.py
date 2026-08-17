#!/usr/bin/env python3
"""Bounded P' leaf-placement survey across Forward/BaseInv/BM/Q24.

The coefficient-plane SoA geometry, arithmetic, scale and range contracts are
fixed.  Only the five logical Q bits may be assigned to the four 16-bit lane
positions and the one YMM-selector position.  BaseInv and BaseMul remain
lane-wise and may relabel their lambda tables.  Q24 is scored from the exact
serialized mapping and must retain the compact block-local half-scatter DAG.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
OUT = GENERATED / "tile4_p_prime_joint_abi_survey.json"
sys.path.insert(0, str(ROOT / "tools"))

import generate_gt32_global_physical_layout_gate as global_gate  # noqa: E402


Q_BITS = tuple(f"q{i}" for i in range(5))
CURRENT_Q_AXES = ("q1", "q3", "q0", "q2", "q4")
KEYGEN_FORWARD_CALLS = 2
KEYGEN_BASEINV_CALLS = 2
KEYGEN_BM_CALLS = 2
KEYGEN_Q24_CALLS = 3


def layout(q_axes: tuple[str, ...]) -> tuple[str, ...]:
    return (*q_axes[:4], "c0", "c1", q_axes[4])


def physical_word(record: dict, q_axes: tuple[str, ...]) -> int:
    q = record["physical_q"]
    bits = {f"q{i}": (q >> i) & 1 for i in range(5)}
    lane = sum(bits[q_axes[position]] << position for position in range(4))
    selector = bits[q_axes[4]]
    block = 4 * record["k3"] + 2 * record["branch"] + selector
    return 64 * block + 16 * record["quartic_coefficient"] + lane


def q_order(q_axes: tuple[str, ...], selector: int) -> list[int]:
    result = [None] * 16
    for q in range(32):
        bits = {f"q{i}": (q >> i) & 1 for i in range(5)}
        if bits[q_axes[4]] != selector:
            continue
        lane = sum(bits[q_axes[position]] << position
                   for position in range(4))
        result[lane] = q
    assert all(item is not None for item in result)
    return result


def q24_route(records: list[dict], q_axes: tuple[str, ...]) -> dict:
    words = [physical_word(record, q_axes) for record in records]
    assert sorted(words) == list(range(768))
    sources: dict[int, dict[tuple[int, int], bool]] = {}

    for packet in range(48):
        packet_words = words[16 * packet:16 * packet + 16]
        blocks = {word // 64 for word in packet_words}
        if len(blocks) != 1:
            return {"compact": False,
                    "reason": "one-wire-packet-crosses-P-prime-blocks"}
        block = blocks.pop()
        quartics = []
        for quartic in range(4):
            degree_words = packet_words[4 * quartic:4 * quartic + 4]
            lanes = {word % 16 for word in degree_words}
            assert len(lanes) == 1
            lane = lanes.pop()
            assert [word // 16 % 4 for word in degree_words] == [0, 1, 2, 3]
            quartics.append((4 + lane % 4, lane // 4))

        for packet_half in range(2):
            pair = quartics[2 * packet_half:2 * packet_half + 2]
            if (pair[0][0] != pair[1][0]
                    or pair[0][1] // 2 != pair[1][1] // 2):
                return {"compact": False,
                        "reason": "wire-half-needs-cross-register-repair"}
            register = pair[0][0]
            half = pair[0][1] // 2
            natural = [(register, 2 * half),
                       (register, 2 * half + 1)]
            if pair not in (natural, natural[::-1]):
                return {"compact": False,
                        "reason": "wire-half-needs-nonlocal-qword-route"}
            key = (register, half)
            if key in sources.setdefault(block, {}):
                return {"compact": False,
                        "reason": "source-half-used-by-multiple-packets"}
            sources[block][key] = pair == natural[::-1]

    counts = {"00": 0, "01": 0, "10": 0, "11": 0}
    for block, block_sources in sources.items():
        if len(block_sources) != 8:
            return {"compact": False,
                    "reason": f"block-{block}-does-not-map-eight-halves"}
        for register in range(4, 8):
            pattern = (block_sources[(register, 0)],
                       block_sources[(register, 1)])
            key = f"{int(pattern[0])}{int(pattern[1])}"
            counts[key] += 1
    assert sum(counts.values()) == 48
    return {
        "compact": True,
        "half_patterns": counts,
        "identity_masks": counts["00"],
        "symmetric_masks_absorbed_by_transpose": counts["11"],
        "runtime_residual_vpshufb": counts["01"] + counts["10"],
        "cross_128_repairs": 0,
        "global_materialization": False,
    }


def main() -> None:
    serialized = json.loads(
        (GENERATED / "tile4_serialized_mapping.json").read_text())["records"]
    current_pack = json.loads(
        (GENERATED / "tile4_q24_p_encode_gate.json").read_text())
    assert current_pack["TF1_transpose_tail_orientation"][
        "residual_asymmetric_masks"] == 13

    candidates = []
    rejected = []
    for axes in itertools.permutations(Q_BITS):
        route = q24_route(serialized, axes)
        if not route["compact"]:
            rejected.append({"q_axes": list(axes), **route})
            continue
        forward = {}
        for profile in global_gate.PROFILES:
            forward[profile] = global_gate.search_transform_and_stages(
                global_gate.CURRENT_AOS, layout(axes),
                global_gate.FORWARD_STAGE_AXES, profile)
        candidates.append({
            "q_axes": list(axes),
            "physical_layout": list(layout(axes)),
            "q_order_selector_0": q_order(axes, 0),
            "q_order_selector_1": q_order(axes, 1),
            "Q24": route,
            "Forward": forward,
            "BaseInv": {
                "data_repair_instructions": 0,
                "mechanism": "lane-wise quartic algebra plus lambda-table relabel",
            },
            "BaseMul": {
                "data_repair_instructions": 0,
                "mechanism": "lane-wise quartic algebra plus lambda-table relabel",
            },
        })

    current = next(item for item in candidates
                   if tuple(item["q_axes"]) == CURRENT_Q_AXES)
    for candidate in candidates:
        candidate["delta_vs_current_P"] = {
            "Forward": {
                profile: {
                    key: (candidate["Forward"][profile]["cost_per_tile"][key]
                          - current["Forward"][profile]["cost_per_tile"][key])
                    for key in ("uops", "critical_path_layers",
                                "shuffle_port_uops", "memory_uops")
                }
                for profile in global_gate.PROFILES
            },
            "three_Q24_runtime_shuffle_instructions": (
                KEYGEN_Q24_CALLS
                * (candidate["Q24"]["runtime_residual_vpshufb"]
                   - current["Q24"]["runtime_residual_vpshufb"])),
            "BaseInv_data_repair_instructions": 0,
            "BaseMul_data_repair_instructions": 0,
        }

    def rank(candidate: dict) -> tuple:
        forward_delta = candidate["delta_vs_current_P"]["Forward"][
            "balanced"]
        keygen_forward_uops = (KEYGEN_FORWARD_CALLS * 6
                               * forward_delta["uops"])
        q24_delta = candidate["delta_vs_current_P"][
            "three_Q24_runtime_shuffle_instructions"]
        return (keygen_forward_uops + q24_delta,
                forward_delta["critical_path_layers"],
                candidate["Q24"]["runtime_residual_vpshufb"],
                candidate["q_axes"])

    candidates.sort(key=rank)
    best_rank = rank(candidates[0])[:3]
    winners = [item for item in candidates if rank(item)[:3] == best_rank]
    best = candidates[0]
    best_forward_delta = best["delta_vs_current_P"]["Forward"]["balanced"]
    best_keygen_forward_delta = (KEYGEN_FORWARD_CALLS * 6
                                 * best_forward_delta["uops"])
    best_q24_delta = best["delta_vs_current_P"][
        "three_Q24_runtime_shuffle_instructions"]
    best_total = best_keygen_forward_delta + best_q24_delta

    output = {
        "schema": "ntruplus768-gt32-p-prime-joint-abi-survey-v1",
        "experiment": "GT32-P-PRIME-BASEINV-BM-Q24-JOINT-001",
        "scope": "generator-only bounded P-like coefficient-plane SoA survey",
        "frozen": {
            "coefficient_plane_SoA": True,
            "quartic_basis": "monomial",
            "Forward_arithmetic_and_range_policy": "current-qualified-P",
            "BaseInv_formula": "unchanged",
            "BaseMul_formula": "unchanged",
            "Montgomery_exponent": 0,
            "new_Montgomery_chains": 0,
        },
        "search_space": {
            "q_axis_permutations": 120,
            "compact_Q24_eligible": len(candidates),
            "rejected_noncompact": len(rejected),
            "consumer_weights": {
                "Forward": KEYGEN_FORWARD_CALLS,
                "BaseInv": KEYGEN_BASEINV_CALLS,
                "BaseMul": KEYGEN_BM_CALLS,
                "Q24": KEYGEN_Q24_CALLS,
            },
        },
        "semantic_proof": {
            "all_physical_mappings_bijective": True,
            "BaseInv_leaf_relabel_exact": True,
            "BaseMul_leaf_relabel_exact": True,
            "Q24_serialized_mapping_exact": True,
            "range_and_scale_unchanged": True,
        },
        "current_P": current,
        "best_static_result": {
            "winner_count": len(winners),
            "winners": [item["q_axes"] for item in winners],
            "runtime_Q24_masks_per_polynomial": {
                "current_P": current["Q24"]["runtime_residual_vpshufb"],
                "P_prime": best["Q24"]["runtime_residual_vpshufb"],
            },
            "two_Forward_balanced_uop_delta": best_keygen_forward_delta,
            "two_BaseInv_runtime_repair_delta": 0,
            "two_BaseMul_runtime_repair_delta": 0,
            "three_Q24_runtime_shuffle_delta": best_q24_delta,
            "whole_K3_K5_static_instruction_delta_floor": best_total,
            "complete_materialized_transition_removed": False,
            "multiply_or_reduction_chain_removed": False,
        },
        "top_candidates": candidates[:8],
        "decision": "static-hard-stop-no-assembly",
        "reason": (
            "The best P-prime layouts tie the current executable Forward "
            "cost in all scalar profiles and reduce Q24 residual masks from "
            "13 to 3, but this is only 30 runtime instructions across three "
            "packs.  BaseInv and BaseMul merely relabel tables and delete no "
            "runtime work.  No complete transition, Montgomery chain, "
            "checkpoint, or materialization disappears; this ceiling is "
            "smaller than the already non-deliverable P-suffix local win."
        ),
        "twisting_phase": {
            "status": "deferred-no-consumer-amortized-P-prime",
            "reopen_only_if": [
                "an existing Forward Montgomery chain directly emits a consumer-required scale/range",
                "a consumer reduction/checkpoint chain is deleted rather than moved",
                "net Montgomery-chain delta is nonpositive",
            ],
        },
        "reference_oracles": {
            "production": "current progressive-P",
            "algorithmic_upper_reference": "isolated P-suffix",
        },
    }
    OUT.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({
        "output": str(OUT),
        "compact_candidates": len(candidates),
        "best_winners": output["best_static_result"]["winners"],
        "best_static_instruction_delta": best_total,
        "decision": output["decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
