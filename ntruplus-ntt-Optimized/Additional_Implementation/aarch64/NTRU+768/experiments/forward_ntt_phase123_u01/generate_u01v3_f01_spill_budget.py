#!/usr/bin/env python3
"""Generate U01v3 one-pass F01 spill-budget experiment artifacts.

The candidate computes Stage12 out0 and out1 once per row/stripe.  The out0
values remain live for Stage345 block0.  The out1 values are the only explicit
spills: they are saved to stack before Stage345 block0 clobbers them and
restored immediately before Stage345 block1.
"""

from __future__ import annotations

import json
from pathlib import Path

from generate_phase123_shared_prefix_v3_block1_block01_fuse import (
    HANDOFF,
    ROWS,
    emit_phase123_shared_prefix,
    emit_stage12_twiddles,
    emit_stage345_setup,
    load_stage345_block,
    qoff,
    transform_stage345_for_handoff,
)
from generate_phase123_shared_prefix_v2 import PHASE123


ROOT = Path(__file__).resolve().parent
NTRU_ROOT = ROOT.parents[1]
ASM_ROOT = NTRU_ROOT / "asm/gt/experiment"
TEST_ROOT = NTRU_ROOT / "gt_test"

SPILL_BASE = 160
SPILL_STRIDE_PER_ROW = 128

FEASIBLE_VARIANTS = {
    "bmin": {
        "symbol": "u01v3_f01_bmin_spill_budget",
        "matrix_alias": "u01v3_block01_f01_bmin",
        "body_label": "u01v3_f01_bmin_spill_budget_body",
        "budget": 8,
        "description": "minimal feasible one-pass F01 spill budget",
    },
    "b8": {
        "symbol": "u01v3_f01_b8_spill_budget",
        "matrix_alias": "u01v3_block01_f01_b8",
        "body_label": "u01v3_f01_b8_spill_budget_body",
        "budget": 8,
        "description": "explicit eight-vector one-pass F01 spill budget",
    },
}

INFEASIBLE_VARIANTS = {
    "b2": {
        "budget": 2,
        "missing": 6,
    },
    "b4": {
        "budget": 4,
        "missing": 4,
    },
}


def spill_offset(row: str, stripe: int) -> int:
    return SPILL_BASE + ROWS.index(row) * SPILL_STRIDE_PER_ROW + stripe * 16


def emit_stage12_block01_onepass(lines: list[str], row: str) -> None:
    emit_stage12_twiddles(lines, row, "block0 live handoff + block1 stack spill")
    for stripe in range(8):
        q0, q8, q16, q24 = stripe, stripe + 8, stripe + 16, stripe + 24
        out0 = HANDOFF[0][q0]
        out1 = HANDOFF[1][q8]
        out0_v = out0.replace("q", "v")
        out1_v = out1.replace("q", "v")
        lines.extend(
            [
                f"    // Stage12 {row} stripe{stripe}: one-pass out0 live, out1 spill.",
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
                f"    add {out0_v}.8h, v16.8h, v13.8h",
                f"    sub {out1_v}.8h, v16.8h, v13.8h",
                "    add v21.8h, v19.8h, v15.8h",
                "    sub v22.8h, v19.8h, v15.8h",
                f"    // str {out0}, [x21, #{qoff(row, q0)}] omitted: block0 handoff Q{q0}.",
                f"    str {out1}, [sp, #{spill_offset(row, stripe)}]    // spill block1 Q{q8}",
                f"    str q21, [x21, #{qoff(row, q16)}]   // block2 Q{q16}",
                f"    str q22, [x21, #{qoff(row, q24)}]   // block3 Q{q24}",
                "",
            ]
        )


def emit_restore_block1(lines: list[str], row: str) -> None:
    lines.append(f"    // Restore {row} block1 handoff values spilled across Stage345 block0.")
    for stripe in range(8):
        q8 = stripe + 8
        reg = HANDOFF[1][q8]
        lines.append(f"    ldr {reg}, [sp, #{spill_offset(row, stripe)}]    // restore Q{q8}")
    lines.append("")


def emit_body(
    label: str,
    phase_lines: list[str],
    stage3450_handoff: list[str],
    stage3451_handoff: list[str],
) -> list[str]:
    lines: list[str] = [
        f"// Generated U01v3 one-pass F01 spill-budget body: {label}.",
        "//",
        "// Shape: shared Phase123 once, Stage12 out0/out1 once, spill only",
        "// block1 live-ins clobbered by unchanged Stage345 block0.",
        "",
        ".text",
        "",
        f"{label}:",
    ]
    emit_phase123_shared_prefix(lines, phase_lines)
    for row in ROWS:
        emit_stage12_block01_onepass(lines, row)
        emit_stage345_setup(lines, row, 0, from_scratch=False)
        lines.extend(stage3450_handoff)
        lines.append("")
        emit_restore_block1(lines, row)
        emit_stage345_setup(lines, row, 1, from_scratch=False)
        lines.extend(stage3451_handoff)
        lines.append("")
    lines.append(f"{label}_end:")
    lines.append("")
    return lines


def emit_wrapper(symbol: str, body_include: str, matrix_alias: str | None = None) -> str:
    alias_lines = []
    alias_end_lines = []
    if matrix_alias:
        alias_lines = [
            f".global {matrix_alias}",
            f".type {matrix_alias}, %function",
            f"{matrix_alias}:",
        ]
        alias_end_lines = [
            f".global {matrix_alias}_end",
            f"{matrix_alias}_end:",
        ]
    return "\n".join(
        [
            f"/* U01v3 one-pass F01 spill-budget candidate: {symbol}. */",
            "",
            ".text",
            ".align 4",
            ".equ STACK_LOC_0, 0",
            "",
            *alias_lines,
            f".global {symbol}",
            f".type {symbol}, %function",
            f"{symbol}:",
            "    sub sp, sp, #544",
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
            f"    .include \"{body_include}\"",
            "",
            "    ldp d14, d15, [sp, #112]",
            "    ldp d12, d13, [sp, #96]",
            "    ldp d10, d11, [sp, #80]",
            "    ldp d8, d9, [sp, #64]",
            "    ldr x23, [sp, #48]",
            "    ldp x21, x22, [sp, #32]",
            "    ldp x19, x20, [sp, #16]",
            "    add sp, sp, #544",
            "    ret",
            f".size {symbol}, .-{symbol}",
            f".global {symbol}_end",
            f"{symbol}_end:",
            *alias_end_lines,
            "",
            ".include \"asm/gt/experiment/forward_ntt/u01_block_first_tables.inc\"",
            "",
        ]
    )


def emit_sentinel(symbol: str) -> str:
    sentinel = f"{symbol}_abi_sentinel"
    return "\n".join(
        [
            ".text",
            ".align 2",
            "",
            ".macro LOAD_CANARY reg, imm16",
            "    movz \\reg, #\\imm16",
            "    movk \\reg, #\\imm16, lsl #16",
            "    movk \\reg, #\\imm16, lsl #32",
            "    movk \\reg, #\\imm16, lsl #48",
            ".endm",
            "",
            ".macro CHECK_X reg, imm16, bit",
            "    LOAD_CANARY x9, \\imm16",
            "    cmp \\reg, x9",
            "    mov x10, #(1 << \\bit)",
            "    csel x10, x10, xzr, ne",
            "    orr x0, x0, x10",
            ".endm",
            "",
            ".macro CHECK_D operand, imm16, bit",
            "    umov x9, \\operand",
            "    LOAD_CANARY x10, \\imm16",
            "    cmp x9, x10",
            "    mov x11, #(1 << \\bit)",
            "    csel x11, x11, xzr, ne",
            "    orr x0, x0, x11",
            ".endm",
            "",
            f".global {sentinel}",
            f".type {sentinel}, %function",
            f"{sentinel}:",
            "    stp x29, x30, [sp, #-16]!",
            "    mov x29, sp",
            "    sub sp, sp, #176",
            "",
            "    stp x19, x20, [sp, #0]",
            "    stp x21, x22, [sp, #16]",
            "    stp x23, x24, [sp, #32]",
            "    stp x25, x26, [sp, #48]",
            "    stp x27, x28, [sp, #64]",
            "    stp d8, d9, [sp, #80]",
            "    stp d10, d11, [sp, #96]",
            "    stp d12, d13, [sp, #112]",
            "    stp d14, d15, [sp, #128]",
            "    stp x0, x1, [sp, #144]",
            "    str x2, [sp, #160]",
            "",
            "    LOAD_CANARY x19, 0x1919",
            "    LOAD_CANARY x20, 0x2020",
            "    LOAD_CANARY x21, 0x2121",
            "    LOAD_CANARY x22, 0x2222",
            "    LOAD_CANARY x23, 0x2323",
            "    LOAD_CANARY x24, 0x2424",
            "    LOAD_CANARY x25, 0x2525",
            "    LOAD_CANARY x26, 0x2626",
            "    LOAD_CANARY x27, 0x2727",
            "    LOAD_CANARY x28, 0x2828",
            "",
            "    LOAD_CANARY x9, 0xd8d8",
            "    fmov d8, x9",
            "    LOAD_CANARY x9, 0xd9d9",
            "    fmov d9, x9",
            "    LOAD_CANARY x9, 0xdada",
            "    fmov d10, x9",
            "    LOAD_CANARY x9, 0xdbdb",
            "    fmov d11, x9",
            "    LOAD_CANARY x9, 0xdcdc",
            "    fmov d12, x9",
            "    LOAD_CANARY x9, 0xdddd",
            "    fmov d13, x9",
            "    LOAD_CANARY x9, 0xdede",
            "    fmov d14, x9",
            "    LOAD_CANARY x9, 0xdfdf",
            "    fmov d15, x9",
            "",
            "    ldp x0, x1, [sp, #144]",
            "    ldr x2, [sp, #160]",
            f"    bl {symbol}",
            "",
            "    mov x0, xzr",
            "    CHECK_X x19, 0x1919, 0",
            "    CHECK_X x20, 0x2020, 1",
            "    CHECK_X x21, 0x2121, 2",
            "    CHECK_X x22, 0x2222, 3",
            "    CHECK_X x23, 0x2323, 4",
            "    CHECK_X x24, 0x2424, 5",
            "    CHECK_X x25, 0x2525, 6",
            "    CHECK_X x26, 0x2626, 7",
            "    CHECK_X x27, 0x2727, 8",
            "    CHECK_X x28, 0x2828, 9",
            "    CHECK_D v8.d[0], 0xd8d8, 10",
            "    CHECK_D v9.d[0], 0xd9d9, 11",
            "    CHECK_D v10.d[0], 0xdada, 12",
            "    CHECK_D v11.d[0], 0xdbdb, 13",
            "    CHECK_D v12.d[0], 0xdcdc, 14",
            "    CHECK_D v13.d[0], 0xdddd, 15",
            "    CHECK_D v14.d[0], 0xdede, 16",
            "    CHECK_D v15.d[0], 0xdfdf, 17",
            "",
            "    ldp d14, d15, [sp, #128]",
            "    ldp d12, d13, [sp, #112]",
            "    ldp d10, d11, [sp, #96]",
            "    ldp d8, d9, [sp, #80]",
            "    ldp x27, x28, [sp, #64]",
            "    ldp x25, x26, [sp, #48]",
            "    ldp x23, x24, [sp, #32]",
            "    ldp x21, x22, [sp, #16]",
            "    ldp x19, x20, [sp, #0]",
            "    add sp, sp, #176",
            "    ldp x29, x30, [sp], #16",
            "    ret",
            "",
            f".size {sentinel}, . - {sentinel}",
            "",
        ]
    )


def emit_test_source() -> str:
    return r'''#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"

#define WORDS NTRUPLUS_N

void u01v3_block01_production_oracle(int16_t out[WORDS],
				     const int16_t input[WORDS],
				     int16_t scratch[WORDS]);
void u01v3_f01_bmin_spill_budget(int16_t out[WORDS],
				 const int16_t input[WORDS],
				 int16_t scratch[WORDS]);
void u01v3_f01_b8_spill_budget(int16_t out[WORDS],
			       const int16_t input[WORDS],
			       int16_t scratch[WORDS]);
int u01v3_f01_bmin_spill_budget_abi_sentinel(int16_t out[WORDS],
					     const int16_t input[WORDS],
					     int16_t scratch[WORDS]);
int u01v3_f01_b8_spill_budget_abi_sentinel(int16_t out[WORDS],
					   const int16_t input[WORDS],
					   int16_t scratch[WORDS]);

static uint32_t lcg_state = 0x2468ace1u;

static uint32_t lcg_next(void)
{
	lcg_state = lcg_state * 1664525u + 1013904223u;
	return lcg_state;
}

static void fill_case(int16_t input[WORDS], int case_id)
{
	const int bound = 3 * (NTRUPLUS_Q - 1);
	const int span = 2 * bound + 1;

	for (int i = 0; i < WORDS; i++) {
		switch (case_id) {
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
		}
	}
}

static int compare_out(const char *name, const int16_t want[WORDS],
		       const int16_t got[WORDS])
{
	int mismatches = 0;

	for (int i = 0; i < WORDS; i++) {
		if (want[i] != got[i]) {
			if (mismatches < 16) {
				printf("%s mismatch[%d]: want=%d got=%d\n",
				       name, i, want[i], got[i]);
			}
			mismatches++;
		}
	}
	return mismatches;
}

static int run_case(const int16_t input[WORDS], uint64_t *abi_mask)
{
	int16_t want[WORDS] __attribute__((aligned(64)));
	int16_t got_bmin[WORDS] __attribute__((aligned(64)));
	int16_t got_b8[WORDS] __attribute__((aligned(64)));
	int16_t got_sentinel[WORDS] __attribute__((aligned(64)));
	int16_t scratch_p[WORDS] __attribute__((aligned(64)));
	int16_t scratch_bmin[WORDS] __attribute__((aligned(64)));
	int16_t scratch_b8[WORDS] __attribute__((aligned(64)));
	int16_t scratch_sentinel[WORDS] __attribute__((aligned(64)));
	int mismatches = 0;

	memset(want, 0x6b, sizeof(want));
	memset(got_bmin, 0x6b, sizeof(got_bmin));
	memset(got_b8, 0x6b, sizeof(got_b8));
	memset(got_sentinel, 0x6b, sizeof(got_sentinel));
	memset(scratch_p, 0xa5, sizeof(scratch_p));
	memset(scratch_bmin, 0xa5, sizeof(scratch_bmin));
	memset(scratch_b8, 0xa5, sizeof(scratch_b8));
	memset(scratch_sentinel, 0xa5, sizeof(scratch_sentinel));

	u01v3_block01_production_oracle(want, input, scratch_p);
	u01v3_f01_bmin_spill_budget(got_bmin, input, scratch_bmin);
	u01v3_f01_b8_spill_budget(got_b8, input, scratch_b8);
	*abi_mask |= (uint64_t)u01v3_f01_bmin_spill_budget_abi_sentinel(
		got_sentinel, input, scratch_sentinel);
	mismatches += compare_out("u01v3_f01_bmin_sentinel", want, got_sentinel);

	memset(got_sentinel, 0x6b, sizeof(got_sentinel));
	memset(scratch_sentinel, 0xa5, sizeof(scratch_sentinel));
	*abi_mask |= (uint64_t)u01v3_f01_b8_spill_budget_abi_sentinel(
		got_sentinel, input, scratch_sentinel);
	mismatches += compare_out("u01v3_f01_b8_sentinel", want, got_sentinel);

	mismatches += compare_out("u01v3_f01_bmin", want, got_bmin);
	mismatches += compare_out("u01v3_f01_b8", want, got_b8);
	return mismatches;
}

int main(void)
{
	int16_t input[WORDS] __attribute__((aligned(64)));
	uint64_t abi_mask = 0;
	int mismatches = 0;

	for (int t = 0; t < 260; t++) {
		fill_case(input, t < 4 ? t : 4);
		mismatches += run_case(input, &abi_mask);
	}

	printf("u01v3_f01_spill_budget_abi_mask=0x%llx\n",
	       (unsigned long long)abi_mask);
	printf("u01v3_f01_spill_budget_mismatches=%d\n", mismatches);
	printf("mismatches = %d\n", mismatches);
	return mismatches == 0 && abi_mask == 0 ? 0 : 1;
}
'''


def main() -> int:
    phase_lines = PHASE123.read_text().splitlines()
    stage345 = {0: load_stage345_block(0), 1: load_stage345_block(1)}
    stage345_handoff = {
        0: transform_stage345_for_handoff(0, stage345[0]),
        1: transform_stage345_for_handoff(1, stage345[1]),
    }

    generated: list[Path] = []
    for key, info in FEASIBLE_VARIANTS.items():
        body_path = ROOT / f"u01v3_f01_{key}_spill_budget_allrows.sym.s"
        wrapper_path = ASM_ROOT / f"u01v3_f01_{key}_spill_budget.S"
        sentinel_path = ASM_ROOT / f"u01v3_f01_{key}_spill_budget_abi_sentinel.S"
        body = emit_body(
            info["body_label"],
            phase_lines,
            stage345_handoff[0],
            stage345_handoff[1],
        )
        body_path.write_text("\n".join(body))
        wrapper_path.write_text(
            emit_wrapper(
                info["symbol"],
                f"experiments/forward_ntt_phase123_u01/{body_path.name}",
                info["matrix_alias"],
            )
        )
        sentinel_path.write_text(emit_sentinel(info["symbol"]))
        generated.extend([body_path, wrapper_path, sentinel_path])

    metadata = {
        "candidate_family": "u01v3_onepass_f01_with_spill_budget",
        "production_default_changed": False,
        "stage12_passes": 1,
        "extra_stage12_raw_q_loads": 0,
        "duplicated_stage12_computation": False,
        "stage345_arithmetic_changed": False,
        "stage345_scatter_changed": False,
        "block1_handoff_registers": [HANDOFF[1][q] for q in range(8, 16)],
        "current_generated_producer_spills_block1_handoff": [HANDOFF[1][q] for q in range(8, 16)],
        "minimum_feasible_budget_per_row": 8,
        "feasible_variants": {
            key: {
                "symbol": info["symbol"],
                "matrix_alias": info["matrix_alias"],
                "spill_budget_per_row": info["budget"],
                "spill_count_q_stores_total": len(ROWS) * info["budget"],
                "restore_count_q_loads_total": len(ROWS) * info["budget"],
                "raw_q_reload_count": 0,
                "status": "generated_assemble_candidate",
            }
            for key, info in FEASIBLE_VARIANTS.items()
        },
        "infeasible_variants": {
            key: {
                "spill_budget_per_row": info["budget"],
                "required_spills_per_row": 8,
                "unpreserved_clobbered_block1_liveins_per_row": info["missing"],
                "status": "infeasible_under_unchanged_stage345_block0_no_raw_reload_no_duplicate_stage12",
            }
            for key, info in INFEASIBLE_VARIANTS.items()
        },
    }
    metadata_path = ROOT / "u01v3_f01_spill_budget_status.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")
    generated.append(metadata_path)

    doc_path = ROOT / "u01v3_f01_spill_budget_design.md"
    doc_path.write_text(
        """# U01v3 F01 One-Pass Spill-Budget Variants

Status: experiment-only.  Production defaults are unchanged.

Budget definition: the budget is the number of block1 handoff vectors per row
that may be preserved across the current one-pass Stage12 producer and
unchanged Stage345 block0 by spilling to stack.

The Stage345-only lower bound is smaller, because Q12 in `q9` is not written by
block0 and `q21` is not used by block0.  The current end-to-end producer still
uses `q9` and `q21` while producing later stripes, so this concrete generator
uses the conservative safe shape: spill all eight block1 handoff registers:

```text
q10 q20 q30 q24 q9 q6 q31 q23
```

Therefore the minimum feasible budget for this current generated producer is
eight vectors per row.  Bmin and B8 are concrete assembly candidates with 24
vector spills and 24 vector restores across the three rows.  They compute
Stage12 once, do not reload raw q inputs, and do not duplicate Stage12.

B2 and B4 are intentionally not emitted as performance candidates.  With only
two or four preserved block1 live-ins, unchanged Stage345 block0 would destroy
the remaining block1 handoff values before Stage345 block1.  Repairing that
would require raw q reloads, duplicate Stage12, or a Stage345 block0 rewrite,
which are outside this task's constraints.
"""
    )
    generated.append(doc_path)

    test_path = TEST_ROOT / "test_u01v3_f01_spill_budget.c"
    test_path.write_text(emit_test_source())
    generated.append(test_path)

    for path in generated:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
