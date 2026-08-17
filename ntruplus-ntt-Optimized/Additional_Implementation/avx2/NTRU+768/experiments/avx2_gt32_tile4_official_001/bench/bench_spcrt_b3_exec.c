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

#include "tile4.h"

#define WORDS 768
#define SAMPLES 20U

void gt32_spcrt_forward_raw_asm(int16_t *, const int16_t *);
void gt32_spcrt_forward_a_repaired_asm(int16_t *, const int16_t *);
void gt32_spcrt_forward_a_repaired_r1_asm(int16_t *, const int16_t *);
void gt32_spcrt_forward_raw_r2_shared_asm(int16_t *, const int16_t *);
void gt32_spcrt_forward_a_repaired_r2_shared_asm(int16_t *, const int16_t *);
void gt32_spcrt_basemul_b3_asm(int16_t *, const int16_t *, const int16_t *);

static int16_t input_a[WORDS] __attribute__((aligned(64)));
static int16_t input_b[WORDS] __attribute__((aligned(64)));
static int16_t control_a[WORDS] __attribute__((aligned(64)));
static int16_t control_b[WORDS] __attribute__((aligned(64)));
static int16_t candidate_a[WORDS] __attribute__((aligned(64)));
static int16_t candidate_b[WORDS] __attribute__((aligned(64)));
static int16_t output[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

typedef void (*bench_fn)(void);

typedef struct {
	int leader;
	int instructions;
	int available;
} pmu_t;

typedef struct {
	double tsc;
	double cycles;
	double instructions;
} measurement_t;

__attribute__((noinline)) static void control_forward2_raw(void)
{
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(control_a, input_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(control_b, input_b);
}

__attribute__((noinline)) static void candidate_forward2_raw(void)
{
	gt32_spcrt_forward_raw_asm(candidate_a, input_a);
	gt32_spcrt_forward_raw_asm(candidate_b, input_b);
}

__attribute__((noinline)) static void candidate_forward2_repaired(void)
{
	gt32_spcrt_forward_a_repaired_asm(candidate_a, input_a);
	gt32_spcrt_forward_raw_asm(candidate_b, input_b);
}

__attribute__((noinline)) static void candidate_forward_raw_one(void)
{
	gt32_spcrt_forward_raw_asm(candidate_a, input_a);
}

__attribute__((noinline)) static void candidate_forward_repaired_one(void)
{
	gt32_spcrt_forward_a_repaired_asm(candidate_a, input_a);
}

__attribute__((noinline)) static void candidate_forward_repaired_r1_one(void)
{
	gt32_spcrt_forward_a_repaired_r1_asm(candidate_a, input_a);
}

__attribute__((noinline)) static void candidate_forward_repaired_r2_one(void)
{
	gt32_spcrt_forward_a_repaired_r2_shared_asm(candidate_a, input_a);
}

__attribute__((noinline)) static void candidate_forward_raw_r2_one(void)
{
	gt32_spcrt_forward_raw_r2_shared_asm(candidate_a, input_a);
}

__attribute__((noinline)) static void control_2f_b3(void)
{
	control_forward2_raw();
	gt32_tile4_basemul_b3_late_asm(output, control_a, control_b);
}

__attribute__((noinline)) static void candidate_2f_b3(void)
{
	candidate_forward2_repaired();
	gt32_spcrt_basemul_b3_asm(output, candidate_a, candidate_b);
}

__attribute__((noinline)) static void candidate_2f_b3_r1(void)
{
	gt32_spcrt_forward_a_repaired_r1_asm(candidate_a, input_a);
	gt32_spcrt_forward_raw_asm(candidate_b, input_b);
	gt32_spcrt_basemul_b3_asm(output, candidate_a, candidate_b);
}

__attribute__((noinline)) static void candidate_2f_b3_r2(void)
{
	gt32_spcrt_forward_a_repaired_r2_shared_asm(candidate_a, input_a);
	gt32_spcrt_forward_raw_r2_shared_asm(candidate_b, input_b);
	gt32_spcrt_basemul_b3_asm(output, candidate_a, candidate_b);
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
	pmu_t result = {-1, -1, 0};
	result.leader = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1, 1);
	if (result.leader < 0)
		return result;
	result.instructions = perf_open(PERF_COUNT_HW_INSTRUCTIONS,
		result.leader, 0);
	if (result.instructions < 0)
		return result;
	result.available = 1;
	return result;
}

static uint64_t tsc_start(void)
{
	_mm_lfence();
	return __rdtsc();
}

static uint64_t tsc_stop(void)
{
	unsigned aux;
	const uint64_t value = __rdtscp(&aux);
	_mm_lfence();
	return value;
}

static measurement_t measure(bench_fn fn, unsigned iterations, pmu_t *pmu)
{
	uint64_t counts[3] = {0, 0, 0};
	measurement_t result = {0, 0, 0};
	if (pmu->available != 0) {
		(void)ioctl(pmu->leader, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
		(void)ioctl(pmu->leader, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
	}
	const uint64_t begin = tsc_start();
	for (unsigned i = 0; i < iterations; i++)
		fn();
	const uint64_t end = tsc_stop();
	if (pmu->available != 0) {
		(void)ioctl(pmu->leader, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
		if (read(pmu->leader, counts, sizeof counts) != (ssize_t)sizeof counts)
			pmu->available = 0;
	}
	result.tsc = (double)(end - begin) / (double)iterations;
	if (pmu->available != 0) {
		result.cycles = (double)counts[1] / (double)iterations;
		result.instructions = (double)counts[2] / (double)iterations;
	}
	sink += (uint16_t)output[iterations % WORDS];
	return result;
}

static void pair(const char *region, unsigned sample, bench_fn control,
	bench_fn candidate, unsigned iterations, pmu_t *pmu)
{
	measurement_t a;
	measurement_t b;
	if ((sample & 1U) == 0U) {
		a = measure(control, iterations, pmu);
		b = measure(candidate, iterations, pmu);
	} else {
		b = measure(candidate, iterations, pmu);
		a = measure(control, iterations, pmu);
	}
	printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n",
		region, sample, a.tsc, b.tsc, b.tsc - a.tsc,
		a.cycles, b.cycles, b.cycles - a.cycles,
		a.instructions, b.instructions, b.instructions - a.instructions);
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 5000U;
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof set, &set) != 0)
		perror("sched_setaffinity");
	for (int i = 0; i < WORDS; i++) {
		input_a[i] = (int16_t)((i * 5 + 1) % 8 - 3);
		input_b[i] = (int16_t)((i * 7 + 3) % 8 - 3);
	}
	control_2f_b3();
	candidate_2f_b3();
	pmu_t pmu = pmu_open();
	printf("META,iterations,%u,pmu,%d,errno,%d\n",
		iterations, pmu.available, pmu.available != 0 ? 0 : errno);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		pair("forward2_raw", sample, control_forward2_raw,
			candidate_forward2_raw, iterations, &pmu);
		pair("repair_r0", sample, candidate_forward_raw_one,
			candidate_forward_repaired_one, iterations, &pmu);
		pair("repair_r1", sample, candidate_forward_raw_one,
			candidate_forward_repaired_r1_one, iterations, &pmu);
		pair("repair_r2", sample, candidate_forward_raw_r2_one,
			candidate_forward_repaired_r2_one, iterations, &pmu);
		pair("forward2_with_repair", sample, control_forward2_raw,
			candidate_forward2_repaired, iterations, &pmu);
		pair("2f_b3_r0", sample, control_2f_b3,
			candidate_2f_b3, iterations, &pmu);
		pair("2f_b3_r1", sample, control_2f_b3,
			candidate_2f_b3_r1, iterations, &pmu);
		pair("2f_b3_r2", sample, control_2f_b3,
			candidate_2f_b3_r2, iterations, &pmu);
	}
	return sink == UINT64_MAX ? 1 : 0;
}
