#define _GNU_SOURCE
#include <errno.h>
#include <linux/perf_event.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <x86intrin.h>

#include "tile4_global_physical.h"

#define WORDS 768
#define SAMPLES 20U

void gt32_global_forward_core_asm(int16_t *, const int16_t *);
void gt32_global_inverse_core_asm(int16_t *, const int16_t *);
void gt32_tile4_frontend_wide_raw_asm(int16_t *, const int16_t *);
void gt32_tile4_attr_forward_all_bm_soa_asm(int16_t *, const int16_t *);
void gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(
	int16_t *, const int16_t *, const int16_t *);
void gt32_tile4_basemul_scale_soa_soa_to_m_private_asm(
	int16_t *, const int16_t *, const int16_t *);
void gt32_tile4_inverse_all_pair_asm(int16_t *, const int16_t *);
void gt32_tile4_inverse_tail_t9_isolated_private_asm(int16_t *,
	const int16_t *);
#ifdef GLOBAL_COMPARE_OFFICIAL
void poly_ntt(int16_t *);
void poly_basemul_scale(int16_t *, const int16_t *, const int16_t *);
void poly_invntt_scale(int16_t *);
#endif

static int16_t input_a[WORDS] __attribute__((aligned(64)));
static int16_t input_b[WORDS] __attribute__((aligned(64)));
#ifndef GLOBAL_COMPARE_OFFICIAL
static int16_t frontend[WORDS] __attribute__((aligned(64)));
static int16_t forward_a[WORDS] __attribute__((aligned(64)));
static int16_t forward_b[WORDS] __attribute__((aligned(64)));
static int16_t product[WORDS] __attribute__((aligned(64)));
static int16_t inverse_rows[WORDS] __attribute__((aligned(64)));
#endif
static int16_t output[WORDS] __attribute__((aligned(64)));
static gt32_global_physical_scratch_t global_scratch
	__attribute__((aligned(64)));
#ifdef GLOBAL_COMPARE_OFFICIAL
static int16_t official_a[WORDS] __attribute__((aligned(64)));
static int16_t official_b[WORDS] __attribute__((aligned(64)));
#endif
static volatile uint64_t sink;

typedef struct {
	int leader;
	int instruction_fd;
	int ref_cycle_fd;
	int available;
} pmu_t;

typedef struct {
	double tsc;
	double cycles;
	double instructions;
	double ref_cycles;
} result_t;

__attribute__((noinline))
static void control(void)
{
#ifdef GLOBAL_COMPARE_OFFICIAL
	memcpy(official_a, input_a, sizeof official_a);
	memcpy(official_b, input_b, sizeof official_b);
	poly_ntt(official_a);
	poly_ntt(official_b);
	poly_basemul_scale(output, official_a, official_b);
	poly_invntt_scale(output);
#else
	gt32_tile4_frontend_wide_raw_asm(frontend, input_a);
	gt32_tile4_attr_forward_all_bm_soa_asm(forward_a, frontend);
	gt32_tile4_frontend_wide_raw_asm(frontend, input_b);
	gt32_tile4_attr_forward_all_bm_soa_asm(forward_b, frontend);
	gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(
		product, forward_a, forward_b);
	gt32_tile4_inverse_all_pair_asm(inverse_rows, product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(output, inverse_rows);
#endif
}

__attribute__((noinline))
static void candidate(void)
{
	gt32_global_physical_polymul_private(output, input_a, input_b,
		&global_scratch);
}

static int perf_open(uint64_t config, int group_fd, int disabled)
{
	struct perf_event_attr attr;
	long result;

	memset(&attr, 0, sizeof attr);
	attr.type = PERF_TYPE_HARDWARE;
	attr.size = sizeof attr;
	attr.config = config;
	attr.disabled = disabled != 0 ? 1U : 0U;
	attr.exclude_kernel = 1U;
	attr.exclude_hv = 1U;
	if (disabled != 0)
		attr.read_format = PERF_FORMAT_GROUP;
	result = syscall(SYS_perf_event_open, &attr, 0, -1, group_fd, 0UL);
	return result < 0 ? -1 : (int)result;
}

static pmu_t pmu_open(void)
{
	pmu_t pmu = {-1, -1, -1, 0};

	pmu.leader = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1, 1);
	if (pmu.leader < 0)
		return pmu;
	pmu.instruction_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS,
		pmu.leader, 0);
	pmu.ref_cycle_fd = perf_open(PERF_COUNT_HW_REF_CPU_CYCLES,
		pmu.leader, 0);
	if (pmu.instruction_fd < 0 || pmu.ref_cycle_fd < 0)
		return pmu;
	pmu.available = 1;
	return pmu;
}

static uint64_t tsc_start(void)
{
	_mm_lfence();
	return __rdtsc();
}

static uint64_t tsc_stop(void)
{
	unsigned aux;
	uint64_t value = __rdtscp(&aux);
	_mm_lfence();
	return value;
}

static result_t measure(void (*fn)(void), unsigned iterations, pmu_t *pmu)
{
	uint64_t begin;
	uint64_t end;
	uint64_t counts[4] = {0, 0, 0, 0};
	result_t result = {0, 0, 0, 0};

	if (pmu->available != 0) {
		(void)ioctl(pmu->leader, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
		(void)ioctl(pmu->leader, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
	}
	begin = tsc_start();
	for (unsigned i = 0; i < iterations; i++)
		fn();
	end = tsc_stop();
	if (pmu->available != 0) {
		(void)ioctl(pmu->leader, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
		if (read(pmu->leader, counts, sizeof counts) != (ssize_t)sizeof counts
			|| counts[0] != 3U)
			pmu->available = 0;
	}
	sink += (uint16_t)output[iterations % WORDS];
	result.tsc = (double)(end - begin) / (double)iterations;
	if (pmu->available != 0) {
		result.cycles = (double)counts[1] / (double)iterations;
		result.instructions = (double)counts[2] / (double)iterations;
		result.ref_cycles = (double)counts[3] / (double)iterations;
	}
	return result;
}

int main(int argc, char **argv)
{
	unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 5000U;
	cpu_set_t set;
	pmu_t pmu;
	int16_t expected[WORDS] __attribute__((aligned(64)));
#ifdef GLOBAL_COMPARE_OFFICIAL
	const char *comparison = "official-main";
#else
	const char *comparison = "current-gt";
#endif

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof set, &set) != 0)
		perror("sched_setaffinity");
	for (unsigned i = 0; i < WORDS; i++) {
		input_a[i] = (int16_t)((int)((i * 97U + 31U) & 7U) - 3);
		input_b[i] = (int16_t)((int)((i * 193U + 17U) & 7U) - 3);
	}
	control();
	memcpy(expected, output, sizeof expected);
	candidate();
#ifdef GLOBAL_COMPARE_OFFICIAL
	for (unsigned i = 0; i < WORDS; i++) {
		int want = expected[i] % 3457;
		int got = output[i] % 3457;
		if (want < 0)
			want += 3457;
		if (got < 0)
			got += 3457;
		if (want != got) {
			fprintf(stderr, "full Official differential mismatch at %u\n", i);
			return 1;
		}
	}
#else
	if (memcmp(expected, output, sizeof expected) != 0) {
		fputs("full coefficient-output mismatch\n", stderr);
		return 1;
	}
#endif
	pmu = pmu_open();
	for (unsigned i = 0; i < 2U; i++) {
		(void)measure(control, 200U, &pmu);
		(void)measure(candidate, 200U, &pmu);
	}
	printf("META,experiment=GT32-GLOBAL-PHYSICAL-001,comparison=%s,iterations=%u,"
		"samples=%u,pmu=%s\n", comparison, iterations, SAMPLES,
		pmu.available != 0 ? "core" : "unavailable");
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		result_t a;
		result_t b;
		if ((sample & 1U) == 0U) {
			a = measure(control, iterations, &pmu);
			b = measure(candidate, iterations, &pmu);
		} else {
			b = measure(candidate, iterations, &pmu);
			a = measure(control, iterations, &pmu);
		}
		printf("SAMPLE,whole,%u,"
			"%.6f,%.6f,%.6f,"
			"%.6f,%.6f,%.6f,"
			"%.6f,%.6f,%.6f,"
			"%.6f,%.6f,%.6f\n", sample,
			a.tsc, b.tsc, b.tsc - a.tsc,
			a.cycles, b.cycles, b.cycles - a.cycles,
			a.instructions, b.instructions, b.instructions - a.instructions,
			a.ref_cycles, b.ref_cycles, b.ref_cycles - a.ref_cycles);
	}
	if (pmu.leader >= 0)
		(void)close(pmu.leader);
	if (pmu.instruction_fd >= 0)
		(void)close(pmu.instruction_fd);
	if (pmu.ref_cycle_fd >= 0)
		(void)close(pmu.ref_cycle_fd);
	return sink == UINT64_MAX ? 1 : 0;
}
