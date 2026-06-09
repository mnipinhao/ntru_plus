#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "params.h"
#include "poly.h"

#ifndef BENCH_ITERS
#define BENCH_ITERS 1000
#endif

#ifndef BENCH_WARMUP
#define BENCH_WARMUP 100
#endif

#ifndef BENCH_BATCH
#define BENCH_BATCH 64
#endif

#ifndef BENCH_LABEL
#define BENCH_LABEL "ntt_mul_pipeline"
#endif

typedef void (*bench_fn)(uint64_t calls);

static poly g_a;
static poly g_b;
static poly g_acc;
static poly g_ntt_a;
static poly g_ntt_b;
static poly g_ntt_acc;
static poly g_freq_out;
static poly g_out;
static volatile uint64_t g_sink;

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

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static void fill_input(poly *a, uint32_t seed)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		a->coeffs[i] =
		    (int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) -
		              NTRUPLUS_Q);
	}
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

static int centered_modq(int64_t a)
{
	int r = modq(a);

	if (r > NTRUPLUS_Q / 2)
	{
		r -= NTRUPLUS_Q;
	}

	return r;
}

static int equal_modq(int16_t a, int16_t b)
{
	return modq((int)a - (int)b) == 0;
}

static void schoolbook_mul_reference(poly *r, const poly *a, const poly *b)
{
	static int64_t tmp[2 * NTRUPLUS_N - 1];

	for (int i = 0; i < 2 * NTRUPLUS_N - 1; i++)
	{
		tmp[i] = 0;
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		for (int j = 0; j < NTRUPLUS_N; j++)
		{
			tmp[i + j] += (int64_t)a->coeffs[i] * b->coeffs[j];
		}
	}

	/* NTRU+768 works modulo X^768 - X^384 + 1, so X^768 = X^384 - 1. */
	for (int i = 2 * NTRUPLUS_N - 2; i >= NTRUPLUS_N; i--)
	{
		const int64_t c = tmp[i];

		tmp[i - NTRUPLUS_N / 2] += c;
		tmp[i - NTRUPLUS_N] -= c;
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		r->coeffs[i] = (int16_t)centered_modq(tmp[i]);
	}
}

static uint64_t checksum_poly(const poly *a)
{
	uint64_t acc = 0x6a09e667f3bcc909ULL;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		acc ^= (uint16_t)a->coeffs[i];
		acc *= 0x100000001b3ULL;
		acc ^= acc >> 32;
	}

	return acc;
}

static void consume_outputs(void)
{
	g_sink = (g_sink << 5) ^ (g_sink >> 7) ^ checksum_poly(&g_out) ^
	         checksum_poly(&g_freq_out) ^ 0x9e3779b97f4a7c15ULL;
}

static int compare_modq(const char *label, const poly *got, const poly *want)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!equal_modq(got->coeffs[i], want->coeffs[i]))
		{
			fprintf(stderr,
			        "%s mismatch at %d: got=%d want=%d\n",
			        label,
			        i,
			        got->coeffs[i],
			        want->coeffs[i]);
			return 0;
		}
	}

	return 1;
}

static int check_pipeline(void)
{
	poly want;
	poly got;
	poly ntt_a;
	poly ntt_b;
	poly freq_out;
#ifdef BENCH_OP_ADD
	poly ntt_acc;
#endif

	schoolbook_mul_reference(&want, &g_a, &g_b);

#ifdef BENCH_OP_ADD
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		want.coeffs[i] =
		    (int16_t)centered_modq((int64_t)want.coeffs[i] +
		                          g_acc.coeffs[i]);
	}
#endif

	poly_ntt(&ntt_a, &g_a);
	poly_ntt(&ntt_b, &g_b);
#ifdef BENCH_OP_ADD
	poly_ntt(&ntt_acc, &g_acc);
	poly_basemul_add(&freq_out, &ntt_a, &ntt_b, &ntt_acc);
#else
	poly_basemul(&freq_out, &ntt_a, &ntt_b);
#endif
	poly_invntt(&got, &freq_out);

	return compare_modq("NTT multiplication pipeline", &got, &want);
}

static void setup_inputs(void)
{
	fill_input(&g_a, 0x243f6a88u);
	fill_input(&g_b, 0x85a308d3u);
	fill_input(&g_acc, 0x13198a2eu);

	poly_ntt(&g_ntt_a, &g_a);
	poly_ntt(&g_ntt_b, &g_b);
	poly_ntt(&g_ntt_acc, &g_acc);
#ifdef BENCH_OP_ADD
	poly_basemul_add(&g_freq_out, &g_ntt_a, &g_ntt_b, &g_ntt_acc);
#else
	poly_basemul(&g_freq_out, &g_ntt_a, &g_ntt_b);
#endif
	poly_invntt(&g_out, &g_freq_out);
}

__attribute__((noinline)) static void target_ntt(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		poly_ntt(&g_ntt_a, &g_a);
	}
}

__attribute__((noinline)) static void target_basemul(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
#ifdef BENCH_OP_ADD
		poly_basemul_add(&g_freq_out, &g_ntt_a, &g_ntt_b, &g_ntt_acc);
#else
		poly_basemul(&g_freq_out, &g_ntt_a, &g_ntt_b);
#endif
	}
}

__attribute__((noinline)) static void target_invntt(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		poly_invntt(&g_out, &g_freq_out);
	}
}

__attribute__((noinline)) static void target_pipeline(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		poly_ntt(&g_ntt_a, &g_a);
		poly_ntt(&g_ntt_b, &g_b);
#ifdef BENCH_OP_ADD
		poly_ntt(&g_ntt_acc, &g_acc);
		poly_basemul_add(&g_freq_out, &g_ntt_a, &g_ntt_b, &g_ntt_acc);
#else
		poly_basemul(&g_freq_out, &g_ntt_a, &g_ntt_b);
#endif
		poly_invntt(&g_out, &g_freq_out);
	}
}

static void run_measure(const char *metric, bench_fn target)
{
	static uint64_t samples[BENCH_ITERS];
	uint64_t total = 0;
	uint64_t wall_start;
	uint64_t wall_end;

	target(BENCH_WARMUP);
	consume_outputs();

	wall_start = read_wall_ns();
	for (int i = 0; i < BENCH_ITERS; i++)
	{
		const uint64_t start = read_counter();

		target(BENCH_BATCH);

		samples[i] = read_counter() - start;
		total += samples[i];
	}
	wall_end = read_wall_ns();
	consume_outputs();

	qsort(samples, BENCH_ITERS, sizeof(samples[0]), cmp_u64);

	printf("%s_ticks/call min=%.3f median=%.3f avg=%.3f p90=%.3f p99=%.3f\n",
	       metric,
	       (double)samples[0] / (double)BENCH_BATCH,
	       (double)samples[BENCH_ITERS / 2] / (double)BENCH_BATCH,
	       ((double)total / (double)BENCH_ITERS) / (double)BENCH_BATCH,
	       (double)samples[(BENCH_ITERS * 90) / 100] / (double)BENCH_BATCH,
	       (double)samples[(BENCH_ITERS * 99) / 100] / (double)BENCH_BATCH);
	printf("%s_wall_ns/call avg=%.2f\n",
	       metric,
	       (double)(wall_end - wall_start) /
	           (double)((uint64_t)BENCH_ITERS * (uint64_t)BENCH_BATCH));
}

int main(void)
{
	setup_inputs();
	if (!check_pipeline())
	{
		return 1;
	}

	printf("bench=%s op=%s iters=%d warmup=%d batch=%d cntfrq=%llu "
	       "correctness=ok\n",
	       BENCH_LABEL,
#ifdef BENCH_OP_ADD
	       "basemul_add",
#else
	       "basemul",
#endif
	       BENCH_ITERS,
	       BENCH_WARMUP,
	       BENCH_BATCH,
	       (unsigned long long)read_counter_freq());

	run_measure("poly_ntt", target_ntt);
#ifdef BENCH_OP_ADD
	run_measure("poly_basemul_add", target_basemul);
#else
	run_measure("poly_basemul", target_basemul);
#endif
	run_measure("poly_invntt", target_invntt);
#ifdef BENCH_OP_ADD
	run_measure("ntt_basemul_add_pipeline", target_pipeline);
#else
	run_measure("ntt_mul_pipeline", target_pipeline);
#endif

	printf("sink=%llu\n", (unsigned long long)g_sink);
	return 0;
}
