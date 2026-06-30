#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "ntt.h"
#include "params.h"
#include "poly.h"

#define GT_BRANCHES 2
#define GT_BRANCH_N (NTRUPLUS_N / GT_BRANCHES)
#define GT_BLOCKS_PER_BRANCH 96
#define GT_ROWS 3
#define GT_ROW_N 32
#define GT_LANES 4

#ifdef TEST_DIRECT_TUPLE
void gt_candidate_a_direct_tuple_poly_ntt(poly *r, const poly *a);
#else
void gt_block_major_poly_ntt(poly *r, const poly *a);
#endif

static int tuple_index(int branch, int row, int k32, int lane)
{
	return branch * GT_BRANCH_N +
	       row * (GT_ROW_N * GT_LANES) +
	       GT_LANES * k32 + lane;
}

static int tuple_physical_j(int row, int k32)
{
	return (GT_ROW_N * row + GT_ROWS * k32) % GT_BLOCKS_PER_BRANCH;
}

static int block_major_index(int branch, int physical_j, int lane)
{
	return branch * GT_BRANCH_N + GT_LANES * physical_j + lane;
}

static void block_major_to_tuple(int16_t tuple[NTRUPLUS_N],
                                 const int16_t block_major[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++) {
		for (int row = 0; row < GT_ROWS; row++) {
			for (int k32 = 0; k32 < GT_ROW_N; k32++) {
				const int physical_j = tuple_physical_j(row, k32);
				for (int lane = 0; lane < GT_LANES; lane++) {
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

static int16_t cbd_pattern(int i, int seed)
{
	return (int16_t)(((37 * i + 13 * seed + (i >> 3)) % 3) - 1);
}

static void fill_small_input(poly *a, int mode, int seed)
{
	for (int i = 0; i < NTRUPLUS_N; i++) {
		const int16_t c = cbd_pattern(i, seed);
		switch (mode) {
		case 0:
			a->coeffs[i] = c;
			break;
		case 1:
			a->coeffs[i] = (int16_t)(3 * c);
			break;
		default:
			a->coeffs[i] = (int16_t)(3 * c + (i == 0 ? 1 : 0));
			break;
		}
	}
}

static const char *mode_name(int mode)
{
	switch (mode) {
	case 0:
		return "cbd1_or_sotp_or_crepmod3";
	case 1:
		return "triple_cbd1";
	default:
		return "triple_cbd1_f_plus_c0";
	}
}

int main(void)
{
	int total_mismatches = 0;

	for (int mode = 0; mode < 3; mode++) {
		for (int seed = 0; seed < 16; seed++) {
			poly a;
			poly got;
			int16_t block_major[NTRUPLUS_N];
			int16_t expected[NTRUPLUS_N];
			int mismatches = 0;

			memset(&got, 0, sizeof(got));
			fill_small_input(&a, mode, seed);
			ntt(block_major, a.coeffs);

#ifdef TEST_DIRECT_TUPLE
			block_major_to_tuple(expected, block_major);
			gt_candidate_a_direct_tuple_poly_ntt(&got, &a);
#else
			memcpy(expected, block_major, sizeof(expected));
			gt_block_major_poly_ntt(&got, &a);
#endif

			for (int i = 0; i < NTRUPLUS_N; i++) {
				if (canon(got.coeffs[i] - expected[i]) != 0) {
					if (mismatches < 32) {
						printf("mode=%s seed=%d idx=%d got=%d expected=%d diffmod=%d\n",
						       mode_name(mode), seed, i,
						       got.coeffs[i], expected[i],
						       canon(got.coeffs[i] - expected[i]));
					}
					mismatches++;
				}
			}

			printf("mode=%s seed=%d mismatches=%d\n",
			       mode_name(mode), seed, mismatches);
			total_mismatches += mismatches;
		}
	}

	printf("total_mismatches=%d\n", total_mismatches);
	return total_mismatches == 0 ? 0 : 1;
}
