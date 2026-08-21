#define _GNU_SOURCE
#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define Q 3457
#define SAMPLES 31
#define FULL_ITERS 2000
#define BLOCK_ITERS 10000

void r7e_e1_block0_asm(uint8_t *, const int16_t *, const int16_t *, const int16_t *);
void r7e_e1_full_asm(uint8_t *, const int16_t *, const int16_t *, const int16_t *);
void r7e_e1_coeff_block0_asm(int16_t *, const int16_t *, const int16_t *, const int16_t *);
void r7e_e1_accum_block0_asm(int32_t *, const int16_t *, const int16_t *, const int16_t *);
void r7e_current_full_asm(uint8_t *, const int16_t *, const int16_t *, const int16_t *, int16_t *);
void r7e_e0_full_asm(uint8_t *, const int16_t *, const int16_t *, const int16_t *, int16_t *);

static int16_t hq[12][4][16] __attribute__((aligned(32)));
static int16_t rq[12][4][16] __attribute__((aligned(32)));
static int16_t mq[12][4][16] __attribute__((aligned(32)));
static int16_t he[12][7][16] __attribute__((aligned(32)));
static int16_t re[12][7][16] __attribute__((aligned(32)));
static int16_t me[12][7][16] __attribute__((aligned(32)));
static int16_t work[12][4][16] __attribute__((aligned(32)));
static int16_t e0scratch[12][7][16] __attribute__((aligned(32)));
static uint8_t control[1152 + 32] __attribute__((aligned(32)));
static uint8_t candidate[1152 + 32] __attribute__((aligned(32)));
static volatile uint64_t sink;

static uint64_t rng_state = 0x059e123456789abcULL;
static uint32_t rng32(void) {
	rng_state ^= rng_state << 7;
	rng_state ^= rng_state >> 9;
	return (uint32_t)rng_state;
}

static int modq(int64_t x) {
	x %= Q;
	if (x < 0) x += Q;
	return (int)x;
}

static int16_t balanced(int64_t x) {
	int value = modq(x);
	if (value > Q / 2) value -= Q;
	return (int16_t)value;
}

static int eval4(const int16_t a[4], int point) {
	int64_t value = a[3];
	value = value * point + a[2];
	value = value * point + a[1];
	value = value * point + a[0];
	return modq(value);
}

static void prepare_case(void) {
	static const int points[7] = {0, 1, -1, 2, -2, 4, -4};
	for (int block = 0; block < 12; ++block) {
		for (int lane = 0; lane < 16; ++lane) {
			int16_t a[4], b[4], m[4];
			for (int degree = 0; degree < 4; ++degree) {
				a[degree] = (int16_t)((int)(rng32() % Q) - Q / 2);
				b[degree] = (int16_t)((int)(rng32() % Q) - Q / 2);
				m[degree] = (int16_t)((int)(rng32() % Q) - Q / 2);
				hq[block][degree][lane] = a[degree];
				rq[block][degree][lane] = b[degree];
				mq[block][degree][lane] = m[degree];
			}
			for (int point = 0; point < 7; ++point) {
				he[block][point][lane] = balanced(eval4(a, points[point]));
				re[block][point][lane] = balanced(eval4(b, points[point]));
				me[block][point][lane] = balanced(eval4(m, points[point]));
			}
		}
	}
}

static void prepare_basis_case(void) {
	memset(hq, 0, sizeof(hq));
	memset(rq, 0, sizeof(rq));
	memset(mq, 0, sizeof(mq));
	memset(he, 0, sizeof(he));
	memset(re, 0, sizeof(re));
	memset(me, 0, sizeof(me));
	for (int block = 0; block < 12; ++block)
		for (int lane = 0; lane < 16; ++lane) {
			hq[block][3][lane] = 1;
			rq[block][3][lane] = 1;
			for (int point = 0; point < 7; ++point) {
				static const int points[7] = {0, 1, -1, 2, -2, 4, -4};
				he[block][point][lane] = balanced((int64_t)points[point] * points[point] * points[point]);
				re[block][point][lane] = he[block][point][lane];
			}
		}
}

static inline uint64_t ticks(void) {
	unsigned aux;
	_mm_lfence();
	uint64_t value = __rdtscp(&aux);
	_mm_lfence();
	return value;
}

static int cmp_u64(const void *left, const void *right) {
	uint64_t a = *(const uint64_t *)left, b = *(const uint64_t *)right;
	return (a > b) - (a < b);
}

static uint64_t median(uint64_t *values) {
	qsort(values, SAMPLES, sizeof(*values), cmp_u64);
	return values[SAMPLES / 2];
}

static uint64_t measure_full(int variant) {
	uint64_t values[SAMPLES];
	for (int sample = 0; sample < SAMPLES; ++sample) {
		uint64_t begin = ticks();
		for (int i = 0; i < FULL_ITERS; ++i) {
			if (variant == 2)
				r7e_e1_full_asm(candidate, &he[0][0][0], &re[0][0][0], &me[0][0][0]);
			else if (variant == 1)
				r7e_e0_full_asm(candidate, &he[0][0][0], &re[0][0][0],
				                 &me[0][0][0], &e0scratch[0][0][0]);
			else
				r7e_current_full_asm(control, &hq[0][0][0], &rq[0][0][0],
				                       &mq[0][0][0], &work[0][0][0]);
			sink += variant ? candidate[i % 1152] : control[i % 1152];
		}
		values[sample] = (ticks() - begin) / FULL_ITERS;
	}
	return median(values);
}

static uint64_t measure_candidate_block(void) {
	uint64_t values[SAMPLES];
	for (int sample = 0; sample < SAMPLES; ++sample) {
		uint64_t begin = ticks();
		for (int i = 0; i < BLOCK_ITERS; ++i) {
			r7e_e1_block0_asm(candidate, &he[0][0][0], &re[0][0][0], &me[0][0][0]);
			sink += candidate[i & 63];
		}
		values[sample] = (ticks() - begin) / BLOCK_ITERS;
	}
	return median(values);
}

static int pmu_mode(const char *mode) {
	prepare_case();
	const int iterations = 250000;
	if (!strcmp(mode, "control")) {
		for (int i = 0; i < iterations; ++i) {
			r7e_current_full_asm(control, &hq[0][0][0], &rq[0][0][0],
			                       &mq[0][0][0], &work[0][0][0]);
			sink += control[i % 1152];
		}
	} else if (!strcmp(mode, "e1")) {
		for (int i = 0; i < iterations; ++i) {
			r7e_e1_full_asm(candidate, &he[0][0][0], &re[0][0][0], &me[0][0][0]);
			sink += candidate[i % 1152];
		}
	} else if (!strcmp(mode, "e0")) {
		for (int i = 0; i < iterations; ++i) {
			r7e_e0_full_asm(candidate, &he[0][0][0], &re[0][0][0],
			                 &me[0][0][0], &e0scratch[0][0][0]);
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
	if (argc == 2 && !strcmp(argv[1], "--basis")) {
		int16_t got[4][16] __attribute__((aligned(32)));
		int32_t accum[8][8] __attribute__((aligned(32)));
		prepare_basis_case();
		r7e_current_full_asm(control, &hq[0][0][0], &rq[0][0][0],
		                       &mq[0][0][0], &work[0][0][0]);
		r7e_e1_full_asm(candidate, &he[0][0][0], &re[0][0][0], &me[0][0][0]);
		r7e_e1_coeff_block0_asm(&got[0][0], &he[0][0][0], &re[0][0][0], &me[0][0][0]);
		r7e_e1_accum_block0_asm(&accum[0][0], &he[0][0][0], &re[0][0][0], &me[0][0][0]);
		printf("memcmp=%d control0=%u candidate0=%u work0=%d\n",
		       memcmp(control, candidate, 1152), control[0], candidate[0], work[0][0][0]);
		for (int degree = 0; degree < 4; ++degree) {
			printf("d%d:", degree);
			for (int lane = 0; lane < 16; ++lane)
				printf(" %d/%d", work[0][degree][lane], got[degree][lane]);
			printf("\n");
		}
		memset(candidate, 0x5a, sizeof(candidate));
		r7e_e0_full_asm(candidate, &he[0][0][0], &re[0][0][0],
		                 &me[0][0][0], &e0scratch[0][0][0]);
		if (memcmp(control, candidate, 1152) != 0) {
			fprintf(stderr, "E0 basis mismatch\n");
			return 1;
		}
		for (int row = 0; row < 8; ++row) {
			printf("a%d:", row);
			for (int lane = 0; lane < 8; ++lane) printf(" %d", accum[row][lane]);
			printf("\n");
		}
		return 0;
	}

	for (int trial = 0; trial < 1000; ++trial) {
		prepare_case();
		memset(control, 0xa5, sizeof(control));
		memset(candidate, 0x5a, sizeof(candidate));
		r7e_current_full_asm(control, &hq[0][0][0], &rq[0][0][0],
		                       &mq[0][0][0], &work[0][0][0]);
		r7e_e1_full_asm(candidate, &he[0][0][0], &re[0][0][0], &me[0][0][0]);
		if (memcmp(control, candidate, 1152) != 0) {
			int16_t got[4][16] __attribute__((aligned(32)));
			r7e_e1_coeff_block0_asm(&got[0][0], &he[0][0][0], &re[0][0][0], &me[0][0][0]);
			for (int degree = 0; degree < 4; ++degree) {
				fprintf(stderr, "degree %d current/got:", degree);
				for (int lane = 0; lane < 16; ++lane)
					fprintf(stderr, " %d/%d", work[0][degree][lane], got[degree][lane]);
				fprintf(stderr, "\n");
			}
			for (int i = 0; i < 1152; ++i) {
				if (control[i] != candidate[i]) {
					fprintf(stderr, "mismatch trial=%d byte=%d control=%u candidate=%u\n",
					        trial, i, control[i], candidate[i]);
					return 1;
				}
			}
		}
		memset(candidate, 0x5a, sizeof(candidate));
		r7e_e0_full_asm(candidate, &he[0][0][0], &re[0][0][0],
		                 &me[0][0][0], &e0scratch[0][0][0]);
		if (memcmp(control, candidate, 1152) != 0) {
			fprintf(stderr, "E0 mismatch trial=%d\n", trial);
			return 1;
		}
		for (int i = 1152; i < (int)sizeof(control); ++i) {
			if (control[i] != 0xa5 || candidate[i] != 0x5a) {
				fprintf(stderr, "canary overwrite byte=%d\n", i);
				return 1;
			}
		}
	}

	prepare_case();
	uint64_t control_tsc = measure_full(0);
	uint64_t e0_tsc = measure_full(1);
	uint64_t e1_tsc = measure_full(2);
	uint64_t block_tsc = measure_candidate_block();
	printf("{\n");
	printf("  \"correctness_trials\": 1000,\n");
	printf("  \"e1_block_tsc\": %llu,\n", (unsigned long long)block_tsc);
	printf("  \"current_full_tsc\": %llu,\n", (unsigned long long)control_tsc);
	printf("  \"e0_full_tsc\": %llu,\n", (unsigned long long)e0_tsc);
	printf("  \"e0_minus_current_tsc\": %lld,\n",
	       (long long)e0_tsc - (long long)control_tsc);
	printf("  \"e1_full_tsc\": %llu,\n", (unsigned long long)e1_tsc);
	printf("  \"e1_minus_current_tsc\": %lld,\n",
	       (long long)e1_tsc - (long long)control_tsc);
	printf("  \"sink\": %llu\n", (unsigned long long)sink);
	printf("}\n");
	return 0;
}
