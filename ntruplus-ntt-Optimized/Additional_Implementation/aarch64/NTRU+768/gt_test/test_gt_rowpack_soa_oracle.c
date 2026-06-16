#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define NTRUPLUS_NTT_REFERENCE_TEST
#include "../ntt.c"

#define GT_BRANCHES 2
#define GT_BRANCH_N (NTRUPLUS_N / GT_BRANCHES)
#define GT_ROWS 3
#define GT_ROW_N 32
#define GT_QUARTIC_LANES 4
#define GT_VECTOR_LANES 8
#define RANDOM_TESTS 16

static int block_index(int branch, int physical_j, int lane)
{
	return branch * GT_BRANCH_N + GT_QUARTIC_LANES * physical_j + lane;
}

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

static void block_to_rowpack(int16_t rowpack[NTRUPLUS_N],
                             const int16_t block[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int physical_j = 0; physical_j < GT_ROWS * GT_ROW_N;
		     physical_j++)
		{
			const int row = row_from_physical_j(physical_j);
			const int k32 = k32_from_physical_j(physical_j);

			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				rowpack[rowpack_index(branch, row, lane, k32)] =
					block[block_index(branch, physical_j, lane)];
			}
		}
	}
}

static void rowpack_to_block(int16_t block[NTRUPLUS_N],
                             const int16_t rowpack[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_ROW_N; k32++)
			{
				const int physical_j = physical_j_from_row_k32(row, k32);

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					block[block_index(branch, physical_j, lane)] =
						rowpack[rowpack_index(branch, row, lane, k32)];
				}
			}
		}
	}
}

static void invntt_gt_rowpack_soa_exact(int16_t r[NTRUPLUS_N],
                                        const int16_t a[NTRUPLUS_N])
{
	int16_t branches[NTRUPLUS_N];

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		const int branch_start = branch * GT_BRANCH_N;
		const int16_t *untwist =
			branch == 0 ? untwist_branch0 : untwist_branch1;

		for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
		{
			int16_t rowbitrev_freq[GT_ROWS * GT_ROW_N];
			int16_t coeffs[GT_ROWS * GT_ROW_N];

			for (int row = 0; row < GT_ROWS; row++)
			{
				for (int k32 = 0; k32 < GT_ROW_N; k32++)
				{
					const int physical_j =
						physical_j_from_row_k32(row, k32);

					rowbitrev_freq[physical_j] =
						a[rowpack_index(branch, row, lane, k32)];
				}
			}

			invntt96_goodthomas_rowfirst(coeffs, rowbitrev_freq);

			for (int i = 0; i < GT_ROWS * GT_ROW_N; i++)
			{
				branches[branch_start + GT_QUARTIC_LANES * i + lane] =
					fqmul(coeffs[i], untwist[i]);
			}
		}
	}

	for (int i = 0; i < GT_BRANCH_N; i++)
	{
		const int16_t t1 = branches[i] + branches[i + GT_BRANCH_N];
		const int16_t t2 =
			fqmul(NTRUPLUS_ZMINUSZ5INV,
			      branches[i] - branches[i + GT_BRANCH_N]);

		r[i] = fqmul(NTRUPLUS_NINV, t1 - t2);
		r[i + GT_BRANCH_N] = fqmul(NTRUPLUS_2NINV, t2);
	}
}

static int modq(int64_t a)
{
	int r = (int)(a % NTRUPLUS_Q);

	if (r < 0)
	{
		r += NTRUPLUS_Q;
	}

	return r;
}

static int equal_modq(int16_t a, int16_t b)
{
	return modq((int)a - (int)b) == 0;
}

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static void fill_pattern(int16_t a[NTRUPLUS_N], unsigned pattern,
                         uint32_t seed)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		switch (pattern)
		{
		case 0:
			a[i] = 0;
			break;
		case 1:
			a[i] = 1;
			break;
		case 2:
			a[i] = (i & 1) ? -1 : 1;
			break;
		case 3:
			a[i] = (i & 1) ? -(NTRUPLUS_Q / 2) : (NTRUPLUS_Q / 2);
			break;
		default:
			a[i] =
				(int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) -
				          NTRUPLUS_Q);
			break;
		}
	}
}

static int compare_modq(const char *label, const int16_t got[NTRUPLUS_N],
                        const int16_t want[NTRUPLUS_N])
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!equal_modq(got[i], want[i]))
		{
			fprintf(stderr,
			        "%s mismatch at %d: got %d want %d\n",
			        label,
			        i,
			        got[i],
			        want[i]);
			return 0;
		}
	}

	return 1;
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

			if (row < 0 || row >= GT_ROWS || k32 < 0 || k32 >= GT_ROW_N ||
			    roundtrip != physical_j)
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

static int check_tagged_roundtrip(void)
{
	int16_t block[NTRUPLUS_N];
	int16_t rowpack[NTRUPLUS_N];
	int16_t roundtrip[NTRUPLUS_N];

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		block[i] = (int16_t)(i + 1);
	}

	block_to_rowpack(rowpack, block);
	rowpack_to_block(roundtrip, rowpack);

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (roundtrip[i] != block[i])
		{
			fprintf(stderr,
			        "tagged rowpack roundtrip mismatch at %d: got %d want %d\n",
			        i,
			        roundtrip[i],
			        block[i]);
			return 0;
		}
	}

	return 1;
}

static int check_row_vectors(void)
{
	int16_t block[NTRUPLUS_N];
	int16_t rowpack[NTRUPLUS_N];

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		block[i] = (int16_t)(1000 + i);
	}

	block_to_rowpack(rowpack, block);

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				for (int chunk = 0; chunk < GT_ROW_N / GT_VECTOR_LANES;
				     chunk++)
				{
					for (int vlane = 0; vlane < GT_VECTOR_LANES; vlane++)
					{
						const int k32 = chunk * GT_VECTOR_LANES + vlane;
						const int physical_j =
							physical_j_from_row_k32(row, k32);
						const int got =
							rowpack[rowpack_index(branch, row, lane, k32)];
						const int want =
							block[block_index(branch, physical_j, lane)];

						if (got != want)
						{
							fprintf(stderr,
							        "row vector mismatch b=%d row=%d lane=%d chunk=%d vlane=%d physical_j=%d got=%d want=%d\n",
							        branch,
							        row,
							        lane,
							        chunk,
							        vlane,
							        physical_j,
							        got,
							        want);
							return 0;
						}
					}
				}
			}
		}
	}

	return 1;
}

static int check_invntt_equivalence(void)
{
	int16_t natural[NTRUPLUS_N];
	int16_t gt_block[NTRUPLUS_N];
	int16_t rowpack[NTRUPLUS_N];
	int16_t got[NTRUPLUS_N];
	int16_t want[NTRUPLUS_N];

	for (unsigned pattern = 0; pattern < 5; pattern++)
	{
		fill_pattern(natural, pattern, 0x12345678u + pattern);
		ntt_gt_rowbitrevlayout(gt_block, natural);
		block_to_rowpack(rowpack, gt_block);
		invntt_gt_rowpack_soa_exact(got, rowpack);
		invntt_gt_rowbitrevlayout_exact(want, gt_block);

		if (!compare_modq("rowpack invntt equivalence", got, want) ||
		    !compare_modq("rowpack roundtrip", got, natural))
		{
			return 0;
		}
	}

	for (int t = 0; t < RANDOM_TESTS; t++)
	{
		fill_pattern(natural, 4, 0x9e3779b9u + (uint32_t)t);
		ntt_gt_rowbitrevlayout(gt_block, natural);
		block_to_rowpack(rowpack, gt_block);
		invntt_gt_rowpack_soa_exact(got, rowpack);
		invntt_gt_rowbitrevlayout_exact(want, gt_block);

		if (!compare_modq("rowpack random invntt equivalence", got, want) ||
		    !compare_modq("rowpack random roundtrip", got, natural))
		{
			return 0;
		}
	}

	return 1;
}

static void print_lambda_samples(void)
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			printf("lambda branch=%d row=%d chunk0:", branch, row);
			for (int vlane = 0; vlane < GT_VECTOR_LANES; vlane++)
			{
				const int physical_j = physical_j_from_row_k32(row, vlane);

				printf(" j%d=%d",
				       physical_j,
				       gt_rowbitrev_lambda[branch][physical_j]);
			}
			printf("\n");
		}
	}
}

int main(void)
{
	int ok = 1;

	ok &= check_mapping_inverse();
	ok &= check_tagged_roundtrip();
	ok &= check_row_vectors();
	ok &= check_invntt_equivalence();

	if (!ok)
	{
		return 1;
	}

	print_lambda_samples();
	printf("GT rowpack SoA oracle: ok\n");
	return 0;
}
