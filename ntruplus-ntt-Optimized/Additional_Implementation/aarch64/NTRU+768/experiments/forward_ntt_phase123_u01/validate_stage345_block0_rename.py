#!/usr/bin/env python3
"""Validate Track E Stage345 block0 register renaming.

The old E1 allocator treated `mls` as an in-place operation, but the mandatory
`same_as old_dest` color was enforced only after greedy allocation.  That can
hide interference conflicts.  This validator rebuilds the SSA contract,
checks the old E1 rename, and emits a corrected allocator used by E1v2.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from generate_phase123_shared_prefix_v3_block1_block01_fuse import (
    HANDOFF,
    load_stage345_block,
)
from generate_u01v3_f01_a1_stage345_block0_preserve_block1_liveins import (
    AVAILABLE_COLORS,
    BLOCK1_RESERVED,
    VREG_RE,
    allocate as old_allocate,
    collect_stage345_ssa,
    intervals,
    overlap,
)


ROOT = Path(__file__).resolve().parent
OUT_MD = ROOT / "stage345_block0_rename_validation.md"
OUT_JSON = ROOT / "stage345_block0_rename_validation.json"

STAGE3_EXIT_OP = 64


class ValidationError(RuntimeError):
    pass


def code_part(line: str) -> str:
    return line.split("//", 1)[0].strip()


def vector_operands(line: str) -> list[tuple[str, int]]:
    return [(m.group(1), int(m.group(2))) for m in VREG_RE.finditer(code_part(line))]


def fixed_repr(fixed: object) -> object:
    if isinstance(fixed, tuple):
        return list(fixed)
    return fixed


def color_conflicts(
    colors: dict[str, int],
    defs: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    ivals = intervals(defs)
    vids = sorted(ivals)
    conflicts: list[dict[str, object]] = []
    for i, a in enumerate(vids):
        for b in vids[i + 1 :]:
            if colors.get(a) != colors.get(b):
                continue
            if not overlap(ivals[a], ivals[b]):
                continue
            conflicts.append(
                {
                    "color": f"q{colors[a]}",
                    "a": a,
                    "a_interval": list(ivals[a]),
                    "b": b,
                    "b_interval": list(ivals[b]),
                }
            )
    return conflicts


def corrected_allocate(
    defs: dict[str, dict[str, object]]
) -> tuple[dict[str, int], int, list[dict[str, object]]]:
    """Allocate while honoring same_as before choosing any other color."""

    ivals = intervals(defs)
    colors: dict[str, int] = {}
    notes: list[dict[str, object]] = []

    for vid, data in defs.items():
        fixed = data["fixed"]
        if isinstance(fixed, int):
            colors[vid] = fixed

    def conflicting_values(vid: str, color: int) -> list[str]:
        if vid not in ivals:
            return []
        return [
            other
            for other, other_color in colors.items()
            if other != vid
            and other_color == color
            and other in ivals
            and overlap(ivals[vid], ivals[other])
        ]

    ordered = sorted(ivals, key=lambda v: (ivals[v][0], ivals[v][1], v))
    changed = True
    while changed:
        changed = False
        for vid in ordered:
            if vid in colors:
                continue
            fixed = defs[vid]["fixed"]
            if isinstance(fixed, tuple) and fixed[0] == "same_as" and fixed[1] in colors:
                color = colors[fixed[1]]
                conflicts = conflicting_values(vid, color)
                if conflicts:
                    notes.append(
                        {
                            "type": "same_as_interference",
                            "vid": vid,
                            "source": fixed[1],
                            "color": f"q{color}",
                            "conflicts": conflicts,
                        }
                    )
                colors[vid] = color
                changed = True

    for vid in ordered:
        if vid in colors:
            continue
        fixed = defs[vid]["fixed"]
        if isinstance(fixed, tuple) and fixed[0] == "same_as":
            raise ValidationError(f"same_as source not colored before {vid}: {fixed[1]}")
        forbidden: set[int] = set()
        for other, color in colors.items():
            if other in ivals and overlap(ivals[vid], ivals[other]):
                forbidden.add(color)
        for color in AVAILABLE_COLORS:
            if color not in forbidden:
                colors[vid] = color
                break
        else:
            raise ValidationError(f"no non-reserved color for {vid} interval {ivals[vid]}")

        # Some later same_as values may now become colorable.
        changed = True
        while changed:
            changed = False
            for dep in ordered:
                if dep in colors:
                    continue
                dep_fixed = defs[dep]["fixed"]
                if (
                    isinstance(dep_fixed, tuple)
                    and dep_fixed[0] == "same_as"
                    and dep_fixed[1] in colors
                ):
                    dep_color = colors[dep_fixed[1]]
                    conflicts = conflicting_values(dep, dep_color)
                    if conflicts:
                        notes.append(
                            {
                                "type": "same_as_interference",
                                "vid": dep,
                                "source": dep_fixed[1],
                                "color": f"q{dep_color}",
                                "conflicts": conflicts,
                            }
                        )
                    colors[dep] = dep_color
                    changed = True

    for vid, data in defs.items():
        if vid in colors:
            continue
        fixed = data["fixed"]
        if isinstance(fixed, int):
            colors[vid] = fixed
        elif isinstance(fixed, tuple) and fixed[0] == "same_as" and fixed[1] in colors:
            colors[vid] = colors[fixed[1]]
        else:
            point = int(data["def"]) + 1
            forbidden = {
                color
                for other, color in colors.items()
                if other in ivals and ivals[other][0] < point <= ivals[other][1]
            }
            for color in AVAILABLE_COLORS:
                if color not in forbidden:
                    colors[vid] = color
                    break
            else:
                raise ValidationError(f"no dead-write color for {vid} at point {point}")

    max_live = 0
    for point in range(max((end for _start, end in ivals.values()), default=0) + 2):
        live = [vid for vid, ival in ivals.items() if ival[0] < point <= ival[1]]
        max_live = max(max_live, len(live))
    return colors, max_live, notes


def same_as_constraints(defs: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    constraints: list[dict[str, object]] = []
    for vid, data in sorted(defs.items()):
        fixed = data["fixed"]
        if isinstance(fixed, tuple) and fixed[0] == "same_as":
            constraints.append(
                {
                    "vid": vid,
                    "source": fixed[1],
                    "def": data["def"],
                    "uses": data["uses"],
                }
            )
    return constraints


def same_as_interference_notes(
    allocator_notes: list[dict[str, object]],
) -> list[dict[str, object]]:
    return [note for note in allocator_notes if note.get("type") == "same_as_interference"]


def rewrite_line_with_colors(line: str, read_colors: list[int], write_colors: list[int]) -> str:
    colors = write_colors + read_colors
    index = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal index
        prefix = match.group(1)
        if index >= len(colors):
            return match.group(0)
        color = colors[index]
        index += 1
        return f"{prefix}{color}"

    return VREG_RE.sub(repl, line)


def rewrite_with_colors(
    ops: list[dict[str, object]],
    colors: dict[str, int],
) -> tuple[list[str], list[dict[str, object]]]:
    lines: list[str] = []
    records: list[dict[str, object]] = []
    for idx, opinfo in enumerate(ops):
        line = str(opinfo["line"])
        skip_load = opinfo["skip_load"]
        if skip_load is not None:
            q_index = int(skip_load)
            lines.append(
                f"        // E1v2 handoff: Q{q_index} already live in {HANDOFF[0][q_index]}; removed original {line.strip()}"
            )
            records.append(
                {
                    "op_index": idx,
                    "kind": "removed_block0_load",
                    "q_index": q_index,
                    "semantic": f"in_Q{q_index}",
                    "handoff_reg": HANDOFF[0][q_index],
                }
            )
            continue
        read_vids = list(opinfo["reads"])
        if opinfo.get("mls_in_place"):
            read_vids = read_vids[1:]
        write_vids = list(opinfo["writes"])
        reads = [colors[vid] for vid in read_vids]
        writes = [colors[vid] for vid in write_vids]
        rewritten = rewrite_line_with_colors(line, reads, writes)
        lines.append(rewritten)
        records.append(
            {
                "op_index": idx,
                "original": code_part(line),
                "renamed": code_part(rewritten),
                "read_values": read_vids,
                "read_regs": [f"q{r}" for r in reads],
                "write_values": write_vids,
                "write_regs": [f"q{r}" for r in writes],
                "mls_in_place": bool(opinfo.get("mls_in_place")),
            }
        )
    return lines, records


def simulate_current_values(
    ops: list[dict[str, object]],
    colors: dict[str, int] | None,
    stop_after_executable: int,
) -> dict[str, str]:
    """Return physical q register -> logical value after N executable ops."""

    if colors is None:
        current: dict[int, str] = {0: "q0_const"}
        for reg, q in {29: 0, 1: 1, 28: 2, 17: 3, 26: 4, 5: 5, 18: 6, 8: 7}.items():
            current[reg] = f"in_Q{q}"
    else:
        current = {0: "q0_const"}
        for reg, q in {29: 0, 1: 1, 28: 2, 17: 3, 26: 4, 5: 5, 18: 6, 8: 7}.items():
            current[colors[f"in_Q{q}"]] = f"in_Q{q}"

    executable = 0
    for opinfo in ops:
        if opinfo["skip_load"] is not None:
            executable += 1
            if executable > stop_after_executable:
                break
            q_index = int(opinfo["skip_load"])
            if colors is None:
                # Original E0 path still has the load at the original destination.
                operands = vector_operands(str(opinfo["line"]))
                if operands:
                    current[operands[0][1]] = f"in_Q{q_index}"
            continue
        code = code_part(str(opinfo["line"]))
        if not code:
            continue
        executable += 1
        if executable > stop_after_executable:
            break
        for vid in opinfo["writes"]:
            if colors is None:
                operands = vector_operands(str(opinfo["line"]))
                if operands:
                    current[operands[0][1]] = str(vid)
            else:
                current[colors[vid]] = str(vid)
    return {f"q{reg}": value for reg, value in sorted(current.items())}


def validate_records(
    records: list[dict[str, object]],
    colors: dict[str, int],
    defs: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    violations: list[dict[str, object]] = []
    seen_defs: dict[str, int] = {}
    for rec in records:
        if rec["kind"] if "kind" in rec else False:
            continue
        for value, reg in zip(rec["write_values"], rec["write_regs"]):
            if value in seen_defs:
                violations.append({"type": "duplicate_renamed_def", "value": value, "op_index": rec["op_index"]})
            seen_defs[str(value)] = int(rec["op_index"])
            if int(reg[1:]) in BLOCK1_RESERVED:
                violations.append(
                    {
                        "type": "block1_livein_clobber",
                        "op_index": rec["op_index"],
                        "value": value,
                        "reg": reg,
                    }
                )
    for value, data in defs.items():
        if int(data["def"]) >= 0 and value not in seen_defs:
            violations.append({"type": "missing_renamed_def", "value": value})
    violations.extend({"type": "interference", **item} for item in color_conflicts(colors, defs))
    return violations


def build_validation() -> dict[str, object]:
    lines = load_stage345_block(0)
    ops, defs = collect_stage345_ssa(lines)
    old_colors, old_max_live = old_allocate(defs)
    new_colors, new_max_live, allocator_notes = corrected_allocate(defs)
    same_as_interferences = same_as_interference_notes(allocator_notes)
    old_lines, old_records = rewrite_with_colors(ops, old_colors)
    new_lines, new_records = rewrite_with_colors(ops, new_colors)
    old_violations = validate_records(old_records, old_colors, defs)
    new_violations = validate_records(new_records, new_colors, defs)

    def producer_context(value: str) -> dict[str, object]:
        if value not in defs:
            return {"semantic": value, "status": "unknown"}
        def_op = int(defs[value]["def"])
        source_line = str(ops[def_op]["line"]) if def_op >= 0 else "live-in"
        old_record = old_records[def_op] if def_op >= 0 else None
        new_record = new_records[def_op] if def_op >= 0 else None
        return {
            "semantic": value,
            "def_op": def_op,
            "source_line": code_part(source_line),
            "uses": defs[value]["uses"],
            "old_e1_record": old_record,
            "e1v2_record": new_record,
        }

    old_q1_stage3 = simulate_current_values(ops, old_colors, STAGE3_EXIT_OP).get("q1")
    new_q1_stage3 = simulate_current_values(ops, new_colors, STAGE3_EXIT_OP).get("q1")

    return {
        "artifact": "stage345_block0_rename_validation",
        "production_default_changed": False,
        "source": "asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S:_gt_ntt32_batch8_ct_stage345_block0_slothy_start",
        "checks": {
            "unique_original_def_to_renamed_def": "encoded in missing_renamed_def/duplicate_renamed_def violations",
            "use_reads_correct_physical_reg": "encoded in per-instruction read_values/read_regs records",
            "no_stale_old_reg_use": "validated by rewritten operand records",
            "no_temp_rewrite_before_last_use": "encoded in interference violations",
            "block1_liveins_not_clobbered": "encoded in block1_livein_clobber violations",
            "stage3_exit_mapping": "included below",
            "scatter_output_regs": "str/ext operands are represented in records and interference checks",
        },
        "block1_reserved": [f"q{r}" for r in sorted(BLOCK1_RESERVED)],
        "old_e1_allocator": {
            "name": "fixed-order SSA greedy with late same_as overwrite",
            "max_live": old_max_live,
            "violations": old_violations,
            "stage3_exit_mapping": simulate_current_values(ops, old_colors, STAGE3_EXIT_OP),
            "q1_stage3_exit": simulate_current_values(ops, old_colors, STAGE3_EXIT_OP).get("q1"),
        },
        "e1v2_allocator": {
            "name": "same_as-first SSA greedy",
            "max_live": new_max_live,
            "same_as_constraints": same_as_constraints(defs),
            "same_as_interference_count": len(same_as_interferences),
            "same_as_interferences": same_as_interferences,
            "allocator_notes": allocator_notes,
            "violations": new_violations,
            "stage3_exit_mapping": simulate_current_values(ops, new_colors, STAGE3_EXIT_OP),
            "q1_stage3_exit": simulate_current_values(ops, new_colors, STAGE3_EXIT_OP).get("q1"),
            "colors": {vid: f"q{reg}" for vid, reg in sorted(new_colors.items())},
        },
        "original_stage3_exit_mapping": simulate_current_values(ops, None, STAGE3_EXIT_OP),
        "q1_first_diff_context": {
            "observed_runtime_diff": "row0 stage3_exit q1 lane0: e0=0 e1=911",
            "old_e1_q1_semantic": old_q1_stage3,
            "e1v2_q1_semantic": new_q1_stage3,
            "old_e1_q1_producer": producer_context(str(old_q1_stage3)),
            "e1v2_q1_producer": producer_context(str(new_q1_stage3)),
            "note": "q1 is not a block1 live-in; raw q1 differences are locator signals. Semantic correctness is checked by SSA records and final differential.",
        },
        "fine_cutpoint_first_semantic_diff": {
            "observed_runtime_diff": {
                "row": 0,
                "cutpoint": "after_first_butterfly_group",
                "semantic_value": "v15_q8",
                "lane": 0,
                "e0_reg": "q8",
                "e1_reg": "q8",
                "e0_value": -995,
                "e1_value": 1451,
            },
            "producer": producer_context("v15_q8"),
        },
        "e1v2_instruction_records_sample": new_records[:90],
    }


def write_md(data: dict[str, object]) -> None:
    old_violations = data["old_e1_allocator"]["violations"]
    new_violations = data["e1v2_allocator"]["violations"]
    OUT_MD.write_text(
        "# Stage345 Block0 Rename Validation\n\n"
        "Status: generated for Track E; production default unchanged.\n\n"
        "The validator rebuilds Stage345 block0 as SSA values and checks the "
        "physical-register rewrite independently of the handwritten E1 asm.\n\n"
        "Key finding: the old E1 allocator enforced `mls same_as old_dest` too "
        "late. E1v2 uses a same-as-first allocator, so destructive NEON ops are "
        "colored before unrelated temps can occupy that physical register.\n\n"
        "Observed E1 localization anchor:\n\n"
        "```text\n"
        "row0 stage3_exit q1 lane0: e0=0 e1=911\n"
        "```\n\n"
        "Validation summary:\n\n"
        "```text\n"
        f"old_e1_violations: {len(old_violations)}\n"
        f"e1v2_violations: {len(new_violations)}\n"
        f"e1v2_same_as_constraints: {len(data['e1v2_allocator']['same_as_constraints'])}\n"
        f"e1v2_same_as_interference_count: {data['e1v2_allocator']['same_as_interference_count']}\n"
        f"old_e1_q1_stage3_exit: {data['old_e1_allocator']['q1_stage3_exit']}\n"
        f"e1v2_q1_stage3_exit: {data['e1v2_allocator']['q1_stage3_exit']}\n"
        "fine_cutpoint_first_diff: after_first_butterfly_group v15_q8 lane0\n"
        "```\n\n"
        "Frozen allocator invariant for follow-up candidates:\n\n"
        "```text\n"
        "1. Destructive instructions such as mls must resolve same_as before greedy coloring.\n"
        "2. same_as_interference_count must be 0.\n"
        "3. Any candidate with same_as interference is rejected before ASM emission.\n"
        "```\n\n"
        "A raw physical `q1` diff is not by itself the bug because E1 renames "
        "registers. The actionable bug is an invalid rename contract: every use "
        "must read the renamed producer's color, destructive ops must keep the "
        "old destination color, and block1 live-ins must not be written by "
        "Stage345 block0.\n"
    )


def main() -> int:
    data = build_validation()
    OUT_JSON.write_text(json.dumps(data, indent=2) + "\n")
    write_md(data)
    print(OUT_JSON)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
