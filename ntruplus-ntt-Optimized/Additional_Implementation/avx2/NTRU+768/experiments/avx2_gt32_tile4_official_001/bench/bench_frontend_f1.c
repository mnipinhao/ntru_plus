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

typedef void (*bench_fn)(void);

static _Alignas(64) int16_t input_a[WORDS], input_b[WORDS];
static _Alignas(64) int16_t frontend_a[WORDS], frontend_b[WORDS];
static _Alignas(64) int16_t output_a[WORDS], output_b[WORDS];
static volatile uint64_t sink;

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

static void frontend_control(void)
{
	gt32_tile4_frontend_wide_raw_asm(frontend_a, input_a);
	sink += (uint16_t)frontend_a[0];
}

static void frontend_candidate(void)
{
	gt32_tile4_frontend_wide_raw_f1_asm(frontend_a, input_a);
	sink += (uint16_t)frontend_a[0];
}

static void frontend_f4(void)
{
	gt32_tile4_frontend_wide_raw_f4_asm(frontend_a, input_a);
	sink += (uint16_t)frontend_a[0];
}

static void frontend_f14(void)
{
	gt32_tile4_frontend_wide_raw_f14_asm(frontend_a, input_a);
	sink += (uint16_t)frontend_a[0];
}

static void frontend_f14_w2(void)
{
	gt32_tile4_frontend_wide_raw_f14_w2_asm(frontend_a, input_a);
	sink += (uint16_t)frontend_a[0];
}

static void full_control(void)
{
	gt32_tile4_frontend_wide_raw_asm(frontend_a, input_a);
	gt32_tile4_forward_all_pair_asm(output_a, frontend_a);
	sink += (uint16_t)output_a[0];
}

static void full_candidate(void)
{
	gt32_tile4_frontend_wide_raw_f1_asm(frontend_a, input_a);
	gt32_tile4_forward_all_pair_asm(output_a, frontend_a);
	sink += (uint16_t)output_a[0];
}

static void full_f4(void)
{
	gt32_tile4_frontend_wide_raw_f4_asm(frontend_a, input_a);
	gt32_tile4_forward_all_pair_asm(output_a, frontend_a);
	sink += (uint16_t)output_a[0];
}

static void full_f14(void)
{
	gt32_tile4_frontend_wide_raw_f14_asm(frontend_a, input_a);
	gt32_tile4_forward_all_pair_asm(output_a, frontend_a);
	sink += (uint16_t)output_a[0];
}

static void full_f14_w2(void)
{
	gt32_tile4_frontend_wide_raw_f14_w2_asm(frontend_a, input_a);
	gt32_tile4_forward_all_pair_asm(output_a, frontend_a);
	sink += (uint16_t)output_a[0];
}

static void two_control(void)
{
	gt32_tile4_frontend_wide_raw_asm(frontend_a, input_a);
	gt32_tile4_forward_all_pair_asm(output_a, frontend_a);
	gt32_tile4_frontend_wide_raw_asm(frontend_b, input_b);
	gt32_tile4_forward_all_pair_asm(output_b, frontend_b);
	sink += (uint16_t)(output_a[0] + output_b[0]);
}

static void two_candidate(void)
{
	gt32_tile4_frontend_wide_raw_f1_asm(frontend_a, input_a);
	gt32_tile4_forward_all_pair_asm(output_a, frontend_a);
	gt32_tile4_frontend_wide_raw_f1_asm(frontend_b, input_b);
	gt32_tile4_forward_all_pair_asm(output_b, frontend_b);
	sink += (uint16_t)(output_a[0] + output_b[0]);
}

static void two_f4(void)
{
	gt32_tile4_frontend_wide_raw_f4_asm(frontend_a, input_a);
	gt32_tile4_forward_all_pair_asm(output_a, frontend_a);
	gt32_tile4_frontend_wide_raw_f4_asm(frontend_b, input_b);
	gt32_tile4_forward_all_pair_asm(output_b, frontend_b);
	sink += (uint16_t)(output_a[0] + output_b[0]);
}

static void two_f14(void)
{
	gt32_tile4_frontend_wide_raw_f14_asm(frontend_a, input_a);
	gt32_tile4_forward_all_pair_asm(output_a, frontend_a);
	gt32_tile4_frontend_wide_raw_f14_asm(frontend_b, input_b);
	gt32_tile4_forward_all_pair_asm(output_b, frontend_b);
	sink += (uint16_t)(output_a[0] + output_b[0]);
}

static void two_f14_w2(void)
{
	gt32_tile4_frontend_wide_raw_f14_w2_asm(frontend_a, input_a);
	gt32_tile4_forward_all_pair_asm(output_a, frontend_a);
	gt32_tile4_frontend_wide_raw_f14_w2_asm(frontend_b, input_b);
	gt32_tile4_forward_all_pair_asm(output_b, frontend_b);
	sink += (uint16_t)(output_a[0] + output_b[0]);
}

static void n5_wave_control(void)
{
	gt32_tile4_forward_all_pair_asm(output_a, frontend_a);
	sink += (uint16_t)output_a[0];
}

static void n5_wave_candidate(void)
{
	gt32_tile4_forward_all_pair_wave_asm(output_a, frontend_a);
	sink += (uint16_t)output_a[0];
}

static void full_f14_w2_n5_wave(void)
{
	gt32_tile4_frontend_wide_raw_f14_w2_asm(frontend_a, input_a);
	gt32_tile4_forward_all_pair_wave_asm(output_a, frontend_a);
	sink += (uint16_t)output_a[0];
}

static double measure(bench_fn function, unsigned iterations)
{
	const uint64_t start = tsc_start();
	for (unsigned i = 0; i < iterations; i++)
		function();
	return (double)(tsc_stop() - start) / iterations;
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

static double measure_cycles(bench_fn function, unsigned iterations, int fd)
{
	uint64_t count = 0;
	(void)ioctl(fd, PERF_EVENT_IOC_RESET, 0);
	(void)ioctl(fd, PERF_EVENT_IOC_ENABLE, 0);
	for (unsigned i = 0; i < iterations; i++)
		function();
	(void)ioctl(fd, PERF_EVENT_IOC_DISABLE, 0);
	if (read(fd, &count, sizeof count) != (ssize_t)sizeof count)
		return 0.0;
	return (double)count / iterations;
}

static int compare_double(const void *left, const void *right)
{
	const double a = *(const double *)left;
	const double b = *(const double *)right;
	return (a > b) - (a < b);
}

static double median(double values[SAMPLES])
{
	double copy[SAMPLES];
	memcpy(copy, values, sizeof copy);
	qsort(copy, SAMPLES, sizeof copy[0], compare_double);
	return 0.5 * (copy[9] + copy[10]);
}

static void run_region(const char *name, bench_fn control, bench_fn candidate,
	unsigned iterations, int perf_fd)
{
	double a[SAMPLES], b[SAMPLES], delta[SAMPLES];
	unsigned wins = 0;
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0U) {
			a[sample] = measure(control, iterations);
			b[sample] = measure(candidate, iterations);
		} else {
			b[sample] = measure(candidate, iterations);
			a[sample] = measure(control, iterations);
		}
		delta[sample] = b[sample] - a[sample];
		wins += delta[sample] < 0.0;
	}
	printf("region=%s control=%.3f candidate=%.3f paired_delta=%.3f wins=%u/%u\n",
		name, median(a), median(b), median(delta), wins, SAMPLES);
	if (perf_fd >= 0) {
		double cycles_a[SAMPLES], cycles_b[SAMPLES], cycles_delta[SAMPLES];
		unsigned cycle_wins = 0;
		for (unsigned sample = 0; sample < SAMPLES; sample++) {
			if ((sample & 1U) == 0U) {
				cycles_a[sample] = measure_cycles(control, iterations, perf_fd);
				cycles_b[sample] = measure_cycles(candidate, iterations, perf_fd);
			} else {
				cycles_b[sample] = measure_cycles(candidate, iterations, perf_fd);
				cycles_a[sample] = measure_cycles(control, iterations, perf_fd);
			}
			cycles_delta[sample] = cycles_b[sample] - cycles_a[sample];
			cycle_wins += cycles_delta[sample] < 0.0;
		}
		printf("pmu_region=%s control_cycles=%.3f candidate_cycles=%.3f paired_delta=%.3f wins=%u/%u\n",
			name, median(cycles_a), median(cycles_b), median(cycles_delta),
			cycle_wins, SAMPLES);
	}
}

static uint32_t random32(uint32_t *state)
{
	*state ^= *state << 13;
	*state ^= *state >> 17;
	*state ^= *state << 5;
	return *state;
}

static int correctness(void)
{
	uint32_t state = UINT32_C(0xf1000001);
	for (unsigned trial = 0; trial < 1000; trial++) {
		for (unsigned i = 0; i < WORDS; i++)
			input_a[i] = (int16_t)((int)(random32(&state) & 7U) - 3);
		gt32_tile4_frontend_wide_raw_asm(frontend_a, input_a);
		gt32_tile4_frontend_wide_raw_f1_asm(frontend_b, input_a);
		if (memcmp(frontend_a, frontend_b, sizeof frontend_a) != 0) {
			fprintf(stderr, "frontend mismatch at trial %u\n", trial);
			return 0;
		}
		gt32_tile4_frontend_wide_raw_f4_asm(frontend_b, input_a);
		if (memcmp(frontend_a, frontend_b, sizeof frontend_a) != 0) {
			fprintf(stderr, "F4 frontend mismatch at trial %u\n", trial);
			return 0;
		}
		gt32_tile4_frontend_wide_raw_f14_asm(frontend_b, input_a);
		if (memcmp(frontend_a, frontend_b, sizeof frontend_a) != 0) {
			fprintf(stderr, "F14 frontend mismatch at trial %u\n", trial);
			return 0;
		}
		gt32_tile4_frontend_wide_raw_f14_w2_asm(frontend_b, input_a);
		if (memcmp(frontend_a, frontend_b, sizeof frontend_a) != 0) {
			fprintf(stderr, "F14-W2 frontend mismatch at trial %u\n", trial);
			return 0;
		}
		gt32_tile4_forward_all_pair_asm(output_a, frontend_a);
		gt32_tile4_forward_all_pair_wave_asm(output_b, frontend_b);
		if (memcmp(output_a, output_b, sizeof output_a) != 0) {
			fprintf(stderr, "forward wave mismatch at trial %u\n", trial);
			return 0;
		}
	}
	return 1;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1 ? (unsigned)strtoul(argv[1], NULL, 0) : 4000U;
	const unsigned cpu = argc > 2 ? (unsigned)strtoul(argv[2], NULL, 0) : 1U;
	const int perf_fd = perf_open_cycles();
	cpu_set_t cpuset;
	CPU_ZERO(&cpuset);
	CPU_SET(cpu, &cpuset);
	if (sched_setaffinity(0, sizeof cpuset, &cpuset) != 0) {
		perror("sched_setaffinity");
		return 2;
	}
	for (unsigned i = 0; i < WORDS; i++) {
		input_a[i] = (int16_t)((int)(i & 7U) - 3);
		input_b[i] = (int16_t)((int)((3U * i + 1U) & 7U) - 3);
	}
	if (!correctness())
		return 1;
	/* Restore deterministic inputs after the differential trials. */
	for (unsigned i = 0; i < WORDS; i++) {
		input_a[i] = (int16_t)((int)(i & 7U) - 3);
		input_b[i] = (int16_t)((int)((3U * i + 1U) & 7U) - 3);
	}
	for (unsigned warm = 0; warm < 100; warm++) {
		full_control();
		full_candidate();
	}
	printf("iterations=%u cpu=%u correctness=pass\n", iterations, cpu);
	run_region("frontend", frontend_control, frontend_candidate, iterations, perf_fd);
	run_region("forward", full_control, full_candidate, iterations, perf_fd);
	run_region("2forward", two_control, two_candidate, iterations, perf_fd);
	run_region("frontend_f4", frontend_control, frontend_f4, iterations, perf_fd);
	run_region("forward_f4", full_control, full_f4, iterations, perf_fd);
	run_region("2forward_f4", two_control, two_f4, iterations, perf_fd);
	run_region("frontend_f14", frontend_control, frontend_f14, iterations, perf_fd);
	run_region("forward_f14", full_control, full_f14, iterations, perf_fd);
	run_region("2forward_f14", two_control, two_f14, iterations, perf_fd);
	run_region("frontend_f14_w2", frontend_f14, frontend_f14_w2, iterations, perf_fd);
	run_region("forward_f14_w2", full_f14, full_f14_w2, iterations, perf_fd);
	run_region("2forward_f14_w2", two_f14, two_f14_w2, iterations, perf_fd);
	run_region("n5_wave", n5_wave_control, n5_wave_candidate, iterations, perf_fd);
	run_region("forward_f14_w2_n5_wave", full_f14, full_f14_w2_n5_wave,
		iterations, perf_fd);
	if (perf_fd >= 0)
		(void)close(perf_fd);
	else
		printf("pmu=unavailable\n");
	printf("sink=%llu\n", (unsigned long long)sink);
	return 0;
}
