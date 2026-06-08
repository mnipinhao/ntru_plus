#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "params.h"
#include "poly.h"

#ifndef BENCH_ITERS
#define BENCH_ITERS 2000
#endif

#ifndef BENCH_WARMUP
#define BENCH_WARMUP 200
#endif

#ifndef BENCH_BATCH
#define BENCH_BATCH 64
#endif

#ifndef BENCH_LABEL
#define BENCH_LABEL "poly_invntt"
#endif

static inline uint64_t read_counter(void)
{
	uint64_t t;

	__asm__ volatile(
	    "isb\n\t"
	    "mrs %0, cntvct_el0\n\t"
	    "isb"
	    : "=r"(t)
	    :
	    : "memory");
	return t;
}

static inline uint64_t read_counter_freq(void)
{
	uint64_t t;

	__asm__ volatile("mrs %0, cntfrq_el0" : "=r"(t));
	return t;
}

static uint64_t read_wall_ns(void)
{
	struct timespec ts;

	clock_gettime(CLOCK_MONOTONIC, &ts);
	return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

static int cmp_u64(const void *a, const void *b)
{
	const uint64_t aa = *(const uint64_t *)a;
	const uint64_t bb = *(const uint64_t *)b;

	return (aa > bb) - (aa < bb);
}

static int modq(int64_t a)
{
	int r = (int)(a % NTRUPLUS_Q);

	if (r < 0)
	{
		r += NTRUPLUS_Q;
	}

	return r;
}

static int equal_modq(int16_t a, int16_t b)
{
	return modq((int)a - (int)b) == 0;
}

static void fill_input(poly *a)
{
	uint32_t seed = 0x12345678u;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		seed = seed * 1664525u + 1013904223u;
		a->coeffs[i] = (int16_t)((int)(seed % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
	}
}

static int check_roundtrip(const poly *want, const poly *freq)
{
	poly got;

	poly_invntt(&got, freq);
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!equal_modq(got.coeffs[i], want->coeffs[i]))
		{
			fprintf(stderr,
			        "pre-bench roundtrip mismatch at %d: got %d want %d\n",
			        i, got.coeffs[i], want->coeffs[i]);
			return 0;
		}
	}

	return 1;
}

int main(void)
{
	poly natural;
	poly freq;
	poly out;
	static uint64_t samples[BENCH_ITERS];
	uint64_t wall_start;
	uint64_t wall_end;
	uint64_t total = 0;
	volatile int16_t sink = 0;

	fill_input(&natural);
	poly_ntt(&freq, &natural);
	if (!check_roundtrip(&natural, &freq))
	{
		return 1;
	}

	for (int i = 0; i < BENCH_WARMUP; i++)
	{
		poly_invntt(&out, &freq);
		sink ^= out.coeffs[i & (NTRUPLUS_N - 1)];
	}

	wall_start = read_wall_ns();
	for (int i = 0; i < BENCH_ITERS; i++)
	{
		const uint64_t start = read_counter();

		for (int j = 0; j < BENCH_BATCH; j++)
		{
			poly_invntt(&out, &freq);
			sink ^= out.coeffs[(i + j) & (NTRUPLUS_N - 1)];
		}

		const uint64_t end = read_counter();

		samples[i] = end - start;
		total += samples[i];
	}
	wall_end = read_wall_ns();

	qsort(samples, BENCH_ITERS, sizeof(samples[0]), cmp_u64);

	printf("bench=%s iters=%d warmup=%d batch=%d cntfrq=%llu sink=%d\n",
	       BENCH_LABEL,
	       BENCH_ITERS,
	       BENCH_WARMUP,
	       BENCH_BATCH,
	       (unsigned long long)read_counter_freq(),
	       sink);
	printf("cntvct_ticks/call min=%.3f median=%.3f avg=%.3f p90=%.3f p99=%.3f\n",
	       (double)samples[0] / (double)BENCH_BATCH,
	       (double)samples[BENCH_ITERS / 2] / (double)BENCH_BATCH,
	       ((double)total / (double)BENCH_ITERS) / (double)BENCH_BATCH,
	       (double)samples[(BENCH_ITERS * 90) / 100] / (double)BENCH_BATCH,
	       (double)samples[(BENCH_ITERS * 99) / 100] / (double)BENCH_BATCH);
	printf("wall_ns/call avg=%.2f\n",
	       (double)(wall_end - wall_start) /
	           (double)((uint64_t)BENCH_ITERS * (uint64_t)BENCH_BATCH));

	return 0;
}
