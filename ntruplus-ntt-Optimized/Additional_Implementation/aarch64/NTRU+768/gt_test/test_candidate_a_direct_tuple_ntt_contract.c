#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "ntt.h"
#include "params.h"
#include "poly.h"

#define GT_TMVP_BRANCHES 2
#define GT_TMVP_BRANCH_N (NTRUPLUS_N / GT_TMVP_BRANCHES)
#define GT_TMVP_BLOCKS_PER_BRANCH 96
#define GT_TMVP_ROWS 3
#define GT_TMVP_ROW_N 32
#define GT_TMVP_QUARTIC_LANES 4

void gt_candidate_a_direct_tuple_poly_ntt(poly *r, const poly *a);
void gt_tuple_poly_invntt(poly *r, const poly *a);

static int tuple_index(int branch, int row, int k32, int lane)
{
	return branch * GT_TMVP_BRANCH_N +
	       row * (GT_TMVP_ROW_N * GT_TMVP_QUARTIC_LANES) +
	       GT_TMVP_QUARTIC_LANES * k32 + lane;
}

static int tuple_physical_j(int row, int k32)
{
	return (GT_TMVP_ROW_N * row + GT_TMVP_ROWS * k32) %
	       GT_TMVP_BLOCKS_PER_BRANCH;
}

static int block_major_index(int branch, int physical_j, int lane)
{
	return branch * GT_TMVP_BRANCH_N +
	       GT_TMVP_QUARTIC_LANES * physical_j + lane;
}

static void block_major_to_tuple(int16_t tuple[NTRUPLUS_N],
                                 const int16_t block_major[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_TMVP_BRANCHES; branch++) {
		for (int row = 0; row < GT_TMVP_ROWS; row++) {
			for (int k32 = 0; k32 < GT_TMVP_ROW_N; k32++) {
				const int physical_j = tuple_physical_j(row, k32);
				for (int lane = 0; lane < GT_TMVP_QUARTIC_LANES; lane++) {
					const int tuple_idx =
						tuple_index(branch, row, k32, lane);
					const int block_idx =
						block_major_index(branch, physical_j, lane);
					tuple[tuple_idx] = block_major[block_idx];
				}
			}
		}
	}
}

static int16_t canon(int16_t x)
{
	int32_t y = x;
	y %= NTRUPLUS_Q;
	if (y < 0) {
		y += NTRUPLUS_Q;
	}
	return (int16_t)y;
}

static void fill_input(poly *a, int seed)
{
	for (int i = 0; i < NTRUPLUS_N; i++) {
		int32_t v = (int32_t)(17 * i + 97 * seed + (i % 11) * (seed + 3));
		a->coeffs[i] = (int16_t)(v % NTRUPLUS_Q);
	}
}

int main(void)
{
	int total_mismatches = 0;

	for (int seed = 0; seed < 8; seed++) {
		poly a;
		poly got;
		poly inv_got;
		int16_t block_major[NTRUPLUS_N];
		int16_t expected[NTRUPLUS_N];
		int16_t inv_expected[NTRUPLUS_N];
		int seed_mismatches = 0;
		int seed_inv_mismatches = 0;

		memset(&got, 0, sizeof(got));
		memset(&inv_got, 0, sizeof(inv_got));
		fill_input(&a, seed);

		ntt(block_major, a.coeffs);
		block_major_to_tuple(expected, block_major);
		gt_candidate_a_direct_tuple_poly_ntt(&got, &a);
		invntt(inv_expected, block_major);
		gt_tuple_poly_invntt(&inv_got, &got);

		for (int i = 0; i < NTRUPLUS_N; i++) {
			if (canon(got.coeffs[i] - expected[i]) != 0) {
				const int branch = i / GT_TMVP_BRANCH_N;
				const int rem0 = i % GT_TMVP_BRANCH_N;
				const int row = rem0 / (GT_TMVP_ROW_N * GT_TMVP_QUARTIC_LANES);
				const int rem1 = rem0 % (GT_TMVP_ROW_N * GT_TMVP_QUARTIC_LANES);
				const int k32 = rem1 / GT_TMVP_QUARTIC_LANES;
				const int lane = rem1 % GT_TMVP_QUARTIC_LANES;

				if (seed_mismatches < 32) {
					printf("seed=%d idx=%d branch=%d row=%d k32=%d lane=%d got=%d expected=%d diffmod=%d\n",
					       seed, i, branch, row, k32, lane,
					       got.coeffs[i], expected[i],
					       canon(got.coeffs[i] - expected[i]));
				}
				seed_mismatches++;
			}
		}

		for (int i = 0; i < NTRUPLUS_N; i++) {
			if (canon(inv_got.coeffs[i] - inv_expected[i]) != 0) {
				if (seed_inv_mismatches < 32) {
					printf("inv seed=%d idx=%d got=%d expected=%d diffmod=%d\n",
					       seed, i, inv_got.coeffs[i],
					       inv_expected[i],
					       canon(inv_got.coeffs[i] -
					             inv_expected[i]));
				}
				seed_inv_mismatches++;
			}
		}

		printf("seed=%d ntt_mismatches=%d invntt_mismatches=%d\n",
		       seed, seed_mismatches, seed_inv_mismatches);
		total_mismatches += seed_mismatches;
		total_mismatches += seed_inv_mismatches;
	}

	printf("total_mismatches=%d\n", total_mismatches);
	return total_mismatches == 0 ? 0 : 1;
}
