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
#include "../generated/tile4_serialized_mapping.h"

enum { WORDS = GT32_TILE4_POLY_WORDS, BYTES = GT32_TILE4_SERIALIZED_BYTES,
	SAMPLES = 20 };
typedef void (*bench_fn)(void);

static _Alignas(64) int16_t input_a[WORDS], input_b[WORDS];
static _Alignas(64) uint8_t output_a[BYTES], output_b[BYTES];
static volatile uint64_t sink;

static uint64_t start_tsc(void) { _mm_lfence(); return __rdtsc(); }
static uint64_t stop_tsc(void) {
	unsigned aux; uint64_t value = __rdtscp(&aux); _mm_lfence(); return value;
}

static void control_one(void) {
	gt32_q24_encode_soa_lazy10788_asm(output_a, input_a); sink += output_a[0];
}
static void candidate_one(void) {
	gt32_q24_encode_soa_tf1_asm(output_a, input_a); sink += output_a[0];
}
static void control_two(void) {
	gt32_q24_encode_soa_lazy10788_asm(output_a, input_a);
	gt32_q24_encode_soa_lazy10788_asm(output_b, input_b);
	sink += output_a[0] + output_b[0];
}
static void candidate_two(void) {
	gt32_q24_encode_soa_tf1_asm(output_a, input_a);
	gt32_q24_encode_soa_tf1_asm(output_b, input_b);
	sink += output_a[0] + output_b[0];
}

static int perf_open(uint64_t config) {
	struct perf_event_attr attr;
	memset(&attr, 0, sizeof attr); attr.type = PERF_TYPE_HARDWARE;
	attr.size = sizeof attr; attr.config = config; attr.disabled = 1;
	attr.exclude_kernel = 1; attr.exclude_hv = 1;
	return (int)syscall(SYS_perf_event_open, &attr, 0, -1, -1, 0UL);
}
static double measure_tsc(bench_fn fn, unsigned iterations) {
	uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++) fn();
	return (double)(stop_tsc() - begin) / iterations;
}
static double measure_perf(bench_fn fn, unsigned iterations, int fd) {
	uint64_t count = 0;
	(void)ioctl(fd, PERF_EVENT_IOC_RESET, 0);
	(void)ioctl(fd, PERF_EVENT_IOC_ENABLE, 0);
	for (unsigned i = 0; i < iterations; i++) fn();
	(void)ioctl(fd, PERF_EVENT_IOC_DISABLE, 0);
	if (read(fd, &count, sizeof count) != (ssize_t)sizeof count) return 0.0;
	return (double)count / iterations;
}
static int cmp_double(const void *a, const void *b) {
	double x = *(const double *)a, y = *(const double *)b;
	return (x > y) - (x < y);
}
static double median(double values[SAMPLES]) {
	double copy[SAMPLES]; memcpy(copy, values, sizeof copy);
	qsort(copy, SAMPLES, sizeof copy[0], cmp_double);
	return 0.5 * (copy[9] + copy[10]);
}
static void run_metric(const char *region, const char *metric, bench_fn control,
	bench_fn candidate, unsigned iterations, int fd) {
	double a[SAMPLES], b[SAMPLES], delta[SAMPLES]; unsigned wins = 0;
	for (unsigned i = 0; i < SAMPLES; i++) {
		if ((i & 1U) == 0) {
			a[i] = fd < 0 ? measure_tsc(control, iterations)
				: measure_perf(control, iterations, fd);
			b[i] = fd < 0 ? measure_tsc(candidate, iterations)
				: measure_perf(candidate, iterations, fd);
		} else {
			b[i] = fd < 0 ? measure_tsc(candidate, iterations)
				: measure_perf(candidate, iterations, fd);
			a[i] = fd < 0 ? measure_tsc(control, iterations)
				: measure_perf(control, iterations, fd);
		}
		delta[i] = b[i] - a[i]; wins += delta[i] < 0.0;
	}
	printf("region=%s metric=%s control=%.3f candidate=%.3f delta=%.3f wins=%u/%u\n",
		region, metric, median(a), median(b), median(delta), wins, SAMPLES);
}

static void reference_pack(uint8_t out[BYTES], const int16_t in[WORDS]) {
	for (unsigned pair = 0; pair < WORDS / 2; pair++) {
		int x = in[gt32_tile4_serialized_to_bm_soa[2 * pair]] % GT32_TILE4_Q;
		int y = in[gt32_tile4_serialized_to_bm_soa[2 * pair + 1]] % GT32_TILE4_Q;
		if (x < 0)
			x += GT32_TILE4_Q;
		if (y < 0)
			y += GT32_TILE4_Q;
		out[3 * pair] = (uint8_t)x;
		out[3 * pair + 1] = (uint8_t)((unsigned)x >> 8)
			| (uint8_t)((unsigned)y << 4);
		out[3 * pair + 2] = (uint8_t)((unsigned)y >> 4);
	}
}
static int correctness(void) {
	uint8_t expected[BYTES];
	for (int value = -12699; value <= 12699; value++) {
		for (unsigned i = 0; i < WORDS; i++) input_a[i] = (int16_t)value;
		reference_pack(expected, input_a);
		gt32_q24_encode_soa_lazy10788_asm(output_a, input_a);
		gt32_q24_encode_soa_tf1_asm(output_b, input_a);
		if (memcmp(expected, output_a, BYTES) || memcmp(expected, output_b, BYTES)) {
			fprintf(stderr, "TF1 mismatch at value %d\n", value); return 0;
		}
	}
	return 1;
}

int main(int argc, char **argv) {
	unsigned iterations = argc > 1 ? (unsigned)strtoul(argv[1], NULL, 0) : 4000;
	unsigned cpu = argc > 2 ? (unsigned)strtoul(argv[2], NULL, 0) : 1;
	cpu_set_t set; CPU_ZERO(&set); CPU_SET(cpu, &set);
	if (sched_setaffinity(0, sizeof set, &set) != 0) { perror("affinity"); return 2; }
	if (!correctness()) return 1;
	for (unsigned i = 0; i < WORDS; i++) {
		input_a[i] = (int16_t)((int)(37 * i % 21577) - 10788);
		input_b[i] = (int16_t)((int)(61 * i % 25399) - 12699);
	}
	for (unsigned i = 0; i < 100; i++) { control_two(); candidate_two(); }
	int cycles = perf_open(PERF_COUNT_HW_CPU_CYCLES);
	int instructions = perf_open(PERF_COUNT_HW_INSTRUCTIONS);
	printf("iterations=%u cpu=%u correctness=pass\n", iterations, cpu);
	run_metric("lazy10788", "tsc", control_one, candidate_one, iterations, -1);
	run_metric("lazy10788", "core_cycles", control_one, candidate_one, iterations, cycles);
	run_metric("lazy10788", "instructions", control_one, candidate_one, iterations, instructions);
	/* Same exact reducer/body, but exercise the proven |x| <= 12699 contract. */
	memcpy(input_a, input_b, sizeof input_a);
	run_metric("highrange12699", "tsc", control_one, candidate_one, iterations, -1);
	run_metric("highrange12699", "core_cycles", control_one, candidate_one, iterations, cycles);
	run_metric("highrange12699", "instructions", control_one, candidate_one, iterations, instructions);
	for (unsigned i = 0; i < WORDS; i++)
		input_a[i] = (int16_t)((int)(37 * i % 21577) - 10788);
	run_metric("two_q24", "tsc", control_two, candidate_two, iterations, -1);
	run_metric("two_q24", "core_cycles", control_two, candidate_two, iterations, cycles);
	run_metric("two_q24", "instructions", control_two, candidate_two, iterations, instructions);
	if (cycles >= 0)
		close(cycles);
	if (instructions >= 0)
		close(instructions);
	printf("sink=%llu\n", (unsigned long long)sink); return 0;
}
