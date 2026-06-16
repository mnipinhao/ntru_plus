#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"

#define GT_BRANCHES 2
#define GT_BRANCH_N (NTRUPLUS_N / GT_BRANCHES)
#define GT_ROWS 3
#define GT_ROW_N 32
#define GT_QUARTIC_LANES 4
#define GT_VECTOR_LANES 8
#define GT_K32_BLOCKS (GT_ROW_N / GT_VECTOR_LANES)

static int physical_j_from_row_k32(int row, int k32)
{
	return (GT_ROW_N * row + GT_ROWS * k32) % (GT_ROWS * GT_ROW_N);
}

static int row_from_physical_j(int physical_j)
{
	return (2 * (physical_j % GT_ROWS)) % GT_ROWS;
}

static int k32_from_physical_j(int physical_j)
{
	const int row = row_from_physical_j(physical_j);

	for (int k32 = 0; k32 < GT_ROW_N; k32++)
	{
		if (physical_j_from_row_k32(row, k32) == physical_j)
		{
			return k32;
		}
	}

	return -1;
}

static int rowpack_index(int branch, int row, int lane, int k32)
{
	return branch * GT_BRANCH_N +
	       row * (GT_QUARTIC_LANES * GT_ROW_N) +
	       lane * GT_ROW_N + k32;
}

static int16_t tag_for(int row, int k32, int vector_lane, int pattern)
{
	const int branch = vector_lane / GT_QUARTIC_LANES;
	const int lane = vector_lane % GT_QUARTIC_LANES;
	const int physical_j = physical_j_from_row_k32(row, k32);

	switch (pattern)
	{
	case 0:
		return (int16_t)(1000 + row * 256 + k32 * 8 + vector_lane);
	case 1:
		return (int16_t)(2000 + branch * 512 + lane * 96 + physical_j);
	default:
		return (int16_t)(3000 + row * 257 + k32 * 17 +
		                 branch * 31 + lane * 7);
	}
}

static void fill_current_row_vectors(
	int16_t row_vectors[GT_ROWS][GT_ROW_N][GT_VECTOR_LANES],
	int pattern)
{
	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			for (int lane = 0; lane < GT_VECTOR_LANES; lane++)
			{
				row_vectors[row][k32][lane] =
					tag_for(row, k32, lane, pattern);
			}
		}
	}
}

static void scatter_current_row_vectors_to_rowpack(
	int16_t rowpack[NTRUPLUS_N],
	int16_t row_vectors[GT_ROWS][GT_ROW_N][GT_VECTOR_LANES])
{
	memset(rowpack, 0, NTRUPLUS_N * sizeof(rowpack[0]));

	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				rowpack[rowpack_index(0, row, lane, k32)] =
					row_vectors[row][k32][lane];
				rowpack[rowpack_index(1, row, lane, k32)] =
					row_vectors[row][k32][lane + GT_QUARTIC_LANES];
			}
		}
	}
}

static void build_v3_plane_liveout(
	int16_t liveout[GT_ROWS][GT_K32_BLOCKS][GT_VECTOR_LANES][GT_VECTOR_LANES],
	int16_t row_vectors[GT_ROWS][GT_ROW_N][GT_VECTOR_LANES])
{
	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int block = 0; block < GT_K32_BLOCKS; block++)
		{
			for (int plane = 0; plane < GT_VECTOR_LANES; plane++)
			{
				for (int vlane = 0; vlane < GT_VECTOR_LANES; vlane++)
				{
					const int k32 = block * GT_VECTOR_LANES + vlane;

					liveout[row][block][plane][vlane] =
						row_vectors[row][k32][plane];
				}
			}
		}
	}
}

static void store_v3_plane_liveout_to_rowpack(
	int16_t rowpack[NTRUPLUS_N],
	int16_t liveout[GT_ROWS][GT_K32_BLOCKS][GT_VECTOR_LANES][GT_VECTOR_LANES])
{
	memset(rowpack, 0, NTRUPLUS_N * sizeof(rowpack[0]));

	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int block = 0; block < GT_K32_BLOCKS; block++)
		{
			for (int plane = 0; plane < GT_VECTOR_LANES; plane++)
			{
				const int branch = plane / GT_QUARTIC_LANES;
				const int lane = plane % GT_QUARTIC_LANES;

				for (int vlane = 0; vlane < GT_VECTOR_LANES; vlane++)
				{
					const int k32 = block * GT_VECTOR_LANES + vlane;

					rowpack[rowpack_index(branch, row, lane, k32)] =
						liveout[row][block][plane][vlane];
				}
			}
		}
	}
}

static int check_mapping_inverse(void)
{
	int seen[NTRUPLUS_N];

	memset(seen, 0, sizeof(seen));

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int physical_j = 0; physical_j < GT_ROWS * GT_ROW_N;
		     physical_j++)
		{
			const int row = row_from_physical_j(physical_j);
			const int k32 = k32_from_physical_j(physical_j);
			const int roundtrip = physical_j_from_row_k32(row, k32);

			if (row < 0 || row >= GT_ROWS || k32 < 0 ||
			    k32 >= GT_ROW_N || roundtrip != physical_j)
			{
				fprintf(stderr,
				        "rowpack map mismatch branch=%d physical_j=%d row=%d k32=%d roundtrip=%d\n",
				        branch,
				        physical_j,
				        row,
				        k32,
				        roundtrip);
				return 0;
			}

			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				const int idx = rowpack_index(branch, row, lane, k32);

				if (idx < 0 || idx >= NTRUPLUS_N || seen[idx])
				{
					fprintf(stderr,
					        "rowpack index collision branch=%d physical_j=%d lane=%d idx=%d\n",
					        branch,
					        physical_j,
					        lane,
					        idx);
					return 0;
				}
				seen[idx] = 1;
			}
		}
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!seen[i])
		{
			fprintf(stderr, "rowpack index %d is unreachable\n", i);
			return 0;
		}
	}

	return 1;
}

static int check_v3_liveout_contract(int pattern)
{
	int16_t row_vectors[GT_ROWS][GT_ROW_N][GT_VECTOR_LANES];
	int16_t liveout[GT_ROWS][GT_K32_BLOCKS][GT_VECTOR_LANES][GT_VECTOR_LANES];
	int16_t want[NTRUPLUS_N];
	int16_t got[NTRUPLUS_N];

	fill_current_row_vectors(row_vectors, pattern);
	scatter_current_row_vectors_to_rowpack(want, row_vectors);
	build_v3_plane_liveout(liveout, row_vectors);
	store_v3_plane_liveout_to_rowpack(got, liveout);

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (got[i] != want[i])
		{
			fprintf(stderr,
			        "v3 register-order contract mismatch pattern=%d index=%d got=%d want=%d\n",
			        pattern,
			        i,
			        got[i],
			        want[i]);
			return 0;
		}
	}

	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int block = 0; block < GT_K32_BLOCKS; block++)
		{
			for (int plane = 0; plane < GT_VECTOR_LANES; plane++)
			{
				for (int vlane = 0; vlane < GT_VECTOR_LANES; vlane++)
				{
					const int k32 = block * GT_VECTOR_LANES + vlane;
					const int branch = plane / GT_QUARTIC_LANES;
					const int lane = plane % GT_QUARTIC_LANES;
					const int16_t want_tag =
						row_vectors[row][k32][plane];
					const int16_t got_tag =
						liveout[row][block][plane][vlane];
					const int out_index =
						rowpack_index(branch, row, lane, k32);

					if (got_tag != want_tag || got[out_index] != want_tag)
					{
						fprintf(stderr,
						        "v3 plane vector mismatch pattern=%d row=%d block=%d plane=%d vlane=%d k32=%d\n",
						        pattern,
						        row,
						        block,
						        plane,
						        vlane,
						        k32);
						return 0;
					}
				}
			}
		}
	}

	return 1;
}

int main(void)
{
	if (!check_mapping_inverse())
	{
		return 1;
	}

	for (int pattern = 0; pattern < 3; pattern++)
	{
		if (!check_v3_liveout_contract(pattern))
		{
			return 1;
		}
	}

	printf("Forward rowpack v3 register-order contract: ok\n");
	printf("liveout vectors per row=%d total=%d lanes/vector=%d\n",
	       GT_K32_BLOCKS * GT_VECTOR_LANES,
	       GT_ROWS * GT_K32_BLOCKS * GT_VECTOR_LANES,
	       GT_VECTOR_LANES);
	printf("required liveout: plane[row][k32_block][branch_lane].h[vlane] -> rowpack_index(branch,row,lane,k32_block*8+vlane)\n");
	return 0;
}
