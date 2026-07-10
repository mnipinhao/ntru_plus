#!/usr/bin/env python3
"""Generate U01v3 F01 A1 one-pass block0+block1 live-in experiment.

A1 computes Stage12 block0 and block1 once per row, keeps both outputs live,
runs a renamed Stage345 block0 that avoids block1 handoff registers, then runs
unchanged Stage345 block1 from the still-live block1 handoff registers.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from generate_phase123_shared_prefix_v2 import PHASE123, extract_region
from generate_phase123_shared_prefix_v3_block1_block01_fuse import (
    HANDOFF,
    ROWS,
    ROW_SCATTER,
    ROW_SCRATCH,
    STAGE345_DEST,
    TW_STAGE3_OFFSET,
    emit_phase123_shared_prefix,
    emit_stage345_setup,
    load_stage345_block,
    transform_stage345_for_handoff,
)
from generate_stage12_block0_first import qoff


ROOT = Path(__file__).resolve().parent
OUT_BODY = ROOT / "u01v3_f01_a1_stage345_block0_preserve_block1_liveins.sym.s"
OUT_LAYOUT = ROOT / "u01v3_f01_a1_stage345_block0_preserve_block1_liveins_layout.json"
OUT_REPORT = ROOT / "u01v3_f01_a1_stage345_block0_preserve_block1_liveins_result.md"

BLOCK1_RESERVED = {6, 9, 10, 20, 23, 24, 30, 31}
BLOCK0_INITIAL = {
    29: "Q0",
    1: "Q1",
    28: "Q2",
    17: "Q3",
    26: "Q4",
    5: "Q5",
    18: "Q6",
    8: "Q7",
}
FIXED_COLORS = {
    "q0_const": 0,
    **{f"in_{name}": reg for reg, name in BLOCK0_INITIAL.items()},
}
AVAILABLE_COLORS = [r for r in range(32) if r not in BLOCK1_RESERVED and r != 0]
VREG_RE = re.compile(r"\b([vdq])(\d+)\b")
BLOCK0_LOAD_RE = re.compile(r"^\s*ldr\s+q(\d+),\s*\[x4,\s*#(\d+)\]")


class AllocError(RuntimeError):
    pass


def vector_rw(line: str) -> tuple[str, list[int], list[int], bool]:
    op = line.split()[0].lower()
    regs = [int(m.group(2)) for m in VREG_RE.finditer(line)]
    mls_in_place = False
    if op in {"ldr", "add", "sub", "sqrdmulh", "mls", "mul", "sqdmulh", "srshr", "ext", "mov"} and regs:
        writes = [regs[0]]
        reads = regs[1:]
        if op == "mls":
            reads = [regs[0]] + regs[1:]
            mls_in_place = True
    elif op == "str":
        writes = []
        reads = regs
    else:
        writes = []
        reads = regs
    return op, writes, reads, mls_in_place


def is_block0_row_load(line: str) -> tuple[int, int] | None:
    match = BLOCK0_LOAD_RE.match(line)
    if not match:
        return None
    reg = int(match.group(1))
    offset = int(match.group(2))
    if offset in {0, 16, 32, 48, 64, 80, 96, 112}:
        return reg, offset // 16
    return None


def collect_stage345_ssa(lines: list[str]) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    current: dict[int, str] = {0: "q0_const"}
    defs: dict[str, dict[str, object]] = {"q0_const": {"def": -1, "uses": [], "fixed": 0}}
    for reg, name in BLOCK0_INITIAL.items():
        vid = f"in_{name}"
        current[reg] = vid
        defs[vid] = {"def": -1, "uses": [], "fixed": reg}

    ops: list[dict[str, object]] = []
    for idx, line in enumerate(lines):
        code = line.split("//", 1)[0].strip()
        if not code:
            ops.append({"line": line, "skip_load": None, "reads": [], "writes": [], "mls_in_place": False})
            continue
        load = is_block0_row_load(code)
        if load:
            dest, q_index = load
            current[dest] = f"in_Q{q_index}"
            ops.append({"line": line, "skip_load": q_index, "reads": [], "writes": [], "mls_in_place": False})
            continue

        _op, writes, reads, mls_in_place = vector_rw(code)
        read_vids: list[str] = []
        for reg in reads:
            if reg not in current:
                raise AllocError(f"read q{reg} before def at Stage345 line {idx}: {line}")
            vid = current[reg]
            defs[vid]["uses"].append(idx)
            read_vids.append(vid)

        write_vids: list[str] = []
        for reg in writes:
            vid = f"v{idx}_q{reg}"
            fixed = None
            if mls_in_place:
                old_vid = current.get(reg)
                if old_vid is None:
                    raise AllocError(f"mls q{reg} before def at Stage345 line {idx}: {line}")
                fixed = ("same_as", old_vid)
            defs[vid] = {"def": idx, "uses": [], "fixed": fixed}
            current[reg] = vid
            write_vids.append(vid)

        ops.append(
            {
                "line": line,
                "skip_load": None,
                "reads": read_vids,
                "writes": write_vids,
                "mls_in_place": mls_in_place,
            }
        )

    return ops, defs


def intervals(defs: dict[str, dict[str, object]]) -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    for vid, data in defs.items():
        uses = data["uses"]
        if not uses:
            continue
        out[vid] = (int(data["def"]), max(int(u) for u in uses))
    return out


def overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def allocate(defs: dict[str, dict[str, object]]) -> tuple[dict[str, int], int]:
    ivals = intervals(defs)
    colors: dict[str, int] = {}

    changed = True
    while changed:
        changed = False
        for vid, data in defs.items():
            fixed = data["fixed"]
            if isinstance(fixed, int) and vid not in colors:
                colors[vid] = fixed
                changed = True
            elif isinstance(fixed, tuple) and fixed[0] == "same_as" and fixed[1] in colors and vid not in colors:
                colors[vid] = colors[fixed[1]]
                changed = True

    for vid in sorted(ivals, key=lambda v: (ivals[v][0], ivals[v][1], v)):
        if vid in colors:
            continue
        forbidden: set[int] = set()
        for other, color in colors.items():
            if other in ivals and overlap(ivals[vid], ivals[other]):
                forbidden.add(color)
        for color in AVAILABLE_COLORS:
            if color not in forbidden:
                colors[vid] = color
                break
        else:
            raise AllocError(f"no non-reserved color for {vid} interval {ivals[vid]}")

    for vid, data in defs.items():
        fixed = data["fixed"]
        if isinstance(fixed, tuple) and fixed[0] == "same_as":
            colors[vid] = colors[fixed[1]]
    for vid, data in defs.items():
        if vid in colors:
            continue
        fixed = data["fixed"]
        if isinstance(fixed, int):
            colors[vid] = fixed
        elif isinstance(fixed, tuple) and fixed[0] == "same_as":
            colors[vid] = colors[fixed[1]]
        else:
            point = int(data["def"]) + 1
            forbidden: set[int] = set()
            for other, color in colors.items():
                if other in ivals and ivals[other][0] < point <= ivals[other][1]:
                    forbidden.add(color)
            for color in AVAILABLE_COLORS:
                if color not in forbidden:
                    colors[vid] = color
                    break
            else:
                raise AllocError(f"no dead-write color for {vid} at point {point}")

    max_live = 0
    for point in range(max((end for _start, end in ivals.values()), default=0) + 2):
        live = [vid for vid, ival in ivals.items() if ival[0] < point <= ival[1]]
        max_live = max(max_live, len(live))
    return colors, max_live


def rewrite_vector_regs(line: str, read_colors: list[int], write_colors: list[int]) -> str:
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


def rename_stage345_block0_preserve_block1(lines: list[str]) -> tuple[list[str], dict[str, object]]:
    ops, defs = collect_stage345_ssa(lines)
    colors, max_live = allocate(defs)

    out: list[str] = []
    for opinfo in ops:
        skip_load = opinfo["skip_load"]
        line = str(opinfo["line"])
        if skip_load is not None:
            q_index = int(skip_load)
            handoff = HANDOFF[0][q_index]
            out.append(
                f"        // A1 handoff: Q{q_index} already live in {handoff}; removed original {line.strip()}"
            )
            continue
        read_vids = list(opinfo["reads"])
        if opinfo.get("mls_in_place"):
            read_vids = read_vids[1:]
        reads = [colors[vid] for vid in read_vids]
        writes = [colors[vid] for vid in opinfo["writes"]]
        out.append(rewrite_vector_regs(line, reads, writes))

    actual_written = sorted(
        {
            colors[vid]
            for vid, data in defs.items()
            if int(data["def"]) >= 0 and vid in colors
        }
    )
    return out, {
        "allocator": "fixed-order SSA greedy",
        "preserved_block1_registers": [f"q{r}" for r in sorted(BLOCK1_RESERVED)],
        "actual_stage345_block0_written_q_registers": [f"q{r}" for r in actual_written],
        "reserved_written": [f"q{r}" for r in sorted(set(actual_written) & BLOCK1_RESERVED)],
        "max_nonreserved_live_values": max_live,
        "available_nonreserved_registers": [f"q{r}" for r in AVAILABLE_COLORS],
    }


def emit_stage12_block01_once(lines: list[str], row: str) -> None:
    lines.extend(
        [
            f"    // ---- {row}: Stage12 one-pass block0+block1 live-out ----",
            "    ldr q2, [x23, #16]",
            "    ldr q3, [x23, #32]",
            "    ldr q4, [x23, #48]",
            "",
        ]
    )
    live_outputs: set[int] = set()
    fixed = {0, 2, 3, 4}
    for stripe in range(8):
        q0, q8, q16, q24 = stripe, stripe + 8, stripe + 16, stripe + 24
        out0 = int(HANDOFF[0][q0][1:])
        out1 = int(HANDOFF[1][q8][1:])
        unavailable = live_outputs | fixed | {out0, out1}
        pool = [r for r in range(1, 32) if r not in unavailable]
        if len(pool) < 9:
            raise AllocError(f"not enough Stage12 temps for {row} stripe{stripe}: {pool}")
        a, b, c, d, t0, t1, t2, t3, red = pool[:9]
        lines.extend(
            [
                f"    // Stage12 {row} stripe{stripe}: Q{q0} -> q{out0}, Q{q8} -> q{out1}; Q{q16}/Q{q24} stored.",
                f"    ldr q{a}, [x21, #{qoff(row, q0)}]",
                f"    ldr q{b}, [x21, #{qoff(row, q8)}]",
                f"    ldr q{c}, [x21, #{qoff(row, q16)}]",
                f"    ldr q{d}, [x21, #{qoff(row, q24)}]",
                f"    add v{t0}.8h, v{b}.8h, v{d}.8h",
                f"    sqrdmulh v{red}.8h, v{t0}.8h, v2.h[0]",
                f"    mls v{t0}.8h, v{red}.8h, v0.h[0]",
                f"    sub v{t1}.8h, v{b}.8h, v{d}.8h",
                f"    sqrdmulh v{red}.8h, v{t1}.8h, v4.h[0]",
                f"    mul v{t1}.8h, v{t1}.8h, v3.h[0]",
                f"    mls v{t1}.8h, v{red}.8h, v0.h[0]",
                f"    add v{t2}.8h, v{a}.8h, v{c}.8h",
                f"    sub v{t3}.8h, v{a}.8h, v{c}.8h",
                f"    add v{out0}.8h, v{t2}.8h, v{t0}.8h",
                f"    sub v{out1}.8h, v{t2}.8h, v{t0}.8h",
                f"    add v{t2}.8h, v{t3}.8h, v{t1}.8h",
                f"    sub v{t3}.8h, v{t3}.8h, v{t1}.8h",
                f"    // str q{out0}, [x21, #{qoff(row, q0)}] omitted: A1 block0 handoff Q{q0}.",
                f"    // str q{out1}, [x21, #{qoff(row, q8)}] omitted: A1 block1 live-in Q{q8}.",
                f"    str q{t2}, [x21, #{qoff(row, q16)}]   // block2 Q{q16}",
                f"    str q{t3}, [x21, #{qoff(row, q24)}]   // block3 Q{q24}",
                "",
            ]
        )
        live_outputs.update({out0, out1})


def emit_stage345_setup_from_scratchless(lines: list[str], row: str, block: int) -> None:
    scatter_offset = ROW_SCATTER[row] + {0: 0, 1: 192}[block]
    if scatter_offset >= 768:
        scatter_offset -= 768
    lines.extend(
        [
            f"    // ---- {row}: Stage345 block{block} from live handoff ----",
            f"    add x10, x19, #{scatter_offset}",
            "    add x14, x19, #768",
            f"    add x12, x23, #{TW_STAGE3_OFFSET}",
            "",
        ]
    )


def emit_body(stage3450_preserve: list[str], stage3451_handoff: list[str]) -> list[str]:
    phase_lines = PHASE123.read_text().splitlines()
    lines: list[str] = [
        "// Generated U01v3 F01 A1 body.",
        "//",
        "// Shape: Stage12 produces block0 and block1 once, Stage345 block0",
        "// preserves block1 live-ins, then Stage345 block1 consumes them.",
        "// No production default change. No S2/S4, twiddle1, or Slothy changes.",
        "",
        ".text",
        "",
        "u01v3_f01_a1_stage345_block0_preserve_block1_liveins_body:",
    ]
    emit_phase123_shared_prefix(lines, phase_lines)
    for row in ROWS:
        emit_stage12_block01_once(lines, row)
        emit_stage345_setup_from_scratchless(lines, row, 0)
        lines.extend(stage3450_preserve)
        lines.append("")
        emit_stage345_setup_from_scratchless(lines, row, 1)
        lines.extend(stage3451_handoff)
        lines.append("")
    lines.append("u01v3_f01_a1_stage345_block0_preserve_block1_liveins_body_end:")
    lines.append("")
    return lines


def main() -> int:
    stage345 = {0: load_stage345_block(0), 1: load_stage345_block(1)}
    stage3450_preserve, allocator_report = rename_stage345_block0_preserve_block1(stage345[0])
    stage3451_handoff = transform_stage345_for_handoff(1, stage345[1])
    OUT_BODY.write_text("\n".join(emit_body(stage3450_preserve, stage3451_handoff)))
    OUT_LAYOUT.write_text(
        json.dumps(
            {
                "candidate": "u01v3_f01_a1_stage345_block0_preserve_block1_liveins",
                "stage12": {
                    "one_pass": True,
                    "duplicated_stage12": False,
                    "extra_raw_q_reloads": 0,
                    "block0_handoff": HANDOFF[0],
                    "block1_liveins": HANDOFF[1],
                    "block2_block3_stored_to_scratch": True,
                },
                "stage345_block0": allocator_report,
                "stage345_block1": {
                    "source": "unchanged block1 arithmetic/scatter with original U01v3 handoff load replacement",
                    "handoff": HANDOFF[1],
                    "dest": STAGE345_DEST[1],
                },
                "expected_boundary_delta": {
                    "removed_stage12_q_stores": 48,
                    "removed_stage345_q_loads": 48,
                    "inserted_vector_moves": 3,
                    "added_vector_spills": 0,
                },
                "validation": {
                    "local_assemble": "passes with clang --target=aarch64-linux-gnu",
                    "pi5_correctness": "fails against u01v3_block01_production_oracle",
                    "pi5_mismatches_observed": 74568,
                    "pi5_abi_mask_observed": "0x0",
                    "pmu": "not run because correctness fails",
                },
            },
            indent=2,
        )
        + "\n"
    )
    OUT_REPORT.write_text(
        "# U01v3 F01 A1: Stage345 Block0 Preserve Block1 Live-ins\n\n"
        "Status: generated experiment-only prototype, not a passing candidate. "
        "Production default is unchanged.\n\n"
        "A1 computes Stage12 block0 and block1 once per row, removes the Q0..Q15 "
        "Stage12 stores, runs a renamed Stage345 block0 that avoids block1 "
        "handoff registers, then runs Stage345 block1 from those live-ins.\n\n"
        "Block1 preserved registers: "
        + ", ".join(f"`q{r}`" for r in sorted(BLOCK1_RESERVED))
        + ".\n\n"
        f"Stage345 block0 allocator peak non-reserved live values: {allocator_report['max_nonreserved_live_values']} "
        f"of {len(AVAILABLE_COLORS)} available non-reserved registers.\n\n"
        "Reserved registers written by renamed Stage345 block0: "
        + (", ".join(allocator_report["reserved_written"]) or "none")
        + ".\n\n"
        "Validation:\n\n"
        "```text\n"
        "local assemble: pass, clang --target=aarch64-linux-gnu\n"
        "Pi5 correctness: fail vs u01v3_block01_production_oracle\n"
        "Pi5 observed mismatches: 74568\n"
        "Pi5 ABI mask: 0x0\n"
        "PMU: not run because correctness fails\n"
        "```\n\n"
        "No block1 spill/reload or raw q reload is introduced by this artifact. "
        "The copied Stage345 scalar wrap chain still has its existing scalar stack "
        "temporaries from the source block.\n"
    )
    for path in (OUT_BODY, OUT_LAYOUT, OUT_REPORT):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
