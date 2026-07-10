#!/usr/bin/env python3
"""Model U01v3 F0123 Track G3 candidates after G1.

G1 keeps E3/F012 and consumes block3 from the Stage12 out3 scratch image.
G3 asks whether block3 scratch consumption can be avoided without returning to
E4-style live-all.  This model is intentionally conservative: it must pass the
hard gate before any physical ASM is emitted.
"""

from __future__ import annotations

import json
from pathlib import Path

from analyze_u01v3_stage345_e4_f0123 import first_consume_sites
from generate_phase123_shared_prefix_v3_block1_block01_fuse import load_stage345_block


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "u01v3_f0123_g3_candidates.json"
OUT_MD = ROOT / "u01v3_f0123_g3_model.md"

ROWS = 3
STRIPES = 8
Q_PER_BLOCK = 8


def executable_count(lines: list[str]) -> int:
    return sum(
        1
        for line in lines
        if (code := line.split("//", 1)[0].strip()) and not code.endswith(":")
    )


def stage345_block_input_loads(block: int) -> int:
    first_q = block * Q_PER_BLOCK
    last_q = first_q + Q_PER_BLOCK - 1
    return sum(
        1
        for site in first_consume_sites(block)
        if first_q <= int(site["q_index"]) <= last_q
    )


def stage345_block_input_contract(block: int) -> list[dict[str, object]]:
    return [
        {
            "q_index": int(site["q_index"]),
            "original_dest": site["original_dest"],
            "first_consume_op_index": int(site["op_index"]),
            "preclobbers": site["preclobbers"],
            "same_dest_handoff_safe": site["original_dest"] not in site["preclobbers"],
        }
        for site in first_consume_sites(block)
    ]


def build_model() -> dict[str, object]:
    block3_stage345_instr_per_row = executable_count(load_stage345_block(3))
    block3_q_loads_per_row = stage345_block_input_loads(3)
    block3_q_loads_total = block3_q_loads_per_row * ROWS
    block3_stage12_out3_stores_total = STRIPES * ROWS

    # Minimal delayed out3 recompute from raw Phase123 row scratch:
    # loads: A/B/C/D per stripe
    # arithmetic: sub(B-D), sqrdmulh, mul, mls, sub(A-C), sub(out3)
    # twiddle loads: q2/q3/q4 per row
    delayed_raw_loads = 4 * STRIPES * ROWS
    delayed_twiddle_loads = 3 * ROWS
    delayed_arithmetic = 6 * STRIPES * ROWS
    delayed_extra_instr = (
        delayed_raw_loads
        + delayed_twiddle_loads
        + delayed_arithmetic
        - block3_q_loads_total
        - block3_stage12_out3_stores_total
    )

    # Partial prefix stores t1 and t3 during Stage12, then later reloads both
    # and subtracts.  This avoids raw reloads but replaces one out3 store with
    # two prefix stores and one block3 q load with two prefix loads plus one
    # arithmetic subtract.
    prefix_stores = 2 * STRIPES * ROWS
    prefix_loads = 2 * STRIPES * ROWS
    prefix_finish_arithmetic = STRIPES * ROWS
    prefix_extra_instr = (
        prefix_stores
        + prefix_loads
        + prefix_finish_arithmetic
        - block3_stage12_out3_stores_total
        - block3_q_loads_total
    )

    block3_input_contract = stage345_block_input_contract(3)
    same_dest_handoff_safe = all(
        bool(site["same_dest_handoff_safe"]) for site in block3_input_contract
    )

    candidates = {
        "G3a_delayed_block3_producer_after_E3": {
            "status": "hard_gate_fail",
            "shape": "After E3/F012 consumes block0/1/2, regenerate Q24..Q31 and hand off directly to Stage345 block3.",
            "extra_arithmetic_instructions": delayed_arithmetic,
            "extra_q_loads": delayed_raw_loads + delayed_twiddle_loads,
            "removed_block3_q_loads": block3_q_loads_total,
            "removed_block3_q_stores_if_applicable": block3_stage12_out3_stores_total,
            "raw_q_reloads": delayed_raw_loads,
            "stack_spills": 0,
            "max_live_q_regs": "producer-local <= 12 plus q0 constant; register pressure is feasible",
            "same_as_interference_feasibility": "not the blocker; block3 same-dest handoff is preclobber-safe",
            "same_dest_handoff_safe": same_dest_handoff_safe,
            "expected_instruction_delta_vs_G1": delayed_extra_instr,
            "expected_cycle_risk": "high: removes 48 memory ops but adds 96 raw q loads, 9 twiddle loads, and 144 arithmetic instructions",
            "hard_gate": {
                "no_raw_q_reload": False,
                "no_stack_spill": True,
                "no_live_all_violation": True,
                "max_live_q_regs_lte_available": True,
                "expected_instruction_count_ok": False,
            },
            "reason": "After G1/E3 Stage12, raw D has been overwritten by out3. Regenerating block3 later needs raw A/B/C/D reloads unless extra prefix state is saved.",
        },
        "G3b_partial_shared_prefix_t1_t3": {
            "status": "not_plausible",
            "shape": "Store t1 and t3 prefix values during Stage12, then finish Q24..Q31 after E3 frees registers.",
            "extra_arithmetic_instructions": prefix_finish_arithmetic,
            "extra_q_loads": prefix_loads,
            "extra_q_stores": prefix_stores,
            "removed_block3_q_loads": block3_q_loads_total,
            "removed_block3_q_stores_if_applicable": block3_stage12_out3_stores_total,
            "raw_q_reloads": 0,
            "stack_spills": 0,
            "max_live_q_regs": "bounded; prefix is memory-resident, not live-all",
            "same_as_interference_feasibility": "feasible, but memory/instruction cost dominates",
            "expected_instruction_delta_vs_G1": prefix_extra_instr,
            "expected_cycle_risk": "high: doubles prefix memory traffic and adds finish arithmetic",
            "hard_gate": {
                "no_raw_q_reload": True,
                "no_stack_spill": True,
                "no_live_all_violation": True,
                "max_live_q_regs_lte_available": True,
                "expected_instruction_count_ok": False,
            },
            "reason": "Avoids raw reloads, but replaces 24 out3 stores and 24 Stage345 q loads with 48 prefix stores, 48 prefix loads, and 24 subtracts.",
        },
        "G3c_bounded_recompute_no_prefix": {
            "status": "hard_gate_fail",
            "shape": "Do not save prefix; recompute block3 from raw row scratch after E3/F012.",
            "extra_arithmetic_instructions": delayed_arithmetic,
            "extra_q_loads": delayed_raw_loads + delayed_twiddle_loads,
            "removed_block3_q_loads": block3_q_loads_total,
            "removed_block3_q_stores_if_applicable": block3_stage12_out3_stores_total,
            "raw_q_reloads": delayed_raw_loads,
            "stack_spills": 0,
            "max_live_q_regs": "feasible locally, but raw reload contract fails",
            "same_as_interference_feasibility": "not the blocker",
            "expected_instruction_delta_vs_G1": delayed_extra_instr,
            "expected_cycle_risk": "high",
            "hard_gate": {
                "no_raw_q_reload": False,
                "no_stack_spill": True,
                "no_live_all_violation": True,
                "max_live_q_regs_lte_available": True,
                "expected_instruction_count_ok": False,
            },
            "reason": "This is effectively G3a without retained prefix; it violates the no raw q reload gate and is far above G1 instruction count.",
        },
    }

    emit_asm = all(
        c["status"] in {"plausible", "model_promising"} for c in candidates.values()
    )

    return {
        "artifact": "u01v3_f0123_g3_model",
        "production_default_changed": False,
        "baseline": {
            "G1": {
                "cycles": 2694,
                "instructions": 3743,
                "block3_q_loads_retained": block3_q_loads_total,
                "block3_stage12_out3_stores": block3_stage12_out3_stores_total,
            },
            "P": {"cycles": 2707, "instructions": 3835},
            "V": {"cycles": 2724, "instructions": 3875},
        },
        "stage345_block3": {
            "instruction_count_per_row": block3_stage345_instr_per_row,
            "input_q_loads_per_row": block3_q_loads_per_row,
            "input_q_loads_total": block3_q_loads_total,
            "input_contract": block3_input_contract,
            "same_dest_handoff_safe": same_dest_handoff_safe,
        },
        "candidate_summary": {
            name: {
                "status": data["status"],
                "expected_instruction_delta_vs_G1": data["expected_instruction_delta_vs_G1"],
                "raw_q_reloads": data["raw_q_reloads"],
                "expected_cycle_risk": data["expected_cycle_risk"],
            }
            for name, data in candidates.items()
        },
        "candidates": candidates,
        "decision": {
            "emit_physical_asm": False,
            "reason": "No G3 candidate passes the hard gate. G3a/G3c require raw q reloads and add about 201 instructions vs G1; G3b avoids raw reloads but adds about 72 instructions and more prefix memory traffic.",
            "next": "Stop F0123 expansion here unless we are willing to redesign deeper Phase123 layout/producer order.",
        },
    }


def write_md(model: dict[str, object]) -> None:
    summary = model["candidate_summary"]
    OUT_MD.write_text(
        "# U01v3 F0123 G3 Model\n\n"
        "Status: model-only.  No physical G3 ASM emitted.  Production default "
        "unchanged.\n\n"
        "Baseline:\n\n"
        "```text\n"
        "G1 = E3/F012 semantic-regalloc + delayed block3 scratch consume\n"
        f"G1 cycles: {model['baseline']['G1']['cycles']}\n"
        f"G1 instructions: {model['baseline']['G1']['instructions']}\n"
        f"G1 retained block3 q loads: {model['baseline']['G1']['block3_q_loads_retained']}\n"
        "```\n\n"
        "The core issue:\n\n"
        "```text\n"
        "G1 Stage12 computes block3 out3 and stores it to scratch.\n"
        "Stage345 block3 later reloads Q24..Q31 from that scratch image.\n"
        "If block3 is regenerated after E3/F012, raw D has already been overwritten by out3.\n"
        "Avoiding the block3 q load therefore needs either raw reloads or extra prefix storage.\n"
        "```\n\n"
        "Candidate summary:\n\n"
        "```text\n"
        + "\n".join(
            f"{name}: status={item['status']}, delta_vs_G1={item['expected_instruction_delta_vs_G1']}, raw_q_reloads={item['raw_q_reloads']}, risk={item['expected_cycle_risk']}"
            for name, item in summary.items()
        )
        + "\n```\n\n"
        "Stage345 block3 direct handoff itself is not the blocker.  Its original "
        "destination registers are preclobber-safe, so a producer could hand off "
        "to those registers if the producer source contract were cheap enough.\n\n"
        "Decision:\n\n"
        "```text\n"
        "emit_physical_asm: false\n"
        "reason: no G3 candidate passes the hard gate\n"
        "G3a/G3c: fail no_raw_q_reload and instruction-count gate\n"
        "G3b: no raw reload, but too much prefix memory traffic and +72 instructions\n"
        "```\n\n"
        "Next meaningful direction:\n\n"
        "```text\n"
        "Keep G1 as the current F0123 sweet spot.\n"
        "Stop F0123 expansion unless we revisit deeper Phase123 layout/producer order.\n"
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
