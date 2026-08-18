#define _GNU_SOURCE
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

enum { WORDS = GT32_TILE4_POLY_WORDS, SAMPLES = 20 };
typedef void (*fn)(int16_t *, const int16_t *, const int16_t *);

static _Alignas(64) int16_t a[WORDS], b[WORDS], out0[WORDS], out1[WORDS];
static volatile uint64_t sink;

static uint32_t random32(uint32_t *state)
{
	*state ^= *state << 13;
	*state ^= *state >> 17;
	*state ^= *state << 5;
	return *state;
}

static uint64_t start_tsc(void) { _mm_lfence(); return __rdtsc(); }
static uint64_t stop_tsc(void)
{
	unsigned aux;
	const uint64_t value = __rdtscp(&aux);
	_mm_lfence();
	return value;
}

static int perf_open_cycles(void)
{
	struct perf_event_attr attr;
	memset(&attr, 0, sizeof attr);
	attr.type = PERF_TYPE_HARDWARE;
	attr.size = sizeof attr;
	attr.config = PERF_COUNT_HW_CPU_CYCLES;
	attr.disabled = 1U;
	attr.exclude_kernel = 1U;
	attr.exclude_hv = 1U;
	const long fd = syscall(SYS_perf_event_open, &attr, 0, -1, -1, 0UL);
	return fd < 0 ? -1 : (int)fd;
}

static double measure_tsc(fn function, unsigned iterations)
{
	const uint64_t start = start_tsc();
	for (unsigned i = 0; i < iterations; i++) function(out0, a, b);
	const uint64_t stop = stop_tsc();
	sink += (uint16_t)out0[0];
	return (double)(stop - start) / iterations;
}

static double measure_cycles(fn function, unsigned iterations, int fd)
{
	uint64_t count = 0;
	(void)ioctl(fd, PERF_EVENT_IOC_RESET, 0);
	(void)ioctl(fd, PERF_EVENT_IOC_ENABLE, 0);
	for (unsigned i = 0; i < iterations; i++) function(out0, a, b);
	(void)ioctl(fd, PERF_EVENT_IOC_DISABLE, 0);
	if (read(fd, &count, sizeof count) != (ssize_t)sizeof count) return 0.0;
	sink += (uint16_t)out0[0];
	return (double)count / iterations;
}

static int cmp_double(const void *left, const void *right)
{
	const double x = *(const double *)left, y = *(const double *)right;
	return (x > y) - (x < y);
}

static double median(double values[SAMPLES])
{
	qsort(values, SAMPLES, sizeof values[0], cmp_double);
	return 0.5 * (values[9] + values[10]);
}

static int correctness(void)
{
	uint32_t state = UINT32_C(0xb3a0e001);
	for (unsigned trial = 0; trial < 1000; trial++) {
		for (unsigned i = 0; i < WORDS; i++) {
			a[i] = (int16_t)((int)(random32(&state) % 4001U) - 2000);
			b[i] = (int16_t)((int)(random32(&state) % 4001U) - 2000);
		}
		gt32_tile4_basemul_general_soa_soa_to_soa_asm(out0, a, b);
		gt32_tile4_basemul_general_soa_soa_to_soa_wave_asm(out1, a, b);
		if (memcmp(out0, out1, sizeof out0) != 0) {
			fprintf(stderr, "B3 wave mismatch at trial %u\n", trial);
			return 0;
		}
	}
	return 1;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1 ? (unsigned)strtoul(argv[1], NULL, 0) : 4000U;
	const unsigned cpu = argc > 2 ? (unsigned)strtoul(argv[2], NULL, 0) : 1U;
	cpu_set_t set;
	CPU_ZERO(&set); CPU_SET(cpu, &set);
	if (sched_setaffinity(0, sizeof set, &set) != 0) { perror("sched_setaffinity"); return 2; }
	if (!correctness()) return 1;
	for (unsigned i = 0; i < WORDS; i++) { a[i] = (int16_t)(i % 3457U); b[i] = (int16_t)((3U*i+1U)%3457U); }
	const int fd = perf_open_cycles();
	double ta[SAMPLES], tb[SAMPLES], td[SAMPLES], ca[SAMPLES], cb[SAMPLES], cd[SAMPLES];
	unsigned tw = 0, cw = 0;
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0U) {
			ta[sample] = measure_tsc(gt32_tile4_basemul_general_soa_soa_to_soa_asm, iterations);
			tb[sample] = measure_tsc(gt32_tile4_basemul_general_soa_soa_to_soa_wave_asm, iterations);
		} else {
			tb[sample] = measure_tsc(gt32_tile4_basemul_general_soa_soa_to_soa_wave_asm, iterations);
			ta[sample] = measure_tsc(gt32_tile4_basemul_general_soa_soa_to_soa_asm, iterations);
		}
		td[sample] = tb[sample] - ta[sample]; tw += td[sample] < 0.0;
		if (fd >= 0) {
			ca[sample] = measure_cycles(gt32_tile4_basemul_general_soa_soa_to_soa_asm, iterations, fd);
			cb[sample] = measure_cycles(gt32_tile4_basemul_general_soa_soa_to_soa_wave_asm, iterations, fd);
			cd[sample] = cb[sample] - ca[sample]; cw += cd[sample] < 0.0;
		}
	}
	printf("region=b3_wave control=%.3f candidate=%.3f paired_delta=%.3f wins=%u/20\n",
		median(ta), median(tb), median(td), tw);
	if (fd >= 0) {
		printf("pmu_region=b3_wave control_cycles=%.3f candidate_cycles=%.3f paired_delta=%.3f wins=%u/20\n",
			median(ca), median(cb), median(cd), cw);
		(void)close(fd);
	}
	printf("correctness=pass iterations=%u cpu=%u sink=%llu\n", iterations, cpu,
		(unsigned long long)sink);
	return 0;
}
