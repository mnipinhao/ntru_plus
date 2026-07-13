#!/usr/bin/env python3
"""Generate U01v3 block1/block2 and cumulative fuse experiment artifacts."""

from __future__ import annotations

import json
import re
from pathlib import Path

from generate_phase123_shared_prefix_v2 import PHASE123, extract_region
from generate_stage12_block0_first import qoff


ROOT = Path(__file__).resolve().parent
NTRU_ROOT = ROOT.parents[1]
NTT32 = NTRU_ROOT / "asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S"

OUT_B1_FUSED = ROOT / "phase123_shared_prefix_v3_block1_fuse_allrows.sym.s"
OUT_B01_F0 = ROOT / "phase123_shared_prefix_v3_block01_f0_allrows.sym.s"
OUT_B01_F1 = ROOT / "phase123_shared_prefix_v3_block01_f1_allrows.sym.s"
OUT_B01_FUSED = ROOT / "phase123_shared_prefix_v3_block01_fuse_allrows.sym.s"
OUT_B2_FUSED = ROOT / "phase123_shared_prefix_v3_block2_fuse_allrows.sym.s"
OUT_B012_F0 = ROOT / "phase123_shared_prefix_v3_block012_f0_allrows.sym.s"
OUT_B012_F1 = ROOT / "phase123_shared_prefix_v3_block012_f1_allrows.sym.s"
OUT_B012_F2 = ROOT / "phase123_shared_prefix_v3_block012_f2_allrows.sym.s"
OUT_B1_SCRATCH = ROOT / "u01v3_stage345_block1_from_scratch_allrows.sym.s"
OUT_B01_SCRATCH = ROOT / "u01v3_stage345_block01_from_scratch_allrows.sym.s"
OUT_B2_SCRATCH = ROOT / "u01v3_stage345_block2_from_scratch_allrows.sym.s"
OUT_B012_SCRATCH = ROOT / "u01v3_stage345_block012_from_scratch_allrows.sym.s"
OUT_B1_LAYOUT = ROOT / "u01v3_block1_layout_map.json"
OUT_B01_LAYOUT = ROOT / "u01v3_block01_layout_map.json"
OUT_B2_LAYOUT = ROOT / "u01v3_block2_layout_map.json"
OUT_B012_LAYOUT = ROOT / "u01v3_block012_layout_map.json"

ROWS = ("row0", "row1", "row2")
ROW_SCRATCH = {"row0": 0, "row1": 512, "row2": 1024}
ROW_SCATTER = {"row0": 0, "row1": 256, "row2": 512}

BLOCK_SCATTER = {0: 0, 1: 192, 2: 384}
TW_STAGE3_OFFSET = 64

STAGE345_DEST = {
    0: {0: "q29", 1: "q6", 2: "q28", 3: "q17", 4: "q26", 5: "q5", 6: "q18", 7: "q8"},
    1: {8: "q10", 9: "q20", 10: "q30", 11: "q1", 12: "q9", 13: "q6", 14: "q31", 15: "q23"},
    2: {16: "q15", 17: "q7", 18: "q6", 19: "q13", 20: "q27", 21: "q17", 22: "q29", 23: "q20"},
}

HANDOFF = {
    0: {0: "q29", 1: "q1", 2: "q28", 3: "q17", 4: "q26", 5: "q5", 6: "q18", 7: "q8"},
    1: {8: "q10", 9: "q20", 10: "q30", 11: "q24", 12: "q9", 13: "q6", 14: "q31", 15: "q23"},
    2: {16: "q15", 17: "q7", 18: "q6", 19: "q13", 20: "q27", 21: "q17", 22: "q29", 23: "q20"},
}

LOAD_RE = re.compile(r"^\s*ldr\s+(q\d+),\s*\[x4,\s*#(\d+)\]")


def emit_phase123_iter(out: list[str], phase_lines: list[str], iteration: int) -> None:
    out.extend(
        [
            f"    // Production Phase123 iter{iteration}, shared prefix once.",
            f"    add x1, x20, #{iteration * 32}",
            f"    add x3, x22, #{iteration * 384}",
            f"    add x4, x21, #{iteration * 64}",
            f"    add x5, x21, #{512 + iteration * 64}",
            f"    add x6, x21, #{1024 + iteration * 64}",
        ]
    )
    out.extend(
        extract_region(
            phase_lines,
            f"slothy_start_ntt_phase123_iter{iteration}",
            f"slothy_end_ntt_phase123_iter{iteration}",
        )
    )
    out.append("")


def emit_phase123_shared_prefix(lines: list[str], phase_lines: list[str]) -> None:
    for iteration in (0, 2, 4, 6, 1, 3, 5, 7):
        emit_phase123_iter(lines, phase_lines, iteration)


def load_stage345_block(block: int) -> list[str]:
    lines = NTT32.read_text().splitlines()
    start = f"_gt_ntt32_batch8_ct_stage345_block{block}_slothy_start:"
    end = f"_gt_ntt32_batch8_ct_stage345_block{block}_slothy_end:"
    inside = False
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == start:
            inside = True
            continue
        if stripped == end:
            break
        if inside:
            out.append(line.rstrip())
    if not out:
        raise ValueError(f"could not extract Stage345 block{block}")
    return out


def transform_stage345_for_handoff(block: int, lines: list[str]) -> list[str]:
    out: list[str] = []
    first_q = block * 8
    last_q = first_q + 7
    for line in lines:
        code = line.split("//", 1)[0].rstrip()
        match = LOAD_RE.match(code)
        if match:
            dest = match.group(1)
            offset = int(match.group(2))
            if offset % 16 != 0:
                raise ValueError(f"unexpected row load offset {offset}")
            q_index = offset // 16
            if first_q <= q_index <= last_q:
                expected_dest = STAGE345_DEST[block][q_index]
                if dest != expected_dest:
                    raise ValueError(
                        f"block{block} Q{q_index} dest changed: {dest} != {expected_dest}"
                    )
                handoff = HANDOFF[block][q_index]
                if handoff == dest:
                    out.append(
                        f"        // U01v3 handoff: Q{q_index} already live in {dest}; "
                        f"removed original {code.strip()}"
                    )
                else:
                    out.append(
                        f"        mov v{dest[1:]}.16b, v{handoff[1:]}.16b"
                        f"                       // U01v3 handoff Q{q_index}: {handoff} -> {dest}"
                    )
                continue
        out.append(line)
    return out


def emit_stage345_setup(lines: list[str], row: str, block: int, from_scratch: bool) -> None:
    desc = "from scratch" if from_scratch else "from live handoff"
    scatter_offset = ROW_SCATTER[row] + BLOCK_SCATTER[block]
    if scatter_offset >= 768:
        scatter_offset -= 768
    lines.extend(
        [
            f"    // ---- {row}: Stage345 block{block} {desc} ----",
            f"    add x10, x19, #{scatter_offset}",
            "    add x14, x19, #768",
            f"    add x12, x23, #{TW_STAGE3_OFFSET}",
        ]
    )
    if from_scratch:
        lines.append(f"    add x4, x21, #{ROW_SCRATCH[row]}")
    lines.append("")


def emit_stage12_twiddles(lines: list[str], row: str, desc: str) -> None:
    lines.extend(
        [
            f"    // ---- {row}: Stage12 {desc} ----",
            "    ldr q2, [x23, #16]",
            "    ldr q3, [x23, #32]",
            "    ldr q4, [x23, #48]",
            "",
        ]
    )


def emit_stage12_block0_handoff(
    lines: list[str],
    row: str,
    stripe: int,
    store_out1: bool,
    store_out2: bool,
    store_out3: bool,
) -> None:
    q0, q8, q16, q24 = stripe, stripe + 8, stripe + 16, stripe + 24
    out_reg = HANDOFF[0][q0]
    out_v = out_reg.replace("q", "v")
    lines.extend(
        [
            f"    // Stage12 {row} stripe{stripe}: out0 Q{q0} stays live in {out_reg}.",
            f"    ldr q9, [x21, #{qoff(row, q0)}]",
            f"    ldr q10, [x21, #{qoff(row, q8)}]",
            f"    ldr q11, [x21, #{qoff(row, q16)}]",
            f"    ldr q12, [x21, #{qoff(row, q24)}]",
            "    add v13.8h, v10.8h, v12.8h",
            "    sqrdmulh v14.8h, v13.8h, v2.h[0]",
            "    mls v13.8h, v14.8h, v0.h[0]",
            "    sub v15.8h, v10.8h, v12.8h",
            "    sqrdmulh v14.8h, v15.8h, v4.h[0]",
            "    mul v15.8h, v15.8h, v3.h[0]",
            "    mls v15.8h, v14.8h, v0.h[0]",
            "    add v16.8h, v9.8h, v11.8h",
            "    sub v19.8h, v9.8h, v11.8h",
            f"    add {out_v}.8h, v16.8h, v13.8h",
            "    sub v20.8h, v16.8h, v13.8h",
            "    add v21.8h, v19.8h, v15.8h",
            "    sub v22.8h, v19.8h, v15.8h",
            f"    // str {out_reg}, [x21, #{qoff(row, q0)}] omitted: U01v3 block0 handoff Q{q0}.",
        ]
    )
    if store_out1:
        lines.append(f"    str q20, [x21, #{qoff(row, q8)}]    // block1 Q{q8}")
    else:
        lines.append(f"    // str q20, [x21, #{qoff(row, q8)}] omitted")
    if store_out2:
        lines.append(f"    str q21, [x21, #{qoff(row, q16)}]   // block2 Q{q16}")
    else:
        lines.append(f"    // str q21, [x21, #{qoff(row, q16)}] omitted")
    if store_out3:
        lines.append(f"    str q22, [x21, #{qoff(row, q24)}]   // block3 Q{q24}")
    else:
        lines.append(f"    // str q22, [x21, #{qoff(row, q24)}] omitted")
    lines.append("")


def emit_stage12_block1_handoff(
    lines: list[str],
    row: str,
    stripe: int,
    store_out0: bool,
    store_out2: bool,
    store_out3: bool,
) -> None:
    q0, q8, q16, q24 = stripe, stripe + 8, stripe + 16, stripe + 24
    out_reg = HANDOFF[1][q8]
    out_v = out_reg.replace("q", "v")
    lines.extend(
        [
            f"    // Stage12 {row} stripe{stripe}: out1 Q{q8} stays live in {out_reg}.",
            f"    ldr q25, [x21, #{qoff(row, q0)}]",
            f"    ldr q26, [x21, #{qoff(row, q8)}]",
            f"    ldr q27, [x21, #{qoff(row, q16)}]",
            f"    ldr q28, [x21, #{qoff(row, q24)}]",
            "    add v11.8h, v26.8h, v28.8h",
            "    sqrdmulh v12.8h, v11.8h, v2.h[0]",
            "    mls v11.8h, v12.8h, v0.h[0]",
            "    sub v13.8h, v26.8h, v28.8h",
            "    sqrdmulh v14.8h, v13.8h, v4.h[0]",
            "    mul v13.8h, v13.8h, v3.h[0]",
            "    mls v13.8h, v14.8h, v0.h[0]",
            "    add v15.8h, v25.8h, v27.8h",
            "    sub v16.8h, v25.8h, v27.8h",
            "    add v17.8h, v15.8h, v11.8h",
            f"    sub {out_v}.8h, v15.8h, v11.8h",
            "    add v18.8h, v16.8h, v13.8h",
            "    sub v19.8h, v16.8h, v13.8h",
        ]
    )
    if store_out0:
        lines.append(f"    str q17, [x21, #{qoff(row, q0)}]    // block0 Q{q0}")
    else:
        lines.append(f"    // str q17, [x21, #{qoff(row, q0)}] omitted")
    lines.append(f"    // str {out_reg}, [x21, #{qoff(row, q8)}] omitted: U01v3 block1 handoff Q{q8}.")
    if store_out2:
        lines.append(f"    str q18, [x21, #{qoff(row, q16)}]   // block2 Q{q16}")
    else:
        lines.append(f"    // str q18, [x21, #{qoff(row, q16)}] omitted")
    if store_out3:
        lines.append(f"    str q19, [x21, #{qoff(row, q24)}]   // block3 Q{q24}")
    else:
        lines.append(f"    // str q19, [x21, #{qoff(row, q24)}] omitted")
    lines.append("")


def emit_stage12_block2_handoff(
    lines: list[str],
    row: str,
    stripe: int,
    store_out0: bool,
    store_out1: bool,
    store_out3: bool,
) -> None:
    q0, q8, q16, q24 = stripe, stripe + 8, stripe + 16, stripe + 24
    out_reg = HANDOFF[2][q16]
    out_v = out_reg.replace("q", "v")
    lines.extend(
        [
            f"    // Stage12 {row} stripe{stripe}: out2 Q{q16} stays live in {out_reg}.",
            f"    ldr q9, [x21, #{qoff(row, q0)}]",
            f"    ldr q10, [x21, #{qoff(row, q8)}]",
            f"    ldr q11, [x21, #{qoff(row, q16)}]",
            f"    ldr q12, [x21, #{qoff(row, q24)}]",
            "    add v18.8h, v10.8h, v12.8h",
            "    sqrdmulh v14.8h, v18.8h, v2.h[0]",
            "    mls v18.8h, v14.8h, v0.h[0]",
            "    sub v21.8h, v10.8h, v12.8h",
            "    sqrdmulh v14.8h, v21.8h, v4.h[0]",
            "    mul v21.8h, v21.8h, v3.h[0]",
            "    mls v21.8h, v14.8h, v0.h[0]",
            "    add v22.8h, v9.8h, v11.8h",
            "    sub v23.8h, v9.8h, v11.8h",
            "    add v24.8h, v22.8h, v18.8h",
            "    sub v25.8h, v22.8h, v18.8h",
            "    sub v26.8h, v23.8h, v21.8h",
        ]
    )
    if store_out0:
        lines.append(f"    str q24, [x21, #{qoff(row, q0)}]    // block0 Q{q0}")
    else:
        lines.append(f"    // str q24, [x21, #{qoff(row, q0)}] omitted")
    if store_out1:
        lines.append(f"    str q25, [x21, #{qoff(row, q8)}]    // block1 Q{q8}")
    else:
        lines.append(f"    // str q25, [x21, #{qoff(row, q8)}] omitted")
    if store_out3:
        lines.append(f"    str q26, [x21, #{qoff(row, q24)}]   // block3 Q{q24}")
    else:
        lines.append(f"    // str q26, [x21, #{qoff(row, q24)}] omitted")
    lines.extend(
        [
            f"    add {out_v}.8h, v23.8h, v21.8h",
            f"    // str {out_reg}, [x21, #{qoff(row, q16)}] omitted: U01v3 block2 handoff Q{q16}.",
            "",
        ]
    )


def emit_stage12_block0_group(lines: list[str], row: str, store_out1: bool, store_out2: bool, store_out3: bool) -> None:
    emit_stage12_twiddles(lines, row, "block0 handoff")
    for stripe in range(8):
        emit_stage12_block0_handoff(lines, row, stripe, store_out1, store_out2, store_out3)


def emit_stage12_block1_group(lines: list[str], row: str, store_out0: bool, store_out2: bool, store_out3: bool) -> None:
    emit_stage12_twiddles(lines, row, "block1 handoff")
    for stripe in range(8):
        emit_stage12_block1_handoff(lines, row, stripe, store_out0, store_out2, store_out3)


def emit_stage12_block2_group(lines: list[str], row: str, store_out0: bool, store_out1: bool, store_out3: bool) -> None:
    emit_stage12_twiddles(lines, row, "block2 handoff")
    for stripe in range(8):
        emit_stage12_block2_handoff(lines, row, stripe, store_out0, store_out1, store_out3)


def emit_scratch_stage345_body(blocks: tuple[int, ...], label: str, stage345: dict[int, list[str]]) -> list[str]:
    block_desc = "_".join(f"block{b}" for b in blocks)
    lines: list[str] = [
        f"// Generated U01v3 helper: run Stage345 {block_desc} from row-major scratch.",
        "//",
        "// Live-in: x19=out, x21=scratch, x23=ntt32 twiddle vector base, v0=q/constants.",
        "",
        ".text",
        "",
        f"{label}:",
    ]
    for row in ROWS:
        for block in blocks:
            emit_stage345_setup(lines, row, block, from_scratch=True)
            lines.extend(stage345[block])
            lines.append("")
    lines.append(f"{label}_end:")
    lines.append("")
    return lines


def common_header(label: str, description: str) -> list[str]:
    return [
        f"// Generated U01v3 {description}.",
        "//",
        "// Do not edit this file by hand; edit",
        "// experiments/forward_ntt_phase123_u01/generate_phase123_shared_prefix_v3_block1_block01_fuse.py.",
        "",
        ".text",
        "",
        f"{label}:",
    ]


def emit_block1_fused(phase_lines: list[str], stage3451_handoff: list[str]) -> list[str]:
    lines = common_header("u01v3_block1_fuse_body", "block1-fuse body")
    emit_phase123_shared_prefix(lines, phase_lines)
    for row in ROWS:
        emit_stage12_block1_group(lines, row, store_out0=True, store_out2=True, store_out3=True)
        emit_stage345_setup(lines, row, 1, from_scratch=False)
        lines.extend(stage3451_handoff)
        lines.append("")
    lines.append("u01v3_block1_fuse_body_end:")
    lines.append("")
    return lines


def emit_block2_fused(phase_lines: list[str], stage3452_handoff: list[str]) -> list[str]:
    lines = common_header("u01v3_block2_fuse_body", "block2-fuse body")
    emit_phase123_shared_prefix(lines, phase_lines)
    for row in ROWS:
        emit_stage12_block2_group(lines, row, store_out0=True, store_out1=True, store_out3=True)
        emit_stage345_setup(lines, row, 2, from_scratch=False)
        lines.extend(stage3452_handoff)
        lines.append("")
    lines.append("u01v3_block2_fuse_body_end:")
    lines.append("")
    return lines


def emit_block01_f0(phase_lines: list[str], stage3450_handoff: list[str], stage3451: list[str]) -> list[str]:
    lines = common_header("u01v3_block01_f0_body", "block0-fused block0+1 body")
    emit_phase123_shared_prefix(lines, phase_lines)
    for row in ROWS:
        emit_stage12_block0_group(lines, row, store_out1=True, store_out2=True, store_out3=True)
        emit_stage345_setup(lines, row, 0, from_scratch=False)
        lines.extend(stage3450_handoff)
        lines.append("")
        emit_stage345_setup(lines, row, 1, from_scratch=True)
        lines.extend(stage3451)
        lines.append("")
    lines.append("u01v3_block01_f0_body_end:")
    lines.append("")
    return lines


def emit_block012_f0(
    phase_lines: list[str],
    stage3450_handoff: list[str],
    stage3451: list[str],
    stage3452: list[str],
) -> list[str]:
    lines = common_header("u01v3_block012_f0_body", "block0-fused block0+1+2 body")
    emit_phase123_shared_prefix(lines, phase_lines)
    for row in ROWS:
        emit_stage12_block0_group(lines, row, store_out1=True, store_out2=True, store_out3=True)
        emit_stage345_setup(lines, row, 0, from_scratch=False)
        lines.extend(stage3450_handoff)
        lines.append("")
        for block, body in ((1, stage3451), (2, stage3452)):
            emit_stage345_setup(lines, row, block, from_scratch=True)
            lines.extend(body)
            lines.append("")
    lines.append("u01v3_block012_f0_body_end:")
    lines.append("")
    return lines


def emit_block01_f1(phase_lines: list[str], stage3450: list[str], stage3451_handoff: list[str]) -> list[str]:
    lines = common_header("u01v3_block01_f1_body", "block1-fused block0+1 body")
    emit_phase123_shared_prefix(lines, phase_lines)
    for row in ROWS:
        emit_stage12_block1_group(lines, row, store_out0=True, store_out2=True, store_out3=True)
        emit_stage345_setup(lines, row, 1, from_scratch=False)
        lines.extend(stage3451_handoff)
        lines.append("")
        emit_stage345_setup(lines, row, 0, from_scratch=True)
        lines.extend(stage3450)
        lines.append("")
    lines.append("u01v3_block01_f1_body_end:")
    lines.append("")
    return lines


def emit_block012_f1(
    phase_lines: list[str],
    stage3450: list[str],
    stage3451_handoff: list[str],
    stage3452: list[str],
) -> list[str]:
    lines = common_header("u01v3_block012_f1_body", "block1-fused block0+1+2 body")
    emit_phase123_shared_prefix(lines, phase_lines)
    for row in ROWS:
        emit_stage12_block1_group(lines, row, store_out0=True, store_out2=True, store_out3=True)
        emit_stage345_setup(lines, row, 1, from_scratch=False)
        lines.extend(stage3451_handoff)
        lines.append("")
        for block, body in ((0, stage3450), (2, stage3452)):
            emit_stage345_setup(lines, row, block, from_scratch=True)
            lines.extend(body)
            lines.append("")
    lines.append("u01v3_block012_f1_body_end:")
    lines.append("")
    return lines


def emit_block012_f2(
    phase_lines: list[str],
    stage3450: list[str],
    stage3451: list[str],
    stage3452_handoff: list[str],
) -> list[str]:
    lines = common_header("u01v3_block012_f2_body", "block2-fused block0+1+2 body")
    emit_phase123_shared_prefix(lines, phase_lines)
    for row in ROWS:
        emit_stage12_block2_group(lines, row, store_out0=True, store_out1=True, store_out3=True)
        emit_stage345_setup(lines, row, 2, from_scratch=False)
        lines.extend(stage3452_handoff)
        lines.append("")
        for block, body in ((0, stage3450), (1, stage3451)):
            emit_stage345_setup(lines, row, block, from_scratch=True)
            lines.extend(body)
            lines.append("")
    lines.append("u01v3_block012_f2_body_end:")
    lines.append("")
    return lines


def emit_block01_fused(phase_lines: list[str], stage3450_handoff: list[str], stage3451_handoff: list[str]) -> list[str]:
    lines = common_header("u01v3_block01_fuse_body", "block0+block1 cumulative fuse body")
    emit_phase123_shared_prefix(lines, phase_lines)
    for row in ROWS:
        lines.append(f"    // {row}: pass A keeps raw scratch unchanged while producing block0.")
        emit_stage12_block0_group(lines, row, store_out1=False, store_out2=False, store_out3=False)
        emit_stage345_setup(lines, row, 0, from_scratch=False)
        lines.extend(stage3450_handoff)
        lines.append("")

        lines.append(f"    // {row}: pass B uses still-raw scratch, produces block1, stores blocks2/3.")
        emit_stage12_block1_group(lines, row, store_out0=False, store_out2=True, store_out3=True)
        emit_stage345_setup(lines, row, 1, from_scratch=False)
        lines.extend(stage3451_handoff)
        lines.append("")
    lines.append("u01v3_block01_fuse_body_end:")
    lines.append("")
    return lines


def layout_entries(block: int) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    stage12_output = {0: "out0", 1: "out1", 2: "out2"}[block]
    for q in range(block * 8, block * 8 + 8):
        stage12_reg = HANDOFF[block][q]
        stage345_reg = STAGE345_DEST[block][q]
        entries.append(
            {
                "semantic_name": f"Q{q}",
                "stage12_output": stage12_output,
                "stage12_register": stage12_reg,
                "original_scratch_store_offset_by_row": {
                    row: qoff(row, q) for row in ROWS
                },
                "stage345_load_offset": q * 16,
                "stage345_load_destination": stage345_reg,
                "proposed_handoff_register": stage12_reg,
                "vector_move_required": stage12_reg != stage345_reg,
                "inserted_move": (
                    f"mov v{stage345_reg[1:]}.16b, v{stage12_reg[1:]}.16b"
                    if stage12_reg != stage345_reg
                    else None
                ),
            }
        )
    return entries


def main() -> int:
    phase_lines = PHASE123.read_text().splitlines()
    stage345 = {0: load_stage345_block(0), 1: load_stage345_block(1), 2: load_stage345_block(2)}
    stage345_handoff = {
        0: transform_stage345_for_handoff(0, stage345[0]),
        1: transform_stage345_for_handoff(1, stage345[1]),
        2: transform_stage345_for_handoff(2, stage345[2]),
    }

    OUT_B1_SCRATCH.write_text(
        "\n".join(emit_scratch_stage345_body((1,), "u01v3_stage345_block1_from_scratch_allrows", stage345))
    )
    OUT_B01_SCRATCH.write_text(
        "\n".join(emit_scratch_stage345_body((0, 1), "u01v3_stage345_block01_from_scratch_allrows", stage345))
    )
    OUT_B2_SCRATCH.write_text(
        "\n".join(emit_scratch_stage345_body((2,), "u01v3_stage345_block2_from_scratch_allrows", stage345))
    )
    OUT_B012_SCRATCH.write_text(
        "\n".join(emit_scratch_stage345_body((0, 1, 2), "u01v3_stage345_block012_from_scratch_allrows", stage345))
    )
    OUT_B1_FUSED.write_text("\n".join(emit_block1_fused(phase_lines, stage345_handoff[1])))
    OUT_B01_F0.write_text("\n".join(emit_block01_f0(phase_lines, stage345_handoff[0], stage345[1])))
    OUT_B01_F1.write_text("\n".join(emit_block01_f1(phase_lines, stage345[0], stage345_handoff[1])))
    OUT_B01_FUSED.write_text("\n".join(emit_block01_fused(phase_lines, stage345_handoff[0], stage345_handoff[1])))
    OUT_B2_FUSED.write_text("\n".join(emit_block2_fused(phase_lines, stage345_handoff[2])))
    OUT_B012_F0.write_text(
        "\n".join(emit_block012_f0(phase_lines, stage345_handoff[0], stage345[1], stage345[2]))
    )
    OUT_B012_F1.write_text(
        "\n".join(emit_block012_f1(phase_lines, stage345[0], stage345_handoff[1], stage345[2]))
    )
    OUT_B012_F2.write_text(
        "\n".join(emit_block012_f2(phase_lines, stage345[0], stage345[1], stage345_handoff[2]))
    )

    OUT_B1_LAYOUT.write_text(
        json.dumps(
            {
                "candidate": "u01v3_block1_fuse",
                "removed_stage12_q_stores": 24,
                "removed_stage345_q_loads": 24,
                "inserted_vector_moves": 3,
                "entries": layout_entries(1),
            },
            indent=2,
        )
        + "\n"
    )
    OUT_B01_LAYOUT.write_text(
        json.dumps(
            {
                "candidate": "u01v3_block01_fuse",
                "removed_stage12_q_stores": 48,
                "removed_stage345_q_loads": 48,
                "inserted_vector_moves": 6,
                "extra_stage12_raw_q_loads_due_to_two_pass": 96,
                "blocks": {"block0": layout_entries(0), "block1": layout_entries(1)},
            },
            indent=2,
        )
        + "\n"
    )
    OUT_B2_LAYOUT.write_text(
        json.dumps(
            {
                "candidate": "u01v3_block2_fuse",
                "removed_stage12_q_stores": 24,
                "removed_stage345_q_loads": 24,
                "inserted_vector_moves": len(ROWS)
                * sum(1 for e in layout_entries(2) if e["vector_move_required"]),
                "entries": layout_entries(2),
            },
            indent=2,
        )
        + "\n"
    )
    OUT_B012_LAYOUT.write_text(
        json.dumps(
            {
                "candidate_family": "u01v3_block012_isolated_fuse_matrix",
                "two_pass_cumulative": False,
                "extra_stage12_raw_q_loads": 0,
                "variants": {
                    "F0": {
                        "fused_block": 0,
                        "removed_stage12_q_stores": 24,
                        "removed_stage345_q_loads": 24,
                        "inserted_vector_moves": len(ROWS)
                        * sum(
                            1 for e in layout_entries(0) if e["vector_move_required"]
                        ),
                    },
                    "F1": {
                        "fused_block": 1,
                        "removed_stage12_q_stores": 24,
                        "removed_stage345_q_loads": 24,
                        "inserted_vector_moves": len(ROWS)
                        * sum(
                            1 for e in layout_entries(1) if e["vector_move_required"]
                        ),
                    },
                    "F2": {
                        "fused_block": 2,
                        "removed_stage12_q_stores": 24,
                        "removed_stage345_q_loads": 24,
                        "inserted_vector_moves": len(ROWS)
                        * sum(
                            1 for e in layout_entries(2) if e["vector_move_required"]
                        ),
                    },
                },
                "blocks": {
                    "block0": layout_entries(0),
                    "block1": layout_entries(1),
                    "block2": layout_entries(2),
                },
            },
            indent=2,
        )
        + "\n"
    )

    for path in (
        OUT_B1_SCRATCH,
        OUT_B01_SCRATCH,
        OUT_B2_SCRATCH,
        OUT_B012_SCRATCH,
        OUT_B1_FUSED,
        OUT_B01_F0,
        OUT_B01_F1,
        OUT_B01_FUSED,
        OUT_B2_FUSED,
        OUT_B012_F0,
        OUT_B012_F1,
        OUT_B012_F2,
        OUT_B1_LAYOUT,
        OUT_B01_LAYOUT,
        OUT_B2_LAYOUT,
        OUT_B012_LAYOUT,
    ):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
