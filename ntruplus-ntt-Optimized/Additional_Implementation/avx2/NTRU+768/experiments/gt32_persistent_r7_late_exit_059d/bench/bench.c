#define _GNU_SOURCE
#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define Q 3457
#define SAMPLES 31
#define BLOCK_ITERS 20000
#define FULL_ITERS 3000

void r7_late_exit_block0_asm(uint8_t *, const int16_t *);
void r7_late_exit_full_asm(uint8_t *, const int16_t *);
void r7_current_q24_block0_asm(uint8_t *, const int16_t *);
void gt32_q24_encode_soa_asm(uint8_t *, const int16_t *);

static int16_t quartic[12][4][16] __attribute__((aligned(32)));
static int16_t r7[12][7][16] __attribute__((aligned(32)));
static uint8_t control[1152 + 32] __attribute__((aligned(32)));
static uint8_t candidate[1152 + 32] __attribute__((aligned(32)));
static volatile uint64_t sink;

static int modq(int64_t x) {
	x %= Q;
	if (x < 0) x += Q;
	return (int)x;
}

static int16_t balanced(int64_t x) {
	int v = modq(x);
	if (v > Q / 2) v -= Q;
	return (int16_t)v;
}

static uint64_t rng_state = 0x059d123456789abcULL;
static uint32_t rng32(void) {
	rng_state ^= rng_state << 7;
	rng_state ^= rng_state >> 9;
	return (uint32_t)rng_state;
}

static int eval4(const int16_t a[4], int t) {
	int64_t value = a[3];
	value = value * t + a[2];
	value = value * t + a[1];
	value = value * t + a[0];
	return modq(value);
}

static void prepare_case(void) {
	static const int points[7] = {0, 1, -1, 2, -2, 4, -4};
	for (int block = 0; block < 12; ++block) {
		for (int lane = 0; lane < 16; ++lane) {
			int16_t a[4];
			for (int degree = 0; degree < 4; ++degree) {
				a[degree] = (int16_t)((int)(rng32() % Q) - Q / 2);
				quartic[block][degree][lane] = a[degree];
			}
			int p[7];
			for (int i = 0; i < 7; ++i) p[i] = eval4(a, points[i]);
			r7[block][0][lane] = balanced(p[0]);
			r7[block][1][lane] = balanced(p[1] + p[2]);
			r7[block][2][lane] = balanced(p[1] - p[2]);
			r7[block][3][lane] = balanced(p[3] + p[4]);
			r7[block][4][lane] = balanced(p[3] - p[4]);
			r7[block][5][lane] = balanced(p[5] + p[6]);
			r7[block][6][lane] = balanced(p[5] - p[6]);
		}
	}
}

static inline uint64_t ticks(void) {
	unsigned aux;
	_mm_lfence();
	uint64_t x = __rdtscp(&aux);
	_mm_lfence();
	return x;
}

static int cmp_u64(const void *a, const void *b) {
	uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;
	return (x > y) - (x < y);
}

static uint64_t median(uint64_t *values) {
	qsort(values, SAMPLES, sizeof(*values), cmp_u64);
	return values[SAMPLES / 2];
}

static uint64_t measure_block(int candidate_path) {
	uint64_t values[SAMPLES];
	for (int sample = 0; sample < SAMPLES; ++sample) {
		uint64_t begin = ticks();
		for (int i = 0; i < BLOCK_ITERS; ++i) {
			if (candidate_path) r7_late_exit_block0_asm(candidate, &r7[0][0][0]);
			else r7_current_q24_block0_asm(control, &quartic[0][0][0]);
			sink += candidate_path ? candidate[i & 63] : control[i & 63];
		}
		values[sample] = (ticks() - begin) / BLOCK_ITERS;
	}
	return median(values);
}

static uint64_t measure_full(int candidate_path) {
	uint64_t values[SAMPLES];
	for (int sample = 0; sample < SAMPLES; ++sample) {
		uint64_t begin = ticks();
		for (int i = 0; i < FULL_ITERS; ++i) {
			if (candidate_path) r7_late_exit_full_asm(candidate, &r7[0][0][0]);
			else gt32_q24_encode_soa_asm(control, &quartic[0][0][0]);
			sink += candidate_path ? candidate[i % 1152] : control[i % 1152];
		}
		values[sample] = (ticks() - begin) / FULL_ITERS;
	}
	return median(values);
}

static int pmu_mode(const char *mode) {
	prepare_case();
	const int iterations = 2000000;
	if (!strcmp(mode, "block-control")) {
		for (int i = 0; i < iterations; ++i) {
			r7_current_q24_block0_asm(control, &quartic[0][0][0]);
			sink += control[i & 63];
		}
	} else if (!strcmp(mode, "block-candidate")) {
		for (int i = 0; i < iterations; ++i) {
			r7_late_exit_block0_asm(candidate, &r7[0][0][0]);
			sink += candidate[i & 63];
		}
	} else if (!strcmp(mode, "full-control")) {
		for (int i = 0; i < iterations / 8; ++i) {
			gt32_q24_encode_soa_asm(control, &quartic[0][0][0]);
			sink += control[i % 1152];
		}
	} else if (!strcmp(mode, "full-candidate")) {
		for (int i = 0; i < iterations / 8; ++i) {
			r7_late_exit_full_asm(candidate, &r7[0][0][0]);
			sink += candidate[i % 1152];
		}
	} else {
		return 2;
	}
	printf("%llu\n", (unsigned long long)sink);
	return 0;
}

int main(int argc, char **argv) {
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(2, &set);
	(void)sched_setaffinity(0, sizeof(set), &set);
	if (argc == 3 && !strcmp(argv[1], "--pmu")) return pmu_mode(argv[2]);

	for (int trial = 0; trial < 1000; ++trial) {
		prepare_case();
		memset(control, 0xa5, sizeof(control));
		memset(candidate, 0x5a, sizeof(candidate));
		gt32_q24_encode_soa_asm(control, &quartic[0][0][0]);
		r7_late_exit_full_asm(candidate, &r7[0][0][0]);
		if (memcmp(control, candidate, 1152) != 0) {
			for (int group = 0; group < 12; ++group) {
				int mismatches = 0;
				for (int i = 0; i < 96; ++i)
					mismatches += control[group * 96 + i] != candidate[group * 96 + i];
				fprintf(stderr, "group %d mismatches %d\n", group, mismatches);
			}
			for (int i = 0; i < 1152; ++i)
				if (control[i] != candidate[i]) {
					fprintf(stderr, "mismatch trial=%d byte=%d control=%u candidate=%u\n",
					        trial, i, control[i], candidate[i]);
					return 1;
			}
		}
		for (int i = 1152; i < (int)sizeof(control); ++i) {
			if (control[i] != 0xa5 || candidate[i] != 0x5a) {
				fprintf(stderr, "output canary overwritten at byte %d control=%u candidate=%u\n",
				        i, control[i], candidate[i]);
				return 1;
			}
		}
	}

	prepare_case();
	r7_current_q24_block0_asm(control, &quartic[0][0][0]);
	r7_late_exit_block0_asm(candidate, &r7[0][0][0]);
	if (memcmp(control, candidate, 96) != 0) {
		fprintf(stderr, "block0 mismatch\n");
		return 1;
	}

	uint64_t bc = measure_block(0), bn = measure_block(1);
	uint64_t fc = measure_full(0), fn = measure_full(1);
	printf("{\n");
	printf("  \"correctness_trials\": 1000,\n");
	printf("  \"block_control_tsc\": %llu,\n", (unsigned long long)bc);
	printf("  \"block_candidate_tsc\": %llu,\n", (unsigned long long)bn);
	printf("  \"block_delta_tsc\": %lld,\n", (long long)bn - (long long)bc);
	printf("  \"full_control_tsc\": %llu,\n", (unsigned long long)fc);
	printf("  \"full_candidate_tsc\": %llu,\n", (unsigned long long)fn);
	printf("  \"full_delta_tsc\": %lld,\n", (long long)fn - (long long)fc);
	printf("  \"sink\": %llu\n", (unsigned long long)sink);
	printf("}\n");
	return 0;
}
