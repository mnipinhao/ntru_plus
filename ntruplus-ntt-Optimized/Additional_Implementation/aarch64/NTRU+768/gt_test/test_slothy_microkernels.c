#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define TEST_LOOP_COUNT 10000
#include "test/counter.h"

#include "params.h"

#define GT_MICRO_BENCH_LOOPS 5000
#define GT_MICRO_INNER_LOOPS 256
#define GT_MICRO_QINV 12929
#define GT_MICRO_R (-147)
#define GT_MICRO_RSQ 867

void baseinv_batch_finish8_n1_opt(int16_t *dst, const int16_t *den_inv);
void base_gt_add32_finalize8_n1_opt(int16_t *dst, const int16_t *raw_soa,
                                    const int16_t *c_soa);
void base_gt_add32_full_pipeline8_n1_opt(int16_t *dst, const int16_t *a,
                                         const int16_t *b, const int16_t *c,
                                         const int16_t *lambda);

static volatile uint32_t bench_sink;

static int16_t centered_modq_u32(uint32_t x)
{
	int16_t r = (int16_t)(x % NTRUPLUS_Q);

	if (r > NTRUPLUS_Q / 2)
		r -= NTRUPLUS_Q;
	return r;
}

static int16_t montgomery_reduce_ref(int32_t a)
{
	int16_t t;

	t = (int16_t)a * GT_MICRO_QINV;
	t = (int16_t)((a - (int32_t)t * NTRUPLUS_Q) >> 16);
	return t;
}

static int same_modq(int16_t a, int16_t b)
{
	int32_t diff = (int32_t)a - b;

	diff %= NTRUPLUS_Q;
	if (diff < 0)
		diff += NTRUPLUS_Q;
	return diff == 0;
}

static void fill_i16(int16_t *a, int n, uint32_t seed)
{
	uint32_t x = seed ? seed : 1;

	for (int i = 0; i < n; i++)
	{
		x = x * 1664525u + 1013904223u;
		a[i] = centered_modq_u32(x);
	}
}

static void __attribute__((noinline))
baseinv_finish8_ref(volatile int16_t *dst, const volatile int16_t *den_inv)
{
	int16_t src[32];

	for (int i = 0; i < 32; i++)
		src[i] = dst[i];

	for (int j = 0; j < 8; j++)
	{
		const int16_t den = den_inv[j];
		const int16_t neg_den = (int16_t)-den;

		dst[4 * j + 0] =
			montgomery_reduce_ref((int32_t)src[4 * j + 0] * den);
		dst[4 * j + 1] =
			montgomery_reduce_ref((int32_t)src[4 * j + 1] * neg_den);
		dst[4 * j + 2] =
			montgomery_reduce_ref((int32_t)src[4 * j + 2] * den);
		dst[4 * j + 3] =
			montgomery_reduce_ref((int32_t)src[4 * j + 3] * neg_den);
	}
}

static void __attribute__((noinline))
add32_finalize8_ref(volatile int16_t *dst,
                    const volatile int16_t *raw_soa,
                    const volatile int16_t *c_soa)
{
	for (int k = 0; k < 4; k++)
	{
		for (int j = 0; j < 8; j++)
		{
			const int idx = 8 * k + j;
			dst[4 * j + k] =
				montgomery_reduce_ref((int32_t)c_soa[idx] * GT_MICRO_R +
				                      (int32_t)raw_soa[idx] * GT_MICRO_RSQ);
		}
	}
}

static void __attribute__((noinline))
full_pipeline8_ref(volatile int16_t *dst, const volatile int16_t *a,
                   const volatile int16_t *b, const volatile int16_t *c,
                   const volatile int16_t *lambda)
{
	for (int j = 0; j < 8; j++)
	{
		const int16_t a0 = a[4 * j + 0];
		const int16_t a1 = a[4 * j + 1];
		const int16_t a2 = a[4 * j + 2];
		const int16_t a3 = a[4 * j + 3];
		const int16_t b0 = b[4 * j + 0];
		const int16_t b1 = b[4 * j + 1];
		const int16_t b2 = b[4 * j + 2];
		const int16_t b3 = b[4 * j + 3];
		const int16_t lam = lambda[j];
		int16_t raw[4];

		const int16_t w2 =
			montgomery_reduce_ref((int32_t)a3 * b3);
		const int16_t w1 =
			montgomery_reduce_ref((int32_t)a2 * b3 +
			                      (int32_t)a3 * b2);
		const int16_t w0 =
			montgomery_reduce_ref((int32_t)a1 * b3 +
			                      (int32_t)a2 * b2 +
			                      (int32_t)a3 * b1);

		raw[0] = montgomery_reduce_ref((int32_t)w0 * lam +
		                               (int32_t)a0 * b0);
		raw[1] = montgomery_reduce_ref((int32_t)w1 * lam +
		                               (int32_t)a0 * b1 +
		                               (int32_t)a1 * b0);
		raw[2] = montgomery_reduce_ref((int32_t)w2 * lam +
		                               (int32_t)a0 * b2 +
		                               (int32_t)a1 * b1 +
		                               (int32_t)a2 * b0);
		raw[3] = montgomery_reduce_ref((int32_t)a0 * b3 +
		                               (int32_t)a1 * b2 +
		                               (int32_t)a2 * b1 +
		                               (int32_t)a3 * b0);

		for (int k = 0; k < 4; k++)
			dst[4 * j + k] =
				montgomery_reduce_ref((int32_t)c[4 * j + k] * GT_MICRO_R +
				                      (int32_t)raw[k] * GT_MICRO_RSQ);
	}
}

static int compare32_modq(const char *label, const int16_t *want,
                          const int16_t *got)
{
	for (int i = 0; i < 32; i++)
	{
		if (!same_modq(want[i], got[i]))
		{
			printf("%s mismatch at %d: want=%d got=%d\n",
			       label, i, want[i], got[i]);
			return 1;
		}
	}

	return 0;
}

static int check_baseinv_finish8(uint32_t seed)
{
	int16_t want[32] __attribute__((aligned(16)));
	int16_t got[32] __attribute__((aligned(16)));
	int16_t den[8] __attribute__((aligned(16)));

	fill_i16(want, 32, seed);
	memcpy(got, want, sizeof(got));
	fill_i16(den, 8, seed + 1000);

	baseinv_finish8_ref(want, den);
	baseinv_batch_finish8_n1_opt(got, den);
	return compare32_modq("baseinv_finish8_n1_opt", want, got);
}

static int check_add32_finalize8(uint32_t seed)
{
	int16_t raw_soa[32] __attribute__((aligned(16)));
	int16_t c_soa[32] __attribute__((aligned(16)));
	int16_t want[32] __attribute__((aligned(16)));
	int16_t got[32] __attribute__((aligned(16)));

	fill_i16(raw_soa, 32, seed);
	fill_i16(c_soa, 32, seed + 2000);
	memset(got, 0, sizeof(got));

	add32_finalize8_ref(want, raw_soa, c_soa);
	base_gt_add32_finalize8_n1_opt(got, raw_soa, c_soa);
	return compare32_modq("base_gt_add32_finalize8_n1_opt", want, got);
}

static int check_add32_full_pipeline8(uint32_t seed)
{
	int16_t a[32] __attribute__((aligned(16)));
	int16_t b[32] __attribute__((aligned(16)));
	int16_t c[32] __attribute__((aligned(16)));
	int16_t lambda[8] __attribute__((aligned(16)));
	int16_t want[32] __attribute__((aligned(16)));
	int16_t got[32] __attribute__((aligned(16)));

	fill_i16(a, 32, seed);
	fill_i16(b, 32, seed + 1000);
	fill_i16(c, 32, seed + 2000);
	fill_i16(lambda, 8, seed + 3000);
	memset(got, 0, sizeof(got));

	full_pipeline8_ref(want, a, b, c, lambda);
	base_gt_add32_full_pipeline8_n1_opt(got, a, b, c, lambda);
	return compare32_modq("base_gt_add32_full_pipeline8_n1_opt", want, got);
}

static unsigned long long adjusted_ticks(unsigned long long start,
                                         unsigned long long end)
{
	unsigned long long elapsed = end - start;

	if (elapsed <= countergap)
		return 0;
	return elapsed - countergap;
}

static unsigned long long bench_baseinv_finish8_ref(void)
{
	int16_t dst[32] __attribute__((aligned(16)));
	int16_t den[8] __attribute__((aligned(16)));
	unsigned long long total = 0;

	fill_i16(dst, 32, 11);
	fill_i16(den, 8, 22);

	for (int i = 0; i < GT_MICRO_BENCH_LOOPS; i++)
	{
		unsigned long long start = counter();
		for (int j = 0; j < GT_MICRO_INNER_LOOPS; j++)
			baseinv_finish8_ref(dst, den);
		unsigned long long end = counter();

		total += adjusted_ticks(start, end);
		bench_sink += (uint16_t)dst[i & 31];
	}

	return total / GT_MICRO_BENCH_LOOPS;
}

static unsigned long long bench_baseinv_finish8_opt(void)
{
	int16_t dst[32] __attribute__((aligned(16)));
	int16_t den[8] __attribute__((aligned(16)));
	unsigned long long total = 0;

	fill_i16(dst, 32, 33);
	fill_i16(den, 8, 44);

	for (int i = 0; i < GT_MICRO_BENCH_LOOPS; i++)
	{
		unsigned long long start = counter();
		for (int j = 0; j < GT_MICRO_INNER_LOOPS; j++)
			baseinv_batch_finish8_n1_opt(dst, den);
		unsigned long long end = counter();

		total += adjusted_ticks(start, end);
		bench_sink += (uint16_t)dst[i & 31];
	}

	return total / GT_MICRO_BENCH_LOOPS;
}

static unsigned long long bench_add32_finalize8_ref(void)
{
	int16_t raw_soa[32] __attribute__((aligned(16)));
	int16_t c_soa[32] __attribute__((aligned(16)));
	int16_t dst[32] __attribute__((aligned(16)));
	unsigned long long total = 0;

	fill_i16(raw_soa, 32, 55);
	fill_i16(c_soa, 32, 66);

	for (int i = 0; i < GT_MICRO_BENCH_LOOPS; i++)
	{
		unsigned long long start = counter();
		for (int j = 0; j < GT_MICRO_INNER_LOOPS; j++)
			add32_finalize8_ref(dst, raw_soa, c_soa);
		unsigned long long end = counter();

		total += adjusted_ticks(start, end);
		bench_sink += (uint16_t)dst[i & 31];
	}

	return total / GT_MICRO_BENCH_LOOPS;
}

static unsigned long long bench_add32_finalize8_opt(void)
{
	int16_t raw_soa[32] __attribute__((aligned(16)));
	int16_t c_soa[32] __attribute__((aligned(16)));
	int16_t dst[32] __attribute__((aligned(16)));
	unsigned long long total = 0;

	fill_i16(raw_soa, 32, 77);
	fill_i16(c_soa, 32, 88);

	for (int i = 0; i < GT_MICRO_BENCH_LOOPS; i++)
	{
		unsigned long long start = counter();
		for (int j = 0; j < GT_MICRO_INNER_LOOPS; j++)
			base_gt_add32_finalize8_n1_opt(dst, raw_soa, c_soa);
		unsigned long long end = counter();

		total += adjusted_ticks(start, end);
		bench_sink += (uint16_t)dst[i & 31];
	}

	return total / GT_MICRO_BENCH_LOOPS;
}

static unsigned long long bench_add32_full_pipeline8_ref(void)
{
	int16_t a[32] __attribute__((aligned(16)));
	int16_t b[32] __attribute__((aligned(16)));
	int16_t c[32] __attribute__((aligned(16)));
	int16_t lambda[8] __attribute__((aligned(16)));
	int16_t dst[32] __attribute__((aligned(16)));
	unsigned long long total = 0;

	fill_i16(a, 32, 101);
	fill_i16(b, 32, 202);
	fill_i16(c, 32, 303);
	fill_i16(lambda, 8, 404);

	for (int i = 0; i < GT_MICRO_BENCH_LOOPS; i++)
	{
		unsigned long long start = counter();
		for (int j = 0; j < GT_MICRO_INNER_LOOPS; j++)
			full_pipeline8_ref(dst, a, b, c, lambda);
		unsigned long long end = counter();

		total += adjusted_ticks(start, end);
		bench_sink += (uint16_t)dst[i & 31];
	}

	return total / GT_MICRO_BENCH_LOOPS;
}

static unsigned long long bench_add32_full_pipeline8_opt(void)
{
	int16_t a[32] __attribute__((aligned(16)));
	int16_t b[32] __attribute__((aligned(16)));
	int16_t c[32] __attribute__((aligned(16)));
	int16_t lambda[8] __attribute__((aligned(16)));
	int16_t dst[32] __attribute__((aligned(16)));
	unsigned long long total = 0;

	fill_i16(a, 32, 505);
	fill_i16(b, 32, 606);
	fill_i16(c, 32, 707);
	fill_i16(lambda, 8, 808);

	for (int i = 0; i < GT_MICRO_BENCH_LOOPS; i++)
	{
		unsigned long long start = counter();
		for (int j = 0; j < GT_MICRO_INNER_LOOPS; j++)
			base_gt_add32_full_pipeline8_n1_opt(dst, a, b, c, lambda);
		unsigned long long end = counter();

		total += adjusted_ticks(start, end);
		bench_sink += (uint16_t)dst[i & 31];
	}

	return total / GT_MICRO_BENCH_LOOPS;
}

int main(void)
{
	unsigned long long baseinv_ref;
	unsigned long long baseinv_opt;
	unsigned long long add32_ref;
	unsigned long long add32_opt;
	unsigned long long full_pipeline_ref;
	unsigned long long full_pipeline_opt;
	int failed = 0;

	for (uint32_t seed = 1; seed <= 32; seed++)
	{
		failed |= check_baseinv_finish8(seed);
		failed |= check_add32_finalize8(seed);
		failed |= check_add32_full_pipeline8(seed);
	}

	printf("slothy_microkernels_correctness: %s\n",
	       failed ? "fail" : "ok");
	if (failed)
		return 1;

	setup_counter();
	baseinv_ref = bench_baseinv_finish8_ref();
	baseinv_opt = bench_baseinv_finish8_opt();
	add32_ref = bench_add32_finalize8_ref();
	add32_opt = bench_add32_finalize8_opt();
	full_pipeline_ref = bench_add32_full_pipeline8_ref();
	full_pipeline_opt = bench_add32_full_pipeline8_opt();

	printf("countergap: %llu ticks\n", countergap);
	printf("slothy_microkernel_inner_loops: %d\n", GT_MICRO_INNER_LOOPS);
	printf("baseinv_finish8_ref_x256         %llu ticks\n", baseinv_ref);
	printf("baseinv_finish8_n1_opt_x256      %llu ticks\n", baseinv_opt);
	printf("baseinv_finish8_ref_mticks       %llu milli-ticks/call\n",
	       (baseinv_ref * 1000) / GT_MICRO_INNER_LOOPS);
	printf("baseinv_finish8_n1_opt_mticks    %llu milli-ticks/call\n",
	       (baseinv_opt * 1000) / GT_MICRO_INNER_LOOPS);
	printf("add32_finalize8_ref_x256         %llu ticks\n", add32_ref);
	printf("add32_finalize8_n1_opt_x256      %llu ticks\n", add32_opt);
	printf("add32_finalize8_ref_mticks       %llu milli-ticks/call\n",
	       (add32_ref * 1000) / GT_MICRO_INNER_LOOPS);
	printf("add32_finalize8_n1_opt_mticks    %llu milli-ticks/call\n",
	       (add32_opt * 1000) / GT_MICRO_INNER_LOOPS);
	printf("add32_full_pipeline8_ref_x256    %llu ticks\n",
	       full_pipeline_ref);
	printf("add32_full_pipeline8_n1_opt_x256 %llu ticks\n",
	       full_pipeline_opt);
	printf("add32_full_pipeline8_ref_mticks  %llu milli-ticks/call\n",
	       (full_pipeline_ref * 1000) / GT_MICRO_INNER_LOOPS);
	printf("add32_full_pipeline8_n1_opt_mticks %llu milli-ticks/call\n",
	       (full_pipeline_opt * 1000) / GT_MICRO_INNER_LOOPS);
	printf("slothy_microkernels_sink: %u\n", bench_sink);

	return 0;
}
