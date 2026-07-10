#!/usr/bin/env python3
"""Model Track G options after E4/F0123 live-all infeasibility."""

from __future__ import annotations

import json
from pathlib import Path

from generate_phase123_shared_prefix_v3_block1_block01_fuse import (
    load_stage345_block,
)
from generate_u01v3_stage345_e3_f012 import (
    BLOCK2_E3_HANDOFF,
    regnum,
)
from generate_u01v3_f01_a1_stage345_block0_preserve_block1_liveins import (
    intervals,
)
from analyze_u01v3_stage345_e4_f0123 import first_consume_sites


ROOT = Path(__file__).resolve().parent
OUT_MD = ROOT / "u01v3_f0123_track_g_model.md"
OUT_JSON = ROOT / "u01v3_f0123_track_g_candidates.json"


def executable_count(lines: list[str]) -> int:
    count = 0
    for line in lines:
        code = line.split("//", 1)[0].strip()
        if code and not code.endswith(":"):
            count += 1
    return count


def stage345_input_count(block: int) -> int:
    first_q = block * 8
    last_q = first_q + 7
    count = 0
    for site in first_consume_sites(block):
        q_index = int(site["q_index"])
        if first_q <= q_index <= last_q:
            count += 1
    return count


def original_input_map(block: int) -> dict[int, int]:
    """Recover the original Stage345 input register contract for a block."""

    return {
        regnum(str(site["original_dest"])): int(site["q_index"])
        for site in first_consume_sites(block)
    }


def stage345_max_live_estimate(block: int) -> int:
    """Return the semantic max-live value for the block's original SSA shape.

    This is a lower-level pressure estimate independent of the final physical
    allocation.  It is enough for the G2 infeasibility proof: block0 needs 15
    colors, but F0123 live-all + one spill leaves only 8 non-future colors.
    """

    from generate_u01v3_stage345_e3_f012 import collect_stage345_ssa
    from generate_phase123_shared_prefix_v3_block1_block01_fuse import HANDOFF

    if block == 0:
        init = {regnum(HANDOFF[0][q]): q for q in range(0, 8)}
    elif block == 1:
        init = {regnum(HANDOFF[1][q]): q for q in range(8, 16)}
    elif block == 2:
        init = {regnum(BLOCK2_E3_HANDOFF[q]): q for q in range(16, 24)}
    else:
        # Use original Stage345 destinations only for pressure estimate.
        init = original_input_map(3)
    _ops, defs = collect_stage345_ssa(load_stage345_block(block), block, init)
    ivals = intervals(defs)
    return max(
        (
            sum(1 for start, end in ivals.values() if start < point <= end)
            for point in range(max((end for _start, end in ivals.values()), default=0) + 2)
        ),
        default=0,
    )


def build_model() -> dict[str, object]:
    stage345_instr = {f"block{b}": executable_count(load_stage345_block(b)) for b in range(4)}
    stage345_inputs = {f"block{b}": stage345_input_count(b) for b in range(4)}
    max_live = {f"block{b}": stage345_max_live_estimate(b) for b in range(4)}

    e3_future_for_block0 = 16
    g2_future_for_block0 = 23
    data_regs_with_q0_reserved = 31
    g2_available_block0_colors = data_regs_with_q0_reserved - g2_future_for_block0

    candidates = {
        "G1_delayed_block3_scratch_consume": {
            "status": "model_promising",
            "shape": "Run E3/F012 first; consume block3 later from the Stage12 block3 scratch image already written by the compact Stage12 producer.",
            "max_live_q_regs": "same as E3 during Stage345 block0/1/2; block3 runs after those live ranges are dead",
            "extra_arithmetic_vs_E3": 0,
            "extra_q_loads_vs_E3": stage345_inputs["block3"] * 3,
            "extra_q_stores_vs_E3": "block3 final scatter stores only; Stage12 block3 scratch stores already exist in E3 producer",
            "q_spills_restores": 0,
            "expected_instruction_delta_vs_E3": stage345_instr["block3"] * 3,
            "feasible_under_q0_reserved": True,
            "notes": "This is not live-all block3 fusion. It is the bounded delayed-consume fallback that keeps no raw reload and no duplicate Stage12.",
        },
        "G2_spill1_live_all": {
            "status": "infeasible",
            "shape": "Keep Q0..Q31 live across Stage345 block0/1/2 with exactly one q spill/restore.",
            "max_live_q_regs": 31,
            "extra_arithmetic_vs_E3": 0,
            "extra_q_loads_vs_E3": 1,
            "extra_q_stores_vs_E3": 1,
            "q_spills_restores": 1,
            "expected_instruction_delta_vs_E3": "not emitted; register allocator feasibility fails before PMU",
            "feasible_under_q0_reserved": False,
            "blocker": {
                "cardinality_deficit_removed_by_one_spill": True,
                "cross_block_allocator_deficit_remains": True,
                "block0_stage345_max_live": max_live["block0"],
                "future_live_regs_reserved_for_block0": g2_future_for_block0,
                "available_block0_colors_with_q0_reserved": g2_available_block0_colors,
                "available_minus_required": g2_available_block0_colors - max_live["block0"],
                "reason": "After reserving block1+block2+block3 live-ins, Stage345 block0 would have only 8 non-future q colors, but its SSA max-live is 15. One q spill fixes global output cardinality, not block0 temporary pressure.",
            },
        },
        "G3_partial_shared_prefix_controlled_recompute": {
            "status": "model_only",
            "shape": "Recompute or delay only the block3-producing part after enough earlier values are consumed.",
            "max_live_q_regs": "bounded by chosen granularity; can avoid live-all pressure",
            "extra_arithmetic_vs_E3": "at least out3 recompute path per stripe if raw/intermediate values are retained",
            "extra_q_loads_vs_E3": "depends on retained raw/intermediate source contract",
            "extra_q_stores_vs_E3": "depends on retained raw/intermediate source contract",
            "q_spills_restores": 0,
            "expected_instruction_delta_vs_E3": "unknown until a concrete retained-source contract is chosen",
            "feasible_under_q0_reserved": "likely, if it avoids keeping block3 live across block0",
            "notes": "Do not build ASM yet. This is the next design path if G1 scratch-consume is not enough and G2 live-all spill remains infeasible.",
        },
    }

    return {
        "artifact": "u01v3_f0123_track_g_model",
        "production_default_changed": False,
        "current_best": "E3/F012",
        "stage345_instruction_counts_per_row": stage345_instr,
        "stage345_input_loads_per_row": stage345_inputs,
        "stage345_semantic_max_live": max_live,
        "q0_reserved": True,
        "data_regs_with_q0_reserved": data_regs_with_q0_reserved,
        "e3_future_reserved_for_block0": e3_future_for_block0,
        "g2_future_reserved_for_block0": g2_future_for_block0,
        "g2_available_block0_colors": g2_available_block0_colors,
        "candidates": candidates,
        "decision": {
            "build_g2_spill1": False,
            "build_g2_reason": candidates["G2_spill1_live_all"]["blocker"]["reason"],
            "build_g1_delayed_block3": True,
            "build_g1_reason": "Model is bounded: no duplicate Stage12, no raw reload, and only Stage345 block3 from the existing Stage12 block3 scratch image is added.",
            "build_g3": False,
        },
    }


def write_md(model: dict[str, object]) -> None:
    g1 = model["candidates"]["G1_delayed_block3_scratch_consume"]
    g2 = model["candidates"]["G2_spill1_live_all"]
    g3 = model["candidates"]["G3_partial_shared_prefix_controlled_recompute"]
    OUT_MD.write_text(
        "# U01v3 F0123 Track G Model\n\n"
        "Status: model generated after E4 live-all failure. Production default "
        "unchanged.\n\n"
        "Summary:\n\n"
        "```text\n"
        f"E3 current best: F012 semantic-regalloc\n"
        f"q0 reserved: {model['q0_reserved']}\n"
        f"data regs with q0 reserved: {model['data_regs_with_q0_reserved']}\n"
        f"Stage345 block0 max-live: {model['stage345_semantic_max_live']['block0']}\n"
        f"G2 future regs reserved for block0: {model['g2_future_reserved_for_block0']}\n"
        f"G2 available block0 colors: {model['g2_available_block0_colors']}\n"
        "```\n\n"
        "G1 delayed block3 scratch-consume:\n\n"
        "```text\n"
        f"status: {g1['status']}\n"
        f"extra_arithmetic_vs_E3: {g1['extra_arithmetic_vs_E3']}\n"
        f"extra_q_loads_vs_E3: {g1['extra_q_loads_vs_E3']}\n"
        f"q_spills_restores: {g1['q_spills_restores']}\n"
        f"expected_instruction_delta_vs_E3: {g1['expected_instruction_delta_vs_E3']}\n"
        "```\n\n"
        "G2 one-vector spill live-all:\n\n"
        "```text\n"
        f"status: {g2['status']}\n"
        f"q_spills_restores: {g2['q_spills_restores']}\n"
        f"block0_stage345_max_live: {g2['blocker']['block0_stage345_max_live']}\n"
        f"available_block0_colors: {g2['blocker']['available_block0_colors_with_q0_reserved']}\n"
        f"available_minus_required: {g2['blocker']['available_minus_required']}\n"
        "```\n\n"
        "The important point is that one spill solves the global 32-output vs "
        "31-data-register count, but it does not solve cross-block preservation. "
        "With block1+block2+block3 live-ins reserved, Stage345 block0 would have "
        "only 8 available q colors while its SSA max-live is 15.\n\n"
        "G3 partial shared-prefix / controlled recompute:\n\n"
        "```text\n"
        f"status: {g3['status']}\n"
        f"feasible_under_q0_reserved: {g3['feasible_under_q0_reserved']}\n"
        "```\n\n"
        "Decision:\n\n"
        "```text\n"
        "Do not build G2_spill1 live-all ASM under current rules.\n"
        "Build G1_delayed_block3 scratch-consume as the bounded Track G prototype.\n"
        "Keep G3 model-only until G1 PMU says scratch-consume is not enough.\n"
        "```\n"
    )


def main() -> int:
    model = build_model()
    OUT_JSON.write_text(json.dumps(model, indent=2) + "\n")
    write_md(model)
    print(OUT_JSON)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
