#include "gt_tmvp_quartic_tmvp_experimental.h"

#include <stdint.h>

#include "ntt.h"

#if NTRUPLUS_N != 768
#error "gt_tmvp_quartic_tmvp_experimental_c is specialized for NTRU+768"
#endif

#define GT_TMVP_BRANCHES 2
#define GT_TMVP_BRANCH_N (NTRUPLUS_N / GT_TMVP_BRANCHES)
#define GT_TMVP_ROWS 3
#define GT_TMVP_ROW_N 32
#define GT_TMVP_QUARTIC_LANES 4

#define GT_TMVP_NTRUPLUS_R (-147)
#define GT_TMVP_NTRUPLUS_RSQ 867
#define GT_TMVP_NTRUPLUS_QINV 12929

const char *gt_tmvp_quartic_tmvp_experimental_status_name(int status)
{
	switch (status)
	{
	case GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK:
		return "OK";
	case GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT:
		return "INVALID_ARGUMENT";
	case GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_DISABLED:
		return "DISABLED";
	default:
		return "UNKNOWN";
	}
}

int gt_tmvp_quartic_tmvp_rowpack_index(int branch, int row, int lane,
                                       int k32)
{
	return branch * GT_TMVP_BRANCH_N +
	       row * (GT_TMVP_QUARTIC_LANES * GT_TMVP_ROW_N) +
	       lane * GT_TMVP_ROW_N + k32;
}

int gt_tmvp_quartic_tmvp_physical_j(int row, int k32)
{
	return (GT_TMVP_ROW_N * row + GT_TMVP_ROWS * k32) %
	       (GT_TMVP_ROWS * GT_TMVP_ROW_N);
}
#if defined(GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C)
static int16_t gt_tmvp_montgomery_reduce(int32_t a)
{
	int16_t t;

	t = (int16_t)a * GT_TMVP_NTRUPLUS_QINV;
	t = (a - (int32_t)t * NTRUPLUS_Q) >> 16;
	return t;
}

static int16_t gt_tmvp_fqmul(int16_t a, int16_t b)
{
	return gt_tmvp_montgomery_reduce((int32_t)a * b);
}

static void gt_tmvp_quartic_leaf_experimental_c(int16_t r[GT_TMVP_QUARTIC_LANES],
                                                const int16_t a[GT_TMVP_QUARTIC_LANES],
                                                const int16_t b[GT_TMVP_QUARTIC_LANES],
                                                int16_t zeta)
{
	r[0] = gt_tmvp_montgomery_reduce((int32_t)a[1] * b[3] +
	                                 (int32_t)a[2] * b[2] +
	                                 (int32_t)a[3] * b[1]);
	r[1] = gt_tmvp_montgomery_reduce((int32_t)a[2] * b[3] +
	                                 (int32_t)a[3] * b[2]);
	r[2] = gt_tmvp_montgomery_reduce((int32_t)a[3] * b[3]);

	r[0] = gt_tmvp_montgomery_reduce((int32_t)r[0] * zeta +
	                                 (int32_t)a[0] * b[0]);
	r[1] = gt_tmvp_montgomery_reduce((int32_t)r[1] * zeta +
	                                 (int32_t)a[0] * b[1] +
	                                 (int32_t)a[1] * b[0]);
	r[2] = gt_tmvp_montgomery_reduce((int32_t)r[2] * zeta +
	                                 (int32_t)a[0] * b[2] +
	                                 (int32_t)a[1] * b[1] +
	                                 (int32_t)a[2] * b[0]);
	r[3] = gt_tmvp_montgomery_reduce((int32_t)a[0] * b[3] +
	                                 (int32_t)a[1] * b[2] +
	                                 (int32_t)a[2] * b[1] +
	                                 (int32_t)a[3] * b[0]);

	r[0] = gt_tmvp_montgomery_reduce((int32_t)r[0] * GT_TMVP_NTRUPLUS_RSQ);
	r[1] = gt_tmvp_montgomery_reduce((int32_t)r[1] * GT_TMVP_NTRUPLUS_RSQ);
	r[2] = gt_tmvp_montgomery_reduce((int32_t)r[2] * GT_TMVP_NTRUPLUS_RSQ);
	r[3] = gt_tmvp_montgomery_reduce((int32_t)r[3] * GT_TMVP_NTRUPLUS_RSQ);
}

static void gt_tmvp_quartic_leaf_add_experimental_c(
	int16_t r[GT_TMVP_QUARTIC_LANES],
	const int16_t a[GT_TMVP_QUARTIC_LANES],
	const int16_t b[GT_TMVP_QUARTIC_LANES],
	const int16_t c[GT_TMVP_QUARTIC_LANES],
	int16_t zeta)
{
	r[0] = gt_tmvp_montgomery_reduce((int32_t)a[1] * b[3] +
	                                 (int32_t)a[2] * b[2] +
	                                 (int32_t)a[3] * b[1]);
	r[1] = gt_tmvp_montgomery_reduce((int32_t)a[2] * b[3] +
	                                 (int32_t)a[3] * b[2]);
	r[2] = gt_tmvp_montgomery_reduce((int32_t)a[3] * b[3]);

	r[0] = gt_tmvp_montgomery_reduce((int32_t)r[0] * zeta +
	                                 (int32_t)a[0] * b[0]);
	r[1] = gt_tmvp_montgomery_reduce((int32_t)r[1] * zeta +
	                                 (int32_t)a[0] * b[1] +
	                                 (int32_t)a[1] * b[0]);
	r[2] = gt_tmvp_montgomery_reduce((int32_t)r[2] * zeta +
	                                 (int32_t)a[0] * b[2] +
	                                 (int32_t)a[1] * b[1] +
	                                 (int32_t)a[2] * b[0]);
	r[3] = gt_tmvp_montgomery_reduce((int32_t)a[0] * b[3] +
	                                 (int32_t)a[1] * b[2] +
	                                 (int32_t)a[2] * b[1] +
	                                 (int32_t)a[3] * b[0]);

	r[0] = gt_tmvp_montgomery_reduce((int32_t)c[0] * GT_TMVP_NTRUPLUS_R +
	                                 (int32_t)r[0] * GT_TMVP_NTRUPLUS_RSQ);
	r[1] = gt_tmvp_montgomery_reduce((int32_t)c[1] * GT_TMVP_NTRUPLUS_R +
	                                 (int32_t)r[1] * GT_TMVP_NTRUPLUS_RSQ);
	r[2] = gt_tmvp_montgomery_reduce((int32_t)c[2] * GT_TMVP_NTRUPLUS_R +
	                                 (int32_t)r[2] * GT_TMVP_NTRUPLUS_RSQ);
	r[3] = gt_tmvp_montgomery_reduce((int32_t)c[3] * GT_TMVP_NTRUPLUS_R +
	                                 (int32_t)r[3] * GT_TMVP_NTRUPLUS_RSQ);
}
#endif

static int gt_tmvp_check_3args(int16_t r[NTRUPLUS_N],
                               const int16_t a[NTRUPLUS_N],
                               const int16_t b[NTRUPLUS_N])
{
	return r != 0 && a != 0 && b != 0;
}

static int gt_tmvp_check_4args(int16_t r[NTRUPLUS_N],
                               const int16_t a[NTRUPLUS_N],
                               const int16_t b[NTRUPLUS_N],
                               const int16_t c[NTRUPLUS_N])
{
	return r != 0 && a != 0 && b != 0 && c != 0;
}

int gt_tmvp_quartic_tmvp_experimental_c(int16_t r[NTRUPLUS_N],
                                        const int16_t a[NTRUPLUS_N],
                                        const int16_t b[NTRUPLUS_N])
{
	if (!gt_tmvp_check_3args(r, a, b))
	{
		return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT;
	}

#if !defined(GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C)
	return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_DISABLED;
#else
	for (int branch = 0; branch < GT_TMVP_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_TMVP_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_TMVP_ROW_N; k32++)
			{
				int16_t aa[GT_TMVP_QUARTIC_LANES];
				int16_t bb[GT_TMVP_QUARTIC_LANES];
				int16_t rr[GT_TMVP_QUARTIC_LANES];
				const int physical_j =
					gt_tmvp_quartic_tmvp_physical_j(row, k32);

				for (int lane = 0; lane < GT_TMVP_QUARTIC_LANES; lane++)
				{
					const int index = gt_tmvp_quartic_tmvp_rowpack_index(
						branch, row, lane, k32);
					aa[lane] = a[index];
					bb[lane] = b[index];
				}

				gt_tmvp_quartic_leaf_experimental_c(
					rr, aa, bb, gt_rowbitrev_lambda[branch][physical_j]);

				for (int lane = 0; lane < GT_TMVP_QUARTIC_LANES; lane++)
				{
					const int index = gt_tmvp_quartic_tmvp_rowpack_index(
						branch, row, lane, k32);
					r[index] = rr[lane];
				}
			}
		}
	}

	return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK;
#endif
}

int gt_tmvp_quartic_tmvp_add_experimental_c(int16_t r[NTRUPLUS_N],
                                            const int16_t a[NTRUPLUS_N],
                                            const int16_t b[NTRUPLUS_N],
                                            const int16_t c[NTRUPLUS_N])
{
	if (!gt_tmvp_check_4args(r, a, b, c))
	{
		return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT;
	}

#if !defined(GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C)
	return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_DISABLED;
#else
	for (int branch = 0; branch < GT_TMVP_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_TMVP_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_TMVP_ROW_N; k32++)
			{
				int16_t aa[GT_TMVP_QUARTIC_LANES];
				int16_t bb[GT_TMVP_QUARTIC_LANES];
				int16_t cc[GT_TMVP_QUARTIC_LANES];
				int16_t rr[GT_TMVP_QUARTIC_LANES];
				const int physical_j =
					gt_tmvp_quartic_tmvp_physical_j(row, k32);

				for (int lane = 0; lane < GT_TMVP_QUARTIC_LANES; lane++)
				{
					const int index = gt_tmvp_quartic_tmvp_rowpack_index(
						branch, row, lane, k32);
					aa[lane] = a[index];
					bb[lane] = b[index];
					cc[lane] = c[index];
				}

				gt_tmvp_quartic_leaf_add_experimental_c(
					rr, aa, bb, cc, gt_rowbitrev_lambda[branch][physical_j]);

				for (int lane = 0; lane < GT_TMVP_QUARTIC_LANES; lane++)
				{
					const int index = gt_tmvp_quartic_tmvp_rowpack_index(
						branch, row, lane, k32);
					r[index] = rr[lane];
				}
			}
		}
	}

	return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK;
#endif
}

int gt_tmvp_quartic_tmvp_incomplete_materialized_stage5_adapter_c(
	int16_t r[NTRUPLUS_N],
	const int16_t a_stage4[NTRUPLUS_N],
	const int16_t b_stage4[NTRUPLUS_N])
{
	if (!gt_tmvp_check_3args(r, a_stage4, b_stage4))
	{
		return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT;
	}

#if !defined(GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C)
	return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_DISABLED;
#else
	for (int branch = 0; branch < GT_TMVP_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_TMVP_ROWS; row++)
		{
			for (int pair = 0; pair < GT_TMVP_ROW_N / 2; pair++)
			{
				const int k_even = 2 * pair;
				const int k_odd = k_even + 1;
				const int even_j =
					gt_tmvp_quartic_tmvp_physical_j(row, k_even);
				const int odd_j =
					gt_tmvp_quartic_tmvp_physical_j(row, k_odd);
				const int16_t w = gt_ntt32_ct_twiddle(5, (unsigned)k_even);
				int16_t a_even[GT_TMVP_QUARTIC_LANES];
				int16_t a_odd[GT_TMVP_QUARTIC_LANES];
				int16_t b_even[GT_TMVP_QUARTIC_LANES];
				int16_t b_odd[GT_TMVP_QUARTIC_LANES];
				int16_t r_even[GT_TMVP_QUARTIC_LANES];
				int16_t r_odd[GT_TMVP_QUARTIC_LANES];

				for (int lane = 0; lane < GT_TMVP_QUARTIC_LANES; lane++)
				{
					const int even_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_even);
					const int odd_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_odd);
					const int16_t awv =
						gt_tmvp_fqmul(a_stage4[odd_index], w);
					const int16_t bwv =
						gt_tmvp_fqmul(b_stage4[odd_index], w);

					a_even[lane] = (int16_t)(a_stage4[even_index] + awv);
					a_odd[lane] = (int16_t)(a_stage4[even_index] - awv);
					b_even[lane] = (int16_t)(b_stage4[even_index] + bwv);
					b_odd[lane] = (int16_t)(b_stage4[even_index] - bwv);
				}

				gt_tmvp_quartic_leaf_experimental_c(
					r_even, a_even, b_even, gt_rowbitrev_lambda[branch][even_j]);
				gt_tmvp_quartic_leaf_experimental_c(
					r_odd, a_odd, b_odd, gt_rowbitrev_lambda[branch][odd_j]);

				for (int lane = 0; lane < GT_TMVP_QUARTIC_LANES; lane++)
				{
					const int even_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_even);
					const int odd_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_odd);

					r[even_index] = (int16_t)(r_even[lane] + r_odd[lane]);
					r[odd_index] = (int16_t)(r_even[lane] - r_odd[lane]);
				}
			}
		}
	}

	return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK;
#endif
}

int gt_tmvp_quartic_tmvp_add_incomplete_materialized_stage5_adapter_c(
	int16_t r[NTRUPLUS_N],
	const int16_t a_stage4[NTRUPLUS_N],
	const int16_t b_stage4[NTRUPLUS_N],
	const int16_t c_stage4[NTRUPLUS_N])
{
	if (!gt_tmvp_check_4args(r, a_stage4, b_stage4, c_stage4))
	{
		return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT;
	}

#if !defined(GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C)
	return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_DISABLED;
#else
	for (int branch = 0; branch < GT_TMVP_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_TMVP_ROWS; row++)
		{
			for (int pair = 0; pair < GT_TMVP_ROW_N / 2; pair++)
			{
				const int k_even = 2 * pair;
				const int k_odd = k_even + 1;
				const int even_j =
					gt_tmvp_quartic_tmvp_physical_j(row, k_even);
				const int odd_j =
					gt_tmvp_quartic_tmvp_physical_j(row, k_odd);
				const int16_t w = gt_ntt32_ct_twiddle(5, (unsigned)k_even);
				int16_t a_even[GT_TMVP_QUARTIC_LANES];
				int16_t a_odd[GT_TMVP_QUARTIC_LANES];
				int16_t b_even[GT_TMVP_QUARTIC_LANES];
				int16_t b_odd[GT_TMVP_QUARTIC_LANES];
				int16_t c_even[GT_TMVP_QUARTIC_LANES];
				int16_t c_odd[GT_TMVP_QUARTIC_LANES];
				int16_t r_even[GT_TMVP_QUARTIC_LANES];
				int16_t r_odd[GT_TMVP_QUARTIC_LANES];

				for (int lane = 0; lane < GT_TMVP_QUARTIC_LANES; lane++)
				{
					const int even_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_even);
					const int odd_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_odd);
					const int16_t awv =
						gt_tmvp_fqmul(a_stage4[odd_index], w);
					const int16_t bwv =
						gt_tmvp_fqmul(b_stage4[odd_index], w);
					const int16_t cwv =
						gt_tmvp_fqmul(c_stage4[odd_index], w);

					a_even[lane] = (int16_t)(a_stage4[even_index] + awv);
					a_odd[lane] = (int16_t)(a_stage4[even_index] - awv);
					b_even[lane] = (int16_t)(b_stage4[even_index] + bwv);
					b_odd[lane] = (int16_t)(b_stage4[even_index] - bwv);
					c_even[lane] = (int16_t)(c_stage4[even_index] + cwv);
					c_odd[lane] = (int16_t)(c_stage4[even_index] - cwv);
				}

				gt_tmvp_quartic_leaf_add_experimental_c(
					r_even, a_even, b_even, c_even,
					gt_rowbitrev_lambda[branch][even_j]);
				gt_tmvp_quartic_leaf_add_experimental_c(
					r_odd, a_odd, b_odd, c_odd,
					gt_rowbitrev_lambda[branch][odd_j]);

				for (int lane = 0; lane < GT_TMVP_QUARTIC_LANES; lane++)
				{
					const int even_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_even);
					const int odd_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_odd);

					r[even_index] = (int16_t)(r_even[lane] + r_odd[lane]);
					r[odd_index] = (int16_t)(r_even[lane] - r_odd[lane]);
				}
			}
		}
	}

	return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK;
#endif
}

int gt_tmvp_quartic_tmvp_incomplete_complete_stage5_adapter_c(
	int16_t r[NTRUPLUS_N],
	const int16_t a_complete[NTRUPLUS_N],
	const int16_t b_complete[NTRUPLUS_N])
{
	if (!gt_tmvp_check_3args(r, a_complete, b_complete))
	{
		return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT;
	}

#if !defined(GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C)
	return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_DISABLED;
#else
	for (int branch = 0; branch < GT_TMVP_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_TMVP_ROWS; row++)
		{
			for (int pair = 0; pair < GT_TMVP_ROW_N / 2; pair++)
			{
				const int k_even = 2 * pair;
				const int k_odd = k_even + 1;
				const int even_j =
					gt_tmvp_quartic_tmvp_physical_j(row, k_even);
				const int odd_j =
					gt_tmvp_quartic_tmvp_physical_j(row, k_odd);
				int16_t a_even[GT_TMVP_QUARTIC_LANES];
				int16_t a_odd[GT_TMVP_QUARTIC_LANES];
				int16_t b_even[GT_TMVP_QUARTIC_LANES];
				int16_t b_odd[GT_TMVP_QUARTIC_LANES];
				int16_t r_even[GT_TMVP_QUARTIC_LANES];
				int16_t r_odd[GT_TMVP_QUARTIC_LANES];

				for (int lane = 0; lane < GT_TMVP_QUARTIC_LANES; lane++)
				{
					const int even_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_even);
					const int odd_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_odd);

					a_even[lane] = a_complete[even_index];
					a_odd[lane] = a_complete[odd_index];
					b_even[lane] = b_complete[even_index];
					b_odd[lane] = b_complete[odd_index];
				}

				gt_tmvp_quartic_leaf_experimental_c(
					r_even, a_even, b_even,
					gt_rowbitrev_lambda[branch][even_j]);
				gt_tmvp_quartic_leaf_experimental_c(
					r_odd, a_odd, b_odd,
					gt_rowbitrev_lambda[branch][odd_j]);

				for (int lane = 0; lane < GT_TMVP_QUARTIC_LANES; lane++)
				{
					const int even_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_even);
					const int odd_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_odd);

					r[even_index] =
						(int16_t)(r_even[lane] + r_odd[lane]);
					r[odd_index] =
						(int16_t)(r_even[lane] - r_odd[lane]);
				}
			}
		}
	}

	return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK;
#endif
}

int gt_tmvp_quartic_tmvp_add_incomplete_complete_stage5_adapter_c(
	int16_t r[NTRUPLUS_N],
	const int16_t a_complete[NTRUPLUS_N],
	const int16_t b_complete[NTRUPLUS_N],
	const int16_t c_complete[NTRUPLUS_N])
{
	if (!gt_tmvp_check_4args(r, a_complete, b_complete, c_complete))
	{
		return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT;
	}

#if !defined(GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C)
	return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_DISABLED;
#else
	for (int branch = 0; branch < GT_TMVP_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_TMVP_ROWS; row++)
		{
			for (int pair = 0; pair < GT_TMVP_ROW_N / 2; pair++)
			{
				const int k_even = 2 * pair;
				const int k_odd = k_even + 1;
				const int even_j =
					gt_tmvp_quartic_tmvp_physical_j(row, k_even);
				const int odd_j =
					gt_tmvp_quartic_tmvp_physical_j(row, k_odd);
				int16_t a_even[GT_TMVP_QUARTIC_LANES];
				int16_t a_odd[GT_TMVP_QUARTIC_LANES];
				int16_t b_even[GT_TMVP_QUARTIC_LANES];
				int16_t b_odd[GT_TMVP_QUARTIC_LANES];
				int16_t c_even[GT_TMVP_QUARTIC_LANES];
				int16_t c_odd[GT_TMVP_QUARTIC_LANES];
				int16_t r_even[GT_TMVP_QUARTIC_LANES];
				int16_t r_odd[GT_TMVP_QUARTIC_LANES];

				for (int lane = 0; lane < GT_TMVP_QUARTIC_LANES; lane++)
				{
					const int even_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_even);
					const int odd_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_odd);

					a_even[lane] = a_complete[even_index];
					a_odd[lane] = a_complete[odd_index];
					b_even[lane] = b_complete[even_index];
					b_odd[lane] = b_complete[odd_index];
					c_even[lane] = c_complete[even_index];
					c_odd[lane] = c_complete[odd_index];
				}

				gt_tmvp_quartic_leaf_add_experimental_c(
					r_even, a_even, b_even, c_even,
					gt_rowbitrev_lambda[branch][even_j]);
				gt_tmvp_quartic_leaf_add_experimental_c(
					r_odd, a_odd, b_odd, c_odd,
					gt_rowbitrev_lambda[branch][odd_j]);

				for (int lane = 0; lane < GT_TMVP_QUARTIC_LANES; lane++)
				{
					const int even_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_even);
					const int odd_index =
						gt_tmvp_quartic_tmvp_rowpack_index(
							branch, row, lane, k_odd);

					r[even_index] =
						(int16_t)(r_even[lane] + r_odd[lane]);
					r[odd_index] =
						(int16_t)(r_even[lane] - r_odd[lane]);
				}
			}
		}
	}

	return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK;
#endif
}
