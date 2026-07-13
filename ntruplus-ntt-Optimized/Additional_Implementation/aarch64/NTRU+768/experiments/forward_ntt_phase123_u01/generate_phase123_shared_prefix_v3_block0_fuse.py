#!/usr/bin/env python3
"""Generate U01v3 block0-fuse experiment artifacts.

U01v3 is a correctness candidate for one boundary only:

  Stage12 out0 Q0..Q7 -> Stage345 block0 input

It keeps Phase123 raw scratch and all later Stage12 scratch stores.  It removes
only the Stage12 Q0..Q7 stores and replaces Stage345 block0 row loads with
register handoff.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from generate_phase123_shared_prefix_v2 import PHASE123, extract_region
from generate_stage12_block0_first import qoff


ROOT = Path(__file__).resolve().parent
NTRU_ROOT = ROOT.parents[1]
BASELINE_STAGE345 = ROOT / "stage345_block0_livein/baseline-stage345-block0.s"
OUT_FUSED = ROOT / "phase123_shared_prefix_v3_block0_fuse_allrows.sym.s"
OUT_SCRATCH_STAGE345 = ROOT / "u01v3_stage345_block0_from_scratch_allrows.sym.s"
OUT_LAYOUT = ROOT / "u01v3_layout_map.json"

ROWS = ("row0", "row1", "row2")
ROW_SCRATCH = {"row0": 0, "row1": 512, "row2": 1024}
ROW_SCATTER = {"row0": 0, "row1": 256, "row2": 512}

# Original production Stage345 block0 load destination contract.
STAGE345_DEST = {
    0: "q29",
    1: "q6",
    2: "q28",
    3: "q17",
    4: "q26",
    5: "q5",
    6: "q18",
    7: "q8",
}

# Handoff registers chosen so Stage12 can produce most values directly into the
# Stage345 expected input register.  Q1 cannot live in q6 because q6 is first
# used by the Stage345 twiddle load, so Q1 is carried in q1 and moved at the
# original row-load site.
HANDOFF = {
    0: "q29",
    1: "q1",
    2: "q28",
    3: "q17",
    4: "q26",
    5: "q5",
    6: "q18",
    7: "q8",
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


def load_stage345_block0() -> list[str]:
    lines = BASELINE_STAGE345.read_text().splitlines()
    inside = False
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == "_gt_ntt32_batch8_ct_stage345_block0_slothy_start:":
            inside = True
            continue
        if stripped == "_gt_ntt32_batch8_ct_stage345_block0_slothy_end:":
            break
        if inside:
            out.append(line.rstrip())
    if not out:
        raise ValueError("could not extract Stage345 block0 baseline")
    return out


def emit_stage12_handoff_stripe(lines: list[str], row: str, stripe: int) -> None:
    q0, q8, q16, q24 = stripe, stripe + 8, stripe + 16, stripe + 24
    out_reg = HANDOFF[stripe]
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
            f"    // str {out_reg}, [x21, #{qoff(row, q0)}] omitted: U01v3 handoff Q{q0}.",
            f"    str q20, [x21, #{qoff(row, q8)}]    // later block1 Q{q8}",
            f"    str q21, [x21, #{qoff(row, q16)}]   // later block2 Q{q16}",
            f"    str q22, [x21, #{qoff(row, q24)}]   // later block3 Q{q24}",
            "",
        ]
    )


def transform_stage345_for_handoff(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        code = line.split("//", 1)[0].rstrip()
        match = LOAD_RE.match(code)
        if match:
            dest = match.group(1)
            offset = int(match.group(2))
            if offset % 16 != 0:
                raise ValueError(f"unexpected row load offset {offset}")
            q_index = offset // 16
            if q_index in STAGE345_DEST:
                expected_dest = STAGE345_DEST[q_index]
                if dest != expected_dest:
                    raise ValueError(
                        f"Stage345 Q{q_index} dest changed: {dest} != {expected_dest}"
                    )
                handoff = HANDOFF[q_index]
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


def emit_stage345_setup(lines: list[str], row: str, from_scratch: bool) -> None:
    lines.extend(
        [
            f"    // ---- {row}: Stage345 block0 {'from scratch' if from_scratch else 'from live handoff'} ----",
            f"    add x10, x19, #{ROW_SCATTER[row]}",
            "    add x14, x19, #768",
            "    add x12, x23, #64",
        ]
    )
    if from_scratch:
        lines.append(f"    add x4, x21, #{ROW_SCRATCH[row]}")
    lines.append("")


def emit_fused_body(phase_lines: list[str], stage345_lines: list[str]) -> list[str]:
    lines: list[str] = [
        "// Generated U01v3 block0-fuse body.",
        "//",
        "// Do not edit this file by hand; edit",
        "// experiments/forward_ntt_phase123_u01/generate_phase123_shared_prefix_v3_block0_fuse.py.",
        "//",
        "// Live-in:",
        "//   x19 = final scatter output base",
        "//   x20 = input base",
        "//   x21 = row-major scratch base",
        "//   x22 = Phase123 twist table base",
        "//   x23 = ntt32 twiddle vector base",
        "//   v0  = q/constants",
        "// Scratch contract:",
        "//   Phase123 raw Q0..Q31 are written to x21 row-major scratch.",
        "//   Stage12 out0 Q0..Q7 are kept in vector registers and not stored.",
        "//   Stage345 block0 row loads are replaced by register handoff.",
        "",
        ".text",
        "",
        "u01v3_block0_fuse_body:",
    ]
    for iteration in (0, 2, 4, 6, 1, 3, 5, 7):
        emit_phase123_iter(lines, phase_lines, iteration)

    transformed_stage345 = transform_stage345_for_handoff(stage345_lines)
    for row in ROWS:
        lines.extend(
            [
                f"    // ---- {row}: Stage12 all stripes, Q0..Q7 live-out ----",
                "    ldr q2, [x23, #16]",
                "    ldr q3, [x23, #32]",
                "    ldr q4, [x23, #48]",
                "",
            ]
        )
        for stripe in range(8):
            emit_stage12_handoff_stripe(lines, row, stripe)
        emit_stage345_setup(lines, row, from_scratch=False)
        lines.extend(transformed_stage345)
        lines.append("")

    lines.append("u01v3_block0_fuse_body_end:")
    lines.append("")
    return lines


def emit_scratch_stage345_body(stage345_lines: list[str]) -> list[str]:
    lines: list[str] = [
        "// Generated U01v3 helper: run Stage345 block0 from row-major scratch.",
        "//",
        "// Live-in:",
        "//   x19 = final scatter output base",
        "//   x21 = row-major post-Stage12 scratch base",
        "//   x23 = ntt32 twiddle vector base",
        "//   v0  = q/constants",
        "",
        ".text",
        "",
        "u01v3_stage345_block0_from_scratch_allrows:",
    ]
    for row in ROWS:
        emit_stage345_setup(lines, row, from_scratch=True)
        lines.extend(stage345_lines)
        lines.append("")
    lines.append("u01v3_stage345_block0_from_scratch_allrows_end:")
    lines.append("")
    return lines


def build_layout_map() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for row in ROWS:
        entries: list[dict[str, object]] = []
        for q in range(8):
            stage12_reg = HANDOFF[q]
            stage345_reg = STAGE345_DEST[q]
            entries.append(
                {
                    "semantic_name": f"Q{q}",
                    "stage12_out0_producer": (
                        f"Stage12 {row} stripe{q}: add {stage12_reg.replace('q', 'v')}.8h, "
                        "v16.8h, v13.8h"
                    ),
                    "stage12_out0_register": stage12_reg,
                    "original_u01v2_scratch_store_offset": qoff(row, q),
                    "original_stage345_block0_load_offset": q * 16,
                    "original_stage345_block0_load_destination": stage345_reg,
                    "proposed_handoff_register": stage12_reg,
                    "vector_move_required": stage12_reg != stage345_reg,
                    "inserted_move": (
                        f"mov v{stage345_reg[1:]}.16b, v{stage12_reg[1:]}.16b"
                        if stage12_reg != stage345_reg
                        else None
                    ),
                    "handoff_register_live_safe": True,
                }
            )
        rows.append(
            {
                "row": row,
                "row_scratch_base": ROW_SCRATCH[row],
                "row_scatter_base": ROW_SCATTER[row],
                "q0_to_q7": entries,
            }
        )
    return {
        "candidate": "u01v3_block0_fuse",
        "removed_stage12_out0_q_stores": 24,
        "removed_stage345_block0_q_loads": 24,
        "inserted_vector_moves": 3,
        "stage345_arithmetic_changed": False,
        "stage345_reduction_changed": False,
        "stage345_scatter_changed": False,
        "rows": rows,
    }


def main() -> int:
    phase_lines = PHASE123.read_text().splitlines()
    stage345_lines = load_stage345_block0()
    OUT_FUSED.write_text("\n".join(emit_fused_body(phase_lines, stage345_lines)))
    OUT_SCRATCH_STAGE345.write_text("\n".join(emit_scratch_stage345_body(stage345_lines)))
    OUT_LAYOUT.write_text(json.dumps(build_layout_map(), indent=2) + "\n")
    print(OUT_FUSED)
    print(OUT_SCRATCH_STAGE345)
    print(OUT_LAYOUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
