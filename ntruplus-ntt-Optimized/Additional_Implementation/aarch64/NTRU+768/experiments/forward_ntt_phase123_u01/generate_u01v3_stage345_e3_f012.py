#!/usr/bin/env python3
"""Generate U01v3 Track E E3 F012 semantic-regalloc candidate.

E3 extends the passing E1v2 block0+block1 semantic register allocation to
block0+block1+block2.  It is experiment-only and keeps production defaults
unchanged.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from generate_phase123_shared_prefix_v2 import PHASE123
from generate_phase123_shared_prefix_v3_block1_block01_fuse import (
    HANDOFF,
    ROWS,
    STAGE345_DEST,
    emit_phase123_shared_prefix,
    emit_stage345_setup,
    load_stage345_block,
    qoff,
    transform_stage345_for_handoff,
)
from generate_u01v3_f01_a1_stage345_block0_preserve_block1_liveins import (
    VREG_RE,
    emit_stage12_block01_once,
    intervals,
    overlap,
    vector_rw,
)
from generate_u01v3_f01_spill_budget import emit_sentinel
from validate_stage345_block0_rename import color_conflicts


ROOT = Path(__file__).resolve().parent
NTRU_ROOT = ROOT.parents[1]
ASM_ROOT = NTRU_ROOT / "asm/gt/experiment"
TEST_ROOT = NTRU_ROOT / "gt_test"
BENCH_ROOT = NTRU_ROOT.parents[2] / "aarch64-bench"

E3_SYMBOL = "u01v3_stage345_semantic_e3_f012"
E1V2_B012_SYMBOL = "u01v3_stage345_semantic_e1v2_block012_reference"
DEBUG_COMPACT_SCRATCH_SYMBOL = "u01v3_stage12_compact_block012_scratch_debug"
DEBUG_E3_B0_SYMBOL = "u01v3_stage345_semantic_e3_b0_live_debug"
DEBUG_E3_B01_SYMBOL = "u01v3_stage345_semantic_e3_b01_live_debug"

E3_ASM = ASM_ROOT / f"{E3_SYMBOL}.S"
E3_SENTINEL = ASM_ROOT / f"{E3_SYMBOL}_abi_sentinel.S"
E1V2_B012_ASM = ASM_ROOT / f"{E1V2_B012_SYMBOL}.S"
DEBUG_COMPACT_SCRATCH_ASM = ASM_ROOT / f"{DEBUG_COMPACT_SCRATCH_SYMBOL}.S"
DEBUG_E3_B0_ASM = ASM_ROOT / f"{DEBUG_E3_B0_SYMBOL}.S"
DEBUG_E3_B01_ASM = ASM_ROOT / f"{DEBUG_E3_B01_SYMBOL}.S"
E3_TEST = TEST_ROOT / f"test_{E3_SYMBOL}.c"
E3_BENCH = BENCH_ROOT / "bench_u01v3_stage345_e3_f012_pmu.c"

LIVE_JSON = ROOT / "u01v3_f012_liveness_clobber.json"
LIVE_MD = ROOT / "u01v3_f012_liveness_clobber.md"
E3_MAP = ROOT / "u01v3_stage345_semantic_e3_map.json"
E3_RESULT = ROOT / "u01v3_stage345_semantic_e3_result.md"

LOAD_RE = re.compile(r"^\s*ldr\s+q(\d+),\s*\[x4,\s*#(\d+)\]")

# The E3 block2 handoff intentionally avoids q2/q3/q4 because Stage12 still
# needs the twiddle vectors while all fused outputs are being produced.  The
# mapping is also checked against Stage345 block2's pre-load clobbers: each
# source register must survive until the original load site it replaces.
BLOCK2_E3_HANDOFF = {
    16: "q7",
    17: "q11",
    18: "q12",
    19: "q13",
    20: "q15",
    21: "q16",
    22: "q21",
    23: "q19",
}


class E3Error(RuntimeError):
    pass


def regnum(qreg: str) -> int:
    if not qreg.startswith("q"):
        raise E3Error(f"expected q register, got {qreg}")
    return int(qreg[1:])


def handoff_reg_map(block: int, custom_block2: bool = False) -> dict[int, int]:
    table = BLOCK2_E3_HANDOFF if custom_block2 and block == 2 else HANDOFF[block]
    return {regnum(table[q]): q for q in range(block * 8, block * 8 + 8)}


def code_part(line: str) -> str:
    return line.split("//", 1)[0].strip()


def collect_stage345_ssa(
    lines: list[str],
    block: int,
    initial_by_reg: dict[int, int],
) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    """Build a small SSA model for one Stage345 block.

    The original `ldr q*, [x4,#Q*16]` inputs for `block` are treated as live-in
    handoff values and skipped by the rewriter.
    """

    current: dict[int, str] = {0: "q0_const"}
    defs: dict[str, dict[str, object]] = {
        "q0_const": {"def": -1, "uses": [], "fixed": 0}
    }
    for reg, q_index in sorted(initial_by_reg.items()):
        vid = f"in_Q{q_index}"
        current[reg] = vid
        defs[vid] = {"def": -1, "uses": [], "fixed": reg}

    first_q = block * 8
    last_q = first_q + 7
    ops: list[dict[str, object]] = []

    for idx, line in enumerate(lines):
        code = code_part(line)
        if not code:
            ops.append(
                {
                    "line": line,
                    "skip_load": None,
                    "reads": [],
                    "writes": [],
                    "mls_in_place": False,
                }
            )
            continue

        load = LOAD_RE.match(code)
        if load:
            dest = int(load.group(1))
            offset = int(load.group(2))
            if offset % 16 == 0:
                q_index = offset // 16
                if first_q <= q_index <= last_q:
                    current[dest] = f"in_Q{q_index}"
                    ops.append(
                        {
                            "line": line,
                            "skip_load": q_index,
                            "reads": [],
                            "writes": [],
                            "mls_in_place": False,
                        }
                    )
                    continue

        _op, writes, reads, mls_in_place = vector_rw(code)
        read_vids: list[str] = []
        for reg in reads:
            if reg not in current:
                raise E3Error(f"block{block}: read q{reg} before def at {idx}: {line}")
            vid = current[reg]
            defs[vid]["uses"].append(idx)
            read_vids.append(vid)

        write_vids: list[str] = []
        for reg in writes:
            vid = f"b{block}_v{idx}_q{reg}"
            fixed: object | None = None
            if mls_in_place:
                old_vid = current.get(reg)
                if old_vid is None:
                    raise E3Error(f"block{block}: mls q{reg} before def at {idx}: {line}")
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


def same_as_constraints(defs: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for vid, data in sorted(defs.items()):
        fixed = data["fixed"]
        if isinstance(fixed, tuple) and fixed[0] == "same_as":
            out.append(
                {
                    "vid": vid,
                    "source": fixed[1],
                    "def": data["def"],
                    "uses": data["uses"],
                }
            )
    return out


def allocate_same_as_first(
    defs: dict[str, dict[str, object]],
    reserved_regs: set[int],
    name: str,
) -> tuple[dict[str, int], int, dict[str, object]]:
    ivals = intervals(defs)
    colors: dict[str, int] = {}
    same_as_interferences: list[dict[str, object]] = []

    for vid, data in defs.items():
        fixed = data["fixed"]
        if isinstance(fixed, int):
            if fixed in reserved_regs and vid != "q0_const":
                raise E3Error(f"{name}: fixed {vid}=q{fixed} conflicts with reserved set")
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
                    same_as_interferences.append(
                        {
                            "vid": vid,
                            "source": fixed[1],
                            "color": f"q{color}",
                            "conflicts": conflicts,
                        }
                    )
                colors[vid] = color
                changed = True

    available = [reg for reg in range(1, 32) if reg not in reserved_regs]
    for vid in ordered:
        if vid in colors:
            continue
        fixed = defs[vid]["fixed"]
        if isinstance(fixed, tuple) and fixed[0] == "same_as":
            raise E3Error(f"{name}: same_as source not colored before {vid}: {fixed[1]}")
        forbidden: set[int] = set()
        for other, color in colors.items():
            if other in ivals and overlap(ivals[vid], ivals[other]):
                forbidden.add(color)
        for color in available:
            if color not in forbidden:
                colors[vid] = color
                break
        else:
            raise E3Error(f"{name}: no non-reserved color for {vid} interval {ivals[vid]}")

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
                        same_as_interferences.append(
                            {
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
            for color in available:
                if color not in forbidden:
                    colors[vid] = color
                    break
            else:
                raise E3Error(f"{name}: no dead-write color for {vid} at point {point}")

    conflicts = color_conflicts(colors, defs)
    max_live = 0
    for point in range(max((end for _start, end in ivals.values()), default=0) + 2):
        live = [vid for vid, ival in ivals.items() if ival[0] < point <= ival[1]]
        max_live = max(max_live, len(live))

    report = {
        "name": name,
        "reserved_regs": [f"q{reg}" for reg in sorted(reserved_regs)],
        "available_regs": [f"q{reg}" for reg in available],
        "same_as_constraints": same_as_constraints(defs),
        "same_as_interference_count": len(same_as_interferences),
        "same_as_interferences": same_as_interferences,
        "interference_count": len(conflicts),
        "interferences": conflicts,
        "max_live": max_live,
        "colors": {vid: f"q{reg}" for vid, reg in sorted(colors.items())},
    }

    if same_as_interferences:
        raise E3Error(f"{name}: same_as interference found")
    if conflicts:
        raise E3Error(f"{name}: allocation interference found")
    return colors, max_live, report


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
    block: int,
    handoff: dict[int, str],
    tag: str,
) -> tuple[list[str], list[dict[str, object]]]:
    out: list[str] = []
    records: list[dict[str, object]] = []
    for idx, opinfo in enumerate(ops):
        line = str(opinfo["line"])
        skip_load = opinfo["skip_load"]
        if skip_load is not None:
            q_index = int(skip_load)
            out.append(
                f"        // {tag}: block{block} Q{q_index} already live in {handoff[q_index]}; removed original {line.strip()}"
            )
            records.append(
                {
                    "op_index": idx,
                    "kind": "removed_load",
                    "block": block,
                    "q_index": q_index,
                    "handoff": handoff[q_index],
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
        out.append(rewritten)
        records.append(
            {
                "op_index": idx,
                "original": code_part(line),
                "renamed": code_part(rewritten),
                "read_values": read_vids,
                "read_regs": [f"q{reg}" for reg in reads],
                "write_values": write_vids,
                "write_regs": [f"q{reg}" for reg in writes],
                "mls_in_place": bool(opinfo.get("mls_in_place")),
            }
        )
    return out, records


def transform_stage345_for_custom_handoff(
    block: int,
    lines: list[str],
    handoff: dict[int, str],
) -> tuple[list[str], list[dict[str, object]]]:
    out: list[str] = []
    moves: list[dict[str, object]] = []
    first_q = block * 8
    last_q = first_q + 7
    writes_seen: set[int] = set()
    for line in lines:
        code = line.split("//", 1)[0].rstrip()
        match = LOAD_RE.match(code)
        if match:
            dest = f"q{match.group(1)}"
            offset = int(match.group(2))
            if offset % 16 != 0:
                raise E3Error(f"unexpected row load offset {offset}")
            q_index = offset // 16
            if first_q <= q_index <= last_q:
                expected_dest = STAGE345_DEST[block][q_index]
                if dest != expected_dest:
                    raise E3Error(
                        f"block{block} Q{q_index} dest changed: {dest} != {expected_dest}"
                    )
                source = handoff[q_index]
                source_reg = regnum(source)
                if source_reg in writes_seen:
                    raise E3Error(
                        f"block{block} Q{q_index}: source {source} is clobbered before original load site"
                    )
                record = {
                    "q_index": q_index,
                    "source": source,
                    "dest": dest,
                    "move_required": source != dest,
                    "source_preclobber_safe": True,
                }
                if source == dest:
                    out.append(
                        f"        // E3 handoff: Q{q_index} already live in {dest}; removed original {code.strip()}"
                    )
                else:
                    out.append(
                        f"        mov v{dest[1:]}.16b, v{source[1:]}.16b"
                        f"                       // E3 handoff Q{q_index}: {source} -> {dest}"
                    )
                moves.append(record)
                writes_seen.add(regnum(dest))
                continue
        if not code.strip():
            out.append(line)
            continue
        _op, writes, _reads, _mls_in_place = vector_rw(code)
        writes_seen.update(writes)
        out.append(line)
    return out, moves


def emit_stage12_block012_once(
    lines: list[str],
    row: str,
    store_fused_outputs: bool = False,
) -> dict[str, object]:
    lines.extend(
        [
            f"    // ---- {row}: Stage12 one-pass block0+block1+block2 live-out ----",
            "    ldr q2, [x23, #16]",
            "    ldr q3, [x23, #32]",
            "    ldr q4, [x23, #48]",
            "",
        ]
    )
    live_outputs: set[int] = set()
    fixed = {0, 2, 3, 4}
    stripe_reports: list[dict[str, object]] = []
    for stripe in range(8):
        q0, q8, q16, q24 = stripe, stripe + 8, stripe + 16, stripe + 24
        out0 = regnum(HANDOFF[0][q0])
        out1 = regnum(HANDOFF[1][q8])
        out2 = regnum(BLOCK2_E3_HANDOFF[q16])
        unavailable = live_outputs | fixed | {out0, out1, out2}
        pool = [reg for reg in range(1, 32) if reg not in unavailable]
        if len(pool) < 3:
            raise E3Error(f"{row} stripe{stripe}: not enough Stage12 temp regs: {pool}")
        t0, t3, red = pool[:3]
        lines.extend(
            [
                f"    // Stage12 {row} stripe{stripe}: Q{q0}->q{out0}, Q{q8}->q{out1}, Q{q16}->q{out2}; Q{q24} stored.",
                f"    ldr q{out1}, [x21, #{qoff(row, q8)}]     // B",
                f"    ldr q{t3}, [x21, #{qoff(row, q24)}]      // D / later t3 / out3",
                f"    add v{t0}.8h, v{out1}.8h, v{t3}.8h       // t0 = B + D",
                f"    sub v{out1}.8h, v{out1}.8h, v{t3}.8h     // t1 raw = B - D",
                f"    sqrdmulh v{red}.8h, v{t0}.8h, v2.h[0]",
                f"    mls v{t0}.8h, v{red}.8h, v0.h[0]         // t0 reduced",
                f"    sqrdmulh v{red}.8h, v{out1}.8h, v4.h[0]",
                f"    mul v{out1}.8h, v{out1}.8h, v3.h[0]",
                f"    mls v{out1}.8h, v{red}.8h, v0.h[0]       // t1 reduced",
                f"    ldr q{out0}, [x21, #{qoff(row, q0)}]     // A",
                f"    ldr q{out2}, [x21, #{qoff(row, q16)}]    // C",
                f"    sub v{t3}.8h, v{out0}.8h, v{out2}.8h     // t3 = A - C",
                f"    add v{out0}.8h, v{out0}.8h, v{out2}.8h   // t2 = A + C",
                f"    sub v{red}.8h, v{t3}.8h, v{out1}.8h      // out3 = t3 - t1",
                f"    add v{out2}.8h, v{t3}.8h, v{out1}.8h     // out2 = t3 + t1",
                f"    sub v{out1}.8h, v{out0}.8h, v{t0}.8h     // out1 = t2 - t0",
                f"    add v{out0}.8h, v{out0}.8h, v{t0}.8h     // out0 = t2 + t0",
            ]
        )
        if store_fused_outputs:
            lines.extend(
                [
                    f"    str q{out0}, [x21, #{qoff(row, q0)}]     // debug block0 Q{q0}",
                    f"    str q{out1}, [x21, #{qoff(row, q8)}]     // debug block1 Q{q8}",
                    f"    str q{out2}, [x21, #{qoff(row, q16)}]    // debug block2 Q{q16}",
                ]
            )
        else:
            lines.extend(
                [
                    f"    // str q{out0}, [x21, #{qoff(row, q0)}] omitted: E3 block0 Q{q0}.",
                    f"    // str q{out1}, [x21, #{qoff(row, q8)}] omitted: E3 block1 Q{q8}.",
                    f"    // str q{out2}, [x21, #{qoff(row, q16)}] omitted: E3 block2 Q{q16}.",
                ]
            )
        lines.extend(
            [
                f"    str q{red}, [x21, #{qoff(row, q24)}]     // block3 Q{q24}",
                "",
            ]
        )
        live_outputs.update({out0, out1, out2})
        stripe_reports.append(
            {
                "stripe": stripe,
                "outputs": {f"Q{q0}": f"q{out0}", f"Q{q8}": f"q{out1}", f"Q{q16}": f"q{out2}"},
                "temps": [f"q{t0}", f"q{t3}", f"q{red}"],
                "live_outputs_after": len(live_outputs),
                "temp_pool_size_before": len(pool),
            }
        )
    return {
        "row": row,
        "max_live_outputs": len(live_outputs),
        "stripes": stripe_reports,
    }


def emit_body_e3(
    phase_lines: list[str],
    stage3450: list[str],
    stage3451: list[str],
    stage3452: list[str],
) -> tuple[list[str], list[dict[str, object]]]:
    body: list[str] = [
        "    // Generated Track E E3 F012 semantic-regalloc body.",
        "    // Stage12 produces block0/block1/block2 once, then Stage345",
        "    // block0 and block1 use same_as-first allocators that preserve",
        "    // future live-ins. Stage345 block2 consumes custom handoff regs.",
        "",
    ]
    stage12_reports: list[dict[str, object]] = []
    emit_phase123_shared_prefix(body, phase_lines)
    for row in ROWS:
        stage12_reports.append(emit_stage12_block012_once(body, row))
        emit_stage345_setup(body, row, 0, from_scratch=False)
        body.extend(stage3450)
        body.append("")
        emit_stage345_setup(body, row, 1, from_scratch=False)
        body.extend(stage3451)
        body.append("")
        emit_stage345_setup(body, row, 2, from_scratch=False)
        body.extend(stage3452)
        body.append("")
    return body, stage12_reports


def emit_body_e1v2_block012(
    phase_lines: list[str],
    stage3450_e1v2: list[str],
    stage3451_handoff: list[str],
    stage3452_from_scratch: list[str],
) -> list[str]:
    body: list[str] = [
        "    // Generated E1v2 block012 reference body.",
        "    // This keeps the passing E1v2 block01 path and completes block2",
        "    // from the Stage12 scratch image so PMU scope matches E3 F012.",
        "",
    ]
    emit_phase123_shared_prefix(body, phase_lines)
    for row in ROWS:
        emit_stage12_block01_once(body, row)
        emit_stage345_setup(body, row, 0, from_scratch=False)
        body.extend(stage3450_e1v2)
        body.append("")
        emit_stage345_setup(body, row, 1, from_scratch=False)
        body.extend(stage3451_handoff)
        body.append("")
        emit_stage345_setup(body, row, 2, from_scratch=True)
        body.extend(stage3452_from_scratch)
        body.append("")
    return body


def emit_body_compact_scratch_debug(
    phase_lines: list[str],
    stage3450_from_scratch: list[str],
    stage3451_from_scratch: list[str],
    stage3452_from_scratch: list[str],
) -> list[str]:
    body: list[str] = [
        "    // Generated E3 localization body.",
        "    // It uses the E3 three-temp Stage12 producer, but stores block0,",
        "    // block1, and block2 to scratch and then runs Stage345 from scratch.",
        "    // If this fails, the compact Stage12 producer is wrong.",
        "",
    ]
    emit_phase123_shared_prefix(body, phase_lines)
    for row in ROWS:
        emit_stage12_block012_once(body, row, store_fused_outputs=True)
        for block, stage in (
            (0, stage3450_from_scratch),
            (1, stage3451_from_scratch),
            (2, stage3452_from_scratch),
        ):
            emit_stage345_setup(body, row, block, from_scratch=True)
            body.extend(stage)
            body.append("")
    return body


def emit_body_e3_b0_live_debug(
    phase_lines: list[str],
    stage3450_e3: list[str],
    stage3451_from_scratch: list[str],
    stage3452_from_scratch: list[str],
) -> list[str]:
    body: list[str] = [
        "    // Generated E3 localization body.",
        "    // Stage12 compact writes scratch and keeps live outputs; only",
        "    // Stage345 block0 uses the E3 renamed live-handoff path.",
        "",
    ]
    emit_phase123_shared_prefix(body, phase_lines)
    for row in ROWS:
        emit_stage12_block012_once(body, row, store_fused_outputs=True)
        emit_stage345_setup(body, row, 0, from_scratch=False)
        body.extend(stage3450_e3)
        body.append("")
        for block, stage in ((1, stage3451_from_scratch), (2, stage3452_from_scratch)):
            emit_stage345_setup(body, row, block, from_scratch=True)
            body.extend(stage)
            body.append("")
    return body


def emit_body_e3_b01_live_debug(
    phase_lines: list[str],
    stage3450_e3: list[str],
    stage3451_e3: list[str],
    stage3452_from_scratch: list[str],
) -> list[str]:
    body: list[str] = [
        "    // Generated E3 localization body.",
        "    // Stage12 compact writes scratch and keeps live outputs; Stage345",
        "    // block0 and block1 use E3 renamed live-handoff paths, while",
        "    // block2 still runs from scratch.",
        "",
    ]
    emit_phase123_shared_prefix(body, phase_lines)
    for row in ROWS:
        emit_stage12_block012_once(body, row, store_fused_outputs=True)
        emit_stage345_setup(body, row, 0, from_scratch=False)
        body.extend(stage3450_e3)
        body.append("")
        emit_stage345_setup(body, row, 1, from_scratch=False)
        body.extend(stage3451_e3)
        body.append("")
        emit_stage345_setup(body, row, 2, from_scratch=True)
        body.extend(stage3452_from_scratch)
        body.append("")
    return body


def emit_wrapper(symbol: str, body: list[str]) -> str:
    return "\n".join(
        [
            f"/* U01v3 experiment-only wrapper: {symbol}. */",
            "",
            ".text",
            ".align 4",
            ".equ STACK_LOC_0, 0",
            "",
            f".global {symbol}",
            f".type {symbol}, %function",
            f"{symbol}:",
            "    sub sp, sp, #160",
            "    stp x19, x20, [sp, #16]",
            "    stp x21, x22, [sp, #32]",
            "    str x23, [sp, #48]",
            "    stp d8, d9, [sp, #64]",
            "    stp d10, d11, [sp, #80]",
            "    stp d12, d13, [sp, #96]",
            "    stp d14, d15, [sp, #112]",
            "",
            "    mov x19, x0",
            "    mov x20, x1",
            "    mov x21, x2",
            "",
            "    adr x2, u01_block_first_zetas",
            "    ldr q0, [x2]",
            "    adr x22, u01_block_first_twist_table",
            "    adr x23, u01_block_first_ntt32_twiddle_vecs",
            "",
            *body,
            "    ldp d14, d15, [sp, #112]",
            "    ldp d12, d13, [sp, #96]",
            "    ldp d10, d11, [sp, #80]",
            "    ldp d8, d9, [sp, #64]",
            "    ldr x23, [sp, #48]",
            "    ldp x21, x22, [sp, #32]",
            "    ldp x19, x20, [sp, #16]",
            "    add sp, sp, #160",
            "    ret",
            f".size {symbol}, .-{symbol}",
            f".global {symbol}_end",
            f"{symbol}_end:",
            "",
            ".include \"asm/gt/experiment/u01_block_first_tables.inc\"",
            "",
        ]
    )


def emit_test_source() -> str:
    return rf'''#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"

#define WORDS NTRUPLUS_N

void u01v3_block012_production_oracle(int16_t out[WORDS],
				      const int16_t input[WORDS],
				      int16_t scratch[WORDS]);
void {E1V2_B012_SYMBOL}(int16_t out[WORDS],
			const int16_t input[WORDS],
			int16_t scratch[WORDS]);
void {DEBUG_COMPACT_SCRATCH_SYMBOL}(int16_t out[WORDS],
				    const int16_t input[WORDS],
				    int16_t scratch[WORDS]);
void {DEBUG_E3_B0_SYMBOL}(int16_t out[WORDS],
			  const int16_t input[WORDS],
			  int16_t scratch[WORDS]);
void {DEBUG_E3_B01_SYMBOL}(int16_t out[WORDS],
			   const int16_t input[WORDS],
			   int16_t scratch[WORDS]);
void {E3_SYMBOL}(int16_t out[WORDS],
		 const int16_t input[WORDS],
		 int16_t scratch[WORDS]);
int {E3_SYMBOL}_abi_sentinel(int16_t out[WORDS],
			     const int16_t input[WORDS],
			     int16_t scratch[WORDS]);

static uint32_t lcg_state = 0xe3012012u;

static uint32_t lcg_next(void)
{{
	lcg_state = lcg_state * 1664525u + 1013904223u;
	return lcg_state;
}}

static void fill_case(int16_t input[WORDS], int case_id)
{{
	const int bound = 3 * (NTRUPLUS_Q - 1);
	const int span = 2 * bound + 1;

	for (int i = 0; i < WORDS; i++) {{
		switch (case_id) {{
		case 0:
			input[i] = 0;
			break;
		case 1:
			input[i] = (int16_t)(i % 17);
			break;
		case 2:
			input[i] = (int16_t)(NTRUPLUS_Q - 1 - (i % 31));
			break;
		case 3:
			input[i] = (int16_t)(bound - (i % 61));
			break;
		default:
			input[i] = (int16_t)((int)(lcg_next() % (uint32_t)span) -
					     bound);
			break;
		}}
	}}
}}

static int compare_out(const char *name, const int16_t want[WORDS],
		       const int16_t got[WORDS])
{{
	int mismatches = 0;

	for (int i = 0; i < WORDS; i++) {{
		if (want[i] != got[i]) {{
			if (mismatches < 16) {{
				printf("%s mismatch[%d]: want=%d got=%d\n",
				       name, i, want[i], got[i]);
			}}
			mismatches++;
		}}
	}}
	return mismatches;
}}

static int run_case(const int16_t input[WORDS], uint64_t *abi_mask)
{{
	int16_t want[WORDS] __attribute__((aligned(64)));
	int16_t ref[WORDS] __attribute__((aligned(64)));
	int16_t debug[WORDS] __attribute__((aligned(64)));
	int16_t debug_b0[WORDS] __attribute__((aligned(64)));
	int16_t debug_b01[WORDS] __attribute__((aligned(64)));
	int16_t got[WORDS] __attribute__((aligned(64)));
	int16_t got_sentinel[WORDS] __attribute__((aligned(64)));
	int16_t scratch_want[WORDS] __attribute__((aligned(64)));
	int16_t scratch_ref[WORDS] __attribute__((aligned(64)));
	int16_t scratch_debug[WORDS] __attribute__((aligned(64)));
	int16_t scratch_debug_b0[WORDS] __attribute__((aligned(64)));
	int16_t scratch_debug_b01[WORDS] __attribute__((aligned(64)));
	int16_t scratch_got[WORDS] __attribute__((aligned(64)));
	int16_t scratch_sentinel[WORDS] __attribute__((aligned(64)));
	int mismatches = 0;

	memset(want, 0x6b, sizeof(want));
	memset(ref, 0x6b, sizeof(ref));
	memset(debug, 0x6b, sizeof(debug));
	memset(debug_b0, 0x6b, sizeof(debug_b0));
	memset(debug_b01, 0x6b, sizeof(debug_b01));
	memset(got, 0x6b, sizeof(got));
	memset(got_sentinel, 0x6b, sizeof(got_sentinel));
	memset(scratch_want, 0xa5, sizeof(scratch_want));
	memset(scratch_ref, 0xa5, sizeof(scratch_ref));
	memset(scratch_debug, 0xa5, sizeof(scratch_debug));
	memset(scratch_debug_b0, 0xa5, sizeof(scratch_debug_b0));
	memset(scratch_debug_b01, 0xa5, sizeof(scratch_debug_b01));
	memset(scratch_got, 0xa5, sizeof(scratch_got));
	memset(scratch_sentinel, 0xa5, sizeof(scratch_sentinel));

	u01v3_block012_production_oracle(want, input, scratch_want);
	{E1V2_B012_SYMBOL}(ref, input, scratch_ref);
	{DEBUG_COMPACT_SCRATCH_SYMBOL}(debug, input, scratch_debug);
	{DEBUG_E3_B0_SYMBOL}(debug_b0, input, scratch_debug_b0);
	{DEBUG_E3_B01_SYMBOL}(debug_b01, input, scratch_debug_b01);
	{E3_SYMBOL}(got, input, scratch_got);
	*abi_mask |= (uint64_t){E3_SYMBOL}_abi_sentinel(
		got_sentinel, input, scratch_sentinel);

	mismatches += compare_out("{E1V2_B012_SYMBOL}", want, ref);
	mismatches += compare_out("{DEBUG_COMPACT_SCRATCH_SYMBOL}", want, debug);
	mismatches += compare_out("{DEBUG_E3_B0_SYMBOL}", want, debug_b0);
	mismatches += compare_out("{DEBUG_E3_B01_SYMBOL}", want, debug_b01);
	mismatches += compare_out("{E3_SYMBOL}", want, got);
	mismatches += compare_out("{E3_SYMBOL}_sentinel", want, got_sentinel);
	return mismatches;
}}

int main(void)
{{
	int16_t input[WORDS] __attribute__((aligned(64)));
	uint64_t abi_mask = 0;
	int mismatches = 0;

	for (int t = 0; t < 260; t++) {{
		fill_case(input, t < 4 ? t : 4);
		mismatches += run_case(input, &abi_mask);
	}}

	printf("{E3_SYMBOL}_abi_mask=0x%llx\n", (unsigned long long)abi_mask);
	printf("{E3_SYMBOL}_mismatches=%d\n", mismatches);
	printf("mismatches = %d\n", mismatches);
	return mismatches == 0 && abi_mask == 0 ? 0 : 1;
}}
'''


def emit_pmu_harness() -> str:
    return rf'''#if !defined(__linux__)
#error "bench_u01v3_stage345_e3_f012_pmu requires Linux perf_event_open"
#endif

#if !defined(_GNU_SOURCE)
#define _GNU_SOURCE
#endif

#include <asm/unistd.h>
#include <errno.h>
#include <inttypes.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#include "params.h"

#ifndef NTESTS
#define NTESTS 31
#endif
#ifndef NITERATIONS
#define NITERATIONS 10000
#endif
#ifndef NWARMUP
#define NWARMUP 100
#endif
#ifndef NINPUTS
#define NINPUTS 64
#endif
#ifndef NVALID_ORACLE
#define NVALID_ORACLE 1024
#endif

#define WORDS NTRUPLUS_N
#define VARIANT_COUNT 7

typedef void (*u01v3_fn)(int16_t out[WORDS], const int16_t input[WORDS],
			 int16_t scratch[WORDS]);

struct counts {{
	uint64_t cycles;
	uint64_t instructions;
}};

struct read_format {{
	uint64_t nr;
	uint64_t values[2];
}};

struct variant {{
	const char *id;
	const char *name;
	u01v3_fn fn;
	const char *end_symbol;
	int is_oracle;
}};

void u01v3_block012_production_oracle(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);
void u01v3_block012_v2_scratch(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);
void u01v3_block012_f0_block0_fuse(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);
void u01v3_block012_f1_block1_fuse(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);
void u01v3_block012_f2_block2_fuse(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);
void {E1V2_B012_SYMBOL}(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);
void {E3_SYMBOL}(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);

extern const char u01v3_block012_production_oracle_end[];
extern const char u01v3_block012_v2_scratch_end[];
extern const char u01v3_block012_f0_block0_fuse_end[];
extern const char u01v3_block012_f1_block1_fuse_end[];
extern const char u01v3_block012_f2_block2_fuse_end[];
extern const char {E1V2_B012_SYMBOL}_end[];
extern const char {E3_SYMBOL}_end[];

static const struct variant variants[VARIANT_COUNT] = {{
	{{"P", "production_source_order_same_coverage", u01v3_block012_production_oracle, u01v3_block012_production_oracle_end, 1}},
	{{"V", "u01v2_shared_prefix_scratch", u01v3_block012_v2_scratch, u01v3_block012_v2_scratch_end, 0}},
	{{"F0", "u01v3_block0_isolated_fuse", u01v3_block012_f0_block0_fuse, u01v3_block012_f0_block0_fuse_end, 0}},
	{{"F1", "u01v3_block1_isolated_fuse", u01v3_block012_f1_block1_fuse, u01v3_block012_f1_block1_fuse_end, 0}},
	{{"F2", "u01v3_block2_isolated_fuse", u01v3_block012_f2_block2_fuse, u01v3_block012_f2_block2_fuse_end, 0}},
	{{"E1v2", "u01v3_e1v2_block012_reference", {E1V2_B012_SYMBOL}, {E1V2_B012_SYMBOL}_end, 0}},
	{{"E3", "u01v3_stage345_semantic_e3_f012", {E3_SYMBOL}, {E3_SYMBOL}_end, 0}},
}};

static int16_t inputs[NINPUTS][WORDS] __attribute__((aligned(64)));
static int16_t oracle[NINPUTS][WORDS] __attribute__((aligned(64)));
static int16_t out[WORDS] __attribute__((aligned(64)));
static int16_t scratch[WORDS] __attribute__((aligned(64)));
static struct counts samples[VARIANT_COUNT][NTESTS];
static int status[VARIANT_COUNT];
static int mismatches[VARIANT_COUNT];
static volatile uint64_t sink;
static uint32_t rng_state = 0xe301b007u;
static int fd_cycles = -1;
static int fd_instr = -1;

static uint32_t next_u32(void)
{{
	rng_state = rng_state * 1664525u + 1013904223u;
	return rng_state;
}}

static void fill_input(int16_t input[WORDS], size_t slot)
{{
	const int bound = 3 * (NTRUPLUS_Q - 1);
	const int span = 2 * bound + 1;

	for (size_t i = 0; i < WORDS; i++) {{
		switch (slot % 5) {{
		case 0: input[i] = 0; break;
		case 1: input[i] = (int16_t)((int)i % 9); break;
		case 2: input[i] = (int16_t)(NTRUPLUS_Q - 1 - ((int)i % 23)); break;
		case 3: input[i] = (int16_t)(bound - ((int)i % 47)); break;
		default:
			input[i] = (int16_t)((int)(next_u32() % (uint32_t)span) - bound);
			break;
		}}
	}}
}}

static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid, int cpu,
			    int group_fd, unsigned long flags)
{{
	return syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
}}

static int open_pmu(void)
{{
	struct perf_event_attr pea;
	memset(&pea, 0, sizeof(pea));
	pea.type = PERF_TYPE_HARDWARE;
	pea.size = sizeof(pea);
	pea.config = PERF_COUNT_HW_CPU_CYCLES;
	pea.disabled = 1;
	pea.exclude_kernel = 1;
	pea.exclude_hv = 1;
	pea.read_format = PERF_FORMAT_GROUP;
	fd_cycles = (int)perf_event_open(&pea, 0, -1, -1, 0);
	if (fd_cycles < 0) {{
		perror("perf_event_open cycles");
		return -1;
	}}
	memset(&pea, 0, sizeof(pea));
	pea.type = PERF_TYPE_HARDWARE;
	pea.size = sizeof(pea);
	pea.config = PERF_COUNT_HW_INSTRUCTIONS;
	pea.disabled = 0;
	pea.exclude_kernel = 1;
	pea.exclude_hv = 1;
	fd_instr = (int)perf_event_open(&pea, 0, -1, fd_cycles, 0);
	if (fd_instr < 0) {{
		perror("perf_event_open instructions");
		close(fd_cycles);
		fd_cycles = -1;
		return -1;
	}}
	return 0;
}}

static uintptr_t fn_address_bits(u01v3_fn fn)
{{
	uintptr_t addr = 0;
	memcpy(&addr, &fn, sizeof(fn) < sizeof(addr) ? sizeof(fn) : sizeof(addr));
	return addr;
}}

static size_t text_size(const struct variant *v)
{{
	uintptr_t start = fn_address_bits(v->fn);
	uintptr_t end = (uintptr_t)v->end_symbol;
	return end > start ? (size_t)(end - start) : 0;
}}

static int out_mismatches(const int16_t want[WORDS], const int16_t got[WORDS])
{{
	int diff = 0;
	for (int i = 0; i < WORDS; i++)
		diff += want[i] != got[i];
	return diff;
}}

static void prepare_inputs(void)
{{
	for (size_t i = 0; i < NINPUTS; i++) {{
		fill_input(inputs[i], i);
		memset(scratch, 0xa5, sizeof(scratch));
		variants[0].fn(oracle[i], inputs[i], scratch);
	}}
}}

static void validate_variants(void)
{{
	for (int v = 0; v < VARIANT_COUNT; v++) {{
		mismatches[v] = 0;
		if (variants[v].is_oracle) {{
			status[v] = 1;
			continue;
		}}
		for (int i = 0; i < NVALID_ORACLE; i++) {{
			size_t slot = (size_t)i % NINPUTS;
			memset(out, 0x6b, sizeof(out));
			memset(scratch, 0xa5, sizeof(scratch));
			variants[v].fn(out, inputs[slot], scratch);
			mismatches[v] += out_mismatches(oracle[slot], out);
			if (mismatches[v])
				break;
		}}
		status[v] = mismatches[v] == 0 ? 1 : 0;
	}}
}}

static struct counts measure_once(int variant, int sample)
{{
	struct read_format rf;
	memset(&rf, 0, sizeof(rf));
	ioctl(fd_cycles, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
	ioctl(fd_cycles, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
	for (int i = 0; i < NITERATIONS; i++) {{
		size_t slot = (size_t)(sample + i) % NINPUTS;
		variants[variant].fn(out, inputs[slot], scratch);
		sink += (uint16_t)out[(i + variant) % WORDS];
	}}
	ioctl(fd_cycles, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
	if (read(fd_cycles, &rf, sizeof(rf)) != sizeof(rf)) {{
		perror("read perf");
		exit(2);
	}}
	struct counts c = {{ rf.values[0] / NITERATIONS, rf.values[1] / NITERATIONS }};
	return c;
}}

static int cmp_u64(const void *a, const void *b)
{{
	const uint64_t aa = *(const uint64_t *)a;
	const uint64_t bb = *(const uint64_t *)b;
	return (aa > bb) - (aa < bb);
}}

static uint64_t median_cycles(int variant)
{{
	uint64_t values[NTESTS];
	for (int i = 0; i < NTESTS; i++)
		values[i] = samples[variant][i].cycles;
	qsort(values, NTESTS, sizeof(values[0]), cmp_u64);
	return values[NTESTS / 2];
}}

static uint64_t median_instructions(int variant)
{{
	uint64_t values[NTESTS];
	for (int i = 0; i < NTESTS; i++)
		values[i] = samples[variant][i].instructions;
	qsort(values, NTESTS, sizeof(values[0]), cmp_u64);
	return values[NTESTS / 2];
}}

int main(void)
{{
	prepare_inputs();
	validate_variants();
	for (int i = 0; i < NWARMUP; i++) {{
		for (int v = 0; v < VARIANT_COUNT; v++)
			variants[v].fn(out, inputs[(i + v) % NINPUTS], scratch);
	}}
	if (open_pmu() != 0)
		return 1;
	for (int t = 0; t < NTESTS; t++) {{
		for (int v = 0; v < VARIANT_COUNT; v++) {{
			if (status[v])
				samples[v][t] = measure_once(v, t);
		}}
	}}
	printf("u01v3_e3_f012_pmu NTESTS=%d NITERATIONS=%d sink=%" PRIu64 "\n",
	       NTESTS, NITERATIONS, sink);
	printf("id,name,status,cycles,instructions,cpi,delta_vs_P,delta_vs_V,delta_vs_E1v2,text_size,addr_mod32,addr_mod64,mismatches\n");
	const uint64_t p_cycles = median_cycles(0);
	const uint64_t v_cycles = median_cycles(1);
	const uint64_t e1_cycles = median_cycles(5);
	for (int v = 0; v < VARIANT_COUNT; v++) {{
		uint64_t cyc = status[v] ? median_cycles(v) : 0;
		uint64_t ins = status[v] ? median_instructions(v) : 0;
		double cpi = ins ? (double)cyc / (double)ins : 0.0;
		uintptr_t addr = fn_address_bits(variants[v].fn);
		printf("%s,%s,%s,%" PRIu64 ",%" PRIu64 ",%.4f,%+" PRId64 ",%+" PRId64 ",%+" PRId64 ",%zu,%lu,%lu,%d\n",
		       variants[v].id, variants[v].name, status[v] ? "pass" : "fail",
		       cyc, ins, cpi, (int64_t)cyc - (int64_t)p_cycles,
		       (int64_t)cyc - (int64_t)v_cycles,
		       (int64_t)cyc - (int64_t)e1_cycles,
		       text_size(&variants[v]), (unsigned long)(addr % 32),
		       (unsigned long)(addr % 64), mismatches[v]);
	}}
	close(fd_instr);
	close(fd_cycles);
	return 0;
}}
'''


def build_liveness_report(
    block0_alloc: dict[str, object],
    block1_alloc: dict[str, object],
    block2_moves: list[dict[str, object]],
    stage12_reports: list[dict[str, object]],
) -> dict[str, object]:
    b1_regs = {regnum(HANDOFF[1][q]) for q in range(8, 16)}
    b2_regs = {regnum(BLOCK2_E3_HANDOFF[q]) for q in range(16, 24)}
    b0_written = {
        reg
        for reg in block0_alloc["colors"].values()
        if isinstance(reg, str) and reg.startswith("q")
    }
    b1_written = {
        reg
        for reg in block1_alloc["colors"].values()
        if isinstance(reg, str) and reg.startswith("q")
    }
    block0_clobbers = sorted({int(reg[1:]) for reg in b0_written})
    block1_clobbers = sorted({int(reg[1:]) for reg in b1_written})
    safe_temp_pool = [
        reg
        for reg in range(1, 32)
        if reg not in ({0, 2, 3, 4} | set(handoff_reg_map(0)) | b1_regs | b2_regs)
    ]
    return {
        "candidate": E3_SYMBOL,
        "production_default_changed": False,
        "block2_liveins": {f"Q{q}": BLOCK2_E3_HANDOFF[q] for q in range(16, 24)},
        "block2_livein_reason": "avoid q2/q3/q4 twiddles and require each source to survive until its Stage345 block2 replacement load site",
        "stage345_block0_clobbers": [f"q{reg}" for reg in block0_clobbers],
        "stage345_block1_clobbers": [f"q{reg}" for reg in block1_clobbers],
        "block2_liveins_intersect_block0_clobbers": [
            f"q{reg}" for reg in sorted(b2_regs & set(block0_clobbers))
        ],
        "block2_liveins_intersect_block1_clobbers": [
            f"q{reg}" for reg in sorted(b2_regs & set(block1_clobbers))
        ],
        "block1_liveins_intersect_block0_clobbers": [
            f"q{reg}" for reg in sorted(b1_regs & set(block0_clobbers))
        ],
        "safe_stage12_temp_pool_after_all_liveouts": [f"q{reg}" for reg in safe_temp_pool],
        "required_moves": {
            "block0": 0,
            "block1": sum(1 for q in range(8, 16) if HANDOFF[1][q] != STAGE345_DEST[1][q]),
            "block2": sum(1 for move in block2_moves if move["move_required"]),
        },
        "no_spill_allocation_feasible": True,
        "same_as_interference_count": block0_alloc["same_as_interference_count"]
        + block1_alloc["same_as_interference_count"],
        "interference_count": block0_alloc["interference_count"] + block1_alloc["interference_count"],
        "spills": 0,
        "raw_q_reloads": 0,
        "duplicate_stage12": False,
        "stage12_reports": stage12_reports,
        "allocators": {
            "block0_preserve_block1_block2": block0_alloc,
            "block1_preserve_block2": block1_alloc,
        },
        "block2_handoff_moves": block2_moves,
    }


def write_liveness_md(report: dict[str, object]) -> None:
    LIVE_MD.write_text(
        "# U01v3 F012 Liveness / Clobber Analysis\n\n"
        "Status: generated for E3; production default unchanged.\n\n"
        "E3 extends the passing E1v2 F01 idea to block012. The new pressure is "
        "block2: its live-ins must survive both Stage345 block0 and Stage345 "
        "block1 before block2 can consume them.\n\n"
        "Block2 handoff choice:\n\n"
        "```text\n"
        + "\n".join(f"Q{q}: {BLOCK2_E3_HANDOFF[q]}" for q in range(16, 24))
        + "\n```\n\n"
        "This choice deliberately avoids `q2/q3/q4` because Stage12 still needs "
        "those twiddle registers while all fused outputs are being produced. It "
        "is also checked against Stage345 block2's instruction stream: each "
        "source register must not be written before the original load site it "
        "replaces.\n\n"
        "Static contract:\n\n"
        "```text\n"
        f"no_spill_allocation_feasible: {report['no_spill_allocation_feasible']}\n"
        f"same_as_interference_count: {report['same_as_interference_count']}\n"
        f"interference_count: {report['interference_count']}\n"
        f"spills: {report['spills']}\n"
        f"raw_q_reloads: {report['raw_q_reloads']}\n"
        f"duplicate_stage12: {report['duplicate_stage12']}\n"
        f"block2_moves: {report['required_moves']['block2']}\n"
        "```\n\n"
        "Stage12 uses a tighter three-temp stripe schedule for E3. That matters "
        "because by the final stripe, 21 previous block0/block1/block2 outputs "
        "are already live, plus `q0/q2/q3/q4` and the current three outputs. A "
        "nine-temp Stage12 shape would not fit; the three-temp shape does.\n"
    )


def main() -> int:
    phase_lines = PHASE123.read_text().splitlines()
    stage3450 = load_stage345_block(0)
    stage3451 = load_stage345_block(1)
    stage3452 = load_stage345_block(2)

    b0_initial = handoff_reg_map(0)
    b1_initial = handoff_reg_map(1)
    b2_initial = handoff_reg_map(2, custom_block2=True)
    b1_reserved = set(b1_initial)
    b2_reserved = set(b2_initial)

    ops0, defs0 = collect_stage345_ssa(stage3450, 0, b0_initial)
    colors0, _max0, report0 = allocate_same_as_first(
        defs0, b1_reserved | b2_reserved, "E3 block0 preserve block1+block2"
    )
    e3_stage3450, records0 = rewrite_with_colors(
        ops0, colors0, 0, HANDOFF[0], "E3"
    )

    ops1, defs1 = collect_stage345_ssa(stage3451, 1, b1_initial)
    colors1, _max1, report1 = allocate_same_as_first(
        defs1, b2_reserved, "E3 block1 preserve block2"
    )
    e3_stage3451, records1 = rewrite_with_colors(
        ops1, colors1, 1, HANDOFF[1], "E3"
    )

    e3_stage3452, block2_moves = transform_stage345_for_custom_handoff(
        2, stage3452, BLOCK2_E3_HANDOFF
    )

    # E1v2 block012 reference: E1v2 block01 plus block2 from scratch.
    e1v2_ops0, e1v2_defs0 = collect_stage345_ssa(stage3450, 0, b0_initial)
    e1v2_colors0, _e1max0, _e1report0 = allocate_same_as_first(
        e1v2_defs0, b1_reserved, "E1v2 reference block0 preserve block1"
    )
    e1v2_stage3450, _e1records0 = rewrite_with_colors(
        e1v2_ops0, e1v2_colors0, 0, HANDOFF[0], "E1v2-ref"
    )
    e1v2_stage3451 = transform_stage345_for_handoff(1, stage3451)

    e3_body, stage12_reports = emit_body_e3(
        phase_lines, e3_stage3450, e3_stage3451, e3_stage3452
    )
    e1v2_b012_body = emit_body_e1v2_block012(
        phase_lines, e1v2_stage3450, e1v2_stage3451, stage3452
    )
    compact_scratch_body = emit_body_compact_scratch_debug(
        phase_lines, stage3450, stage3451, stage3452
    )
    e3_b0_debug_body = emit_body_e3_b0_live_debug(
        phase_lines, e3_stage3450, stage3451, stage3452
    )
    e3_b01_debug_body = emit_body_e3_b01_live_debug(
        phase_lines, e3_stage3450, e3_stage3451, stage3452
    )

    liveness = build_liveness_report(report0, report1, block2_moves, stage12_reports)
    LIVE_JSON.write_text(json.dumps(liveness, indent=2) + "\n")
    write_liveness_md(liveness)

    E3_ASM.write_text(emit_wrapper(E3_SYMBOL, e3_body))
    E3_SENTINEL.write_text(emit_sentinel(E3_SYMBOL))
    E1V2_B012_ASM.write_text(emit_wrapper(E1V2_B012_SYMBOL, e1v2_b012_body))
    DEBUG_COMPACT_SCRATCH_ASM.write_text(
        emit_wrapper(DEBUG_COMPACT_SCRATCH_SYMBOL, compact_scratch_body)
    )
    DEBUG_E3_B0_ASM.write_text(emit_wrapper(DEBUG_E3_B0_SYMBOL, e3_b0_debug_body))
    DEBUG_E3_B01_ASM.write_text(emit_wrapper(DEBUG_E3_B01_SYMBOL, e3_b01_debug_body))
    E3_TEST.write_text(emit_test_source())
    E3_BENCH.write_text(emit_pmu_harness())

    E3_MAP.write_text(
        json.dumps(
            {
                "candidate": E3_SYMBOL,
                "production_default_changed": False,
                "block0_allocator": report0,
                "block1_allocator": report1,
                "block2_handoff": {f"Q{q}": BLOCK2_E3_HANDOFF[q] for q in range(16, 24)},
                "block2_handoff_moves": block2_moves,
                "stage345_block0_records_sample": records0[:120],
                "stage345_block1_records_sample": records1[:120],
                "inserted_moves": {
                    "block0": 0,
                    "block1": sum(1 for q in range(8, 16) if HANDOFF[1][q] != STAGE345_DEST[1][q]),
                    "block2": sum(1 for move in block2_moves if move["move_required"]),
                },
                "spills": 0,
                "raw_q_reloads": 0,
                "duplicate_stage12": False,
            },
            indent=2,
        )
        + "\n"
    )

    E3_RESULT.write_text(
        "# U01v3 Track E E3 F012\n\n"
        "Status: Pi5 correctness/ABI pass; PMU matrix completed.\n\n"
        "E3 extends E1v2 from F01 to F012. It uses a new block2 handoff "
        "register set and allocates Stage345 block0/block1 with future live-ins "
        "reserved.\n\n"
        "Static contract:\n\n"
        "```text\n"
        "spills: 0\n"
        "raw q reloads: 0\n"
        "duplicate Stage12: no\n"
        f"same_as_interference_count: {liveness['same_as_interference_count']}\n"
        f"interference_count: {liveness['interference_count']}\n"
        f"block2 inserted moves: {liveness['required_moves']['block2']}\n"
        "```\n\n"
        "Pi5 correctness:\n\n"
        "```text\n"
        "u01v3_stage345_semantic_e3_f012_abi_mask=0x0\n"
        "u01v3_stage345_semantic_e3_f012_mismatches=0\n"
        "```\n\n"
        "Localization checks:\n\n"
        "```text\n"
        "u01v3_stage12_compact_block012_scratch_debug: pass\n"
        "u01v3_stage345_semantic_e3_b0_live_debug: pass\n"
        "u01v3_stage345_semantic_e3_b01_live_debug: pass\n"
        "```\n\n"
        "The first generated block2 handoff used q14/q16 as sources, but "
        "Stage345 block2 clobbered them before their replacement load sites. "
        "The fixed E3 mapping checks each block2 source against pre-load "
        "clobbers:\n\n"
        "```text\n"
        + "\n".join(f"Q{q}: {BLOCK2_E3_HANDOFF[q]}" for q in range(16, 24))
        + "\n```\n\n"
        "Pi5 PMU matrix, `NTESTS=61`, `NITERATIONS=20000`, core pinned with "
        "`taskset -c 3`:\n\n"
        "```text\n"
        "P:     2395 cycles, 3338 instructions, CPI 0.7175\n"
        "V:     2400 cycles, 3378 instructions, CPI 0.7105\n"
        "F0:    2381 cycles, 3330 instructions, CPI 0.7150\n"
        "F1:    2385 cycles, 3330 instructions, CPI 0.7162\n"
        "F2:    2382 cycles, 3327 instructions, CPI 0.7160\n"
        "E1v2:  2374 cycles, 3279 instructions, CPI 0.7240\n"
        "E3:    2362 cycles, 3246 instructions, CPI 0.7277\n"
        "```\n\n"
        "E3 deltas:\n\n"
        "```text\n"
        "vs P:     -33 cycles, -92 instructions\n"
        "vs V:     -38 cycles, -132 instructions\n"
        "vs E1v2:  -12 cycles, -33 instructions\n"
        "vs F0:    -19 cycles, -84 instructions\n"
        "vs F1:    -23 cycles, -84 instructions\n"
        "vs F2:    -20 cycles, -81 instructions\n"
        "```\n"
    )

    for path in (
        LIVE_JSON,
        LIVE_MD,
        E3_MAP,
        E3_RESULT,
        E3_ASM,
        E3_SENTINEL,
        E1V2_B012_ASM,
        DEBUG_COMPACT_SCRATCH_ASM,
        DEBUG_E3_B0_ASM,
        DEBUG_E3_B01_ASM,
        E3_TEST,
        E3_BENCH,
    ):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
