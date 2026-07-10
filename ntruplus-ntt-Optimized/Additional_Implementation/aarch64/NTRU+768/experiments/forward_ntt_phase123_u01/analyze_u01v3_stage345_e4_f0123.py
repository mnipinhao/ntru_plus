#!/usr/bin/env python3
"""Analyze U01v3 Track E E4/F0123 feasibility.

This is deliberately model-only unless the hard no-spill/no-reload/no-recompute
constraints are feasible.  E4 would extend E3/F012 to keep block3 live-ins too,
so the first gate is register cardinality before writing any physical asm.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from generate_phase123_shared_prefix_v3_block1_block01_fuse import (
    HANDOFF,
    load_stage345_block,
)
from generate_u01v3_stage345_e3_f012 import BLOCK2_E3_HANDOFF, regnum
from generate_u01v3_f01_a1_stage345_block0_preserve_block1_liveins import (
    vector_rw,
)


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "u01v3_f0123_liveness_clobber.json"
OUT_MD = ROOT / "u01v3_f0123_liveness_clobber.md"

LOAD_RE = re.compile(r"^\s*ldr\s+q(\d+),\s*\[x4,\s*#(\d+)\]")
TOTAL_Q_REGS = 32
Q0_CONSTANT_REG = 0


def code_part(line: str) -> str:
    return line.split("//", 1)[0].strip()


def write_regs_in_stage345(block: int) -> list[str]:
    writes: set[int] = set()
    for line in load_stage345_block(block):
        code = code_part(line)
        if not code:
            continue
        _op, write_regs, _read_regs, _mls = vector_rw(code)
        writes.update(write_regs)
    return [f"q{reg}" for reg in sorted(writes)]


def first_consume_sites(block: int) -> list[dict[str, object]]:
    sites: list[dict[str, object]] = []
    writes_seen: set[int] = set()
    for op_index, line in enumerate(load_stage345_block(block)):
        code = code_part(line)
        match = LOAD_RE.match(code)
        if match:
            dest = int(match.group(1))
            offset = int(match.group(2))
            if offset % 16 == 0:
                q_index = offset // 16
                if block * 8 <= q_index <= block * 8 + 7:
                    sites.append(
                        {
                            "q_index": q_index,
                            "semantic": f"Q{q_index}",
                            "op_index": op_index,
                            "original_load": code,
                            "original_dest": f"q{dest}",
                            "preclobbers": [f"q{reg}" for reg in sorted(writes_seen)],
                        }
                    )
                    writes_seen.add(dest)
                    continue
        if not code:
            continue
        _op, write_regs, _read_regs, _mls = vector_rw(code)
        writes_seen.update(write_regs)
    return sites


def e3_live_output_regs() -> dict[str, str]:
    live: dict[str, str] = {}
    for q in range(0, 8):
        live[f"Q{q}"] = HANDOFF[0][q]
    for q in range(8, 16):
        live[f"Q{q}"] = HANDOFF[1][q]
    for q in range(16, 24):
        live[f"Q{q}"] = BLOCK2_E3_HANDOFF[q]
    return live


def build_report() -> dict[str, object]:
    e3_regs = {regnum(reg) for reg in e3_live_output_regs().values()}
    q0_reserved = {Q0_CONSTANT_REG}
    globally_data_capable = sorted(set(range(TOTAL_Q_REGS)) - q0_reserved)
    free_after_e3 = sorted(set(globally_data_capable) - e3_regs)

    required_all_outputs = 32
    required_block3_outputs = 8
    max_data_regs = len(globally_data_capable)
    free_for_block3_after_e3 = len(free_after_e3)

    feasible_no_spill = (
        required_all_outputs <= max_data_regs
        and required_block3_outputs <= free_for_block3_after_e3
    )
    blocker = None
    if not feasible_no_spill:
        blocker = {
            "type": "register_cardinality",
            "summary": "F0123 needs 32 simultaneously live data vectors, but q0 must remain the modular-constant vector for Stage345, leaving at most 31 data-capable q registers.",
            "required_all_outputs": required_all_outputs,
            "max_data_regs_with_q0_reserved": max_data_regs,
            "global_deficit": required_all_outputs - max_data_regs,
            "e3_live_output_regs": len(e3_regs),
            "free_data_regs_after_e3": free_for_block3_after_e3,
            "required_block3_outputs": required_block3_outputs,
            "block3_deficit_after_e3": required_block3_outputs - free_for_block3_after_e3,
        }

    return {
        "candidate": "u01v3_stage345_semantic_e4_f0123",
        "production_default_changed": False,
        "status": "feasibility_failed" if not feasible_no_spill else "feasible",
        "allocator_invariants": {
            "destructive_same_as": "mls destructive dest must inherit old_dest color before greedy coloring",
            "same_as_interference_count_required": 0,
            "allocator_interference_count_required": 0,
            "first_consume_safety": "handoff physical register must not be clobbered before first semantic consumer",
            "cross_block_preservation": "block3 live-ins must survive Stage345 block0/block1/block2 until block3 consumes them",
            "abi": {
                "no_x18": True,
                "no_x19_x30_or_sp_unless_saved": True,
                "abi_sentinel_required": True,
            },
        },
        "feasible_no_spill": feasible_no_spill,
        "feasible_no_reload": feasible_no_spill,
        "feasible_no_recompute": feasible_no_spill,
        "blocker": blocker,
        "register_cardinality": {
            "total_neon_q_registers": TOTAL_Q_REGS,
            "reserved_q0_constant": True,
            "data_capable_registers_with_q0_reserved": [
                f"q{reg}" for reg in globally_data_capable
            ],
            "required_simultaneous_outputs_f0123": required_all_outputs,
            "max_simultaneous_data_outputs": max_data_regs,
            "global_output_deficit": max(0, required_all_outputs - max_data_regs),
            "e3_live_outputs": e3_live_output_regs(),
            "free_data_registers_after_e3_f012": [f"q{reg}" for reg in free_after_e3],
            "required_block3_liveins": required_block3_outputs,
            "block3_deficit_after_e3": max(
                0, required_block3_outputs - free_for_block3_after_e3
            ),
        },
        "block3_liveins": {
            f"Q{q}": None for q in range(24, 32)
        },
        "handoff_regs": {
            f"Q{q}": None for q in range(24, 32)
        },
        "required_vector_moves": None,
        "required_moves_reason": "not computed because no complete no-spill handoff assignment exists",
        "first_consume_safe": False,
        "first_consume_clobber_violations": None,
        "first_consume_sites": {
            "block3": first_consume_sites(3),
        },
        "stage345_clobbers": {
            "block0_original_write_regs": write_regs_in_stage345(0),
            "block1_original_write_regs": write_regs_in_stage345(1),
            "block2_original_write_regs": write_regs_in_stage345(2),
            "block3_original_write_regs": write_regs_in_stage345(3),
        },
        "safe_register_pool": {
            "global_data_capable": [f"q{reg}" for reg in globally_data_capable],
            "available_for_block3_after_e3": [f"q{reg}" for reg in free_after_e3],
            "available_for_block3_count": free_for_block3_after_e3,
            "required_for_block3_count": required_block3_outputs,
        },
        "emit_e4_asm": False,
        "emit_reason": "E4 physical asm/test/bench are not emitted because feasibility_no_spill is false.",
        "track_g_implication": "Use delayed producer / partial shared-prefix model if F0123 remains desired; current semantic-regalloc live-all strategy cannot satisfy no-spill/no-reload/no-recompute.",
    }


def write_md(report: dict[str, object]) -> None:
    blocker = report["blocker"]
    cardinality = report["register_cardinality"]
    OUT_MD.write_text(
        "# U01v3 E4 / F0123 Liveness Feasibility\n\n"
        "Status: feasibility failed; no E4 physical asm emitted. Production "
        "default unchanged.\n\n"
        "E4 would extend E3 from F012 to F0123 by keeping block3 Q24..Q31 live "
        "in registers while Stage345 block0, block1, and block2 run. Under the "
        "current hard rules this is blocked before allocator search: F0123 "
        "needs all 32 Stage12 outputs live, while `q0` must remain the modular "
        "constant vector used by Stage345 reductions.\n\n"
        "Feasibility summary:\n\n"
        "```text\n"
        f"feasible_no_spill: {report['feasible_no_spill']}\n"
        f"feasible_no_reload: {report['feasible_no_reload']}\n"
        f"feasible_no_recompute: {report['feasible_no_recompute']}\n"
        f"required_simultaneous_outputs_f0123: {cardinality['required_simultaneous_outputs_f0123']}\n"
        f"max_simultaneous_data_outputs_with_q0_reserved: {cardinality['max_simultaneous_data_outputs']}\n"
        f"global_output_deficit: {cardinality['global_output_deficit']}\n"
        f"available_for_block3_after_e3: {cardinality['free_data_registers_after_e3_f012']}\n"
        f"required_block3_liveins: {cardinality['required_block3_liveins']}\n"
        f"block3_deficit_after_e3: {cardinality['block3_deficit_after_e3']}\n"
        "```\n\n"
        "Blocker:\n\n"
        "```text\n"
        f"{blocker['summary'] if blocker else 'none'}\n"
        "```\n\n"
        "Block3 first-consume sites were still extracted for future Track G or "
        "spill-budget work; see `u01v3_f0123_liveness_clobber.json` for the "
        "exact load order, original destination registers, and preclobber sets.\n\n"
        "Consequence:\n\n"
        "```text\n"
        "Do not emit u01v3_stage345_semantic_e4_f0123.S under the current rules.\n"
        "A valid F0123 route needs at least one of: delayed producer, partial shared-prefix, one explicit spill, or a controlled reload/recompute contract.\n"
        "```\n"
    )


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n")
    write_md(report)
    print(OUT_JSON)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
