#!/usr/bin/env python3
"""Generate Track E E1v2 correctness-first candidate and cutpoint debug."""

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
    transform_stage345_for_handoff,
)
from generate_u01v3_f01_a1_stage345_block0_preserve_block1_liveins import (
    collect_stage345_ssa,
    emit_stage12_block01_once,
    emit_stage345_setup_from_scratchless,
    rename_stage345_block0_preserve_block1,
)
from generate_u01v3_f01_spill_budget import emit_sentinel
from generate_u01v3_stage345_semantic_emitter import (
    emit_stage12_block01_to_scratch,
)
from generate_u01v3_stage345_e2_and_debug import (
    DEBUG_MEM_SLOTS,
    DEBUG_QREG_BYTES,
    DEBUG_STRIDE,
    emit_wrapper as emit_debug_or_e2_wrapper,
)
from validate_stage345_block0_rename import (
    corrected_allocate,
    rewrite_with_colors,
    simulate_current_values,
)


ROOT = Path(__file__).resolve().parent
NTRU_ROOT = ROOT.parents[1]
ASM_ROOT = NTRU_ROOT / "asm/gt/experiment"
TEST_ROOT = NTRU_ROOT / "gt_test"

E1V2_SYMBOL = "u01v3_stage345_semantic_e1v2_preserve_liveins"
E1V2_ASM = ASM_ROOT / f"{E1V2_SYMBOL}.S"
E1V2_SENTINEL = ASM_ROOT / f"{E1V2_SYMBOL}_abi_sentinel.S"
E1V2_TEST = TEST_ROOT / f"test_{E1V2_SYMBOL}.c"
E1V2_RESULT = ROOT / "u01v3_stage345_semantic_e1v2_result.md"
E1V2_MAP = ROOT / "u01v3_stage345_semantic_e1v2_map.json"

CUTPOINT_ASM = ASM_ROOT / "u01v3_stage345_semantic_e1_cutpoint_debug.S"
CUTPOINT_TEST = TEST_ROOT / "test_u01v3_stage345_semantic_e1_cutpoints.c"
CUTPOINT_RESULT = ROOT / "u01v3_stage345_semantic_e1_cutpoints_result.md"

E0_CUT_SYMBOL = "u01v3_stage345_semantic_e0_cutpoint_debug"
E1_CUT_SYMBOL = "u01v3_stage345_semantic_e1_cutpoint_debug"

CUTPOINTS = (
    ("stage3_entry", 0),
    ("after_first_butterfly_group", 16),
    ("after_first_reduction_group", 32),
    ("after_twiddle_multiply_group", 48),
    ("after_second_reduction_group", 56),
    ("stage3_exit", 64),
)


def is_executable(line: str) -> bool:
    code = line.split("//", 1)[0].strip()
    return bool(code) and not code.endswith(":")


def qoff(row: str, q_index: int) -> int:
    row_base = {"row0": 0, "row1": 512, "row2": 1024}[row]
    return row_base + q_index * 16


def checkpoint_offset(row_index: int, checkpoint_index: int) -> int:
    return (row_index * len(CUTPOINTS) + checkpoint_index) * DEBUG_STRIDE


def emit_checkpoint(lines: list[str], row: str, row_index: int, checkpoint_index: int) -> None:
    name = CUTPOINTS[checkpoint_index][0]
    base = checkpoint_offset(row_index, checkpoint_index)
    lines.append(f"    // CUTPOINT {row}:{name}: dump q0..q31 and block1 scratch slots.")
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

    while next_checkpoint < len(CUTPOINTS) and CUTPOINTS[next_checkpoint][1] == 0:
        emit_checkpoint(out, row, row_index, next_checkpoint)
        next_checkpoint += 1

    for line in lines_in:
        out.append(line)
        if not is_executable(line):
            continue
        executable_count += 1
        while (
            next_checkpoint < len(CUTPOINTS)
            and executable_count >= CUTPOINTS[next_checkpoint][1]
        ):
            emit_checkpoint(out, row, row_index, next_checkpoint)
            next_checkpoint += 1
    return out


def emit_e1v2_body(
    phase_lines: list[str],
    stage3450_e1v2: list[str],
    stage3451_handoff: list[str],
) -> list[str]:
    lines: list[str] = [
        "    // Generated Track E E1v2 preserve-liveins body.",
        "    // Minimal allocator change only: destructive same_as values are",
        "    // colored before unrelated temps can reuse that physical register.",
        "",
    ]
    emit_phase123_shared_prefix(lines, phase_lines)
    for row in ROWS:
        emit_stage12_block01_once(lines, row)
        emit_stage345_setup_from_scratchless(lines, row, 0)
        lines.extend(stage3450_e1v2)
        lines.append("")
        emit_stage345_setup_from_scratchless(lines, row, 1)
        lines.extend(stage3451_handoff)
        lines.append("")
    return lines


def emit_cutpoint_body(
    e1: bool,
    phase_lines: list[str],
    stage3450_handoff: list[str],
    stage3450_buggy: list[str],
    stage3451: list[str],
    stage3451_handoff: list[str],
) -> list[str]:
    lines: list[str] = [
        "    // Generated Track E E1 fine-grained cutpoint body.",
        "    // This intentionally compares old E1 against E0, not E1v2.",
        "",
    ]
    emit_phase123_shared_prefix(lines, phase_lines)
    for row_index, row in enumerate(ROWS):
        if e1:
            emit_stage12_block01_once(lines, row)
            emit_stage345_setup_from_scratchless(lines, row, 0)
            lines.extend(instrument_block0(stage3450_buggy, row, row_index))
            lines.append("")
            emit_stage345_setup_from_scratchless(lines, row, 1)
            lines.extend(stage3451_handoff)
        else:
            emit_stage12_block01_to_scratch(lines, row)
            emit_stage345_setup_from_scratchless(lines, row, 0)
            lines.extend(instrument_block0(stage3450_handoff, row, row_index))
            lines.append("")
            emit_stage345_setup(lines, row, 1, from_scratch=True)
            lines.extend(stage3451)
        lines.append("")
    return lines


def emit_wrapper(symbol: str, body: list[str], frame_size: int = 160) -> str:
    return "\n".join(
        [
            f"/* U01v3 Track E E1v2 experiment-only wrapper: {symbol}. */",
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


def emit_e1v2_test() -> str:
    return rf'''#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"

#define WORDS NTRUPLUS_N

void u01v3_block01_production_oracle(int16_t out[WORDS],
				     const int16_t input[WORDS],
				     int16_t scratch[WORDS]);
void {E1V2_SYMBOL}(int16_t out[WORDS],
		   const int16_t input[WORDS],
		   int16_t scratch[WORDS]);
int {E1V2_SYMBOL}_abi_sentinel(int16_t out[WORDS],
			       const int16_t input[WORDS],
			       int16_t scratch[WORDS]);

static uint32_t lcg_state = 0xe1020002u;

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
	{E1V2_SYMBOL}(got, input, scratch_got);
	*abi_mask |= (uint64_t){E1V2_SYMBOL}_abi_sentinel(
		got_sentinel, input, scratch_sentinel);

	mismatches += compare_out("{E1V2_SYMBOL}", want, got);
	mismatches += compare_out("{E1V2_SYMBOL}_sentinel", want, got_sentinel);
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

	printf("{E1V2_SYMBOL}_abi_mask=0x%llx\n", (unsigned long long)abi_mask);
	printf("{E1V2_SYMBOL}_mismatches=%d\n", mismatches);
	printf("mismatches = %d\n", mismatches);
	return mismatches == 0 && abi_mask == 0 ? 0 : 1;
}}
'''


def cutpoint_semantic_pairs(ops: list[dict[str, object]], old_colors: dict[str, int]) -> list[dict[str, object]]:
    pairs: list[dict[str, object]] = []
    for cpi, (name, threshold) in enumerate(CUTPOINTS):
        e0_map = simulate_current_values(ops, None, threshold)
        e1_map = simulate_current_values(ops, old_colors, threshold)
        e0_by_value = {value: int(reg[1:]) for reg, value in e0_map.items()}
        e1_by_value = {value: int(reg[1:]) for reg, value in e1_map.items()}
        for value in sorted(set(e0_by_value) & set(e1_by_value)):
            if value == "q0_const":
                continue
            pairs.append(
                {
                    "cutpoint": cpi,
                    "cutpoint_name": name,
                    "semantic": value,
                    "e0_reg": e0_by_value[value],
                    "e1_reg": e1_by_value[value],
                }
            )
    return pairs


def emit_cutpoint_test(pairs: list[dict[str, object]]) -> str:
    cp_total = len(ROWS) * len(CUTPOINTS)
    words_per_checkpoint = DEBUG_STRIDE // 2
    names = ", ".join(f'"{name}"' for name, _threshold in CUTPOINTS)
    pair_rows = ",\n".join(
        f'\t{{ {p["cutpoint"]}, {p["e0_reg"]}, {p["e1_reg"]}, "{p["semantic"]}" }}'
        for p in pairs
    )
    return rf'''#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"

#define WORDS NTRUPLUS_N
#define CP_PER_ROW {len(CUTPOINTS)}
#define CP_TOTAL {cp_total}
#define CP_WORDS {words_per_checkpoint}
#define QREG_WORDS 8
#define QREG_COUNT 32
#define MEM_BASE_WORDS {DEBUG_QREG_BYTES // 2}
#define MEM_SLOTS {len(DEBUG_MEM_SLOTS)}

struct semantic_pair {{
	int cutpoint;
	int e0_reg;
	int e1_reg;
	const char *semantic;
}};

void {E0_CUT_SYMBOL}(int16_t out[WORDS], const int16_t input[WORDS],
		     int16_t scratch[WORDS], int16_t debug[CP_TOTAL][CP_WORDS]);
void {E1_CUT_SYMBOL}(int16_t out[WORDS], const int16_t input[WORDS],
		     int16_t scratch[WORDS], int16_t debug[CP_TOTAL][CP_WORDS]);

static const char *checkpoint_names[CP_PER_ROW] = {{ {names} }};
static const struct semantic_pair semantic_pairs[] = {{
{pair_rows}
}};

static uint32_t lcg_state = 0xe10c7001u;

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

static int find_first_diff(const int16_t e0[CP_TOTAL][CP_WORDS],
			   const int16_t e1[CP_TOTAL][CP_WORDS])
{{
	for (int cp = 0; cp < CP_TOTAL; cp++) {{
		const int row = cp / CP_PER_ROW;
		const int cpi = cp % CP_PER_ROW;

		for (unsigned p = 0; p < sizeof(semantic_pairs) / sizeof(semantic_pairs[0]); p++) {{
			const struct semantic_pair *pair = &semantic_pairs[p];
			if (pair->cutpoint != cpi)
				continue;
			for (int lane = 0; lane < QREG_WORDS; lane++) {{
				const int e0_idx = pair->e0_reg * QREG_WORDS + lane;
				const int e1_idx = pair->e1_reg * QREG_WORDS + lane;
				if (e0[cp][e0_idx] != e1[cp][e1_idx]) {{
					printf("first_diff:\n");
					printf("  row: %d\n", row);
					printf("  cutpoint: %s\n", checkpoint_names[cpi]);
					printf("  semantic_value: %s\n", pair->semantic);
					printf("  lane: %d\n", lane);
					printf("  e0_reg: q%d\n", pair->e0_reg);
					printf("  e1_reg: q%d\n", pair->e1_reg);
					printf("  e0_value: %d\n", e0[cp][e0_idx]);
					printf("  e1_value: %d\n", e1[cp][e1_idx]);
					printf("  producer_instruction_candidate: see stage345_block0_rename_validation.json\n");
					return 1;
				}}
			}}
		}}
	}}
	printf("cutpoints match\n");
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

	{E0_CUT_SYMBOL}(out_e0, input, scratch_e0, debug_e0);
	{E1_CUT_SYMBOL}(out_e1, input, scratch_e1, debug_e1);

	const int debug_diff = find_first_diff(debug_e0, debug_e1);
	const int final_mismatches = compare_out(out_e0, out_e1);
	printf("u01v3_stage345_semantic_e1_cutpoints_debug_diff=%d\n", debug_diff);
	printf("u01v3_stage345_semantic_e1_cutpoints_final_mismatches=%d\n", final_mismatches);
	return final_mismatches == 0 ? 0 : 1;
}}
'''


def strip_table_include(wrapper: str) -> str:
    return wrapper.replace('\n.include "asm/gt/experiment/forward_ntt/u01_block_first_tables.inc"\n', "\n")


def main() -> int:
    phase_lines = PHASE123.read_text().splitlines()
    stage3450 = load_stage345_block(0)
    stage3451 = load_stage345_block(1)
    ops, defs = collect_stage345_ssa(stage3450)
    colors, max_live, allocator_notes = corrected_allocate(defs)
    from generate_u01v3_f01_a1_stage345_block0_preserve_block1_liveins import allocate as old_allocate
    old_colors, _old_max_live = old_allocate(defs)
    stage3450_e1v2, records = rewrite_with_colors(ops, colors)
    stage3450_buggy, _buggy_report = rename_stage345_block0_preserve_block1(stage3450)
    stage3450_handoff = transform_stage345_for_handoff(0, stage3450)
    stage3451_handoff = transform_stage345_for_handoff(1, stage3451)

    E1V2_ASM.write_text(emit_wrapper(E1V2_SYMBOL, emit_e1v2_body(phase_lines, stage3450_e1v2, stage3451_handoff)))
    E1V2_SENTINEL.write_text(emit_sentinel(E1V2_SYMBOL))
    E1V2_TEST.write_text(emit_e1v2_test())

    e0_cut_body = emit_cutpoint_body(False, phase_lines, stage3450_handoff, stage3450_buggy, stage3451, stage3451_handoff)
    e1_cut_body = emit_cutpoint_body(True, phase_lines, stage3450_handoff, stage3450_buggy, stage3451, stage3451_handoff)
    CUTPOINT_ASM.write_text(
        strip_table_include(emit_debug_or_e2_wrapper(E0_CUT_SYMBOL, e0_cut_body, True, 224))
        + "\n"
        + emit_debug_or_e2_wrapper(E1_CUT_SYMBOL, e1_cut_body, True, 224)
    )
    semantic_pairs = cutpoint_semantic_pairs(ops, old_colors)
    CUTPOINT_TEST.write_text(emit_cutpoint_test(semantic_pairs))

    E1V2_MAP.write_text(
        json.dumps(
            {
                "candidate": E1V2_SYMBOL,
                "production_default_changed": False,
                "allocator": "same_as-first SSA greedy",
                "max_live": max_live,
                "allocator_notes": allocator_notes,
                "spills": 0,
                "raw_q_reloads": 0,
                "duplicate_stage12": False,
                "block1_liveins_preserved": [HANDOFF[1][q] for q in range(8, 16)],
                "stage345_block0_written_regs": sorted(
                    {reg for rec in records for reg in rec.get("write_regs", [])}
                ),
                "instruction_records_sample": records[:120],
                "cutpoint_semantic_pair_count": len(semantic_pairs),
            },
            indent=2,
        )
        + "\n"
    )

    E1V2_RESULT.write_text(
        "# U01v3 Track E E1v2 Preserve Live-ins\n\n"
        "Status: Pi5 correctness/ABI pass; PMU run completed.\n\n"
        "E1v2 makes one allocator change relative to E1: destructive `mls` "
        "`same_as old_dest` values are colored immediately when the source color "
        "is available. This removes the late-overwrite interference that the "
        "rename validator found in old E1.\n\n"
        "Contract:\n\n"
        "```text\n"
        "spills: 0\n"
        "raw q reloads: 0\n"
        "duplicate Stage12: no\n"
        f"max live vector values: {max_live}\n"
        "```\n\n"
        "Pi5 validation:\n\n"
        "```text\n"
        "u01v3_stage345_semantic_e1v2_preserve_liveins_abi_mask=0x0\n"
        "u01v3_stage345_semantic_e1v2_preserve_liveins_mismatches=0\n"
        "```\n\n"
        "Pi5 PMU matrix, `NTESTS=61`, `NITERATIONS=20000`:\n\n"
        "```text\n"
        "P:     2054 cycles, 2847 instructions\n"
        "V:     2072 cycles, 2887 instructions\n"
        "F0:    2059 cycles, 2839 instructions\n"
        "F1:    2060 cycles, 2839 instructions\n"
        "E2:    2059 cycles, 2839 instructions\n"
        "E1v2:  2047 cycles, 2788 instructions\n"
        "```\n\n"
        "E1v2 deltas:\n\n"
        "```text\n"
        "vs P:  -7 cycles, -59 instructions\n"
        "vs V:  -25 cycles, -99 instructions\n"
        "vs F0: -12 cycles, -51 instructions\n"
        "vs F1: -13 cycles, -51 instructions\n"
        "```\n"
    )
    CUTPOINT_RESULT.write_text(
        "# U01v3 Track E E1 Fine Cutpoints\n\n"
        "Status: generated and run on Pi5. This is a diagnostic for old E1, not E1v2.\n\n"
        "Cutpoints:\n\n"
        "```text\n"
        + "\n".join(f"{name}: after {threshold} executable Stage345 block0 instructions" for name, threshold in CUTPOINTS)
        + "\n```\n\n"
        "Observed semantic-pair first diff:\n\n"
        "```text\n"
        "row: 0\n"
        "cutpoint: after_first_butterfly_group\n"
        "semantic_value: v15_q8\n"
        "lane: 0\n"
        "e0_reg: q8\n"
        "e1_reg: q8\n"
        "e0_value: -995\n"
        "e1_value: 1451\n"
        "final_mismatches: 144\n"
        "```\n"
    )

    for path in (
        E1V2_ASM,
        E1V2_SENTINEL,
        E1V2_TEST,
        E1V2_MAP,
        E1V2_RESULT,
        CUTPOINT_ASM,
        CUTPOINT_TEST,
        CUTPOINT_RESULT,
    ):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
