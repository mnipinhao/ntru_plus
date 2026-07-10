#!/usr/bin/env python3
"""Build semantic IR and first-wave allocation candidates for U01v3 F01.

This is intentionally an analysis/codegen gate, not a blind register rewrite.
It records why a candidate can or cannot be emitted under the no-spill,
no-raw-reload, no-duplicate-Stage12 constraints.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from generate_phase123_shared_prefix_v3_block1_block01_fuse import (
    HANDOFF,
    STAGE345_DEST,
    load_stage345_block,
    transform_stage345_for_handoff,
)


ROOT = Path(__file__).resolve().parent
OUT_IR = ROOT / "u01v3_stage345_block01_semantic_ir.json"
OUT_CANDIDATES = ROOT / "u01v3_stage345_block01_regalloc_candidates.json"

VREG_RE = re.compile(r"\b([vq])(\d+)(?:\.|,|\s|\])")
WRITE_RE = re.compile(r"^\s*(?P<op>[a-z0-9.]+)\s+(?P<class>[vq])(?P<num>\d+)(?P<tail>[.,\s]|$)")
LOAD_RE = re.compile(r"^\s*ldr\s+(q\d+),\s*\[x4,\s*#(\d+)\]")
VECTOR_STORE_OPS = {"str", "st1", "st2", "st3", "st4"}

ABI_SENSITIVE_VREGS = {f"q{i}" for i in range(8, 16)}
RESERVED_VREGS = {"q0"}


def regnum(reg: str) -> int:
    return int(reg[1:])


def sorted_regs(regs: set[str] | list[str]) -> list[str]:
    return sorted(regs, key=regnum)


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].strip()


def vector_reads(line: str) -> list[str]:
    code = strip_comment(line)
    regs = [f"q{int(num)}" for _cls, num in VREG_RE.findall(code)]
    write = WRITE_RE.match(code)
    if write:
        dest = f"q{int(write.group('num'))}"
        regs = regs[1:] if regs and regs[0] == dest else regs
    return regs


def vector_write(line: str) -> str | None:
    code = strip_comment(line)
    if not code:
        return None
    op = code.split(None, 1)[0]
    if op in VECTOR_STORE_OPS or op.startswith("st"):
        return None
    match = WRITE_RE.match(code)
    if not match:
        return None
    return f"q{int(match.group('num'))}"


def stage345_summary(block: int, handoff: bool) -> dict[str, Any]:
    lines = load_stage345_block(block)
    if handoff:
        lines = transform_stage345_for_handoff(block, lines)

    reads: set[str] = set()
    writes: set[str] = set()
    ops: list[dict[str, Any]] = []
    load_replacements: list[dict[str, Any]] = []
    for idx, line in enumerate(lines):
        code = strip_comment(line)
        write = vector_write(line)
        line_reads = vector_reads(line)
        reads.update(line_reads)
        if write:
            writes.add(write)
        match = LOAD_RE.match(code)
        if match:
            load_replacements.append(
                {
                    "line_index": idx,
                    "dest": match.group(1),
                    "scratch_offset": int(match.group(2)),
                    "q_index": int(match.group(2)) // 16,
                }
            )
        ops.append(
            {
                "index": idx,
                "text": line,
                "reads": line_reads,
                "writes": [write] if write else [],
            }
        )
    return {
        "block": block,
        "handoff": handoff,
        "instruction_count": len(lines),
        "vector_reads": sorted_regs(reads),
        "vector_writes": sorted_regs(writes),
        "vector_regs_not_written": [f"q{i}" for i in range(32) if f"q{i}" not in writes],
        "abi_sensitive_writes": sorted_regs(writes & ABI_SENSITIVE_VREGS),
        "load_replacements": load_replacements,
        "ops": ops,
    }


def semantic_inputs() -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for block in (0, 1):
        stage = f"stage345_block{block}"
        for q in range(block * 8, block * 8 + 8):
            name = f"B{block}_Q{q - block * 8}"
            values.append(
                {
                    "semantic_name": name,
                    "q_index": q,
                    "producer": "Stage12",
                    "first_use": f"{stage}_input",
                    "last_use": f"{stage}_input_consumed",
                    "physical_register_if_fixed": HANDOFF[block][q],
                    "stage345_consumer_register": STAGE345_DEST[block][q],
                    "can_rename": True,
                    "can_clobber_after_last_use": True,
                    "must_preserve_until": f"{stage}_input_consumed",
                }
            )
    return values


def build_ir() -> dict[str, Any]:
    block0 = stage345_summary(0, handoff=True)
    block1 = stage345_summary(1, handoff=True)
    block1_live_regs = {HANDOFF[1][q] for q in range(8, 16)}
    block0_writes = set(block0["vector_writes"])
    clobbered = sorted_regs(block1_live_regs & block0_writes)
    preserved = sorted_regs(block1_live_regs - block0_writes)
    free_across_block0 = [
        reg
        for reg in block0["vector_regs_not_written"]
        if reg not in RESERVED_VREGS and reg not in block1_live_regs
    ]

    return {
        "candidate_family": "u01v3_stage345_block01_regalloc",
        "scope": "U01v3 F01 block0+block1 only",
        "global_constraints": {
            "production_default_changed": False,
            "mix_s2_s4": False,
            "mix_twiddle1": False,
            "slothy_first_wave": False,
            "stack_spill_primary": False,
            "extra_raw_q_loads": False,
            "duplicate_stage12": False,
        },
        "semantic_values": semantic_inputs(),
        "stage345": {
            "block0_handoff": block0,
            "block1_handoff": block1,
        },
        "block1_livein_hazard": {
            "block1_live_regs": sorted_regs(block1_live_regs),
            "clobbered_by_current_block0": clobbered,
            "preserved_by_current_block0": preserved,
            "free_vector_regs_across_current_block0": free_across_block0,
            "needs_block0_regalloc_rewrite_for_no_spill": len(clobbered) > len(free_across_block0),
        },
    }


def candidate_record(
    name: str,
    status: str,
    reason: str,
    *,
    raw_q_loads: int = 0,
    duplicate_stage12: bool = False,
    stack_spills: int = 0,
    vector_moves: int | str = 0,
    asm_emit: bool = False,
    next_action: str | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "reason": reason,
        "metrics": {
            "extra_raw_q_loads": raw_q_loads,
            "duplicate_stage12": duplicate_stage12,
            "stack_spills": stack_spills,
            "inserted_vector_moves": vector_moves,
        },
        "emit_asm_in_first_wave": asm_emit,
        "next_action": next_action,
    }


def search_candidates(ir: dict[str, Any]) -> dict[str, Any]:
    hazard = ir["block1_livein_hazard"]
    clobbered = hazard["clobbered_by_current_block0"]
    free_regs = hazard["free_vector_regs_across_current_block0"]
    block0_writes = set(ir["stage345"]["block0_handoff"]["vector_writes"])
    block1_live = set(hazard["block1_live_regs"])
    nonreserved_pool = {f"q{i}" for i in range(1, 32)} - block1_live
    pool_after_avoiding_block1 = sorted_regs(nonreserved_pool)

    candidates = [
        candidate_record(
            "R01a_delayed_produce_layout",
            "infeasible",
            "Producing block0, consuming block0, then producing block1 requires either reloading raw Stage12 inputs from scratch or recomputing Stage12. Both are forbidden.",
            raw_q_loads=96,
            duplicate_stage12=True,
            next_action="Do not emit; this is the old two-pass failure mode in different words.",
        ),
        candidate_record(
            "R01b_keep_block1_live_remap_block0_temps",
            "search_feasible_codegen_not_trusted_yet",
            "A no-spill allocation exists only if Stage345 block0 is rebuilt so its temps avoid all block1 live-in registers. Prior A1 proved a physical SSA rename can avoid these regs, but correctness failed, so this must be regenerated from a stronger semantic DAG before PMU.",
            stack_spills=0,
            vector_moves=">=3 existing block1 Q11 bridge unless block1 input contract changes",
            asm_emit=False,
            next_action="Build a verified Stage345 block0 DAG emitter; do not reuse the A1 physical-regex rename as a performance candidate.",
        ),
        candidate_record(
            "R01c_consumer_shaped_producer",
            "blocked_by_overlapping_consumer_regs",
            "The current block0 and block1 consumer-shaped physical registers overlap and Stage345 block0 writes most of the block1 consumer set. This requires choosing a new block1 consumer contract together with a block0 temp allocation, not only changing Stage12 outputs.",
            stack_spills=0,
            vector_moves="unknown until new block1 consumer contract is chosen",
            asm_emit=False,
            next_action="Search block1 input contract jointly with block0 temp allocation.",
        ),
        candidate_record(
            "R01d_minimal_vector_move_bridge",
            "infeasible_with_current_block0",
            f"Current Stage345 block0 clobbers {len(clobbered)} block1 live-ins ({' '.join(clobbered)}), but only {len(free_regs)} non-reserved parking regs survive block0 ({' '.join(free_regs) or 'none'}). A <=4-move bridge cannot preserve the live set without stack spill.",
            vector_moves=">4 or requires block0 rewrite",
            asm_emit=False,
            next_action="Only revisit after R01b creates a block0 allocation with more surviving parking regs.",
        ),
    ]

    return {
        "candidate_family": "u01v3_stage345_block01_regalloc",
        "search_policy": {
            "priority_1": "correctness_safe",
            "priority_2": "zero_raw_q_reload",
            "priority_3": "zero_stack_spill",
            "priority_4": "minimize_vector_moves",
            "priority_5": "minimize_simultaneous_live_q_registers",
            "priority_6": "avoid_abi_sensitive_regs_unless_sentinel_covers_them",
        },
        "hard_constraints_checked": {
            "block1_liveins_not_clobbered_by_block0": False,
            "raw_q_reloads": 0,
            "stack_spills_primary": 0,
            "duplicate_stage12": False,
            "no_x18": True,
            "no_new_gpr_callee_saved": True,
        },
        "hazard_summary": {
            "block0_current_writes": sorted_regs(block0_writes),
            "block1_liveins": hazard["block1_live_regs"],
            "block1_liveins_clobbered_by_current_block0": clobbered,
            "free_regs_across_current_block0": free_regs,
            "nonreserved_pool_if_block0_avoids_block1_liveins": pool_after_avoiding_block1,
        },
        "candidates": candidates,
        "first_wave_decision": {
            "emit_primary_asm": False,
            "reason": "No candidate is correctness-safe at the semantic-regalloc level yet. R01b is the only plausible no-spill path, but it requires a verified semantic Stage345 block0 DAG emitter; the previous A1 physical rename failed correctness.",
        },
    }


def main() -> int:
    ir = build_ir()
    candidates = search_candidates(ir)
    OUT_IR.write_text(json.dumps(ir, indent=2) + "\n")
    OUT_CANDIDATES.write_text(json.dumps(candidates, indent=2) + "\n")
    print(OUT_IR)
    print(OUT_CANDIDATES)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
