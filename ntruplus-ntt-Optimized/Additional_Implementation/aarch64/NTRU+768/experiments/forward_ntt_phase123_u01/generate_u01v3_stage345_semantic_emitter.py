#!/usr/bin/env python3
"""Generate U01v3 F01 Track E semantic Stage345 emitter artifacts.

E0 is intentionally conservative: it proves the emitter shape by reproducing
the current Stage345 block0+block1 behavior before any register-allocation
rewrite is attempted.
"""

from __future__ import annotations

import json
from pathlib import Path

from generate_phase123_shared_prefix_v2 import PHASE123
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
from generate_u01v3_f01_a1_stage345_block0_preserve_block1_liveins import (
    AVAILABLE_COLORS,
    BLOCK1_RESERVED,
    emit_stage12_block01_once,
    emit_stage345_setup_from_scratchless,
    rename_stage345_block0_preserve_block1,
)
from generate_u01v3_f01_spill_budget import emit_sentinel


ROOT = Path(__file__).resolve().parent
NTRU_ROOT = ROOT.parents[1]
ASM_ROOT = NTRU_ROOT / "asm/gt/experiment"
TEST_ROOT = NTRU_ROOT / "gt_test"

E0_SYMBOL = "u01v3_stage345_semantic_e0_reproduce"
E1_SYMBOL = "u01v3_stage345_semantic_e1_preserve_liveins"
E0_ASM = ASM_ROOT / f"{E0_SYMBOL}.S"
E1_ASM = ASM_ROOT / f"{E1_SYMBOL}.S"
E0_TEST = TEST_ROOT / f"test_{E0_SYMBOL}.c"
E1_TEST = TEST_ROOT / f"test_{E1_SYMBOL}.c"
DESIGN_MD = ROOT / "u01v3_stage345_semantic_emitter_design.md"
DAG_JSON = ROOT / "u01v3_stage345_semantic_dag.json"
E1_RESULT_MD = ROOT / "u01v3_stage345_semantic_e1_result.md"

E0_VALIDATION = {
    "local_assemble": "pass, clang -target aarch64-linux-gnu",
    "pi5_correctness": "pass",
    "pi5_abi_mask": "0x0",
    "pi5_mismatches": 0,
    "pmu": "not_run",
}
E1_VALIDATION = {
    "local_assemble": "pass, clang -target aarch64-linux-gnu",
    "pi5_correctness": "fail",
    "pi5_abi_mask": "0x0",
    "pi5_mismatches": 74572,
    "pmu": "not_run_because_correctness_failed",
}


def emit_stage12_block01_to_scratch(lines: list[str], row: str) -> None:
    emit_stage12_twiddles(lines, row, "semantic E0 block0 live + block1 scratch")
    for stripe in range(8):
        q0, q8, q16, q24 = stripe, stripe + 8, stripe + 16, stripe + 24
        out0 = HANDOFF[0][q0]
        out1 = HANDOFF[1][q8]
        out0_v = out0.replace("q", "v")
        out1_v = out1.replace("q", "v")
        lines.extend(
            [
                f"    // Stage12 {row} stripe{stripe}: out0 live, out1 stored for block1.",
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
                f"    // str {out0}, [x21, #{qoff(row, q0)}] omitted: block0 live handoff Q{q0}.",
                f"    str {out1}, [x21, #{qoff(row, q8)}]    // block1 Q{q8}",
                f"    str q21, [x21, #{qoff(row, q16)}]   // block2 Q{q16}",
                f"    str q22, [x21, #{qoff(row, q24)}]   // block3 Q{q24}",
                "",
            ]
        )


def emit_e0_body(
    phase_lines: list[str],
    stage3450_handoff: list[str],
    stage3451_from_scratch: list[str],
) -> list[str]:
    lines: list[str] = [
        "    // Generated Track E E0 semantic reproduction body.",
        "    // Stage12 is computed once per row/stripe; Stage345 block0 consumes",
        "    // live out0 registers, and block1 reproduces current from-scratch",
        "    // Stage345 behavior from the Stage12 scratch image.",
        "",
    ]
    emit_phase123_shared_prefix(lines, phase_lines)
    for row in ROWS:
        emit_stage12_block01_to_scratch(lines, row)
        emit_stage345_setup(lines, row, 0, from_scratch=False)
        lines.extend(stage3450_handoff)
        lines.append("")
        emit_stage345_setup(lines, row, 1, from_scratch=True)
        lines.extend(stage3451_from_scratch)
        lines.append("")
    return lines


def emit_e1_body(
    phase_lines: list[str],
    stage3450_preserve: list[str],
    stage3451_handoff: list[str],
) -> list[str]:
    lines: list[str] = [
        "    // Generated Track E E1 preserve-liveins body.",
        "    // Stage12 produces block0 and block1 once, Stage345 block0 avoids",
        "    // q6/q9/q10/q20/q23/q24/q30/q31, and Stage345 block1 consumes",
        "    // those still-live handoff registers.",
        "",
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
    return lines


def emit_wrapper(symbol: str, body: list[str]) -> str:
    return "\n".join(
        [
            f"/* U01v3 F01 Track E E0 semantic reproduction: {symbol}. */",
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
            "    adr x23, u01_block_first_gt_ntt32_batch8_twiddle_vecs",
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
            ".include \"asm/gt/experiment/forward_ntt/u01_block_first_tables.inc\"",
            "",
        ]
    )


def emit_test_source(symbol: str) -> str:
    return rf'''#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"

#define WORDS NTRUPLUS_N

void u01v3_block01_production_oracle(int16_t out[WORDS],
				     const int16_t input[WORDS],
				     int16_t scratch[WORDS]);
void {symbol}(int16_t out[WORDS],
		 const int16_t input[WORDS],
		 int16_t scratch[WORDS]);
int {symbol}_abi_sentinel(int16_t out[WORDS],
			     const int16_t input[WORDS],
			     int16_t scratch[WORDS]);

static uint32_t lcg_state = 0xe0015e0du;

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
	int16_t got[WORDS] __attribute__((aligned(64)));
	int16_t got_sentinel[WORDS] __attribute__((aligned(64)));
	int16_t scratch_want[WORDS] __attribute__((aligned(64)));
	int16_t scratch_got[WORDS] __attribute__((aligned(64)));
	int16_t scratch_sentinel[WORDS] __attribute__((aligned(64)));
	int mismatches = 0;

	memset(want, 0x6b, sizeof(want));
	memset(got, 0x6b, sizeof(got));
	memset(got_sentinel, 0x6b, sizeof(got_sentinel));
	memset(scratch_want, 0xa5, sizeof(scratch_want));
	memset(scratch_got, 0xa5, sizeof(scratch_got));
	memset(scratch_sentinel, 0xa5, sizeof(scratch_sentinel));

	u01v3_block01_production_oracle(want, input, scratch_want);
	{symbol}(got, input, scratch_got);
	*abi_mask |= (uint64_t){symbol}_abi_sentinel(
		got_sentinel, input, scratch_sentinel);

	mismatches += compare_out("{symbol}", want, got);
	mismatches += compare_out("{symbol}_sentinel", want, got_sentinel);
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

	printf("{symbol}_abi_mask=0x%llx\n",
	       (unsigned long long)abi_mask);
	printf("{symbol}_mismatches=%d\n", mismatches);
	printf("mismatches = %d\n", mismatches);
	return mismatches == 0 && abi_mask == 0 ? 0 : 1;
}}
'''


def write_design() -> None:
    DESIGN_MD.write_text(
        """# U01v3 F01 Track E Stage345 Semantic Emitter

Status: E0 passes correctness/ABI; E1 fails correctness.  Production defaults
are unchanged.

Scope is only F01 block0+block1.  The emitter is deliberately conservative:
Stage12 block0 and block1 are computed once per row/stripe, block0 out0 values
remain live for Stage345 block0, and block1 out1 values are written to the
normal Stage12 scratch slots before current Stage345 block1 is run from
scratch.

E0 does not optimize or remap Stage345 arithmetic.  It only replaces the
current block0 Stage345 Q0..Q7 scratch loads with the established live handoff
registers.  Stage345 block1 is emitted in the current from-scratch shape to
reproduce behavior before any allocation rewrite.

The E1 gate is correctness plus ABI pass for E0.  If E0 fails, Track E stops
and no block0 allocation rewrite is attempted.

E1 is emitted only after E0 passes.  It reuses the current fixed-order SSA
allocation experiment for Stage345 block0 under Track E-owned filenames, so the
failure is isolated from shared candidates and production defaults.
"""
    )


def write_dag(
    stage3450_handoff: list[str],
    stage3451_from_scratch: list[str],
    stage3450_preserve: list[str],
    stage3451_handoff: list[str],
    allocator_report: dict[str, object],
) -> None:
    data = {
        "candidate_family": "u01v3_stage345_semantic",
        "production_default_changed": False,
        "scope": "F01 block0+block1 only",
        "e0": {
            "symbol": E0_SYMBOL,
            "stage12_passes": 1,
            "duplicate_stage12_computation": False,
            "extra_raw_q_loads": 0,
            "q_stack_spills": 0,
            "scalar_stack_temporaries": "inherits current Stage345 STACK_LOC_0 x-register temporaries",
            "stage345_block0": {
                "source": "asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S:_gt_ntt32_batch8_ct_stage345_block0_slothy_start",
                "mode": "live handoff",
                "scratch_loads_removed_for_q": list(range(0, 8)),
                "instruction_lines": len(stage3450_handoff),
            },
            "stage345_block1": {
                "source": "asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S:_gt_ntt32_batch8_ct_stage345_block1_slothy_start",
                "mode": "current from-scratch reproduction",
                "instruction_lines": len(stage3451_from_scratch),
            },
            "block0_handoff": [
                {"q_index": q, "reg": HANDOFF[0][q]} for q in range(0, 8)
            ],
            "block1_stage12_scratch": [
                {
                    "q_index": q,
                    "producer_reg": HANDOFF[1][q],
                    "scratch_offsets_by_row": {row: qoff(row, q) for row in ROWS},
                }
                for q in range(8, 16)
            ],
            "validation": {
                "assemble": E0_VALIDATION["local_assemble"],
                "correctness": E0_VALIDATION["pi5_correctness"],
                "abi": E0_VALIDATION["pi5_abi_mask"],
                "mismatches": E0_VALIDATION["pi5_mismatches"],
                "pmu": E0_VALIDATION["pmu"],
            },
        },
        "e1": {
            "symbol": E1_SYMBOL,
            "stage12_passes": 1,
            "duplicate_stage12_computation": False,
            "extra_raw_q_loads": 0,
            "q_stack_spills": 0,
            "scalar_stack_temporaries": "inherits current Stage345 STACK_LOC_0 x-register temporaries",
            "stage345_block0": {
                "source": "asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S:_gt_ntt32_batch8_ct_stage345_block0_slothy_start",
                "mode": "renamed to preserve block1 live-ins",
                "instruction_lines": len(stage3450_preserve),
                "allocator": allocator_report,
            },
            "stage345_block1": {
                "source": "asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S:_gt_ntt32_batch8_ct_stage345_block1_slothy_start",
                "mode": "live handoff",
                "instruction_lines": len(stage3451_handoff),
            },
            "block1_preserved_liveins": [f"q{r}" for r in sorted(BLOCK1_RESERVED)],
            "validation": {
                "assemble": E1_VALIDATION["local_assemble"],
                "correctness": E1_VALIDATION["pi5_correctness"],
                "abi": E1_VALIDATION["pi5_abi_mask"],
                "mismatches": E1_VALIDATION["pi5_mismatches"],
                "pmu": E1_VALIDATION["pmu"],
            },
        },
    }
    DAG_JSON.write_text(json.dumps(data, indent=2) + "\n")


def write_e1_result(allocator_report: dict[str, object]) -> None:
    E1_RESULT_MD.write_text(
        "# U01v3 F01 Track E E1 Preserve Live-ins\n\n"
        "Status: correctness failed; PMU not run.  Production default is unchanged.\n\n"
        "E1 computes Stage12 block0 and block1 once per row, keeps both block0 "
        "and block1 handoff values live, renames Stage345 block0 away from the "
        "block1 live-in registers, then runs Stage345 block1 from the live "
        "block1 handoff registers.\n\n"
        "Preserved block1 registers: "
        + ", ".join(f"`q{r}`" for r in sorted(BLOCK1_RESERVED))
        + ".\n\n"
        "Stage345 block0 reserved registers written: "
        + (", ".join(f"`{reg}`" for reg in allocator_report["reserved_written"]) or "none")
        + ".\n\n"
        f"Allocator peak non-reserved live values: {allocator_report['max_nonreserved_live_values']} "
        f"of {len(AVAILABLE_COLORS)} available non-reserved registers.\n\n"
        "Validation:\n\n"
        "```text\n"
        f"local assemble: {E1_VALIDATION['local_assemble']}\n"
        f"Pi5 correctness: {E1_VALIDATION['pi5_correctness']}\n"
        f"Pi5 mismatches: {E1_VALIDATION['pi5_mismatches']}\n"
        f"Pi5 ABI mask: {E1_VALIDATION['pi5_abi_mask']}\n"
        f"PMU: {E1_VALIDATION['pmu']}\n"
        "```\n"
    )


def main() -> int:
    phase_lines = PHASE123.read_text().splitlines()
    stage3450 = load_stage345_block(0)
    stage3451 = load_stage345_block(1)
    stage3450_handoff = transform_stage345_for_handoff(0, stage3450)
    stage3450_preserve, allocator_report = rename_stage345_block0_preserve_block1(stage3450)
    stage3451_handoff = transform_stage345_for_handoff(1, stage3451)

    e0_body = emit_e0_body(phase_lines, stage3450_handoff, stage3451)
    E0_ASM.write_text(emit_wrapper(E0_SYMBOL, e0_body))
    (ASM_ROOT / f"{E0_SYMBOL}_abi_sentinel.S").write_text(emit_sentinel(E0_SYMBOL))
    E0_TEST.write_text(emit_test_source(E0_SYMBOL))

    e1_body = emit_e1_body(phase_lines, stage3450_preserve, stage3451_handoff)
    E1_ASM.write_text(emit_wrapper(E1_SYMBOL, e1_body))
    (ASM_ROOT / f"{E1_SYMBOL}_abi_sentinel.S").write_text(emit_sentinel(E1_SYMBOL))
    E1_TEST.write_text(emit_test_source(E1_SYMBOL))
    write_e1_result(allocator_report)

    write_design()
    write_dag(stage3450_handoff, stage3451, stage3450_preserve, stage3451_handoff, allocator_report)

    for path in (
        DESIGN_MD,
        DAG_JSON,
        E1_RESULT_MD,
        Path(__file__),
        E0_ASM,
        ASM_ROOT / f"{E0_SYMBOL}_abi_sentinel.S",
        E0_TEST,
        E1_ASM,
        ASM_ROOT / f"{E1_SYMBOL}_abi_sentinel.S",
        E1_TEST,
    ):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
