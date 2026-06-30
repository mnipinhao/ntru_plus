#include <stdint.h>
#include <stdio.h>

#define TEST_LOOP_COUNT 5000
#include "test/counter.h"

#include "ntt.h"
#include "params.h"
#include "poly.h"

#define GT_BASEMUL_BENCH_LOOPS 5000

void poly_basemul_gt_ref(poly *r, const poly *a, const poly *b);

static volatile uint32_t bench_sink;

static int16_t centered_modq_u32(uint32_t x)
{
	int16_t r = (int16_t)(x % NTRUPLUS_Q);

	if (r > NTRUPLUS_Q / 2)
		r -= NTRUPLUS_Q;
	return r;
}

static void fill_poly(poly *a, uint32_t seed)
{
	uint32_t x = seed ? seed : 1;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		x = x * 1664525u + 1013904223u;
		a->coeffs[i] = centered_modq_u32(x);
	}
}

static int same_modq(int16_t a, int16_t b)
{
	int32_t diff = (int32_t)a - b;

	diff %= NTRUPLUS_Q;
	if (diff < 0)
		diff += NTRUPLUS_Q;
	return diff == 0;
}

static int compare_poly_modq(const char *label, const poly *want,
                             const poly *got)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!same_modq(want->coeffs[i], got->coeffs[i]))
		{
			printf("%s mismatch at %d: want=%d got=%d\n",
			       label, i, want->coeffs[i], got->coeffs[i]);
			return 1;
		}
	}

	return 0;
}

static unsigned long long adjusted_ticks(unsigned long long start,
                                         unsigned long long end)
{
	unsigned long long elapsed = end - start;

	if (elapsed <= countergap)
		return 0;
	return elapsed - countergap;
}

static unsigned long long bench_basemul(const poly *a, const poly *b)
{
	poly out;
	unsigned long long total = 0;

	for (int i = 0; i < GT_BASEMUL_BENCH_LOOPS; i++)
	{
		unsigned long long start = counter();
		poly_basemul(&out, a, b);
		unsigned long long end = counter();

		total += adjusted_ticks(start, end);
		bench_sink += (uint32_t)out.coeffs[i & (NTRUPLUS_N - 1)];
	}

	return total / GT_BASEMUL_BENCH_LOOPS;
}

int main(void)
{
	poly a, b;
	poly want, got;

	setup_counter();

	fill_poly(&a, 101);
	fill_poly(&b, 202);

	poly_basemul_gt_ref(&want, &a, &b);
	poly_basemul(&got, &a, &b);
	if (compare_poly_modq("poly_basemul", &want, &got))
		return 1;

	printf("gt_basemul_asm_correctness: ok\n");
	printf("countergap: %llu ticks\n", countergap);
	printf("poly_basemul                %llu ticks\n", bench_basemul(&a, &b));
	printf("gt_basemul_asm_sink: %u\n", bench_sink);

	return 0;
}
