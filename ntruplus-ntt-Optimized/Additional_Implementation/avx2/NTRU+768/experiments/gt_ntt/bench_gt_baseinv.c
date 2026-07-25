#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt_baseinv_native.h"
#include "gt_ntt_avx2.h"

#define BENCH_SETS 64U
#define BENCH_DEFAULT_CALLS UINT64_C(100000)
#define BENCH_WARMUPS 1000U

static int16_t coefficient_inputs[BENCH_SETS][GT_NTT_N]
	__attribute__((aligned(32)));
static int16_t centered_inputs[BENCH_SETS][GT_NTT_N]
	__attribute__((aligned(32)));
static int16_t lazy_inputs[BENCH_SETS][GT_NTT_N]
	__attribute__((aligned(32)));
static int16_t scratch[BENCH_SETS][GT_NTT_N]
	__attribute__((aligned(32)));
static int16_t inverse_outputs[BENCH_SETS][GT_NTT_N]
	__attribute__((aligned(32)));
static volatile uint64_t benchmark_sink;

static uint32_t rng_state = UINT32_C(0x243f6a88);

static uint32_t next_u32(void)
{
	uint32_t x = rng_state;

	x ^= x << 13;
	x ^= x >> 17;
	x ^= x << 5;
	rng_state = x;
	return x;
}

static int prepare_inputs(void)
{
	for (unsigned set = 0; set < BENCH_SETS; set++) {
		unsigned attempts = 0;

		do {
			for (unsigned i = 0; i < GT_NTT_N; i++) {
				coefficient_inputs[set][i] =
					(int16_t)((int)(next_u32() % 3U) - 1);
			}
			/* Model the key-generation f distribution's nonzero constant. */
			coefficient_inputs[set][0] =
				(int16_t)(coefficient_inputs[set][0] + 1);
			gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm(
				centered_inputs[set], coefficient_inputs[set]);
			attempts++;
		} while (gt_baseinv_native_centered_avx2(
			inverse_outputs[set], centered_inputs[set]) != 0 &&
			attempts < 10000U);

		if (attempts == 10000U) {
			return 1;
		}
		gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
			lazy_inputs[set], coefficient_inputs[set]);
		if (gt_baseinv_native_center_on_load_avx2(
			inverse_outputs[set], lazy_inputs[set]) != 0) {
			return 1;
		}
		if (gt_baseinv_native_l3_avx2(
			inverse_outputs[set], lazy_inputs[set]) != 0) {
			return 1;
		}
	}
	return 0;
}

static uint64_t parse_calls(const char *text)
{
	char *end = NULL;
	const unsigned long long parsed = strtoull(text, &end, 10);

	if (text[0] == '\0' || end == NULL || *end != '\0' || parsed == 0) {
		return 0;
	}
	return (uint64_t)parsed;
}

static void consume_outputs(uint64_t calls, uint64_t failures)
{
	uint64_t checksum = failures;

	for (unsigned set = 0; set < BENCH_SETS; set++) {
		checksum += (uint16_t)inverse_outputs[set][
			(unsigned)(calls + set) % GT_NTT_N];
	}
	benchmark_sink = checksum;
}

int main(int argc, char **argv)
{
	const char *mode;
	uint64_t calls = BENCH_DEFAULT_CALLS;
	uint64_t failures = 0;

	if (argc < 2 || argc > 3) {
		fprintf(stderr,
			"usage: %s centered|center-on-load|l3|forward-centered|forward-lazy|forward-lazy-direct [calls]\n",
			argv[0]);
		return 2;
	}
	mode = argv[1];
	if (argc == 3) {
		calls = parse_calls(argv[2]);
		if (calls == 0) {
			fprintf(stderr, "invalid call count: %s\n", argv[2]);
			return 2;
		}
	}
	if (prepare_inputs() != 0) {
		fputs("could not prepare invertible benchmark operands\n", stderr);
		return 1;
	}

	if (strcmp(mode, "centered") == 0) {
		for (unsigned i = 0; i < BENCH_WARMUPS; i++) {
			failures += (uint64_t)gt_baseinv_native_centered_asm_avx2(
				inverse_outputs[i & (BENCH_SETS - 1U)],
				centered_inputs[i & (BENCH_SETS - 1U)]);
		}
		failures = 0;
		for (uint64_t i = 0; i < calls; i++) {
			const unsigned set =
				(unsigned)i & (BENCH_SETS - 1U);

			failures += (uint64_t)gt_baseinv_native_centered_asm_avx2(
				inverse_outputs[set], centered_inputs[set]);
		}
	} else if (strcmp(mode, "center-on-load") == 0) {
		for (unsigned i = 0; i < BENCH_WARMUPS; i++) {
			failures +=
				(uint64_t)gt_baseinv_native_center_on_load_asm_avx2(
					inverse_outputs[i & (BENCH_SETS - 1U)],
					lazy_inputs[i & (BENCH_SETS - 1U)]);
		}
		failures = 0;
		for (uint64_t i = 0; i < calls; i++) {
			const unsigned set =
				(unsigned)i & (BENCH_SETS - 1U);

			failures +=
				(uint64_t)gt_baseinv_native_center_on_load_asm_avx2(
					inverse_outputs[set], lazy_inputs[set]);
		}
	} else if (strcmp(mode, "l3") == 0) {
		for (unsigned i = 0; i < BENCH_WARMUPS; i++) {
			failures += (uint64_t)gt_baseinv_native_l3_asm_avx2(
				inverse_outputs[i & (BENCH_SETS - 1U)],
				lazy_inputs[i & (BENCH_SETS - 1U)]);
		}
		failures = 0;
		for (uint64_t i = 0; i < calls; i++) {
			const unsigned set =
				(unsigned)i & (BENCH_SETS - 1U);

			failures += (uint64_t)gt_baseinv_native_l3_asm_avx2(
				inverse_outputs[set], lazy_inputs[set]);
		}
	} else if (strcmp(mode, "forward-centered") == 0) {
		for (unsigned i = 0; i < BENCH_WARMUPS; i++) {
			const unsigned set = i & (BENCH_SETS - 1U);

			gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm(
				scratch[set], coefficient_inputs[set]);
			failures += (uint64_t)gt_baseinv_native_centered_asm_avx2(
				inverse_outputs[set], scratch[set]);
		}
		failures = 0;
		for (uint64_t i = 0; i < calls; i++) {
			const unsigned set =
				(unsigned)i & (BENCH_SETS - 1U);

			gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm(
				scratch[set], coefficient_inputs[set]);
			failures += (uint64_t)gt_baseinv_native_centered_asm_avx2(
				inverse_outputs[set], scratch[set]);
		}
	} else if (strcmp(mode, "forward-lazy") == 0) {
		for (unsigned i = 0; i < BENCH_WARMUPS; i++) {
			const unsigned set = i & (BENCH_SETS - 1U);

			gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
				scratch[set], coefficient_inputs[set]);
			failures +=
				(uint64_t)gt_baseinv_native_center_on_load_asm_avx2(
					inverse_outputs[set], scratch[set]);
		}
		failures = 0;
		for (uint64_t i = 0; i < calls; i++) {
			const unsigned set =
				(unsigned)i & (BENCH_SETS - 1U);

			gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
				scratch[set], coefficient_inputs[set]);
			failures +=
				(uint64_t)gt_baseinv_native_center_on_load_asm_avx2(
					inverse_outputs[set], scratch[set]);
		}
	} else if (strcmp(mode, "forward-lazy-direct") == 0) {
		for (unsigned i = 0; i < BENCH_WARMUPS; i++) {
			const unsigned set = i & (BENCH_SETS - 1U);

			gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
				scratch[set], coefficient_inputs[set]);
			failures += (uint64_t)gt_baseinv_native_l3_asm_avx2(
				inverse_outputs[set], scratch[set]);
		}
		failures = 0;
		for (uint64_t i = 0; i < calls; i++) {
			const unsigned set =
				(unsigned)i & (BENCH_SETS - 1U);

			gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
				scratch[set], coefficient_inputs[set]);
			failures += (uint64_t)gt_baseinv_native_l3_asm_avx2(
				inverse_outputs[set], scratch[set]);
		}
	} else {
		fprintf(stderr, "unknown mode: %s\n", mode);
		return 2;
	}

	consume_outputs(calls, failures);
	printf("mode=%s calls=%llu failures=%llu checksum=%llu\n",
		mode, (unsigned long long)calls,
		(unsigned long long)failures,
		(unsigned long long)benchmark_sink);
	return failures != 0;
}
