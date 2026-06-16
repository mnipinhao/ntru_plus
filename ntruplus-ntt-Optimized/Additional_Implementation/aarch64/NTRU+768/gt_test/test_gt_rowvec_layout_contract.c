#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define NTRUPLUS_NTT_REFERENCE_TEST
#include "../ntt.c"

#define GT_BRANCHES 2
#define GT_BRANCH_N (NTRUPLUS_N / GT_BRANCHES)
#define GT_BLOCKS_PER_BRANCH 96
#define GT_ROWS 3
#define GT_ROW_N 32
#define GT_QUARTIC_LANES 4
#define GT_VECTOR_LANES 8

static int block_index(int branch, int physical_j, int lane)
{
	return branch * GT_BRANCH_N + GT_QUARTIC_LANES * physical_j + lane;
}

static int physical_j_from_row_k32(int row, int k32)
{
	return (GT_ROW_N * row + GT_ROWS * k32) % GT_BLOCKS_PER_BRANCH;
}

static int rowvec_index(int row, int k32, int blane)
{
	return row * (GT_ROW_N * GT_VECTOR_LANES) +
	       k32 * GT_VECTOR_LANES + blane;
}

static void block_to_rowvec(int16_t rowvec[NTRUPLUS_N],
                            const int16_t block[NTRUPLUS_N])
{
	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			const int physical_j = physical_j_from_row_k32(row, k32);

			for (int branch = 0; branch < GT_BRANCHES; branch++)
			{
				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					const int blane = branch * GT_QUARTIC_LANES + lane;

					rowvec[rowvec_index(row, k32, blane)] =
						block[block_index(branch, physical_j, lane)];
				}
			}
		}
	}
}

static void rowvec_to_block(int16_t block[NTRUPLUS_N],
                            const int16_t rowvec[NTRUPLUS_N])
{
	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			const int physical_j = physical_j_from_row_k32(row, k32);

			for (int branch = 0; branch < GT_BRANCHES; branch++)
			{
				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					const int blane = branch * GT_QUARTIC_LANES + lane;

					block[block_index(branch, physical_j, lane)] =
						rowvec[rowvec_index(row, k32, blane)];
				}
			}
		}
	}
}

static void scatter_row_vectors_to_rowvec(
	int16_t rowvec[NTRUPLUS_N],
	int16_t row_vectors[GT_ROWS][GT_ROW_N][GT_VECTOR_LANES])
{
	memset(rowvec, 0, NTRUPLUS_N * sizeof(rowvec[0]));

	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			for (int blane = 0; blane < GT_VECTOR_LANES; blane++)
			{
				rowvec[rowvec_index(row, k32, blane)] =
					row_vectors[row][k32][blane];
			}
		}
	}
}

static void scatter_row_vectors_to_block(
	int16_t block[NTRUPLUS_N],
	int16_t row_vectors[GT_ROWS][GT_ROW_N][GT_VECTOR_LANES])
{
	memset(block, 0, NTRUPLUS_N * sizeof(block[0]));

	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			const int physical_j = physical_j_from_row_k32(row, k32);

			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				block[block_index(0, physical_j, lane)] =
					row_vectors[row][k32][lane];
				block[block_index(1, physical_j, lane)] =
					row_vectors[row][k32][lane + GT_QUARTIC_LANES];
			}
		}
	}
}

static int check_mapping_bijection(void)
{
	int seen_rowvec[NTRUPLUS_N];
	int seen_block[NTRUPLUS_N];

	memset(seen_rowvec, 0, sizeof(seen_rowvec));
	memset(seen_block, 0, sizeof(seen_block));

	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			const int physical_j = physical_j_from_row_k32(row, k32);

			if (physical_j < 0 || physical_j >= GT_BLOCKS_PER_BRANCH)
			{
				fprintf(stderr,
				        "rowvec physical_j out of range row=%d k32=%d physical_j=%d\n",
				        row,
				        k32,
				        physical_j);
				return 0;
			}

			for (int branch = 0; branch < GT_BRANCHES; branch++)
			{
				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					const int blane = branch * GT_QUARTIC_LANES + lane;
					const int ridx = rowvec_index(row, k32, blane);
					const int bidx = block_index(branch, physical_j, lane);

					if (ridx < 0 || ridx >= NTRUPLUS_N ||
					    seen_rowvec[ridx])
					{
						fprintf(stderr,
						        "rowvec index collision row=%d k32=%d blane=%d idx=%d\n",
						        row,
						        k32,
						        blane,
						        ridx);
						return 0;
					}
					if (bidx < 0 || bidx >= NTRUPLUS_N || seen_block[bidx])
					{
						fprintf(stderr,
						        "block index collision branch=%d physical_j=%d lane=%d idx=%d\n",
						        branch,
						        physical_j,
						        lane,
						        bidx);
						return 0;
					}

					seen_rowvec[ridx] = 1;
					seen_block[bidx] = 1;
				}
			}
		}
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!seen_rowvec[i] || !seen_block[i])
		{
			fprintf(stderr,
			        "rowvec bijection gap at %d: rowvec=%d block=%d\n",
			        i,
			        seen_rowvec[i],
			        seen_block[i]);
			return 0;
		}
	}

	return 1;
}

static int check_block_roundtrip(void)
{
	int16_t block[NTRUPLUS_N];
	int16_t rowvec[NTRUPLUS_N];
	int16_t roundtrip[NTRUPLUS_N];

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		block[i] = (int16_t)(i - 384);
	}

	block_to_rowvec(rowvec, block);
	rowvec_to_block(roundtrip, rowvec);

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (roundtrip[i] != block[i])
		{
			fprintf(stderr,
			        "rowvec block roundtrip mismatch at %d: got=%d want=%d\n",
			        i,
			        roundtrip[i],
			        block[i]);
			return 0;
		}
	}

	return 1;
}

static int check_row_vector_boundary_model(void)
{
	int16_t row_vectors[GT_ROWS][GT_ROW_N][GT_VECTOR_LANES];
	int16_t block[NTRUPLUS_N];
	int16_t direct[NTRUPLUS_N];
	int16_t from_block[NTRUPLUS_N];

	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			for (int blane = 0; blane < GT_VECTOR_LANES; blane++)
			{
				row_vectors[row][k32][blane] =
					(int16_t)(1000 + row * 256 + k32 * 8 + blane);
			}
		}
	}

	scatter_row_vectors_to_block(block, row_vectors);
	scatter_row_vectors_to_rowvec(direct, row_vectors);
	block_to_rowvec(from_block, block);

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (from_block[i] != direct[i])
		{
			fprintf(stderr,
			        "row-vector rowvec scatter mismatch at %d: got=%d want=%d\n",
			        i,
			        from_block[i],
			        direct[i]);
			return 0;
		}
	}

	return 1;
}

static int check_lambda_pattern(void)
{
	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			const int physical_j = physical_j_from_row_k32(row, k32);

			for (int blane = 0; blane < GT_VECTOR_LANES; blane++)
			{
				const int branch = blane / GT_QUARTIC_LANES;
				const int16_t rowvec_lane_lambda =
					gt_rowbitrev_lambda[branch][physical_j];
				const int16_t want = blane < GT_QUARTIC_LANES
				                         ? gt_rowbitrev_lambda[0][physical_j]
				                         : gt_rowbitrev_lambda[1][physical_j];

				if (rowvec_lane_lambda != want)
				{
					fprintf(stderr,
					        "rowvec lambda mismatch row=%d k32=%d blane=%d got=%d want=%d\n",
					        row,
					        k32,
					        blane,
					        rowvec_lane_lambda,
					        want);
					return 0;
				}
			}
		}
	}

	return 1;
}

static void print_mapping_samples(void)
{
	for (int row = 0; row < GT_ROWS; row++)
	{
		printf("rowvec row=%d k32[0..7] physical_j:", row);
		for (int k32 = 0; k32 < GT_VECTOR_LANES; k32++)
		{
			printf(" %d", physical_j_from_row_k32(row, k32));
		}
		printf("\n");
	}

	for (int row = 0; row < GT_ROWS; row++)
	{
		const int physical_j = physical_j_from_row_k32(row, 0);

		printf("rowvec lambda row=%d k32=0 lanes:", row);
		for (int blane = 0; blane < GT_VECTOR_LANES; blane++)
		{
			const int branch = blane / GT_QUARTIC_LANES;

			printf(" %d", gt_rowbitrev_lambda[branch][physical_j]);
		}
		printf("\n");
	}
}

int main(void)
{
	if (!check_mapping_bijection() ||
	    !check_block_roundtrip() ||
	    !check_row_vector_boundary_model() ||
	    !check_lambda_pattern())
	{
		return 1;
	}

	print_mapping_samples();
	printf("GT rowvec layout contract: ok\n");
	return 0;
}
