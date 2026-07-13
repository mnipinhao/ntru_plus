#!/usr/bin/env python3
"""Generate Track E correctness-localization and E2 parking-bridge artifacts.

This is experiment-only glue.  It does not change production defaults and does
not introduce a performance candidate.  The point is to separate three facts:

1. E1's renamed Stage345 block0 is currently wrong.
2. The Stage12 one-pass block0/block1 producer can still be made correct if
   block1 values are parked across unchanged block0.
3. The next no-spill allocator needs an SSA value contract, not a clobber list.
"""

from __future__ import annotations

import json
from pathlib import Path

from generate_phase123_shared_prefix_v2 import PHASE123
from generate_phase123_shared_prefix_v3_block1_block01_fuse import (
    HANDOFF,
    ROWS,
    emit_phase123_shared_prefix,
    emit_stage345_setup,
    load_stage345_block,
    qoff,
    transform_stage345_for_handoff,
)
from generate_u01v3_f01_a1_stage345_block0_preserve_block1_liveins import (
    AVAILABLE_COLORS,
    BLOCK1_RESERVED,
    collect_stage345_ssa,
    intervals,
    rename_stage345_block0_preserve_block1,
    emit_stage12_block01_once,
    emit_stage345_setup_from_scratchless,
)
from generate_u01v3_f01_spill_budget import (
    SPILL_BASE,
    SPILL_STRIDE_PER_ROW,
    emit_restore_block1,
    emit_sentinel,
    emit_stage12_block01_onepass,
)
from generate_u01v3_stage345_semantic_emitter import emit_stage12_block01_to_scratch


ROOT = Path(__file__).resolve().parent
NTRU_ROOT = ROOT.parents[1]
ASM_ROOT = NTRU_ROOT / "asm/gt/experiment"
TEST_ROOT = NTRU_ROOT / "gt_test"

E0_DEBUG_SYMBOL = "u01v3_stage345_semantic_e0_debug"
E1_DEBUG_SYMBOL = "u01v3_stage345_semantic_e1_debug"
E2_SYMBOL = "u01v3_stage345_semantic_e2_parking_bridge"

DEBUG_STRIDE = 640
DEBUG_QREG_BYTES = 32 * 16
DEBUG_MEM_SLOTS = list(range(8, 16))
CHECKPOINTS = (
    ("stage3_exit", 64),
    ("stage4_exit", 109),
    ("stage5_exit", 148),
    ("block0_exit", 10_000),
)

CONTRACT_JSON = ROOT / "stage345_block0_contract.json"
LOCALIZE_MD = ROOT / "u01v3_stage345_semantic_e1_localization.md"
E2_RESULT_MD = ROOT / "u01v3_stage345_semantic_e2_result.md"


def spill_offset(row: str, stripe: int) -> int:
    return SPILL_BASE + ROWS.index(row) * SPILL_STRIDE_PER_ROW + stripe * 16


def is_executable(line: str) -> bool:
    code = line.split("//", 1)[0].strip()
    return bool(code) and not code.endswith(":")


def checkpoint_offset(row_index: int, checkpoint_index: int) -> int:
    return (row_index * len(CHECKPOINTS) + checkpoint_index) * DEBUG_STRIDE


def emit_checkpoint(lines: list[str], row: str, row_index: int, checkpoint_index: int) -> None:
    name = CHECKPOINTS[checkpoint_index][0]
    base = checkpoint_offset(row_index, checkpoint_index)
    lines.append(f"    // DEBUG checkpoint {row}:{name}: dump q0..q31 and block1 scratch slots.")
    for reg in range(32):
        lines.append(f"    str q{reg}, [x24, #{base + reg * 16}]")
    lines.append("    str q25, [sp, #176]                 // preserve debug temp")
    mem_base = base + DEBUG_QREG_BYTES
    for slot, q_index in enumerate(DEBUG_MEM_SLOTS):
        lines.append(f"    ldr q25, [x21, #{qoff(row, q_index)}]")
        lines.append(f"    str q25, [x24, #{mem_base + slot * 16}]    // scratch Q{q_index}")
    lines.append("    ldr q25, [sp, #176]")
    lines.append("")


def instrument_block0(lines_in: list[str], row: str, row_index: int) -> list[str]:
    out: list[str] = []
    executable_count = 0
    next_checkpoint = 0

    for line in lines_in:
        out.append(line)
        if is_executable(line):
            executable_count += 1
            if (
                next_checkpoint < len(CHECKPOINTS) - 1
                and executable_count >= CHECKPOINTS[next_checkpoint][1]
            ):
                emit_checkpoint(out, row, row_index, next_checkpoint)
                next_checkpoint += 1

    while next_checkpoint < len(CHECKPOINTS):
        emit_checkpoint(out, row, row_index, next_checkpoint)
        next_checkpoint += 1
    return out


def emit_debug_body(
    e1: bool,
    phase_lines: list[str],
    stage3450_handoff: list[str],
    stage3450_preserve: list[str],
    stage3451: list[str],
    stage3451_handoff: list[str],
) -> list[str]:
    lines: list[str] = [
        "    // Generated Track E localization debug body.",
        "    // x24 points at debug buffer. Each checkpoint stores q0..q31 plus",
        "    // block1 scratch slots Q8..Q15. The Stage345 block0 cutpoints are",
        "    // source-order windows used only for localization.",
        "",
    ]
    emit_phase123_shared_prefix(lines, phase_lines)
    for row_index, row in enumerate(ROWS):
        if e1:
            emit_stage12_block01_once(lines, row)
            emit_stage345_setup_from_scratchless(lines, row, 0)
            lines.extend(instrument_block0(stage3450_preserve, row, row_index))
            lines.append("")
            emit_stage345_setup_from_scratchless(lines, row, 1)
            lines.extend(stage3451_handoff)
        else:
            emit_stage12_block01_to_scratch(lines, row)
            emit_stage345_setup(lines, row, 0, from_scratch=False)
            lines.extend(instrument_block0(stage3450_handoff, row, row_index))
            lines.append("")
            emit_stage345_setup(lines, row, 1, from_scratch=True)
            lines.extend(stage3451)
        lines.append("")
    return lines


def emit_e2_body(
    phase_lines: list[str],
    stage3450_handoff: list[str],
    stage3451_handoff: list[str],
) -> list[str]:
    lines: list[str] = [
        "    // Generated Track E E2 parking bridge.",
        "    // Stage12 produces block0 and block1 once. Block1 handoff values are",
        "    // parked in this wrapper frame across unchanged Stage345 block0, then",
        "    // restored before Stage345 block1 consumes the live-handoff contract.",
        "",
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
    return lines


def emit_wrapper(symbol: str, body: list[str], debug: bool, frame_size: int) -> str:
    save_x24 = debug
    return "\n".join(
        [
            f"/* U01v3 Track E experiment-only wrapper: {symbol}. */",
            "",
            ".text",
            ".align 4",
            ".equ STACK_LOC_0, 0",
            "",
            f".global {symbol}",
            f".type {symbol}, %function",
            f"{symbol}:",
            f"    sub sp, sp, #{frame_size}",
            "    stp x19, x20, [sp, #16]",
            "    stp x21, x22, [sp, #32]",
            "    str x23, [sp, #48]",
            "    stp d8, d9, [sp, #64]",
            "    stp d10, d11, [sp, #80]",
            "    stp d12, d13, [sp, #96]",
            "    stp d14, d15, [sp, #112]",
            *(
                [
                    "    str x24, [sp, #144]",
                    "    str x25, [sp, #152]",
                ]
                if save_x24
                else []
            ),
            "",
            "    mov x19, x0",
            "    mov x20, x1",
            "    mov x21, x2",
            *(["    mov x24, x3"] if save_x24 else []),
            "",
            "    adr x2, u01_block_first_zetas",
            "    ldr q0, [x2]",
            "    adr x22, u01_block_first_twist_table",
            "    adr x23, u01_block_first_ntt32_twiddle_vecs",
            "",
            *body,
            *(
                [
                    "    ldr x25, [sp, #152]",
                    "    ldr x24, [sp, #144]",
                ]
                if save_x24
                else []
            ),
            "    ldp d14, d15, [sp, #112]",
            "    ldp d12, d13, [sp, #96]",
            "    ldp d10, d11, [sp, #80]",
            "    ldp d8, d9, [sp, #64]",
            "    ldr x23, [sp, #48]",
            "    ldp x21, x22, [sp, #32]",
            "    ldp x19, x20, [sp, #16]",
            f"    add sp, sp, #{frame_size}",
            "    ret",
            f".size {symbol}, .-{symbol}",
            f".global {symbol}_end",
            f"{symbol}_end:",
            "",
            ".include \"asm/gt/experiment/forward_ntt/u01_block_first_tables.inc\"",
            "",
        ]
    )


def emit_e2_test() -> str:
    return rf'''#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"

#define WORDS NTRUPLUS_N

void u01v3_block01_production_oracle(int16_t out[WORDS],
				     const int16_t input[WORDS],
				     int16_t scratch[WORDS]);
void {E2_SYMBOL}(int16_t out[WORDS],
		 const int16_t input[WORDS],
		 int16_t scratch[WORDS]);
int {E2_SYMBOL}_abi_sentinel(int16_t out[WORDS],
			     const int16_t input[WORDS],
			     int16_t scratch[WORDS]);

static uint32_t lcg_state = 0xe2001001u;

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
	{E2_SYMBOL}(got, input, scratch_got);
	*abi_mask |= (uint64_t){E2_SYMBOL}_abi_sentinel(
		got_sentinel, input, scratch_sentinel);

	mismatches += compare_out("{E2_SYMBOL}", want, got);
	mismatches += compare_out("{E2_SYMBOL}_sentinel", want, got_sentinel);
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

	printf("{E2_SYMBOL}_abi_mask=0x%llx\n", (unsigned long long)abi_mask);
	printf("{E2_SYMBOL}_mismatches=%d\n", mismatches);
	printf("mismatches = %d\n", mismatches);
	return mismatches == 0 && abi_mask == 0 ? 0 : 1;
}}
'''


def emit_localize_test() -> str:
    cp_total = len(ROWS) * len(CHECKPOINTS)
    words_per_checkpoint = DEBUG_STRIDE // 2
    return rf'''#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"

#define WORDS NTRUPLUS_N
#define CP_ROWS 3
#define CP_PER_ROW {len(CHECKPOINTS)}
#define CP_TOTAL {cp_total}
#define CP_WORDS {words_per_checkpoint}
#define QREG_WORDS 8
#define QREG_COUNT 32
#define MEM_BASE_WORDS {DEBUG_QREG_BYTES // 2}
#define MEM_SLOTS {len(DEBUG_MEM_SLOTS)}

void {E0_DEBUG_SYMBOL}(int16_t out[WORDS], const int16_t input[WORDS],
		       int16_t scratch[WORDS], int16_t debug[CP_TOTAL][CP_WORDS]);
void {E1_DEBUG_SYMBOL}(int16_t out[WORDS], const int16_t input[WORDS],
		       int16_t scratch[WORDS], int16_t debug[CP_TOTAL][CP_WORDS]);

static const char *checkpoint_names[CP_PER_ROW] = {{
	"stage3_exit", "stage4_exit", "stage5_exit", "block0_exit"
}};

static uint32_t lcg_state = 0xe10db6d5u;

static uint32_t lcg_next(void)
{{
	lcg_state = lcg_state * 1664525u + 1013904223u;
	return lcg_state;
}}

static void fill_randomish(int16_t input[WORDS])
{{
	const int bound = 3 * (NTRUPLUS_Q - 1);
	const int span = 2 * bound + 1;

	for (int i = 0; i < WORDS; i++) {{
		if (i & 1)
			input[i] = (int16_t)((int)(lcg_next() % (uint32_t)span) - bound);
		else
			input[i] = (int16_t)(NTRUPLUS_Q - 1 - (i % 31));
	}}
}}

static int find_first_debug_diff(const int16_t e0[CP_TOTAL][CP_WORDS],
				 const int16_t e1[CP_TOTAL][CP_WORDS])
{{
	for (int cp = 0; cp < CP_TOTAL; cp++) {{
		const int row = cp / CP_PER_ROW;
		const int cpi = cp % CP_PER_ROW;

		for (int reg = 0; reg < QREG_COUNT; reg++) {{
			for (int lane = 0; lane < QREG_WORDS; lane++) {{
				const int idx = reg * QREG_WORDS + lane;
				if (e0[cp][idx] != e1[cp][idx]) {{
					printf("first_debug_diff row%d %s q%d lane%d: e0=%d e1=%d\n",
					       row, checkpoint_names[cpi], reg, lane,
					       e0[cp][idx], e1[cp][idx]);
					return 1;
				}}
			}}
		}}

		for (int slot = 0; slot < MEM_SLOTS; slot++) {{
			for (int lane = 0; lane < QREG_WORDS; lane++) {{
				const int idx = MEM_BASE_WORDS + slot * QREG_WORDS + lane;
				if (e0[cp][idx] != e1[cp][idx]) {{
					printf("first_mem_diff row%d %s scratch_Q%d lane%d: e0=%d e1=%d\n",
					       row, checkpoint_names[cpi], {DEBUG_MEM_SLOTS[0]} + slot, lane,
					       e0[cp][idx], e1[cp][idx]);
					return 1;
				}}
			}}
		}}
	}}
	printf("debug checkpoints match\n");
	return 0;
}}

static int compare_out(const int16_t e0[WORDS], const int16_t e1[WORDS])
{{
	int mismatches = 0;

	for (int i = 0; i < WORDS; i++) {{
		if (e0[i] != e1[i]) {{
			if (mismatches < 16)
				printf("final mismatch[%d]: e0=%d e1=%d\n", i, e0[i], e1[i]);
			mismatches++;
		}}
	}}
	return mismatches;
}}

int main(void)
{{
	int16_t input[WORDS] __attribute__((aligned(64)));
	int16_t out_e0[WORDS] __attribute__((aligned(64)));
	int16_t out_e1[WORDS] __attribute__((aligned(64)));
	int16_t scratch_e0[WORDS] __attribute__((aligned(64)));
	int16_t scratch_e1[WORDS] __attribute__((aligned(64)));
	int16_t debug_e0[CP_TOTAL][CP_WORDS] __attribute__((aligned(64)));
	int16_t debug_e1[CP_TOTAL][CP_WORDS] __attribute__((aligned(64)));

	memset(out_e0, 0x6b, sizeof(out_e0));
	memset(out_e1, 0x6b, sizeof(out_e1));
	memset(scratch_e0, 0xa5, sizeof(scratch_e0));
	memset(scratch_e1, 0xa5, sizeof(scratch_e1));
	memset(debug_e0, 0xcc, sizeof(debug_e0));
	memset(debug_e1, 0xdd, sizeof(debug_e1));
	fill_randomish(input);

	{E0_DEBUG_SYMBOL}(out_e0, input, scratch_e0, debug_e0);
	{E1_DEBUG_SYMBOL}(out_e1, input, scratch_e1, debug_e1);

	const int debug_diff = find_first_debug_diff(debug_e0, debug_e1);
	const int final_mismatches = compare_out(out_e0, out_e1);

	printf("u01v3_stage345_semantic_e1_localize_debug_diff=%d\n", debug_diff);
	printf("u01v3_stage345_semantic_e1_localize_final_mismatches=%d\n", final_mismatches);
	return final_mismatches == 0 ? 0 : 1;
}}
'''


def contract_json(allocator_report: dict[str, object]) -> dict[str, object]:
    stage3450 = load_stage345_block(0)
    ops, defs = collect_stage345_ssa(stage3450)
    ivals = intervals(defs)

    values = []
    for vid, data in sorted(defs.items(), key=lambda item: (int(item[1]["def"]), item[0])):
        fixed = data.get("fixed")
        if isinstance(fixed, tuple):
            fixed_repr: object = list(fixed)
        else:
            fixed_repr = fixed
        values.append(
            {
                "logical_value": vid,
                "lane_shape": "8h",
                "def_op": data["def"],
                "uses": data["uses"],
                "last_use": max(data["uses"]) if data["uses"] else None,
                "fixed": fixed_repr,
                "interval": list(ivals[vid]) if vid in ivals else None,
            }
        )

    classified_regs = {}
    block1_by_reg = {int(reg[1:]): q for q, reg in HANDOFF[1].items()}
    for reg in (6, 9, 10, 20, 21, 23, 24, 30, 31):
        entry: dict[str, object] = {"register": f"q{reg}"}
        if reg in block1_by_reg:
            q_index = block1_by_reg[reg]
            entry.update(
                {
                    "class": "block1_live_in",
                    "semantic": f"B1_Q{q_index}",
                    "must_survive_block0_until": "Stage345 block1 handoff load-replacement site",
                    "e2_action": "park_to_stack_and_restore",
                    "spill_offsets_by_row": {
                        row: spill_offset(row, q_index - 8) for row in ROWS
                    },
                }
            )
        elif reg == 21:
            entry.update(
                {
                    "class": "safe_temp_pool",
                    "semantic": "not a block1 live-in in current handoff contract",
                    "e2_action": "available for Stage12/block0 temporaries; not trusted as the only parking register",
                }
            )
        classified_regs[f"q{reg}"] = entry

    return {
        "artifact": "stage345_block0_contract",
        "production_default_changed": False,
        "scope": "Track E F01 block0+block1 only",
        "source": "asm/slothy/production/my_32ntt.opt.s:_ntt32_stage345_block0_slothy_start",
        "warning": "E1 failed correctness; this contract is the required input for the next no-spill allocator.",
        "stage345_block0_ssa": {
            "operation_count_including_comments": len(ops),
            "logical_values": values,
            "destructive_ops_modeled": [
                "mls dest is both read and written; new SSA value fixed to same physical color as old dest",
                "scalar stack temporaries at STACK_LOC_0 are not vector values",
                "str reads vector low half; ext produces high-half store source",
            ],
        },
        "classifications": classified_regs,
        "block1_consumer_expectations": [
            {
                "q_index": q,
                "stage12_handoff_reg": HANDOFF[1][q],
                "stage345_expected_load_dest": {
                    8: "q10",
                    9: "q20",
                    10: "q30",
                    11: "q1",
                    12: "q9",
                    13: "q6",
                    14: "q31",
                    15: "q23",
                }[q],
                "bridge_required": HANDOFF[1][q]
                != {
                    8: "q10",
                    9: "q20",
                    10: "q30",
                    11: "q1",
                    12: "q9",
                    13: "q6",
                    14: "q31",
                    15: "q23",
                }[q],
            }
            for q in range(8, 16)
        ],
        "e1_failed_allocator": allocator_report,
        "e2_parking_bridge": {
            "symbol": E2_SYMBOL,
            "stage12_passes": 1,
            "duplicate_stage12_computation": False,
            "extra_raw_q_loads": 0,
            "parked_values": [f"B1_Q{q}" for q in range(8, 16)],
            "q_spills": 24,
            "q_restores": 24,
            "purpose": "correctness proof point, not a performance candidate",
            "validation": {
                "local_assemble": "pass, clang -target aarch64-linux-gnu",
                "pi5_correctness": "pass",
                "pi5_mismatches": 0,
                "pi5_abi_mask": "0x0",
                "pmu": "not_run_by_rule",
            },
        },
    }


def write_reports(allocator_report: dict[str, object]) -> None:
    LOCALIZE_MD.write_text(
        "# U01v3 Track E E1 Differential Localization\n\n"
        "Status: harness generated and run on Pi5. Production default is unchanged.\n\n"
        "The localization harness compares `E0 semantic reproduction` with "
        "`E1 preserve-liveins` and records four source-order Stage345 block0 "
        "checkpoints per row: Stage3 exit, Stage4 exit, Stage5 exit, and "
        "block0 exit. Each checkpoint dumps `q0..q31` plus block1 scratch "
        "slots `Q8..Q15`.\n\n"
        "Important caveat: E1 intentionally renames physical registers, so the "
        "first raw q-register difference is not automatically the semantic bug. "
        "It is a locator. The decisive correctness signal remains the final "
        "block0/block1 output mismatch; the contract JSON maps which registers "
        "are live-ins, temps, live-outs, or parked values.\n\n"
        "Observed Pi5 localization run:\n\n"
        "```text\n"
        "first_debug_diff row0 stage3_exit q1 lane0: e0=0 e1=911\n"
        "u01v3_stage345_semantic_e1_localize_debug_diff=1\n"
        "u01v3_stage345_semantic_e1_localize_final_mismatches=144\n"
        "```\n"
    )
    E2_RESULT_MD.write_text(
        "# U01v3 Track E E2 Parking Bridge\n\n"
        "Status: Pi5 correctness and ABI pass. PMU intentionally not run in this round.\n\n"
        "E2 is deliberately conservative. It keeps the one-pass Stage12 "
        "block0/block1 producer, but parks all block1 live-ins to the wrapper "
        "frame before running unchanged Stage345 block0. It then restores those "
        "values and runs Stage345 block1 through the live-handoff contract.\n\n"
        "This is not a performance candidate. It is a correctness proof point "
        "that separates Stage12/block1 handoff correctness from the failed E1 "
        "Stage345 block0 SSA allocator.\n\n"
        "Parking plan:\n\n"
        "```text\n"
        "q spills:    24  (8 block1 vectors * 3 rows)\n"
        "q restores:  24\n"
        "raw q reloads: 0\n"
        "duplicate Stage12: no\n"
        "Slothy: no\n"
        "```\n\n"
        "Validation:\n\n"
        "```text\n"
        "local assemble: pass, clang -target aarch64-linux-gnu\n"
        "Pi5 correctness: pass\n"
        "Pi5 mismatches: 0\n"
        "Pi5 ABI mask: 0x0\n"
        "PMU: not run by rule\n"
        "```\n\n"
        "E1 allocator summary retained for comparison:\n\n"
        "```text\n"
        f"reserved_written: {allocator_report['reserved_written']}\n"
        f"max_nonreserved_live_values: {allocator_report['max_nonreserved_live_values']}\n"
        "```\n"
    )


def main() -> int:
    phase_lines = PHASE123.read_text().splitlines()
    stage3450 = load_stage345_block(0)
    stage3451 = load_stage345_block(1)
    stage3450_handoff = transform_stage345_for_handoff(0, stage3450)
    stage3450_preserve, allocator_report = rename_stage345_block0_preserve_block1(stage3450)
    stage3451_handoff = transform_stage345_for_handoff(1, stage3451)

    debug_e0 = emit_debug_body(False, phase_lines, stage3450_handoff, stage3450_preserve, stage3451, stage3451_handoff)
    debug_e1 = emit_debug_body(True, phase_lines, stage3450_handoff, stage3450_preserve, stage3451, stage3451_handoff)
    e2_body = emit_e2_body(phase_lines, stage3450_handoff, stage3451_handoff)

    (ASM_ROOT / f"{E0_DEBUG_SYMBOL}.S").write_text(emit_wrapper(E0_DEBUG_SYMBOL, debug_e0, True, 224))
    (ASM_ROOT / f"{E1_DEBUG_SYMBOL}.S").write_text(emit_wrapper(E1_DEBUG_SYMBOL, debug_e1, True, 224))
    (ASM_ROOT / f"{E2_SYMBOL}.S").write_text(emit_wrapper(E2_SYMBOL, e2_body, False, 544))
    (ASM_ROOT / f"{E2_SYMBOL}_abi_sentinel.S").write_text(emit_sentinel(E2_SYMBOL))

    (TEST_ROOT / "test_u01v3_stage345_semantic_e1_localize.c").write_text(emit_localize_test())
    (TEST_ROOT / f"test_{E2_SYMBOL}.c").write_text(emit_e2_test())

    CONTRACT_JSON.write_text(json.dumps(contract_json(allocator_report), indent=2) + "\n")
    write_reports(allocator_report)

    for path in (
        ASM_ROOT / f"{E0_DEBUG_SYMBOL}.S",
        ASM_ROOT / f"{E1_DEBUG_SYMBOL}.S",
        ASM_ROOT / f"{E2_SYMBOL}.S",
        ASM_ROOT / f"{E2_SYMBOL}_abi_sentinel.S",
        TEST_ROOT / "test_u01v3_stage345_semantic_e1_localize.c",
        TEST_ROOT / f"test_{E2_SYMBOL}.c",
        CONTRACT_JSON,
        LOCALIZE_MD,
        E2_RESULT_MD,
    ):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
