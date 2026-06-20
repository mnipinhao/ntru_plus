#include <stdint.h>
#include <stdio.h>

#define TEST_LOOP_COUNT 1000
#include "test/counter.h"

#include "gt_tmvp_quartic_tmvp_experimental.h"
#include "ntt.h"
#include "params.h"

#if !defined(__aarch64__)
#error "bench_gt_tmvp_quartic_tmvp_current requires AArch64 counter support"
#endif

#define GT_BENCH_BRANCHES 2
#define GT_BENCH_BRANCH_N (NTRUPLUS_N / GT_BENCH_BRANCHES)
#define GT_BENCH_ROWS 3
#define GT_BENCH_ROW_N 32
#define GT_BENCH_LANES 4
#define GT_LAZYOUT_INPUT_MIN (-13208)
#define GT_LAZYOUT_INPUT_MAX 13696
#define GT_LAZYOUT_BOUND_LIMIT 6144
#define GT_LAZYOUT_BOUND_DELTA (3 * NTRUPLUS_Q)

#ifndef GT_TMVP_BENCH_SAMPLES
#define GT_TMVP_BENCH_SAMPLES 101
#endif

#ifndef GT_TMVP_BENCH_INNER
#define GT_TMVP_BENCH_INNER 24
#endif

static volatile uint32_t bench_sink;

void bench_kpqc_final_poly_basemul(int16_t r[NTRUPLUS_N],
                                   const int16_t a[NTRUPLUS_N],
                                   const int16_t b[NTRUPLUS_N]);
void bench_kpqc_final_poly_basemul_add(int16_t r[NTRUPLUS_N],
                                       const int16_t a[NTRUPLUS_N],
                                       const int16_t b[NTRUPLUS_N],
                                       const int16_t c[NTRUPLUS_N]);
void bench_production_gt_poly_basemul(int16_t r[NTRUPLUS_N],
                                      const int16_t a[NTRUPLUS_N],
                                      const int16_t b[NTRUPLUS_N]);
void bench_production_gt_poly_basemul_add(int16_t r[NTRUPLUS_N],
                                          const int16_t a[NTRUPLUS_N],
                                          const int16_t b[NTRUPLUS_N],
                                          const int16_t c[NTRUPLUS_N]);
void bench_gt_tmvp_fused_adapter_stage_copy_asm(int16_t r[NTRUPLUS_N],
                                                const int16_t a[NTRUPLUS_N]);
void bench_gt_tmvp_fused_direct_mul_asm(int16_t r[NTRUPLUS_N],
                                        const int16_t a[NTRUPLUS_N],
                                        const int16_t b[NTRUPLUS_N]);
void bench_gt_tmvp_fused_direct_add_asm(int16_t r[NTRUPLUS_N],
                                        const int16_t a[NTRUPLUS_N],
                                        const int16_t b[NTRUPLUS_N],
                                        const int16_t c[NTRUPLUS_N]);
void bench_gt_tmvp_fused_transpose_mul_asm(int16_t r[NTRUPLUS_N],
                                           const int16_t a[NTRUPLUS_N],
                                           const int16_t b[NTRUPLUS_N]);
void bench_gt_tmvp_fused_transpose_add_asm(int16_t r[NTRUPLUS_N],
                                           const int16_t a[NTRUPLUS_N],
                                           const int16_t b[NTRUPLUS_N],
                                           const int16_t c[NTRUPLUS_N]);
int gt_tmvp_quartic_tmvp_experimental_asm_bound_inputs_fast(
	int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N],
	const int16_t b[NTRUPLUS_N]);
int gt_tmvp_quartic_tmvp_add_experimental_asm_bound_inputs_fast(
	int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N],
	const int16_t b[NTRUPLUS_N], const int16_t c[NTRUPLUS_N]);

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static int16_t bounded_sample(uint32_t *state)
{
	return (int16_t)((int)(next_u32(state) % (2 * NTRUPLUS_Q)) -
	                 NTRUPLUS_Q);
}

static int16_t lazyout_sample(uint32_t *state)
{
	const int span = GT_LAZYOUT_INPUT_MAX - GT_LAZYOUT_INPUT_MIN + 1;

	return (int16_t)(GT_LAZYOUT_INPUT_MIN + (int)(next_u32(state) % span));
}

static int16_t bound_lazyout_input(int16_t x)
{
	int v = x;

	if ((int)x > GT_LAZYOUT_BOUND_LIMIT)
	{
		v -= GT_LAZYOUT_BOUND_DELTA;
	}
	if ((int)x < -GT_LAZYOUT_BOUND_LIMIT)
	{
		v += GT_LAZYOUT_BOUND_DELTA;
	}
	return (int16_t)v;
}

static int centered_mod_q(int x)
{
	int r = x % NTRUPLUS_Q;

	if (r < 0)
	{
		r += NTRUPLUS_Q;
	}
	if (r > NTRUPLUS_Q / 2)
	{
		r -= NTRUPLUS_Q;
	}
	return r;
}

static int16_t bench_montgomery_reduce(int32_t a)
{
	int16_t t;

	t = (int16_t)a * 12929;
	t = (a - (int32_t)t * NTRUPLUS_Q) >> 16;
	return t;
}

static void bench_quartic_leaf_mul(int16_t r[GT_BENCH_LANES],
                                   const int16_t a[GT_BENCH_LANES],
                                   const int16_t b[GT_BENCH_LANES],
                                   int16_t zeta)
{
	r[0] = bench_montgomery_reduce((int32_t)a[1] * b[3] +
	                               (int32_t)a[2] * b[2] +
	                               (int32_t)a[3] * b[1]);
	r[1] = bench_montgomery_reduce((int32_t)a[2] * b[3] +
	                               (int32_t)a[3] * b[2]);
	r[2] = bench_montgomery_reduce((int32_t)a[3] * b[3]);

	r[0] = bench_montgomery_reduce((int32_t)r[0] * zeta +
	                               (int32_t)a[0] * b[0]);
	r[1] = bench_montgomery_reduce((int32_t)r[1] * zeta +
	                               (int32_t)a[0] * b[1] +
	                               (int32_t)a[1] * b[0]);
	r[2] = bench_montgomery_reduce((int32_t)r[2] * zeta +
	                               (int32_t)a[0] * b[2] +
	                               (int32_t)a[1] * b[1] +
	                               (int32_t)a[2] * b[0]);
	r[3] = bench_montgomery_reduce((int32_t)a[0] * b[3] +
	                               (int32_t)a[1] * b[2] +
	                               (int32_t)a[2] * b[1] +
	                               (int32_t)a[3] * b[0]);

	r[0] = bench_montgomery_reduce((int32_t)r[0] * 867);
	r[1] = bench_montgomery_reduce((int32_t)r[1] * 867);
	r[2] = bench_montgomery_reduce((int32_t)r[2] * 867);
	r[3] = bench_montgomery_reduce((int32_t)r[3] * 867);
}

static void bench_quartic_leaf_add(int16_t r[GT_BENCH_LANES],
                                   const int16_t a[GT_BENCH_LANES],
                                   const int16_t b[GT_BENCH_LANES],
                                   const int16_t c[GT_BENCH_LANES],
                                   int16_t zeta)
{
	r[0] = bench_montgomery_reduce((int32_t)a[1] * b[3] +
	                               (int32_t)a[2] * b[2] +
	                               (int32_t)a[3] * b[1]);
	r[1] = bench_montgomery_reduce((int32_t)a[2] * b[3] +
	                               (int32_t)a[3] * b[2]);
	r[2] = bench_montgomery_reduce((int32_t)a[3] * b[3]);

	r[0] = bench_montgomery_reduce((int32_t)r[0] * zeta +
	                               (int32_t)a[0] * b[0]);
	r[1] = bench_montgomery_reduce((int32_t)r[1] * zeta +
	                               (int32_t)a[0] * b[1] +
	                               (int32_t)a[1] * b[0]);
	r[2] = bench_montgomery_reduce((int32_t)r[2] * zeta +
	                               (int32_t)a[0] * b[2] +
	                               (int32_t)a[1] * b[1] +
	                               (int32_t)a[2] * b[0]);
	r[3] = bench_montgomery_reduce((int32_t)a[0] * b[3] +
	                               (int32_t)a[1] * b[2] +
	                               (int32_t)a[2] * b[1] +
	                               (int32_t)a[3] * b[0]);

	r[0] = bench_montgomery_reduce((int32_t)c[0] * -147 +
	                               (int32_t)r[0] * 867);
	r[1] = bench_montgomery_reduce((int32_t)c[1] * -147 +
	                               (int32_t)r[1] * 867);
	r[2] = bench_montgomery_reduce((int32_t)c[2] * -147 +
	                               (int32_t)r[2] * 867);
	r[3] = bench_montgomery_reduce((int32_t)c[3] * -147 +
	                               (int32_t)r[3] * 867);
}

static void fill_i16(int16_t v[NTRUPLUS_N], uint32_t seed)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		v[i] = bounded_sample(&seed);
	}
}

static void fill_lazyout_i16(int16_t v[NTRUPLUS_N], uint32_t seed)
{
	static const int16_t edges[] = {
		GT_LAZYOUT_INPUT_MIN, -6145, -6144, -6143, -3457,
		-1728, 0, 1728, 3457, 6143, 6144, 6145,
		GT_LAZYOUT_INPUT_MAX,
	};
	const int nedges = (int)(sizeof(edges) / sizeof(edges[0]));

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (i < nedges)
		{
			v[i] = edges[i];
		}
		else
		{
			v[i] = lazyout_sample(&seed);
		}
	}
}

static int make_bounded_lazyout_inputs(const char *label,
                                       int16_t out[NTRUPLUS_N],
                                       const int16_t in[NTRUPLUS_N])
{
	int max_abs = 0;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		const int16_t x = in[i];
		const int16_t y = bound_lazyout_input(x);
		const int abs_y = y < 0 ? -(int)y : (int)y;

		if (abs_y > max_abs)
		{
			max_abs = abs_y;
		}
		if (abs_y > GT_LAZYOUT_BOUND_LIMIT)
		{
			fprintf(stderr, "%s bound failure at %d: in=%d out=%d\n",
			        label, i, x, y);
			return 0;
		}
		if (centered_mod_q(x) != centered_mod_q(y))
		{
			fprintf(stderr, "%s modulo failure at %d: in=%d out=%d\n",
			        label, i, x, y);
			return 0;
		}
		out[i] = y;
	}

	if (max_abs > GT_LAZYOUT_BOUND_LIMIT)
	{
		fprintf(stderr, "%s unexpected bounded max_abs=%d\n", label,
		        max_abs);
		return 0;
	}
	return 1;
}

static int block_major_index(int branch, int physical_j, int lane)
{
	return branch * GT_BENCH_BRANCH_N + GT_BENCH_LANES * physical_j + lane;
}

static void block_major_to_rowpack(int16_t rowpack[NTRUPLUS_N],
                                   const int16_t block_major[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BENCH_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_BENCH_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_BENCH_ROW_N; k32++)
			{
				const int physical_j =
					gt_tmvp_quartic_tmvp_physical_j(row, k32);

				for (int lane = 0; lane < GT_BENCH_LANES; lane++)
				{
					const int rowpack_idx =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k32);
					const int block_idx =
						block_major_index(branch, physical_j, lane);

					rowpack[rowpack_idx] = block_major[block_idx];
				}
			}
		}
	}
}

static void rowpack_to_block_major(int16_t block_major[NTRUPLUS_N],
                                   const int16_t rowpack[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BENCH_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_BENCH_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_BENCH_ROW_N; k32++)
			{
				const int physical_j =
					gt_tmvp_quartic_tmvp_physical_j(row, k32);

				for (int lane = 0; lane < GT_BENCH_LANES; lane++)
				{
					const int rowpack_idx =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k32);
					const int block_idx =
						block_major_index(branch, physical_j, lane);

					block_major[block_idx] = rowpack[rowpack_idx];
				}
			}
		}
	}
}

static void adapter_mul_c(int16_t r[NTRUPLUS_N],
                          const int16_t a[NTRUPLUS_N],
                          const int16_t b[NTRUPLUS_N])
{
	int16_t ar[NTRUPLUS_N];
	int16_t br[NTRUPLUS_N];
	int16_t rr[NTRUPLUS_N];

	block_major_to_rowpack(ar, a);
	block_major_to_rowpack(br, b);
	(void)gt_tmvp_quartic_tmvp_experimental_c(rr, ar, br);
	rowpack_to_block_major(r, rr);
}

static void adapter_mul_asm(int16_t r[NTRUPLUS_N],
                            const int16_t a[NTRUPLUS_N],
                            const int16_t b[NTRUPLUS_N])
{
	int16_t ar[NTRUPLUS_N];
	int16_t br[NTRUPLUS_N];
	int16_t rr[NTRUPLUS_N];

	block_major_to_rowpack(ar, a);
	block_major_to_rowpack(br, b);
	(void)gt_tmvp_quartic_tmvp_experimental_asm_fast(rr, ar, br);
	rowpack_to_block_major(r, rr);
}

static void adapter_add_c(int16_t r[NTRUPLUS_N],
                          const int16_t a[NTRUPLUS_N],
                          const int16_t b[NTRUPLUS_N],
                          const int16_t c[NTRUPLUS_N])
{
	int16_t ar[NTRUPLUS_N];
	int16_t br[NTRUPLUS_N];
	int16_t cr[NTRUPLUS_N];
	int16_t rr[NTRUPLUS_N];

	block_major_to_rowpack(ar, a);
	block_major_to_rowpack(br, b);
	block_major_to_rowpack(cr, c);
	(void)gt_tmvp_quartic_tmvp_add_experimental_c(rr, ar, br, cr);
	rowpack_to_block_major(r, rr);
}

static void adapter_add_asm(int16_t r[NTRUPLUS_N],
                            const int16_t a[NTRUPLUS_N],
                            const int16_t b[NTRUPLUS_N],
                            const int16_t c[NTRUPLUS_N])
{
	int16_t ar[NTRUPLUS_N];
	int16_t br[NTRUPLUS_N];
	int16_t cr[NTRUPLUS_N];
	int16_t rr[NTRUPLUS_N];

	block_major_to_rowpack(ar, a);
	block_major_to_rowpack(br, b);
	block_major_to_rowpack(cr, c);
	(void)gt_tmvp_quartic_tmvp_add_experimental_asm_fast(rr, ar, br, cr);
	rowpack_to_block_major(r, rr);
}

static void fused_adapter_mul_c(int16_t r[NTRUPLUS_N],
                                const int16_t a[NTRUPLUS_N],
                                const int16_t b[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BENCH_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_BENCH_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_BENCH_ROW_N; k32++)
			{
				const int physical_j =
					gt_tmvp_quartic_tmvp_physical_j(row, k32);
				const int block_idx =
					block_major_index(branch, physical_j, 0);

				bench_quartic_leaf_mul(r + block_idx,
				                       a + block_idx,
				                       b + block_idx,
				                       gt_rowbitrev_lambda[branch][physical_j]);
			}
		}
	}
}

static void fused_adapter_add_c(int16_t r[NTRUPLUS_N],
                                const int16_t a[NTRUPLUS_N],
                                const int16_t b[NTRUPLUS_N],
                                const int16_t c[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BENCH_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_BENCH_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_BENCH_ROW_N; k32++)
			{
				const int physical_j =
					gt_tmvp_quartic_tmvp_physical_j(row, k32);
				const int block_idx =
					block_major_index(branch, physical_j, 0);

				bench_quartic_leaf_add(r + block_idx,
				                       a + block_idx,
				                       b + block_idx,
				                       c + block_idx,
				                       gt_rowbitrev_lambda[branch][physical_j]);
			}
		}
	}
}

static void fused_adapter_stage_copy_c(int16_t r[NTRUPLUS_N],
                                       const int16_t a[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BENCH_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_BENCH_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_BENCH_ROW_N; k32++)
			{
				const int physical_j =
					gt_tmvp_quartic_tmvp_physical_j(row, k32);
				const int block_idx =
					block_major_index(branch, physical_j, 0);

				for (int lane = 0; lane < GT_BENCH_LANES; lane++)
				{
					r[block_idx + lane] = a[block_idx + lane];
				}
			}
		}
	}
}

static int compare_exact(const char *label,
                         const int16_t got[NTRUPLUS_N],
                         const int16_t want[NTRUPLUS_N])
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (got[i] != want[i])
		{
			fprintf(stderr,
			        "%s mismatch at %d: got=%d want=%d delta=%d\n",
			        label, i, got[i], want[i], (int)got[i] - want[i]);
			return 0;
		}
	}
	return 1;
}

static int check_fused_stage_probe(const int16_t a[NTRUPLUS_N])
{
	int16_t got[NTRUPLUS_N];
	int16_t want[NTRUPLUS_N];

	fused_adapter_stage_copy_c(want, a);
	bench_gt_tmvp_fused_adapter_stage_copy_asm(got, a);
	if (!compare_exact("fused_stage_copy_asm", got, want))
	{
		return 0;
	}

	if (!compare_exact("fused_stage_copy_input", got, a))
	{
		return 0;
	}

	return 1;
}

static int check_fused_adapter_probe(const int16_t a[NTRUPLUS_N],
                                     const int16_t b[NTRUPLUS_N],
                                     const int16_t c[NTRUPLUS_N])
{
	int16_t got[NTRUPLUS_N];
	int16_t want[NTRUPLUS_N];

	fused_adapter_mul_c(got, a, b);
	adapter_mul_c(want, a, b);
	if (!compare_exact("fused_adapter_mul_c", got, want))
	{
		return 0;
	}

	fused_adapter_add_c(got, a, b, c);
	adapter_add_c(want, a, b, c);
	if (!compare_exact("fused_adapter_add_c", got, want))
	{
		return 0;
	}

	return 1;
}

static int check_fused_direct_asm_probe(const int16_t a[NTRUPLUS_N],
                                        const int16_t b[NTRUPLUS_N],
                                        const int16_t c[NTRUPLUS_N])
{
	int16_t got[NTRUPLUS_N];
	int16_t want[NTRUPLUS_N];

	bench_gt_tmvp_fused_direct_mul_asm(got, a, b);
	fused_adapter_mul_c(want, a, b);
	if (!compare_exact("fused_direct_mul_asm", got, want))
	{
		return 0;
	}

	bench_gt_tmvp_fused_direct_add_asm(got, a, b, c);
	fused_adapter_add_c(want, a, b, c);
	if (!compare_exact("fused_direct_add_asm", got, want))
	{
		return 0;
	}

	return 1;
}

static int check_fused_transpose_asm_probe(const int16_t a[NTRUPLUS_N],
                                           const int16_t b[NTRUPLUS_N],
                                           const int16_t c[NTRUPLUS_N])
{
	int16_t got[NTRUPLUS_N];
	int16_t want[NTRUPLUS_N];

	bench_gt_tmvp_fused_transpose_mul_asm(got, a, b);
	fused_adapter_mul_c(want, a, b);
	if (!compare_exact("fused_transpose_mul_asm", got, want))
	{
		return 0;
	}

	bench_gt_tmvp_fused_transpose_add_asm(got, a, b, c);
	fused_adapter_add_c(want, a, b, c);
	if (!compare_exact("fused_transpose_add_asm", got, want))
	{
		return 0;
	}

	return 1;
}

static int check_lazyout_bound_inputs_probe(const int16_t a[NTRUPLUS_N],
                                            const int16_t b[NTRUPLUS_N],
                                            const int16_t c[NTRUPLUS_N])
{
	int16_t ba[NTRUPLUS_N];
	int16_t bb[NTRUPLUS_N];
	int16_t bc[NTRUPLUS_N];
	int16_t got[NTRUPLUS_N];
	int16_t want[NTRUPLUS_N];
	int status;

	if (!make_bounded_lazyout_inputs("lazyout_a", ba, a) ||
	    !make_bounded_lazyout_inputs("lazyout_b", bb, b) ||
	    !make_bounded_lazyout_inputs("lazyout_c", bc, c))
	{
		return 0;
	}

	status = gt_tmvp_quartic_tmvp_experimental_asm_bound_inputs_fast(got, a, b);
	if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "bound_inputs_mul_asm status=%s\n",
		        gt_tmvp_quartic_tmvp_experimental_status_name(status));
		return 0;
	}
	(void)gt_tmvp_quartic_tmvp_experimental_c(want, ba, bb);
	if (!compare_exact("lazyout_bound_inputs_mul_asm", got, want))
	{
		return 0;
	}

	status = gt_tmvp_quartic_tmvp_add_experimental_asm_bound_inputs_fast(
		got, a, b, c);
	if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "bound_inputs_add_asm status=%s\n",
		        gt_tmvp_quartic_tmvp_experimental_status_name(status));
		return 0;
	}
	(void)gt_tmvp_quartic_tmvp_add_experimental_c(want, ba, bb, bc);
	if (!compare_exact("lazyout_bound_inputs_add_asm", got, want))
	{
		return 0;
	}

	return 1;
}

static void sort_u64(uint64_t *v, int n)
{
	for (int i = 1; i < n; i++)
	{
		const uint64_t x = v[i];
		int j = i - 1;

		while (j >= 0 && v[j] > x)
		{
			v[j + 1] = v[j];
			j--;
		}
		v[j + 1] = x;
	}
}

typedef void (*bench_target)(int16_t r[NTRUPLUS_N],
                             const int16_t a[NTRUPLUS_N],
                             const int16_t b[NTRUPLUS_N],
                             const int16_t c[NTRUPLUS_N]);

struct bench_result
{
	const char *name;
	uint64_t min_ticks;
	uint64_t median_ticks;
	uint64_t mean_ticks;
};

static void target_rowpack_mul_c(int16_t r[NTRUPLUS_N],
                                 const int16_t a[NTRUPLUS_N],
                                 const int16_t b[NTRUPLUS_N],
                                 const int16_t c[NTRUPLUS_N])
{
	(void)c;
	(void)gt_tmvp_quartic_tmvp_experimental_c(r, a, b);
}

static void target_rowpack_mul_asm(int16_t r[NTRUPLUS_N],
                                   const int16_t a[NTRUPLUS_N],
                                   const int16_t b[NTRUPLUS_N],
                                   const int16_t c[NTRUPLUS_N])
{
	(void)c;
	(void)gt_tmvp_quartic_tmvp_experimental_asm_fast(r, a, b);
}

static void target_rowpack_add_c(int16_t r[NTRUPLUS_N],
                                 const int16_t a[NTRUPLUS_N],
                                 const int16_t b[NTRUPLUS_N],
                                 const int16_t c[NTRUPLUS_N])
{
	(void)gt_tmvp_quartic_tmvp_add_experimental_c(r, a, b, c);
}

static void target_rowpack_add_asm(int16_t r[NTRUPLUS_N],
                                   const int16_t a[NTRUPLUS_N],
                                   const int16_t b[NTRUPLUS_N],
                                   const int16_t c[NTRUPLUS_N])
{
	(void)gt_tmvp_quartic_tmvp_add_experimental_asm_fast(r, a, b, c);
}

static void target_rowpack_mul_bound_inputs_asm(int16_t r[NTRUPLUS_N],
                                                const int16_t a[NTRUPLUS_N],
                                                const int16_t b[NTRUPLUS_N],
                                                const int16_t c[NTRUPLUS_N])
{
	(void)c;
	(void)gt_tmvp_quartic_tmvp_experimental_asm_bound_inputs_fast(r, a, b);
}

static void target_rowpack_add_bound_inputs_asm(int16_t r[NTRUPLUS_N],
                                                const int16_t a[NTRUPLUS_N],
                                                const int16_t b[NTRUPLUS_N],
                                                const int16_t c[NTRUPLUS_N])
{
	(void)gt_tmvp_quartic_tmvp_add_experimental_asm_bound_inputs_fast(r, a, b,
	                                                                 c);
}

static void target_adapter_mul_c(int16_t r[NTRUPLUS_N],
                                 const int16_t a[NTRUPLUS_N],
                                 const int16_t b[NTRUPLUS_N],
                                 const int16_t c[NTRUPLUS_N])
{
	(void)c;
	adapter_mul_c(r, a, b);
}

static void target_adapter_mul_asm(int16_t r[NTRUPLUS_N],
                                   const int16_t a[NTRUPLUS_N],
                                   const int16_t b[NTRUPLUS_N],
                                   const int16_t c[NTRUPLUS_N])
{
	(void)c;
	adapter_mul_asm(r, a, b);
}

static void target_adapter_add_c(int16_t r[NTRUPLUS_N],
                                 const int16_t a[NTRUPLUS_N],
                                 const int16_t b[NTRUPLUS_N],
                                 const int16_t c[NTRUPLUS_N])
{
	adapter_add_c(r, a, b, c);
}

static void target_adapter_add_asm(int16_t r[NTRUPLUS_N],
                                   const int16_t a[NTRUPLUS_N],
                                   const int16_t b[NTRUPLUS_N],
                                   const int16_t c[NTRUPLUS_N])
{
	adapter_add_asm(r, a, b, c);
}

static void target_fused_adapter_mul_c(int16_t r[NTRUPLUS_N],
                                       const int16_t a[NTRUPLUS_N],
                                       const int16_t b[NTRUPLUS_N],
                                       const int16_t c[NTRUPLUS_N])
{
	(void)c;
	fused_adapter_mul_c(r, a, b);
}

static void target_fused_adapter_add_c(int16_t r[NTRUPLUS_N],
                                       const int16_t a[NTRUPLUS_N],
                                       const int16_t b[NTRUPLUS_N],
                                       const int16_t c[NTRUPLUS_N])
{
	fused_adapter_add_c(r, a, b, c);
}

static void target_fused_stage_copy_c(int16_t r[NTRUPLUS_N],
                                      const int16_t a[NTRUPLUS_N],
                                      const int16_t b[NTRUPLUS_N],
                                      const int16_t c[NTRUPLUS_N])
{
	(void)b;
	(void)c;
	fused_adapter_stage_copy_c(r, a);
}

static void target_fused_stage_copy_asm(int16_t r[NTRUPLUS_N],
                                        const int16_t a[NTRUPLUS_N],
                                        const int16_t b[NTRUPLUS_N],
                                        const int16_t c[NTRUPLUS_N])
{
	(void)b;
	(void)c;
	bench_gt_tmvp_fused_adapter_stage_copy_asm(r, a);
}

static void target_fused_direct_mul_asm(int16_t r[NTRUPLUS_N],
                                        const int16_t a[NTRUPLUS_N],
                                        const int16_t b[NTRUPLUS_N],
                                        const int16_t c[NTRUPLUS_N])
{
	(void)c;
	bench_gt_tmvp_fused_direct_mul_asm(r, a, b);
}

static void target_fused_direct_add_asm(int16_t r[NTRUPLUS_N],
                                        const int16_t a[NTRUPLUS_N],
                                        const int16_t b[NTRUPLUS_N],
                                        const int16_t c[NTRUPLUS_N])
{
	bench_gt_tmvp_fused_direct_add_asm(r, a, b, c);
}

static void target_fused_transpose_mul_asm(int16_t r[NTRUPLUS_N],
                                           const int16_t a[NTRUPLUS_N],
                                           const int16_t b[NTRUPLUS_N],
                                           const int16_t c[NTRUPLUS_N])
{
	(void)c;
	bench_gt_tmvp_fused_transpose_mul_asm(r, a, b);
}

static void target_fused_transpose_add_asm(int16_t r[NTRUPLUS_N],
                                           const int16_t a[NTRUPLUS_N],
                                           const int16_t b[NTRUPLUS_N],
                                           const int16_t c[NTRUPLUS_N])
{
	bench_gt_tmvp_fused_transpose_add_asm(r, a, b, c);
}

static void target_kpqc_final_mul_asm(int16_t r[NTRUPLUS_N],
                                      const int16_t a[NTRUPLUS_N],
                                      const int16_t b[NTRUPLUS_N],
                                      const int16_t c[NTRUPLUS_N])
{
	(void)c;
	bench_kpqc_final_poly_basemul(r, a, b);
}

static void target_kpqc_final_add_asm(int16_t r[NTRUPLUS_N],
                                      const int16_t a[NTRUPLUS_N],
                                      const int16_t b[NTRUPLUS_N],
                                      const int16_t c[NTRUPLUS_N])
{
	bench_kpqc_final_poly_basemul_add(r, a, b, c);
}

static void target_production_gt_mul_asm(int16_t r[NTRUPLUS_N],
                                         const int16_t a[NTRUPLUS_N],
                                         const int16_t b[NTRUPLUS_N],
                                         const int16_t c[NTRUPLUS_N])
{
	(void)c;
	bench_production_gt_poly_basemul(r, a, b);
}

static void target_production_gt_add_asm(int16_t r[NTRUPLUS_N],
                                         const int16_t a[NTRUPLUS_N],
                                         const int16_t b[NTRUPLUS_N],
                                         const int16_t c[NTRUPLUS_N])
{
	bench_production_gt_poly_basemul_add(r, a, b, c);
}

static struct bench_result run_one(const char *name, bench_target target,
                                   const int16_t a[NTRUPLUS_N],
                                   const int16_t b[NTRUPLUS_N],
                                   const int16_t c[NTRUPLUS_N])
{
	int16_t r[NTRUPLUS_N];
	uint64_t samples[GT_TMVP_BENCH_SAMPLES];
	uint64_t total = 0;

	for (int i = 0; i < GT_TMVP_BENCH_SAMPLES; i++)
	{
		int tap = i;
		const uint64_t begin = counter();
		for (int j = 0; j < GT_TMVP_BENCH_INNER; j++)
		{
			target(r, a, b, c);
			bench_sink += (uint32_t)(uint16_t)r[tap] + (uint32_t)(j + 1);
			tap += 29;
			if (tap >= NTRUPLUS_N)
			{
				tap -= NTRUPLUS_N;
			}
		}
		const uint64_t end = counter();
		uint64_t elapsed = end - begin;

		if (elapsed > countergap)
		{
			elapsed -= countergap;
		}

		samples[i] = elapsed / GT_TMVP_BENCH_INNER;
		total += samples[i];
	}

	sort_u64(samples, GT_TMVP_BENCH_SAMPLES);

	{
		struct bench_result result;
		result.name = name;
		result.min_ticks = samples[0];
		result.median_ticks = samples[GT_TMVP_BENCH_SAMPLES / 2];
		result.mean_ticks = total / GT_TMVP_BENCH_SAMPLES;
		return result;
	}
}

static int write_report(const struct bench_result *results, int nresults)
{
	FILE *f = fopen("docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-current-bench-report.yml",
	                "w");

	if (f == 0)
	{
		return 0;
	}

	fprintf(f, "benchmark_status: experimental_current_comparison_done\n");
	fprintf(f, "selected_path: complete_ntt32_quartic_tmvp\n");
	fprintf(f, "clock_source: cntvct_el0\n");
	fprintf(f, "metric_unit: cntvct_ticks_per_call\n");
	fprintf(f, "samples: %d\n", GT_TMVP_BENCH_SAMPLES);
	fprintf(f, "inner_iterations_per_sample: %d\n", GT_TMVP_BENCH_INNER);
	fprintf(f, "countergap_ticks: %llu\n", countergap);
	fprintf(f, "sink_after_run: %u\n", bench_sink);
	fprintf(f, "comparison_goal: tmvp_vs_kpqc_final_gt_production_rowback\n");
	fprintf(f, "compared_surfaces: rowpack_kernel_block_major_adapter_fused_probe_stage_copy_fused_direct_asm_fused_transpose_asm_and_basemul_asm_baselines\n");
	fprintf(f, "lambda_load_strategy: rowpack_ordered_vector_table\n");
	fprintf(f, "lambda_rowpack_table_bytes: 384\n");
	fprintf(f, "lambda_address_generation: streaming_postincrement\n");
	fprintf(f, "rowpack_address_generation: row_base_plus_k_postincrement\n");
	fprintf(f, "rowpack_asm_fast_entry_used: true\n");
	fprintf(f, "stack_lambda_gather_used: false\n");
	fprintf(f, "lazyout_bounding_probe_added: true\n");
	fprintf(f, "lazyout_bounding_rule: add_or_sub_3q_when_abs_exceeds_6144\n");
	fprintf(f, "lazyout_bounding_input_min: %d\n", GT_LAZYOUT_INPUT_MIN);
	fprintf(f, "lazyout_bounding_input_max: %d\n", GT_LAZYOUT_INPUT_MAX);
	fprintf(f, "lazyout_bounding_safe_limit_abs: %d\n",
	        GT_LAZYOUT_BOUND_LIMIT);
	fprintf(f, "lazyout_bounding_observed_output_max_abs: %d\n",
	        GT_LAZYOUT_BOUND_LIMIT);
	fprintf(f, "lazyout_bounding_exact_check: pass_against_c_with_prebounded_inputs\n");
	fprintf(f, "lazyout_bounding_mul_inputs_reduced: a_b\n");
	fprintf(f, "lazyout_bounding_add_inputs_reduced: a_b_c\n");
	fprintf(f, "fused_adapter_probe_added: true\n");
	fprintf(f, "fused_adapter_probe_exact_check: pass_against_current_adapter_c\n");
	fprintf(f, "fused_adapter_reductions_in_layout_movement: false\n");
	fprintf(f, "fused_stage_copy_asm_probe_added: true\n");
	fprintf(f, "fused_stage_copy_asm_exact_check: pass_against_c_and_input\n");
	fprintf(f, "fused_stage_copy_reductions: false\n");
	fprintf(f, "fused_direct_asm_probe_added: true\n");
	fprintf(f, "fused_direct_asm_exact_check: pass_against_fused_adapter_c\n");
	fprintf(f, "fused_direct_asm_layout: production_block_major_direct_gather_scatter\n");
	fprintf(f, "fused_direct_asm_reductions_in_layout_movement: false\n");
	fprintf(f, "fused_transpose_asm_probe_added: true\n");
	fprintf(f, "fused_transpose_asm_exact_check: pass_against_fused_adapter_c\n");
	fprintf(f, "fused_transpose_asm_layout: production_block_major_dload_transpose_gather_scatter\n");
	fprintf(f, "fused_transpose_asm_reductions_in_layout_movement: false\n");
	fprintf(f, "kpqc_final_basemul_asm_baseline_added: true\n");
	fprintf(f, "production_gt_basemul_asm_baseline_added: true\n");
	fprintf(f, "rowback_surface_included_by_adapter_paths: true\n");
	fprintf(f, "benchmark_or_cycle_claim_made: true\n");
	fprintf(f, "correctness_claim_made: false\n");
	fprintf(f, "final_candidate_selected: false\n");
	fprintf(f, "results:\n");
	for (int i = 0; i < nresults; i++)
	{
		fprintf(f, "  - name: %s\n", results[i].name);
		fprintf(f, "    min_ticks: %llu\n",
		        (unsigned long long)results[i].min_ticks);
		fprintf(f, "    median_ticks: %llu\n",
		        (unsigned long long)results[i].median_ticks);
		fprintf(f, "    mean_ticks: %llu\n",
		        (unsigned long long)results[i].mean_ticks);
	}
	fprintf(f, "notes:\n");
	fprintf(f, "  - adapter paths include block-major to rowpack conversion and rowpack to block-major conversion.\n");
	fprintf(f, "  - fused-adapter C probe directly stages public block-major indices and does not reduce during layout movement.\n");
	fprintf(f, "  - fused-stage-copy ASM probe is load/store-only and gives a single-surface staging lower bound, not a full fused multiplication cost.\n");
	fprintf(f, "  - fused-direct ASM probe uses the rowpack batch8 arithmetic with public production block-major gather/scatter loads and stores.\n");
	fprintf(f, "  - fused-transpose ASM probe loads each quartic leaf with d-loads and transposes 8x4 halfword blocks into the same batch8 arithmetic layout.\n");
	fprintf(f, "  - fused-adapter exact check compares against the current block-major adapter C path before timing.\n");
	fprintf(f, "  - fused-direct ASM exact check compares against the fused-adapter C probe before timing.\n");
	fprintf(f, "  - fused-transpose ASM exact check compares against the fused-adapter C probe before timing.\n");
	fprintf(f, "  - kpqc-final and production-gt baseline rows measure their ASM basemul/basemul_add surfaces with benchmark-only renamed symbols.\n");
	fprintf(f, "  - baseline rows are not mathematical-output comparisons because stock, GT, and TMVP consume different transformed-domain layouts.\n");
	fprintf(f, "  - ASM rowpack kernels use a rowpack-vector-order lambda table rather than per-batch stack gather.\n");
	fprintf(f, "  - rowpack ASM timing calls the fast entry; public checked entry remains covered by the ASM wiring test.\n");
	fprintf(f, "  - lazyout bound-input rows measure an opt-in ASM entry that bounds rowpack inputs after load and before the first widening multiply.\n");
	fprintf(f, "  - lazyout bound-input correctness compares against the C TMVP path fed with pre-bounded inputs that are congruent modulo q.\n");
	fprintf(f, "  - this report does not benchmark full KEM keygen/encap/decap cycle counts.\n");
	fprintf(f, "  - this report does not select a final candidate.\n");
	fprintf(f, "recommended_next_gate: compare_lazyout_ntt_saving_against_rowpack_bound_inputs_delta\n");
	fclose(f);

	return 1;
}

int main(void)
{
	int16_t a[NTRUPLUS_N];
	int16_t b[NTRUPLUS_N];
	int16_t c[NTRUPLUS_N];
	int16_t lazy_a[NTRUPLUS_N];
	int16_t lazy_b[NTRUPLUS_N];
	int16_t lazy_c[NTRUPLUS_N];
	struct bench_result results[24];
	int nresults = 0;

	fill_i16(a, 0x10203040u);
	fill_i16(b, 0x55667788u);
	fill_i16(c, 0x9abcdef0u);
	fill_lazyout_i16(lazy_a, 0x13579bdfu);
	fill_lazyout_i16(lazy_b, 0x2468ace0u);
	fill_lazyout_i16(lazy_c, 0x0badf00du);

	if (!check_fused_stage_probe(a))
	{
		return 1;
	}

	if (!check_fused_adapter_probe(a, b, c))
	{
		return 1;
	}

	if (!check_fused_direct_asm_probe(a, b, c))
	{
		return 1;
	}

	if (!check_fused_transpose_asm_probe(a, b, c))
	{
		return 1;
	}

	if (!check_lazyout_bound_inputs_probe(lazy_a, lazy_b, lazy_c))
	{
		return 1;
	}

	setup_counter();

	results[nresults++] = run_one("rowpack_mul_c", target_rowpack_mul_c,
	                              a, b, c);
	results[nresults++] = run_one("rowpack_mul_asm", target_rowpack_mul_asm,
	                              a, b, c);
	results[nresults++] = run_one("rowpack_add_c", target_rowpack_add_c,
	                              a, b, c);
	results[nresults++] = run_one("rowpack_add_asm", target_rowpack_add_asm,
	                              a, b, c);
	results[nresults++] = run_one("rowpack_lazy_mul_asm",
	                              target_rowpack_mul_asm, lazy_a, lazy_b,
	                              lazy_c);
	results[nresults++] = run_one("rowpack_lazy_mul_bound_inputs_asm",
	                              target_rowpack_mul_bound_inputs_asm,
	                              lazy_a, lazy_b, lazy_c);
	results[nresults++] = run_one("rowpack_lazy_add_asm",
	                              target_rowpack_add_asm, lazy_a, lazy_b,
	                              lazy_c);
	results[nresults++] = run_one("rowpack_lazy_add_bound_inputs_asm",
	                              target_rowpack_add_bound_inputs_asm,
	                              lazy_a, lazy_b, lazy_c);
	results[nresults++] = run_one("adapter_mul_c", target_adapter_mul_c,
	                              a, b, c);
	results[nresults++] = run_one("adapter_mul_asm", target_adapter_mul_asm,
	                              a, b, c);
	results[nresults++] = run_one("adapter_add_c", target_adapter_add_c,
	                              a, b, c);
	results[nresults++] = run_one("adapter_add_asm", target_adapter_add_asm,
	                              a, b, c);
	results[nresults++] = run_one("fused_adapter_mul_c",
	                              target_fused_adapter_mul_c, a, b, c);
	results[nresults++] = run_one("fused_adapter_add_c",
	                              target_fused_adapter_add_c, a, b, c);
	results[nresults++] = run_one("fused_stage_copy_c",
	                              target_fused_stage_copy_c, a, b, c);
	results[nresults++] = run_one("fused_stage_copy_asm",
	                              target_fused_stage_copy_asm, a, b, c);
	results[nresults++] = run_one("fused_direct_mul_asm",
	                              target_fused_direct_mul_asm, a, b, c);
	results[nresults++] = run_one("fused_direct_add_asm",
	                              target_fused_direct_add_asm, a, b, c);
	results[nresults++] = run_one("fused_transpose_mul_asm",
	                              target_fused_transpose_mul_asm, a, b, c);
	results[nresults++] = run_one("fused_transpose_add_asm",
	                              target_fused_transpose_add_asm, a, b, c);
	results[nresults++] = run_one("kpqc_final_mul_asm",
	                              target_kpqc_final_mul_asm, a, b, c);
	results[nresults++] = run_one("kpqc_final_add_asm",
	                              target_kpqc_final_add_asm, a, b, c);
	results[nresults++] = run_one("production_gt_mul_asm",
	                              target_production_gt_mul_asm, a, b, c);
	results[nresults++] = run_one("production_gt_add_asm",
	                              target_production_gt_add_asm, a, b, c);

	if (!write_report(results, nresults))
	{
		fprintf(stderr, "could not write current benchmark report\n");
		return 1;
	}

	printf("complete-NTT32 quartic TMVP current benchmark summary:\n");
	printf("  samples: %d\n", GT_TMVP_BENCH_SAMPLES);
	printf("  inner iterations/sample: %d\n", GT_TMVP_BENCH_INNER);
	printf("  countergap ticks: %llu\n", countergap);
	for (int i = 0; i < nresults; i++)
	{
		printf("  %-16s min=%llu median=%llu mean=%llu cntvct_ticks/call\n",
		       results[i].name,
		       (unsigned long long)results[i].min_ticks,
		       (unsigned long long)results[i].median_ticks,
		       (unsigned long long)results[i].mean_ticks);
	}
	printf("  sink: %u\n", bench_sink);

	return 0;
}
