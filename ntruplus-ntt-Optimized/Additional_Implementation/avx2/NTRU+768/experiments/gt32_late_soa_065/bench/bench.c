#define _GNU_SOURCE
#include "full_chain.h"

#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SAMPLES 41
#define FRONTEND_ITERS 3500U
#define ARITHMETIC_ITERS 1800U
#define TAIL_ITERS 3500U
#define FULL_ITERS 800U

enum {
	VARIANT_C0,
	VARIANT_C1,
	VARIANT_L0,
	VARIANT_COUNT
};

enum {
	COMPONENT_FRONTEND2,
	COMPONENT_ARITHMETIC,
	COMPONENT_TAIL,
	COMPONENT_FULL,
	COMPONENT_COUNT
};

static int16_t input_a[LATE065_WORDS] __attribute__((aligned(64)));
static int16_t input_b[LATE065_WORDS] __attribute__((aligned(64)));
static int16_t frontend_a[LATE065_WORDS] __attribute__((aligned(64)));
static int16_t frontend_b[LATE065_WORDS] __attribute__((aligned(64)));
static int16_t tail_input[LATE065_WORDS] __attribute__((aligned(64)));
static int16_t output[VARIANT_COUNT][LATE065_WORDS] __attribute__((aligned(64)));
static late065_scratch scratch[VARIANT_COUNT] __attribute__((aligned(64)));
static volatile uint64_t sink;

static uint64_t ticks(void)
{
	unsigned aux;
	_mm_lfence();
	const uint64_t value = __rdtscp(&aux);
	_mm_lfence();
	return value;
}

static int cmp_double(const void *a, const void *b)
{
	const double x = *(const double *)a;
	const double y = *(const double *)b;
	return (x > y) - (x < y);
}

static double median(double *values)
{
	qsort(values, SAMPLES, sizeof(*values), cmp_double);
	return values[SAMPLES / 2];
}

static void arithmetic_once(unsigned variant)
{
	if (variant == VARIANT_C0) {
		gt32_tile4_forward_all_pair_asm(scratch[variant].operand_a,
			frontend_a);
		gt32_tile4_forward_all_pair_asm(scratch[variant].operand_b,
			frontend_b);
		gt32_tile4_basemul_c3center_late_aos_private_asm(
			scratch[variant].product, scratch[variant].operand_a,
			scratch[variant].operand_b);
		gt32_tile4_inverse_all_pair_asm(output[variant],
			scratch[variant].product);
	} else if (variant == VARIANT_C1) {
		gt32_tile4_forward_all_pair_asm(scratch[variant].operand_a,
			frontend_a);
		gt32_tile4_forward_all_pair_asm(scratch[variant].operand_b,
			frontend_b);
		gt32_tile4_attr_basemul_i1_stage01_fused_asm(
			scratch[variant].product, scratch[variant].operand_a,
			scratch[variant].operand_b);
		gt32_tile4_attr_inverse_i1_cross3_asm(output[variant],
			scratch[variant].product);
	} else {
		gt32_tile4_attr_forward_all_bm_soa_asm(
			scratch[variant].operand_a, frontend_a);
		gt32_tile4_attr_forward_all_bm_soa_asm(
			scratch[variant].operand_b, frontend_b);
		late_soa_full_basemul_i2_fused_asm(scratch[variant].product,
			scratch[variant].operand_a, scratch[variant].operand_b);
		gt32_tile4_attr_inverse_i1_cross3_asm(output[variant],
			scratch[variant].product);
	}
}

static void run_once(unsigned variant, unsigned component)
{
	if (component == COMPONENT_FRONTEND2) {
		gt32_tile4_frontend_wide_raw_asm(scratch[variant].operand_a,
			input_a);
		gt32_tile4_frontend_wide_raw_asm(scratch[variant].operand_b,
			input_b);
	} else if (component == COMPONENT_ARITHMETIC) {
		arithmetic_once(variant);
	} else if (component == COMPONENT_TAIL) {
		gt32_tile4_inverse_tail_t9_isolated_private_asm(output[variant],
			tail_input);
	} else if (variant == VARIANT_C0) {
		late065_chain_c0(output[variant], input_a, input_b,
			&scratch[variant]);
	} else if (variant == VARIANT_C1) {
		late065_chain_c1(output[variant], input_a, input_b,
			&scratch[variant]);
	} else {
		late065_chain_l0(output[variant], input_a, input_b,
			&scratch[variant]);
	}
}

static uint16_t sample_word(unsigned variant, unsigned component,
	unsigned iteration)
{
	if (component == COMPONENT_FRONTEND2)
		return (uint16_t)scratch[variant].operand_b[iteration % LATE065_WORDS];
	return (uint16_t)output[variant][iteration % LATE065_WORDS];
}

static double run(unsigned variant, unsigned component, unsigned iterations)
{
	const uint64_t begin = ticks();
	for (unsigned i = 0; i < iterations; ++i) {
		run_once(variant, component);
		sink += sample_word(variant, component, i);
	}
	return (double)(ticks() - begin) / (double)iterations;
}

static unsigned iterations_for(unsigned component)
{
	static const unsigned table[COMPONENT_COUNT] = {
		FRONTEND_ITERS, ARITHMETIC_ITERS, TAIL_ITERS, FULL_ITERS
	};
	return table[component];
}

static void prepare(void)
{
	uint64_t state = UINT64_C(0x065123456789abcd);
	for (unsigned i = 0; i < LATE065_WORDS; ++i) {
		state ^= state << 7; state ^= state >> 9;
		input_a[i] = (int16_t)((int)(state & 7U) - 3);
		state ^= state << 7; state ^= state >> 9;
		input_b[i] = (int16_t)((int)(state & 7U) - 3);
	}
	gt32_tile4_frontend_wide_raw_asm(frontend_a, input_a);
	gt32_tile4_frontend_wide_raw_asm(frontend_b, input_b);
	arithmetic_once(VARIANT_C0);
	memcpy(tail_input, output[VARIANT_C0], sizeof(tail_input));
}

static void pin_first_cpu(void)
{
	cpu_set_t available;
	cpu_set_t one;
	CPU_ZERO(&available);
	if (sched_getaffinity(0, sizeof(available), &available) != 0)
		return;
	for (int cpu = 0; cpu < CPU_SETSIZE; ++cpu) {
		if (!CPU_ISSET(cpu, &available))
			continue;
		CPU_ZERO(&one);
		CPU_SET(cpu, &one);
		(void)sched_setaffinity(0, sizeof(one), &one);
		return;
	}
}

static unsigned parse_variant(const char *name)
{
	if (!strcmp(name, "c0")) return VARIANT_C0;
	if (!strcmp(name, "c1")) return VARIANT_C1;
	if (!strcmp(name, "late")) return VARIANT_L0;
	fprintf(stderr, "unknown variant: %s\n", name);
	exit(2);
}

static unsigned parse_component(const char *name)
{
	if (!strcmp(name, "frontend2")) return COMPONENT_FRONTEND2;
	if (!strcmp(name, "arithmetic")) return COMPONENT_ARITHMETIC;
	if (!strcmp(name, "tail")) return COMPONENT_TAIL;
	if (!strcmp(name, "full")) return COMPONENT_FULL;
	fprintf(stderr, "unknown component: %s\n", name);
	exit(2);
}

static int pmu(const char *variant_name, const char *component_name)
{
	const unsigned variant = parse_variant(variant_name);
	const unsigned component = parse_component(component_name);
	static const unsigned pmu_iters[COMPONENT_COUNT] = {
		400000U, 220000U, 400000U, 150000U
	};
	(void)run(variant, component, pmu_iters[component]);
	printf("%llu\n", (unsigned long long)sink);
	return 0;
}

int main(int argc, char **argv)
{
	pin_first_cpu();
	prepare();
	if (argc == 4 && !strcmp(argv[1], "--pmu"))
		return pmu(argv[2], argv[3]);

	double c1[COMPONENT_COUNT][SAMPLES];
	double late[COMPONENT_COUNT][SAMPLES];
	for (unsigned sample = 0; sample < SAMPLES; ++sample) {
		const int reverse = (int)(sample & 1U);
		for (unsigned component = 0; component < COMPONENT_COUNT; ++component) {
			const unsigned iters = iterations_for(component);
			double control;
			double v1;
			double vl;
			if (!reverse) {
				control = run(VARIANT_C0, component, iters);
				v1 = run(VARIANT_C1, component, iters);
				vl = run(VARIANT_L0, component, iters);
			} else {
				vl = run(VARIANT_L0, component, iters);
				v1 = run(VARIANT_C1, component, iters);
				control = run(VARIANT_C0, component, iters);
			}
			c1[component][sample] = v1 - control;
			late[component][sample] = vl - control;
		}
	}

	printf("{\"delta_tsc\":{\"c1\":{\"frontend2\":%.3f,"
	       "\"arithmetic\":%.3f,\"tail\":%.3f,\"full\":%.3f},"
	       "\"late\":{\"frontend2\":%.3f,\"arithmetic\":%.3f,"
	       "\"tail\":%.3f,\"full\":%.3f}},\"sink\":%llu}\n",
		median(c1[COMPONENT_FRONTEND2]),
		median(c1[COMPONENT_ARITHMETIC]),
		median(c1[COMPONENT_TAIL]), median(c1[COMPONENT_FULL]),
		median(late[COMPONENT_FRONTEND2]),
		median(late[COMPONENT_ARITHMETIC]),
		median(late[COMPONENT_TAIL]), median(late[COMPONENT_FULL]),
		(unsigned long long)sink);
	return 0;
}
