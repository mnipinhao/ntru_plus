#!/usr/bin/env python3
"""Generate U01v3 F0123 Track G artifacts.

Track G follows the E4 live-all feasibility failure.  It does not try to keep
block3 live across Stage345 block0/1/2.  Instead, G1 keeps the verified E3
F012 fused path and consumes block3 later from the Stage12 scratch image that
E3 already writes.
"""

from __future__ import annotations

import json
from pathlib import Path

from generate_phase123_shared_prefix_v2 import PHASE123
from generate_phase123_shared_prefix_v3_block1_block01_fuse import (
    ROWS,
    emit_phase123_shared_prefix,
    load_stage345_block,
)
from generate_u01v3_f01_spill_budget import emit_sentinel
from generate_u01v3_stage345_e3_f012 import (
    BLOCK2_E3_HANDOFF,
    allocate_same_as_first,
    collect_stage345_ssa,
    emit_body_e3,
    emit_stage12_block012_once,
    emit_wrapper,
    handoff_reg_map,
    rewrite_with_colors,
    transform_stage345_for_custom_handoff,
)
from generate_phase123_shared_prefix_v3_block1_block01_fuse import HANDOFF


ROOT = Path(__file__).resolve().parent
NTRU_ROOT = ROOT.parents[1]
ASM_ROOT = NTRU_ROOT / "asm/gt/experiment"
TEST_ROOT = NTRU_ROOT / "gt_test"
BENCH_ROOT = NTRU_ROOT.parents[2] / "aarch64-bench"

SCRATCH_B0123 = ROOT / "u01v3_stage345_block0123_from_scratch_allrows.sym.s"
G1_MAP = ROOT / "u01v3_f0123_g1_delayed_block3_map.json"
G1_RESULT = ROOT / "u01v3_f0123_track_g_result.md"

P_SYMBOL = "u01v3_f0123_production_oracle"
V_SYMBOL = "u01v3_f0123_v2_scratch"
G1_SYMBOL = "u01v3_f0123_g1_delayed_block3"

P_ASM = ASM_ROOT / f"{P_SYMBOL}.S"
V_ASM = ASM_ROOT / f"{V_SYMBOL}.S"
G1_ASM = ASM_ROOT / f"{G1_SYMBOL}.S"
G1_SENTINEL = ASM_ROOT / f"{G1_SYMBOL}_abi_sentinel.S"
G1_TEST = TEST_ROOT / "test_u01v3_f0123_track_g.c"
G1_BENCH = BENCH_ROOT / "bench_u01v3_f0123_track_g_pmu.c"

ROW_SCRATCH = {"row0": 0, "row1": 512, "row2": 1024}
ROW_SCATTER = {"row0": 0, "row1": 256, "row2": 512}
BLOCK_SCATTER = {0: 0, 1: 192, 2: 384, 3: 576}
TW_STAGE3_OFFSET = 64


def emit_stage345_setup_g(lines: list[str], row: str, block: int, from_scratch: bool) -> None:
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


def emit_scratch_stage345_body_g(blocks: tuple[int, ...], label: str, stage345: dict[int, list[str]]) -> list[str]:
    block_desc = "_".join(f"block{b}" for b in blocks)
    lines: list[str] = [
        f"// Generated U01v3 Track G helper: run Stage345 {block_desc} from row-major scratch.",
        "//",
        "// Live-in: x19=out, x21=scratch, x23=ntt32 twiddle vector base, v0=q/constants.",
        "",
        ".text",
        "",
        f"{label}:",
    ]
    for row in ROWS:
        for block in blocks:
            emit_stage345_setup_g(lines, row, block, from_scratch=True)
            lines.extend(stage345[block])
            lines.append("")
    lines.append(f"{label}_end:")
    lines.append("")
    return lines


def build_e3_stage345() -> tuple[list[str], list[str], list[str], dict[str, object]]:
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
        defs0, b1_reserved | b2_reserved, "G1 block0 preserve block1+block2"
    )
    e3_stage3450, records0 = rewrite_with_colors(ops0, colors0, 0, HANDOFF[0], "G1/E3")

    ops1, defs1 = collect_stage345_ssa(stage3451, 1, b1_initial)
    colors1, _max1, report1 = allocate_same_as_first(
        defs1, b2_reserved, "G1 block1 preserve block2"
    )
    e3_stage3451, records1 = rewrite_with_colors(ops1, colors1, 1, HANDOFF[1], "G1/E3")

    e3_stage3452, block2_moves = transform_stage345_for_custom_handoff(
        2, stage3452, BLOCK2_E3_HANDOFF
    )

    metadata = {
        "block0_allocator": report0,
        "block1_allocator": report1,
        "block0_records_sample": records0[:80],
        "block1_records_sample": records1[:80],
        "block2_handoff": {f"Q{q}": BLOCK2_E3_HANDOFF[q] for q in range(16, 24)},
        "block2_handoff_moves": block2_moves,
    }
    return e3_stage3450, e3_stage3451, e3_stage3452, metadata


def emit_body_g1(
    phase_lines: list[str],
    stage3450: list[str],
    stage3451: list[str],
    stage3452: list[str],
    stage3453: list[str],
) -> tuple[list[str], list[dict[str, object]]]:
    body: list[str] = [
        "    // Generated Track G G1 F0123 body.",
        "    // E3/F012 is unchanged.  Block3 is consumed after block0/1/2",
        "    // from the Stage12 block3 scratch image already written by the",
        "    // compact Stage12 producer.",
        "",
    ]
    stage12_reports: list[dict[str, object]] = []
    emit_phase123_shared_prefix(body, phase_lines)
    for row in ROWS:
        stage12_reports.append(emit_stage12_block012_once(body, row))
        emit_stage345_setup_g(body, row, 0, from_scratch=False)
        body.extend(stage3450)
        body.append("")
        emit_stage345_setup_g(body, row, 1, from_scratch=False)
        body.extend(stage3451)
        body.append("")
        emit_stage345_setup_g(body, row, 2, from_scratch=False)
        body.extend(stage3452)
        body.append("")
        emit_stage345_setup_g(body, row, 3, from_scratch=True)
        body.extend(stage3453)
        body.append("")
    return body, stage12_reports


def emit_p_wrapper(symbol: str) -> str:
    return "\n".join(
        [
            f"/* U01v3 F0123 Track G oracle wrapper: {symbol}. */",
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
            "    mov x1, x20",
            "    mov x13, x21",
            "    mov x4, x21",
            "    add x5, x21, #512",
            "    add x6, x21, #1024",
            "",
            "    adr x2, u01_block_first_zetas",
            "    ldr q0, [x2]",
            "    adr x3, u01_block_first_twist_table",
            "    adr x23, u01_block_first_ntt32_twiddle_vecs",
            "    mov x12, x23",
            "",
            "    .include \"experiments/forward_ntt_phase123_u01/phase123_production_stage12_block0_oracle_allrows.sym.s\"",
            "    .include \"experiments/forward_ntt_phase123_u01/u01v3_stage345_block0123_from_scratch_allrows.sym.s\"",
            "",
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


def emit_v_wrapper(symbol: str) -> str:
    return "\n".join(
        [
            f"/* U01v3 F0123 Track G scratch baseline wrapper: {symbol}. */",
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
            "    mov x13, x21",
            "    mov x14, x20",
            "    adr x2, u01_block_first_zetas",
            "    ldr q0, [x2]",
            "    adr x15, u01_block_first_twist_table",
            "    adr x23, u01_block_first_ntt32_twiddle_vecs",
            "    mov x12, x23",
            "",
            "    .include \"experiments/forward_ntt_phase123_u01/phase123_shared_prefix_v2_allrows.sym.s\"",
            "    .include \"experiments/forward_ntt_phase123_u01/u01v3_stage345_block0123_from_scratch_allrows.sym.s\"",
            "",
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

void {P_SYMBOL}(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);
void {V_SYMBOL}(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);
void {G1_SYMBOL}(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);
int {G1_SYMBOL}_abi_sentinel(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);

static uint32_t lcg_state = 0xf0123001u;

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
		case 0: input[i] = 0; break;
		case 1: input[i] = (int16_t)(i % 17); break;
		case 2: input[i] = (int16_t)(NTRUPLUS_Q - 1 - (i % 31)); break;
		case 3: input[i] = (int16_t)(bound - (i % 61)); break;
		default:
			input[i] = (int16_t)((int)(lcg_next() % (uint32_t)span) - bound);
			break;
		}}
	}}
}}

static int compare_out(const char *name, const int16_t want[WORDS], const int16_t got[WORDS])
{{
	int mismatches = 0;

	for (int i = 0; i < WORDS; i++) {{
		if (want[i] != got[i]) {{
			if (mismatches < 16)
				printf("%s mismatch[%d]: want=%d got=%d\n", name, i, want[i], got[i]);
			mismatches++;
		}}
	}}
	return mismatches;
}}

static int run_case(const int16_t input[WORDS], uint64_t *abi_mask)
{{
	int16_t want[WORDS] __attribute__((aligned(64)));
	int16_t vgot[WORDS] __attribute__((aligned(64)));
	int16_t ggot[WORDS] __attribute__((aligned(64)));
	int16_t sgot[WORDS] __attribute__((aligned(64)));
	int16_t scratch_want[WORDS] __attribute__((aligned(64)));
	int16_t scratch_v[WORDS] __attribute__((aligned(64)));
	int16_t scratch_g[WORDS] __attribute__((aligned(64)));
	int16_t scratch_s[WORDS] __attribute__((aligned(64)));
	int mismatches = 0;

	memset(want, 0x6b, sizeof(want));
	memset(vgot, 0x6b, sizeof(vgot));
	memset(ggot, 0x6b, sizeof(ggot));
	memset(sgot, 0x6b, sizeof(sgot));
	memset(scratch_want, 0xa5, sizeof(scratch_want));
	memset(scratch_v, 0xa5, sizeof(scratch_v));
	memset(scratch_g, 0xa5, sizeof(scratch_g));
	memset(scratch_s, 0xa5, sizeof(scratch_s));

	{P_SYMBOL}(want, input, scratch_want);
	{V_SYMBOL}(vgot, input, scratch_v);
	{G1_SYMBOL}(ggot, input, scratch_g);
	*abi_mask |= (uint64_t){G1_SYMBOL}_abi_sentinel(sgot, input, scratch_s);

	mismatches += compare_out("{V_SYMBOL}", want, vgot);
	mismatches += compare_out("{G1_SYMBOL}", want, ggot);
	mismatches += compare_out("{G1_SYMBOL}_sentinel", want, sgot);
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

	printf("{G1_SYMBOL}_abi_mask=0x%llx\n", (unsigned long long)abi_mask);
	printf("{G1_SYMBOL}_mismatches=%d\n", mismatches);
	printf("mismatches = %d\n", mismatches);
	return mismatches == 0 && abi_mask == 0 ? 0 : 1;
}}
'''


def emit_pmu_harness() -> str:
    return rf'''#if !defined(__linux__)
#error "bench_u01v3_f0123_track_g_pmu requires Linux perf_event_open"
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
#define VARIANT_COUNT 3

typedef void (*u01v3_fn)(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);

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

void {P_SYMBOL}(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);
void {V_SYMBOL}(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);
void {G1_SYMBOL}(int16_t out[WORDS], const int16_t input[WORDS], int16_t scratch[WORDS]);

extern const char {P_SYMBOL}_end[];
extern const char {V_SYMBOL}_end[];
extern const char {G1_SYMBOL}_end[];

static const struct variant variants[VARIANT_COUNT] = {{
	{{"P", "production_source_order_f0123", {P_SYMBOL}, {P_SYMBOL}_end, 1}},
	{{"V", "u01v2_shared_prefix_scratch_f0123", {V_SYMBOL}, {V_SYMBOL}_end, 0}},
	{{"G1", "u01v3_g1_delayed_block3", {G1_SYMBOL}, {G1_SYMBOL}_end, 0}},
}};

static int16_t inputs[NINPUTS][WORDS] __attribute__((aligned(64)));
static int16_t oracle[NINPUTS][WORDS] __attribute__((aligned(64)));
static int16_t out[WORDS] __attribute__((aligned(64)));
static int16_t scratch[WORDS] __attribute__((aligned(64)));
static struct counts samples[VARIANT_COUNT][NTESTS];
static int status[VARIANT_COUNT];
static int mismatches[VARIANT_COUNT];
static volatile uint64_t sink;
static uint32_t rng_state = 0xf01230b7u;
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

static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid, int cpu, int group_fd, unsigned long flags)
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
		memset(oracle[i], 0x6b, sizeof(oracle[i]));
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
	printf("u01v3_f0123_track_g_pmu NTESTS=%d NITERATIONS=%d sink=%" PRIu64 "\n", NTESTS, NITERATIONS, sink);
	printf("id,name,status,cycles,instructions,cpi,delta_vs_P,delta_vs_V,text_size,addr_mod32,addr_mod64,mismatches\n");
	const uint64_t p_cycles = median_cycles(0);
	const uint64_t v_cycles = median_cycles(1);
	for (int v = 0; v < VARIANT_COUNT; v++) {{
		uint64_t cyc = status[v] ? median_cycles(v) : 0;
		uint64_t ins = status[v] ? median_instructions(v) : 0;
		double cpi = ins ? (double)cyc / (double)ins : 0.0;
		uintptr_t addr = fn_address_bits(variants[v].fn);
		printf("%s,%s,%s,%" PRIu64 ",%" PRIu64 ",%.4f,%+" PRId64 ",%+" PRId64 ",%zu,%lu,%lu,%d\n",
		       variants[v].id, variants[v].name, status[v] ? "pass" : "fail",
		       cyc, ins, cpi, (int64_t)cyc - (int64_t)p_cycles,
		       (int64_t)cyc - (int64_t)v_cycles, text_size(&variants[v]),
		       (unsigned long)(addr % 32), (unsigned long)(addr % 64),
		       mismatches[v]);
	}}
	close(fd_instr);
	close(fd_cycles);
	return 0;
}}
'''


def main() -> int:
    phase_lines = PHASE123.read_text().splitlines()
    stage345 = {block: load_stage345_block(block) for block in range(4)}
    e3_stage3450, e3_stage3451, e3_stage3452, e3_meta = build_e3_stage345()
    g1_body, stage12_reports = emit_body_g1(
        phase_lines, e3_stage3450, e3_stage3451, e3_stage3452, stage345[3]
    )

    SCRATCH_B0123.write_text(
        "\n".join(
            emit_scratch_stage345_body_g(
                (0, 1, 2, 3),
                "u01v3_stage345_block0123_from_scratch_allrows",
                stage345,
            )
        )
    )
    P_ASM.write_text(emit_p_wrapper(P_SYMBOL))
    V_ASM.write_text(emit_v_wrapper(V_SYMBOL))
    G1_ASM.write_text(emit_wrapper(G1_SYMBOL, g1_body))
    G1_SENTINEL.write_text(emit_sentinel(G1_SYMBOL))
    G1_TEST.write_text(emit_test_source())
    G1_BENCH.write_text(emit_pmu_harness())

    G1_MAP.write_text(
        json.dumps(
            {
                "candidate": G1_SYMBOL,
                "production_default_changed": False,
                "track_g_model": "u01v3_f0123_track_g_candidates.json",
                "shape": "E3/F012 live handoff plus delayed block3 from Stage12 scratch",
                "same_coverage_oracle": P_SYMBOL,
                "scratch_baseline": V_SYMBOL,
                "removed_q_stores_vs_v": 72,
                "removed_q_loads_vs_v": 72,
                "block3_stage345_q_loads_retained": 24,
                "q_spills_restores": 0,
                "raw_q_reloads": 0,
                "duplicate_stage12": False,
                "stage12_reports": stage12_reports,
                "e3_metadata": e3_meta,
            },
            indent=2,
        )
        + "\n"
    )

    G1_RESULT.write_text(
        "# U01v3 F0123 Track G\n\n"
        "Status: generated.  Production default unchanged.\n\n"
        "E4 live-all was not emitted because the hard register contract is "
        "infeasible with q0 reserved.  G2_spill1 is also not emitted: one "
        "spill removes the global cardinality deficit, but Stage345 block0 "
        "would still have only 8 non-future colors while its SSA max-live is "
        "15.\n\n"
        "Generated G1 candidate:\n\n"
        "```text\n"
        f"symbol: {G1_SYMBOL}\n"
        "shape: E3/F012 live handoff + delayed block3 scratch consume\n"
        "spills: 0\n"
        "raw q reloads: 0\n"
        "duplicate Stage12: no\n"
        "block3 q loads retained: 24\n"
        "same coverage oracle: u01v3_f0123_production_oracle\n"
        "scratch baseline: u01v3_f0123_v2_scratch\n"
        "```\n\n"
        "Pi5 correctness/PMU results are pending.\n"
    )

    for path in (SCRATCH_B0123, P_ASM, V_ASM, G1_ASM, G1_SENTINEL, G1_TEST, G1_BENCH, G1_MAP, G1_RESULT):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
