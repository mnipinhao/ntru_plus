#!/usr/bin/env python3
"""Generate the G1C BMScale live-result to inverse-head scheduling contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def signed16(value: int) -> int:
    value %= 1 << 16
    return value - (1 << 16) if value >= (1 << 15) else value


def instructions(source: str) -> list[str]:
    result = []
    for raw in source.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.endswith(":") or line.startswith((".", "/*", "*")):
            continue
        result.append(line)
    return result


def emit_words(label: str, values: list[int]) -> str:
    return f".p2align 5\n{label}:\n  .word " + ", ".join(map(str, values)) + "\n"


def emit_bytes(label: str, values: list[int]) -> str:
    return f".p2align 5\n{label}:\n  .byte " + ", ".join(map(str, values)) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--basemul-source", type=Path, required=True)
    parser.add_argument("--lifecycle-audit", type=Path, required=True)
    parser.add_argument("--inverse-head-oracle", type=Path, required=True)
    parser.add_argument("--pipeline-layout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--asm-constants", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    source = args.basemul_source.read_text()
    lifecycle = json.loads(args.lifecycle_audit.read_text())
    inverse = json.loads(args.inverse_head_oracle.read_text())
    layout = json.loads(args.pipeline_layout.read_text())
    body = source.split("poly_basemul_scale:", 1)[1]
    first_block, remainder = re.split(r"add\s+\$128,\s*%rsi", body, maxsplit=1)
    required = (
        "vmovdqa %ymm5,   (%rdi)", "vmovdqa %ymm6, 32(%rdi)",
        "vmovdqa %ymm7, 64(%rdi)", "vmovdqa %ymm1, 96(%rdi)",
        "vmovdqa 64(%rsi), %ymm5", "vmovdqa 96(%rsi), %ymm6",
        "vmovdqa 64(%rdx), %ymm7", "vmovdqa 96(%rdx), %ymm8",
    )
    for fragment in required:
        if fragment not in first_block:
            raise SystemExit(f"Official BMScale live-tail fragment disappeared: {fragment}")
    if "add $64,  %rcx" not in remainder or "_looptop_basemul_scale" not in remainder:
        raise SystemExit("Official BMScale two-block loop structure changed")
    if lifecycle["functions"]["poly_basemul_scale"]["distinct_ymm_count"] != 16:
        raise SystemExit("Official BMScale no longer touches all 16 YMM registers")

    early_end = first_block.index("vmovdqa %ymm7, 64(%rdi)")
    late_start = first_block.index("vmovdqa 64(%rsi), %ymm5", early_end)
    late_end = first_block.index("vmovdqa %ymm1, 96(%rdi)", late_start)
    overwrite_gap = instructions(first_block[late_start:late_end])

    direct_rows = []
    header_rows = []
    asm = "/* Generated G1C BMScale-live direct inverse distance-1 constants. */\n.section .rodata\n"
    asm += emit_words(".Lgt_g1c_bmscale_q", [Q] * 16)
    asm += emit_words(".Lgt_g1c_bmscale_qinv", [QINV] * 16)
    asm += emit_bytes(
        ".Lgt_g1c_bmscale_adjacent_word_swap",
        [byte for lane in range(2) for word in range(8)
         for byte in (lane * 16 + 2 * (word ^ 1), lane * 16 + 2 * (word ^ 1) + 1)],
    )
    for row in inverse["rows"]:
        inverse_mod = row["inverse_distance1_twiddle_mod_q"]
        alternating_mod = []
        for value in inverse_mod:
            alternating_mod.extend((value, (-value) % Q))
        alternating_mont = [centered(value * R) for value in alternating_mod]
        alternating_qinv = [signed16(value * QINV) for value in alternating_mont]
        direct_rows.append({
            "physical_row": row["physical_row"],
            "frequency_p": row["frequency_p"],
            "lane_semantics": "even lane is blended away after +z^-1 product; odd lane uses -z^-1 because odd difference is D-S",
            "inverse_twiddle_alternating_mod_q": alternating_mod,
            "inverse_twiddle_alternating_montgomery_signed": alternating_mont,
            "inverse_twiddle_alternating_qinv_signed16": alternating_qinv,
        })
        header_rows.append((alternating_mont, alternating_qinv))
        asm += emit_words(
            f".Lgt_g1c_bmscale_row{row['physical_row']}_direct_inverse_d1_zeta",
            alternating_mont)
        asm += emit_words(
            f".Lgt_g1c_bmscale_row{row['physical_row']}_direct_inverse_d1_qinv",
            alternating_qinv)

    cell_by_key = {
        (cell["branch"], cell["gt_row_physical_trit_reversed"],
         cell["ntt16_lane_physical_bit_reversed"]): cell
        for cell in layout["cells"]
    }
    arithmetic_rows = []
    for branch in range(2):
        for row in range(9):
            cells = [cell_by_key[(branch, row, lane)] for lane in range(16)]
            arithmetic_rows.append({
                "branch": branch,
                "physical_row": row,
                "frequency_p": cells[0]["ntt9_frequency_p"],
                "frequency_q_by_lane": [cell["ntt16_frequency_q"] for cell in cells],
                "factor_mod_q_by_lane": [cell["factor_mod_q"] for cell in cells],
                "factor_montgomery_signed_by_lane": [cell["basemul_factor_montgomery"]
                                                       for cell in cells],
                "factor_qinv_signed16_by_lane": [cell["basemul_factor_qinv_signed16"]
                                                  for cell in cells],
                "input_terminal_vectors": [0, 1, 2, 3],
            })
            asm += emit_words(
                f".Lgt_g1c_bmscale_branch{branch}_row{row}_factor_zeta",
                arithmetic_rows[-1]["factor_montgomery_signed_by_lane"])
            asm += emit_words(
                f".Lgt_g1c_bmscale_branch{branch}_row{row}_factor_qinv",
                arithmetic_rows[-1]["factor_qinv_signed16_by_lane"])

    materialized_pair_schedule = [
        "vperm2i128 low halves of cj,cj+1",
        "vperm2i128 high halves of cj,cj+1",
        "vpshufb each temporary to [even4,odd4] per 128-bit lane",
        "vpunpcklqdq to form packed even-q vector",
        "vpunpckhqdq to form packed odd-q vector",
    ]
    direct_schedule = [
        "vpshufb adjacent-word swap",
        "vpaddw original,swapped -> duplicated S+D",
        "vpsubw original,swapped -> [S-D,D-S]",
        "four-instruction Montgomery reduce/multiply by alternating [z^-1,-z^-1]",
        "vpblendw even sums with odd twisted differences",
    ]
    document = {
        "schema": "gt-g1c-bmscale-live-tail/v2",
        "checkpoint": "G1C2-contract-BMScale-live-tail",
        "parameter": 1152,
        "official_live_result_cutpoints": {
            "early": {
                "results": {"c0": "ymm5", "c1": "ymm6", "c2": "ymm7"},
                "operands_that_must_survive_for_c3": {
                    "a0": "ymm1", "a1": "ymm2", "b0": "ymm3", "b1": "ymm4"},
                "stores": [0, 32, 64],
            },
            "late": {"results": {"c3": "ymm1"}, "stores": [96]},
            "c2_register_overwrite": "ymm7 is reloaded with b2 immediately after the early stores",
            "instructions_between_c2_store_and_c3_store": len(overwrite_gap),
            "all_ymm_registers_touched_by_function": 16,
            "arithmetic_changed": False,
        },
        "gt_bmscale_arithmetic_contract": {
            "input_layout": "gt_row_terminal_lane",
            "row_blocks": 18,
            "terminal_polynomial": "degree-4 product modulo X^4-factor(branch,p,q)",
            "schedule_policy": "preserve Official BMScale product/add/reduction schedule and rekey only lane factor constants",
            "operand_transform_scales": [4, 4],
            "output_transform_scale": 16,
            "output_montgomery_r_exponent": -1,
            "rows": arithmetic_rows,
        },
        "materialized_persistent_pair_path": {
            "id": "C2-P",
            "disposition": "diagnostic-not-authorized-as-zero-seam",
            "routing_schedule_per_terminal_pair": materialized_pair_schedule,
            "routing_instructions_per_terminal_pair": 6,
            "routing_instructions_per_row": 12,
            "routing_instructions_full_transform": 216,
            "final_vector_stores_per_row": 4,
            "c0_c1": "can be packed at the early cutpoint",
            "c2_c3": "not simultaneously live in the faithful Official arithmetic schedule",
            "faithful_schedule_minimum_extra_memory": {
                "temporary_c2_stores_per_row": 1,
                "temporary_c2_loads_per_row": 1,
                "full_transform_temporary_stores": 18,
                "full_transform_temporary_loads": 18,
            },
            "retain_c2_in_register": "not authorized: Official touches all 16 YMM and linked liveness is unproved",
            "prior_eight_per_row_estimate": "superseded by explicit reversible AVX2 schedule",
        },
        "live_direct_inverse_path": {
            "id": "C2-L",
            "disposition": "selected-for-linked-ASM-prototype",
            "schedule_per_terminal_coefficient": direct_schedule,
            "instructions_per_terminal_coefficient": 8,
            "instructions_per_row": 32,
            "terminal_coefficients_per_row": 4,
            "edge_input_loads": 0,
            "post_inverse_d1_stores_per_row": 4,
            "materialized_BMScale_to_inverse_seam": False,
            "early_cutpoint": "consume c0,c1,c2 sequentially while preserving a0,a1,b0,b1",
            "late_cutpoint": "consume c3 after its final add chain",
            "output_layout": "canonical interleaved twice-pre-distance1 lanes per terminal coefficient",
            "designed_peak_live_ymm_upper_bound": 16,
            "prior_peak_13_estimate": "superseded: omitted BMScale-core liveness before the early cutpoint",
            "peak_bound_status": "must be certified by linked-object backward dataflow audit",
            "scale_and_range_source": "generated/g1c-adjusted-inverse-head.json",
        },
        "direct_inverse_rows": direct_rows,
        "selection": {
            "selected": "C2-L",
            "reason": "consume results at their actual live cutpoints; avoid persistent packing and the c2/c3 lifetime gap",
            "C2_P_rejected": False,
            "C2_P_role": "retain as a materialized diagnostic if linked C2-L needs isolation",
            "cycle_claim": None,
        },
        "prototype_gate": {
            "linked_C2_L_asm_authorized": True,
            "must_preserve_official_bmscale_arithmetic": True,
            "must_not_add_standalone_converter": True,
            "required_before_timing": [
                "bit-exact BMScale differential in canonicalized output",
                "linked inverse-distance1 differential for all 1152 cells",
                "BMScale output and inverse-head cutpoint range checks",
                "no call, frame, vector spill, or materialized edge load/store audit",
            ],
            "cycles": None,
        },
        "source_sha256": {
            "official_basemul": sha256(args.basemul_source),
            "lifecycle_audit": sha256(args.lifecycle_audit),
            "inverse_head_oracle": sha256(args.inverse_head_oracle),
            "pipeline_layout": sha256(args.pipeline_layout),
        },
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"

    header = """#ifndef NTRUPLUS1152_EXP001_G1C_BMSCALE_LIVE_TAIL_H
#define NTRUPLUS1152_EXP001_G1C_BMSCALE_LIVE_TAIL_H

#include <stdint.h>

"""
    header += "static const int16_t ntruplus1152_exp001_g1c_bmscale_direct_d1_zeta[9][16] = {\n"
    for values, _ in header_rows:
        header += "  {" + ", ".join(map(str, values)) + "},\n"
    header += "};\n\nstatic const int16_t ntruplus1152_exp001_g1c_bmscale_direct_d1_qinv[9][16] = {\n"
    for _, values in header_rows:
        header += "  {" + ", ".join(map(str, values)) + "},\n"
    header += "};\n\n"
    header += "static const int16_t ntruplus1152_exp001_g1c_bmscale_factor_mod_q[2][9][16] = {\n"
    for branch in range(2):
        header += "  {\n"
        for row in range(9):
            values = arithmetic_rows[branch * 9 + row]["factor_mod_q_by_lane"]
            header += "    {" + ", ".join(map(str, values)) + "},\n"
        header += "  },\n"
    header += "};\n\n#endif\n"

    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated G1C BMScale live-tail contract is stale")
        if not args.header.is_file() or args.header.read_text() != header:
            raise SystemExit("generated G1C BMScale live-tail header is stale")
        if not args.asm_constants.is_file() or args.asm_constants.read_text() != asm:
            raise SystemExit("generated G1C BMScale live-tail ASM constants are stale")
        return 0
    args.output.write_text(rendered)
    args.header.write_text(header)
    args.asm_constants.write_text(asm)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
