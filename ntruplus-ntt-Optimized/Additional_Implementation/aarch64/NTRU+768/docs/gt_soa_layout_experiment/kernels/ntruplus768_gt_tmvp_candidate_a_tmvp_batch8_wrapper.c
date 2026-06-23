#include "gt_tmvp_quartic_tmvp_experimental.h"

#include <stdint.h>

#include "ntt.h"

#if NTRUPLUS_N != 768
#error "Candidate A TMVP batch8 wrapper is specialized for NTRU+768"
#endif

#define GT_TMVP_BATCH8_BRANCHES 2
#define GT_TMVP_BATCH8_BRANCH_N (NTRUPLUS_N / GT_TMVP_BATCH8_BRANCHES)
#define GT_TMVP_BATCH8_ROWS 3
#define GT_TMVP_BATCH8_ROW_N 32
#define GT_TMVP_BATCH8_QUARTIC_LANES 4
#define GT_TMVP_BATCH8_BLOCKS 2
#define GT_TMVP_BATCH8_PAIRS_PER_BLOCK 8
#define GT_TMVP_BATCH8_CONSTS 40

#define GT_TMVP_BATCH8_QINV 12929
#define GT_TMVP_BATCH8_QINV_NEG (-12929)
#define GT_TMVP_BATCH8_RSQ 867

void ntruplus768_gt_tmvp_candidate_a_tmvp_batch8(
	int16_t *out, const int16_t *a, const int16_t *b,
	const int16_t *consts);

static int16_t gt_tmvp_batch8_consts[GT_TMVP_BATCH8_BRANCHES]
                                     [GT_TMVP_BATCH8_ROWS]
                                     [GT_TMVP_BATCH8_BLOCKS]
                                     [GT_TMVP_BATCH8_CONSTS]
	__attribute__((aligned(16)));
static int gt_tmvp_batch8_consts_ready;

static int gt_tmvp_batch8_rowpack_index(int branch, int row, int lane,
                                        int k32)
{
	return branch * GT_TMVP_BATCH8_BRANCH_N +
	       row * (GT_TMVP_BATCH8_QUARTIC_LANES * GT_TMVP_BATCH8_ROW_N) +
	       lane * GT_TMVP_BATCH8_ROW_N + k32;
}

static int gt_tmvp_batch8_physical_j(int row, int k32)
{
	return (GT_TMVP_BATCH8_ROW_N * row + GT_TMVP_BATCH8_ROWS * k32) %
	       (GT_TMVP_BATCH8_ROWS * GT_TMVP_BATCH8_ROW_N);
}

static int16_t gt_tmvp_batch8_montgomery_reduce(int32_t a)
{
	int16_t t = (int16_t)a * GT_TMVP_BATCH8_QINV;

	t = (a - (int32_t)t * NTRUPLUS_Q) >> 16;
	return t;
}

static int16_t gt_tmvp_batch8_stage5_pre_from_normal(int16_t mul)
{
	const int32_t scaled = (int32_t)mul * 32768;

	if (scaled >= 0)
	{
		return (int16_t)((scaled + NTRUPLUS_Q / 2) / NTRUPLUS_Q);
	}
	return (int16_t)(-((-scaled + NTRUPLUS_Q / 2) / NTRUPLUS_Q));
}

static void gt_tmvp_batch8_init_consts(void)
{
	if (gt_tmvp_batch8_consts_ready)
	{
		return;
	}

	for (int branch = 0; branch < GT_TMVP_BATCH8_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_TMVP_BATCH8_ROWS; row++)
		{
			for (int block = 0; block < GT_TMVP_BATCH8_BLOCKS; block++)
			{
				int16_t *c = gt_tmvp_batch8_consts[branch][row][block];

				c[0] = NTRUPLUS_Q;
				c[1] = 19412;
				c[2] = GT_TMVP_BATCH8_QINV_NEG;
				c[3] = GT_TMVP_BATCH8_RSQ;

				for (int i = 0; i < GT_TMVP_BATCH8_PAIRS_PER_BLOCK; i++)
				{
					const int k_even =
						block * 2 * GT_TMVP_BATCH8_PAIRS_PER_BLOCK +
						2 * i;
					const int k_odd = k_even + 1;
					const int16_t w_mont =
						gt_ntt32_ct_twiddle(5, (unsigned)k_even);
					const int16_t w_normal =
						gt_tmvp_batch8_montgomery_reduce(w_mont);

					c[8 + i] = w_normal;
					c[16 + i] =
						gt_tmvp_batch8_stage5_pre_from_normal(w_normal);
					c[24 + i] =
						gt_rowbitrev_lambda[branch]
						                   [gt_tmvp_batch8_physical_j(row,
						                                                   k_even)];
					c[32 + i] =
						gt_rowbitrev_lambda[branch]
						                   [gt_tmvp_batch8_physical_j(row,
						                                                   k_odd)];
				}
			}
		}
	}

	gt_tmvp_batch8_consts_ready = 1;
}

int gt_tmvp_quartic_tmvp_incomplete_candidate_a_asm(
	int16_t r[NTRUPLUS_N],
	const int16_t a_stage4[NTRUPLUS_N],
	const int16_t b_stage4[NTRUPLUS_N])
{
	if (r == 0 || a_stage4 == 0 || b_stage4 == 0)
	{
		return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT;
	}

	gt_tmvp_batch8_init_consts();
	for (int branch = 0; branch < GT_TMVP_BATCH8_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_TMVP_BATCH8_ROWS; row++)
		{
			for (int block = 0; block < GT_TMVP_BATCH8_BLOCKS; block++)
			{
				const int k32 =
					block * 2 * GT_TMVP_BATCH8_PAIRS_PER_BLOCK;
				const int offset =
					gt_tmvp_batch8_rowpack_index(branch, row, 0, k32);

				ntruplus768_gt_tmvp_candidate_a_tmvp_batch8(
					&r[offset], &a_stage4[offset], &b_stage4[offset],
					gt_tmvp_batch8_consts[branch][row][block]);
			}
		}
	}

	return GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK;
}

int gt_tmvp_quartic_tmvp_add_incomplete_candidate_a_asm(
	int16_t r[NTRUPLUS_N],
	const int16_t a_stage4[NTRUPLUS_N],
	const int16_t b_stage4[NTRUPLUS_N],
	const int16_t c_stage4[NTRUPLUS_N])
{
	return gt_tmvp_quartic_tmvp_add_incomplete_materialized_stage5_adapter_c(
		r, a_stage4, b_stage4, c_stage4);
}
