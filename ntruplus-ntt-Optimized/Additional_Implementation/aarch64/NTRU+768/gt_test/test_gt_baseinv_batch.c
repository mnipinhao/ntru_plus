#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define TEST_LOOP_COUNT 2000
#include "test/counter.h"

#include "ntt.h"
#include "params.h"
#include "poly.h"

#define GT_TEST_BRANCHES 2
#define GT_TEST_BRANCH_N (NTRUPLUS_N / GT_TEST_BRANCHES)
#define GT_TEST_BLOCKS_PER_BRANCH 96
#define GT_TEST_ROWS 3
#define GT_TEST_ROW_N 32
#define GT_TEST_QUARTIC_LANES 4
#define GT_BASEINV_BENCH_LOOPS 2000
#define GT_TEST_R (-147)

int poly_baseinv_gt_ref(poly *r, const poly *a);
int poly_baseinv_gt_batch(poly *r, const poly *a);
int poly_baseinv_gt_batch_scaled_r(poly *r, const poly *a);
int poly_baseinv_gt_tuple_batch(poly *r, const poly *a);

static volatile uint32_t bench_sink;

static int block_major_index(int branch, int physical_j, int lane)
{
	return branch * GT_TEST_BRANCH_N +
	       GT_TEST_QUARTIC_LANES * physical_j + lane;
}

static int tuple_index(int branch, int row, int k32, int lane)
{
	return branch * GT_TEST_BRANCH_N +
	       row * (GT_TEST_ROW_N * GT_TEST_QUARTIC_LANES) +
	       GT_TEST_QUARTIC_LANES * k32 + lane;
}

static int tuple_physical_j(int row, int k32)
{
	return (GT_TEST_ROW_N * row + GT_TEST_ROWS * k32) %
	       GT_TEST_BLOCKS_PER_BRANCH;
}

static void block_major_to_tuple(poly *tuple, const poly *block_major)
{
	for (int branch = 0; branch < GT_TEST_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_TEST_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_TEST_ROW_N; k32++)
			{
				const int physical_j = tuple_physical_j(row, k32);

				for (int lane = 0; lane < GT_TEST_QUARTIC_LANES; lane++)
				{
					tuple->coeffs[tuple_index(branch, row, k32, lane)] =
						block_major->coeffs[
							block_major_index(branch, physical_j, lane)];
				}
			}
		}
	}
}

static int poly_baseinv_tuple_ref(poly *r, const poly *a)
{
	for (int branch = 0; branch < GT_TEST_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_TEST_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_TEST_ROW_N; k32++)
			{
				const int pos = tuple_index(branch, row, k32, 0);
				const int physical_j = tuple_physical_j(row, k32);

				if (baseinv(r->coeffs + pos, a->coeffs + pos,
				            gt_rowbitrev_lambda[branch][physical_j]))
				{
					memset(r->coeffs, 0, sizeof(r->coeffs));
					return 1;
				}
			}
		}
	}

	return 0;
}

static int16_t centered_modq(uint32_t x)
{
	int16_t r = (int16_t)(x % NTRUPLUS_Q);

	if (r > NTRUPLUS_Q / 2)
		r -= NTRUPLUS_Q;
	return r;
}

static int16_t centered_modq_i32(int32_t x)
{
	x %= NTRUPLUS_Q;
	if (x > NTRUPLUS_Q / 2)
		x -= NTRUPLUS_Q;
	if (x < -NTRUPLUS_Q / 2)
		x += NTRUPLUS_Q;
	return (int16_t)x;
}

static void scale_poly_by_r(poly *r, const poly *a)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
		r->coeffs[i] = centered_modq_i32((int32_t)a->coeffs[i] * GT_TEST_R);
}

static void fill_poly(poly *a, uint32_t seed)
{
	uint32_t x = seed ? seed : 1;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		x = x * 1664525u + 1013904223u;
		a->coeffs[i] = centered_modq(x);
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
			return 0;
		}
	}

	return 1;
}

static int check_block_major_seed(uint32_t seed)
{
	poly a;
	poly want;
	poly got;
	int want_ret;
	int got_ret;

	fill_poly(&a, seed);

	want_ret = poly_baseinv_gt_ref(&want, &a);
	got_ret = poly_baseinv_gt_batch(&got, &a);

	if (want_ret != got_ret)
	{
		printf("block-major seed %u return mismatch: want=%d got=%d\n",
		       seed, want_ret, got_ret);
		return 0;
	}

	return compare_poly_modq("block-major batch baseinv", &want, &got);
}

static int check_block_major_scaled_seed(uint32_t seed)
{
	poly a;
	poly want;
	poly got;
	int want_ret;
	int got_ret;

	fill_poly(&a, seed);

	want_ret = poly_baseinv_gt_ref(&want, &a);
	if (want_ret == 0)
		scale_poly_by_r(&want, &want);
	got_ret = poly_baseinv_gt_batch_scaled_r(&got, &a);

	if (want_ret != got_ret)
	{
		printf("block-major scaled seed %u return mismatch: want=%d got=%d\n",
		       seed, want_ret, got_ret);
		return 0;
	}

	return compare_poly_modq("block-major scaled-R batch baseinv", &want,
	                         &got);
}

static int check_tuple_seed(uint32_t seed)
{
	poly block_major;
	poly tuple;
	poly want;
	poly got;
	int want_ret;
	int got_ret;

	fill_poly(&block_major, seed);
	block_major_to_tuple(&tuple, &block_major);

	want_ret = poly_baseinv_tuple_ref(&want, &tuple);
	got_ret = poly_baseinv_gt_tuple_batch(&got, &tuple);

	if (want_ret != got_ret)
	{
		printf("tuple seed %u return mismatch: want=%d got=%d\n",
		       seed, want_ret, got_ret);
		return 0;
	}

	return compare_poly_modq("tuple batch baseinv", &want, &got);
}

static int check_forced_failure(void)
{
	poly zero;
	poly got;
	int ret;

	memset(&zero, 0, sizeof(zero));

	ret = poly_baseinv_gt_batch(&got, &zero);
	if (ret != 1)
	{
		printf("block-major zero failure mismatch: got ret=%d\n", ret);
		return 0;
	}
	if (!compare_poly_modq("block-major zero output", &zero, &got))
		return 0;

	ret = poly_baseinv_gt_batch_scaled_r(&got, &zero);
	if (ret != 1)
	{
		printf("block-major scaled zero failure mismatch: got ret=%d\n", ret);
		return 0;
	}
	if (!compare_poly_modq("block-major scaled zero output", &zero, &got))
		return 0;

	ret = poly_baseinv_gt_tuple_batch(&got, &zero);
	if (ret != 1)
	{
		printf("tuple zero failure mismatch: got ret=%d\n", ret);
		return 0;
	}
	if (!compare_poly_modq("tuple zero output", &zero, &got))
		return 0;

	return 1;
}

static void prepare_invertible_block_major(poly *a)
{
	poly tmp;

	for (uint32_t seed = 1; ; seed++)
	{
		fill_poly(a, seed);
		if (poly_baseinv_gt_ref(&tmp, a) == 0)
			return;
	}
}

typedef int (*baseinv_target)(poly *r, const poly *a);

static unsigned long long bench_one(baseinv_target target, const poly *a)
{
	poly out;
	unsigned long long total = 0;

	for (int i = 0; i < GT_BASEINV_BENCH_LOOPS; i++)
	{
		unsigned long long start = counter();
		int ret = target(&out, a);
		unsigned long long end = counter();

		total += end - start - countergap;
		bench_sink += (uint16_t)out.coeffs[(17 * i) & (NTRUPLUS_N - 1)];
		bench_sink += (uint32_t)ret;
	}

	return total / GT_BASEINV_BENCH_LOOPS;
}

int main(void)
{
	poly block_major;
	poly tuple;
	unsigned long long scalar_block_ticks;
	unsigned long long batch_block_ticks;
	unsigned long long batch_block_scaled_ticks;
	unsigned long long scalar_tuple_ticks;
	unsigned long long batch_tuple_ticks;
	int ok = 1;

	for (uint32_t seed = 1; seed <= 32; seed++)
	{
		ok &= check_block_major_seed(seed);
		ok &= check_block_major_scaled_seed(seed);
		ok &= check_tuple_seed(seed);
	}
	ok &= check_forced_failure();

	printf("gt_baseinv_batch_correctness: %s\n", ok ? "ok" : "fail");
	if (!ok)
		return 1;

	prepare_invertible_block_major(&block_major);
	block_major_to_tuple(&tuple, &block_major);

	setup_counter();
	scalar_block_ticks = bench_one(poly_baseinv_gt_ref, &block_major);
	batch_block_ticks = bench_one(poly_baseinv_gt_batch, &block_major);
	batch_block_scaled_ticks =
		bench_one(poly_baseinv_gt_batch_scaled_r, &block_major);
	scalar_tuple_ticks = bench_one(poly_baseinv_tuple_ref, &tuple);
	batch_tuple_ticks = bench_one(poly_baseinv_gt_tuple_batch, &tuple);

	printf("gt_baseinv_batch_bench_loops: %d\n", GT_BASEINV_BENCH_LOOPS);
	printf("gt_scalar_block_baseinv_ticks: %llu\n", scalar_block_ticks);
	printf("gt_batch_block_baseinv_ticks: %llu\n", batch_block_ticks);
	printf("gt_batch_block_baseinv_scaled_r_ticks: %llu\n",
	       batch_block_scaled_ticks);
	printf("gt_scalar_tuple_baseinv_ticks: %llu\n", scalar_tuple_ticks);
	printf("gt_batch_tuple_baseinv_ticks: %llu\n", batch_tuple_ticks);
	printf("gt_baseinv_batch_sink: %u\n", bench_sink);

	return 0;
}
