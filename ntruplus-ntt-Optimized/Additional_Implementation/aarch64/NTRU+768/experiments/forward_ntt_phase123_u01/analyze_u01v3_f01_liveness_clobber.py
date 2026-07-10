#!/usr/bin/env python3
"""Analyze U01v3 F01 one-pass block0 clobbers vs block1 live-ins."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from generate_phase123_shared_prefix_v3_block1_block01_fuse import (
    HANDOFF,
    ROWS,
    STAGE345_DEST,
    load_stage345_block,
    transform_stage345_for_handoff,
)


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "u01v3_f01_liveness_clobber.json"
OUT_MD = ROOT / "u01v3_f01_liveness_clobber.md"

WRITE_RE = re.compile(r"^\s*(?P<op>[a-z0-9.]+)\s+(?P<class>[vq])(?P<num>\d+)(?P<tail>[.,\s]|$)")
READ_RE = re.compile(r"\b([vq])(\d+)(?:\.|,|\s|\])")

VECTOR_STORE_OPS = {"str", "st1", "st2", "st3", "st4"}


@dataclass(frozen=True)
class WriteEvent:
    index: int
    op: str
    reg: str
    line: str


def normalized_reg(reg_class: str, num: str) -> str:
    return f"q{int(num)}"


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].rstrip()


def vector_write_events(lines: list[str]) -> list[WriteEvent]:
    events: list[WriteEvent] = []
    for index, line in enumerate(lines):
        code = strip_comment(line).strip()
        if not code:
            continue
        op = code.split(None, 1)[0]
        if op in VECTOR_STORE_OPS or op.startswith("st"):
            continue
        match = WRITE_RE.match(code)
        if not match:
            continue
        events.append(
            WriteEvent(
                index=index,
                op=op,
                reg=normalized_reg(match.group("class"), match.group("num")),
                line=code,
            )
        )
    return events


def vector_reads(line: str) -> set[str]:
    code = strip_comment(line)
    regs = {normalized_reg(cls, num) for cls, num in READ_RE.findall(code)}
    write = WRITE_RE.match(code.strip())
    if write:
        regs.discard(normalized_reg(write.group("class"), write.group("num")))
    return regs


def first_write(events: list[WriteEvent], reg: str) -> WriteEvent | None:
    return next((event for event in events if event.reg == reg), None)


def all_writes(events: list[WriteEvent], reg: str) -> list[WriteEvent]:
    return [event for event in events if event.reg == reg]


def analyze() -> dict[str, object]:
    stage3450 = load_stage345_block(0)
    stage3450_handoff = transform_stage345_for_handoff(0, stage3450)
    events = vector_write_events(stage3450_handoff)
    written_regs = sorted({event.reg for event in events}, key=lambda reg: int(reg[1:]))
    unwritten_regs = [f"q{i}" for i in range(32) if f"q{i}" not in set(written_regs)]

    block0_liveins = [
        {
            "q": f"Q{q}",
            "semantic": f"block0_Q{q}",
            "stage12_handoff_reg": HANDOFF[0][q],
            "stage345_consumer_reg": STAGE345_DEST[0][q],
            "move_required": HANDOFF[0][q] != STAGE345_DEST[0][q],
        }
        for q in range(0, 8)
    ]
    block1_liveins = [
        {
            "q": f"Q{q}",
            "semantic": f"block1_Q{q}",
            "stage12_handoff_reg": HANDOFF[1][q],
            "stage345_consumer_reg": STAGE345_DEST[1][q],
            "move_required": HANDOFF[1][q] != STAGE345_DEST[1][q],
        }
        for q in range(8, 16)
    ]

    clobbers: list[dict[str, object]] = []
    for entry in block1_liveins:
        reg = str(entry["stage12_handoff_reg"])
        first = first_write(events, reg)
        writes = all_writes(events, reg)
        clobbers.append(
            {
                **entry,
                "clobbered_by_stage345_block0": first is not None,
                "first_clobber": (
                    {
                        "stage345_handoff_line_index": first.index,
                        "op": first.op,
                        "instruction": first.line,
                    }
                    if first
                    else None
                ),
                "write_count_in_stage345_block0": len(writes),
                "first_three_writes": [
                    {
                        "stage345_handoff_line_index": event.index,
                        "op": event.op,
                        "instruction": event.line,
                    }
                    for event in writes[:3]
                ],
            }
        )

    block1_livein_regs = {
        str(entry["stage12_handoff_reg"]) for entry in block1_liveins
    }
    reserved_live_regs = {
        "q0": "modulus/constants live across kernel",
    }
    usable_parking_regs = [
        reg
        for reg in unwritten_regs
        if reg not in reserved_live_regs and reg not in block1_livein_regs
    ]
    clobbered_count = sum(1 for item in clobbers if item["clobbered_by_stage345_block0"])
    max_register_parking = len(usable_parking_regs)
    min_q_spills_with_parking = max(0, clobbered_count - max_register_parking)
    min_q_spills_without_parking = clobbered_count

    spill_budget = {}
    for budget in (0, 2, 4, 7, 8):
        preserved = min(budget + max_register_parking, clobbered_count)
        spill_budget[f"B{budget}"] = {
            "memory_q_spills_per_row": budget,
            "parking_regs_used": min(max_register_parking, max(0, clobbered_count - budget)),
            "preserved_block1_liveins_per_row": preserved,
            "feasible_without_raw_reload_or_duplicate_stage12": preserved == clobbered_count,
        }
    spill_budget["Bmin"] = {
        "memory_q_spills_per_row": min_q_spills_with_parking,
        "parking_regs_used": max_register_parking,
        "preserved_block1_liveins_per_row": clobbered_count,
        "feasible_without_raw_reload_or_duplicate_stage12": True,
    }

    return {
        "candidate": "u01v3_f01_onepass_liveness_clobber",
        "scope": "Stage345 block0 handoff body vs block1 Q8..Q15 live-ins",
        "constraints": {
            "production_default_changed": False,
            "s2_s4_mixed": False,
            "twiddle1_mixed": False,
            "slothy_mixed": False,
            "raw_q_reloads_allowed": False,
            "duplicate_stage12_allowed": False,
        },
        "stage345_block0_handoff": {
            "instruction_lines": len(stage3450_handoff),
            "vector_write_regs": written_regs,
            "vector_regs_not_written": unwritten_regs,
            "block1_livein_regs": sorted(block1_livein_regs, key=lambda reg: int(reg[1:])),
            "usable_parking_regs_without_rewriting_block0": usable_parking_regs,
            "reserved_unwritten_regs": reserved_live_regs,
        },
        "block0_liveins": block0_liveins,
        "block1_liveins": block1_liveins,
        "block1_clobbers_by_stage345_block0": clobbers,
        "summary": {
            "block1_liveins_total_per_row": len(block1_liveins),
            "block1_liveins_clobbered_per_row": clobbered_count,
            "block1_liveins_preserved_in_original_regs_per_row": len(block1_liveins) - clobbered_count,
            "usable_vector_parking_regs_per_row": max_register_parking,
            "min_q_spills_per_row_if_q21_parking_allowed": min_q_spills_with_parking,
            "min_q_spills_per_row_without_parking": min_q_spills_without_parking,
            "no_spill_A1_feasible_without_rewriting_stage345_block0_register_allocation": clobbered_count <= max_register_parking,
        },
        "spill_budget_feasibility": spill_budget,
    }


def write_markdown(result: dict[str, object]) -> None:
    s = result["summary"]
    b0 = result["stage345_block0_handoff"]
    rows = result["block1_clobbers_by_stage345_block0"]
    budget = result["spill_budget_feasibility"]

    lines: list[str] = [
        "# U01v3 F01 Liveness / Clobber Analyzer",
        "",
        "Date: 2026-07-09",
        "",
        "Status: analysis artifact only.  Production default is unchanged.  This",
        "does not mix S2/S4, twiddle1 semantic changes, or Slothy.",
        "",
        "## Scope",
        "",
        "This analyzes the one-pass F01 shape:",
        "",
        "```text",
        "Stage12 computes block0 Q0..Q7 and block1 Q8..Q15 once",
        "  -> Stage345 block0 consumes Q0..Q7 from registers",
        "  -> block1 Q8..Q15 must survive until Stage345 block1",
        "```",
        "",
        "The analyzed consumer is the existing Stage345 block0 handoff body,",
        "not the original scratch-load block0 body.",
        "",
        "## Stage345 Block0 Write Set",
        "",
        "Vector registers written by Stage345 block0 handoff:",
        "",
        "```text",
        " ".join(b0["vector_write_regs"]),
        "```",
        "",
        "Vector registers not written:",
        "",
        "```text",
        " ".join(b0["vector_regs_not_written"]),
        "```",
        "",
        "`q0` is reserved for constants, so the only usable parking register",
        "without rewriting block0 register allocation is:",
        "",
        "```text",
        " ".join(b0["usable_parking_regs_without_rewriting_block0"]) or "(none)",
        "```",
        "",
        "## Block1 Live-In Clobbers",
        "",
        "| Q | live reg | Stage345 block1 reg | first block0 clobber |",
        "|---|---|---|---|",
    ]
    for item in rows:
        first = item["first_clobber"]
        first_text = first["instruction"] if first else "not clobbered"
        lines.append(
            f"| {item['q']} | {item['stage12_handoff_reg']} | "
            f"{item['stage345_consumer_reg']} | `{first_text}` |"
        )

    lines.extend(
        [
            "",
            "## Summary",
            "",
            "```text",
            f"block1 live-ins per row:              {s['block1_liveins_total_per_row']}",
            f"clobbered by Stage345 block0:         {s['block1_liveins_clobbered_per_row']}",
            f"preserved in original regs:           {s['block1_liveins_preserved_in_original_regs_per_row']}",
            f"usable parking regs without rewrite:  {s['usable_vector_parking_regs_per_row']}",
            f"min q spills with q21 parking:        {s['min_q_spills_per_row_if_q21_parking_allowed']}",
            f"min q spills without parking:         {s['min_q_spills_per_row_without_parking']}",
            "```",
            "",
            "## A1 Feasibility",
            "",
            "A1 is not feasible as a no-spill, no-raw-reload, no-duplicate-Stage12",
            "candidate while keeping the current Stage345 block0 register allocation.",
            "",
            "Reason: 7 of 8 block1 live-ins are clobbered by Stage345 block0.  The",
            "only block1 live-in that survives in place is Q12 in `q9`.  Apart from",
            "that already-occupied live register, only one non-reserved vector",
            "register (`q21`) is not written by block0.  To make A1 possible without",
            "spills, block0 itself would need a new register allocation that",
            "explicitly avoids the block1 live-in set.",
            "",
            "## Spill Budget Feasibility",
            "",
            "This table is a Stage345-block0-only lower bound.  It assumes the block1",
            "live-in registers already exist at the point where Stage345 block0 starts.",
            "The current Stage12 producer may need a larger spill budget because it",
            "reuses some of these registers while producing later stripes.",
            "",
            "| candidate | memory q spills / row | parking regs | feasible under current block0? |",
            "|---|---:|---:|---|",
        ]
    )
    for name in ("B0", "B2", "B4", "B7", "B8", "Bmin"):
        if name not in budget:
            continue
        item = budget[name]
        feasible = "yes" if item["feasible_without_raw_reload_or_duplicate_stage12"] else "no"
        lines.append(
            f"| {name} | {item['memory_q_spills_per_row']} | "
            f"{item['parking_regs_used']} | {feasible} |"
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "```text",
            "B2 and B4 cannot preserve all block1 live-ins under the unchanged block0",
            "write set.  Bmin is 6 q spills per row if q21 is used as a parking",
            "register; otherwise the straightforward safe budget is B7 or B8.",
            "```",
            "",
            "The generated end-to-end spill-budget prototype currently uses the safer",
            "B8 shape for both Bmin and B8, because the present Stage12 producer reuses",
            "`q9` and `q21` while producing later stripes.  A true 6-spill Bmin would",
            "need a Stage12 producer with an explicit post-stripe liveness contract.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")


def main() -> int:
    result = analyze()
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n")
    write_markdown(result)
    print(OUT_JSON)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
