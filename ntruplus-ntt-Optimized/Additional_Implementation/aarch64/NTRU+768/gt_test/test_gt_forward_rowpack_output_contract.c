#include <stdint.h>
#include <stdio.h>
#include <string.h>

#if defined(TEST_GT_FORWARD_ROWPACK_V2_ASM) || \
	defined(TEST_GT_FORWARD_ROWPACK_V3_ASM)
#include "poly.h"
#endif

#define NTRUPLUS_NTT_REFERENCE_TEST
#include "../ntt.c"

#define GT_BRANCHES 2
#define GT_BRANCH_N (NTRUPLUS_N / GT_BRANCHES)
#define GT_ROWS 3
#define GT_ROW_N 32
#define GT_QUARTIC_LANES 4
#define GT_VECTOR_LANES 8
#ifndef RANDOM_TESTS
#define RANDOM_TESTS 16
#endif

static int observed_min = INT16_MAX;
static int observed_max = INT16_MIN;
static unsigned observed_samples;

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

static void ntt_gt_rowpack_soa_layout(int16_t r[NTRUPLUS_N],
                                      const int16_t a[NTRUPLUS_N])
{
	int16_t work[NTRUPLUS_N];

	for (int i = 0; i < NTRUPLUS_N / 2; i++)
	{
		const int16_t t1 =
			fqmul(NTRUPLUS_ZETA_TOP_SPLIT, a[i + NTRUPLUS_N / 2]);

		work[i + NTRUPLUS_N / 2] = a[i] + a[i + NTRUPLUS_N / 2] - t1;
		work[i] = a[i] + t1;
	}

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		const int branch_start = branch * GT_BRANCH_N;
		const int16_t *twist =
			branch == 0 ? twist_branch0 : twist_branch1;

		for (int i = 0; i < GT_ROWS * GT_ROW_N; i++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				work[branch_start + GT_QUARTIC_LANES * i + lane] =
					fqmul(work[branch_start + GT_QUARTIC_LANES * i + lane],
					      twist[i]);
			}
		}

		for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
		{
			int16_t in[GT_ROWS * GT_ROW_N];
			int16_t out[GT_ROWS * GT_ROW_N];

			for (int i = 0; i < GT_ROWS * GT_ROW_N; i++)
			{
				in[i] =
					work[branch_start + GT_QUARTIC_LANES * i + lane];
			}

			ntt96_goodthomas(out, in);

			for (int physical_j = 0; physical_j < GT_ROWS * GT_ROW_N;
			     physical_j++)
			{
				const int row = row_from_physical_j(physical_j);
				const int k32 = k32_from_physical_j(physical_j);

				r[rowpack_index(branch, row, lane, k32)] = out[physical_j];
			}
		}
	}
}

static void ntt_gt_rowpack_soa_active(int16_t r[NTRUPLUS_N],
                                      const int16_t a[NTRUPLUS_N])
{
#if defined(TEST_GT_FORWARD_ROWPACK_V2_ASM) || \
	defined(TEST_GT_FORWARD_ROWPACK_V3_ASM)
	poly in;
	poly out;

	memcpy(in.coeffs, a, sizeof(in.coeffs));
	poly_ntt(&out, &in);
	memcpy(r, out.coeffs, sizeof(out.coeffs));
#else
	ntt_gt_rowpack_soa_layout(r, a);
#endif
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
			        "%s mismatch at %d: got=%d want=%d\n",
			        label,
			        i,
			        got[i],
			        want[i]);
			return 0;
		}
	}

	return 1;
}

static void record_output_range(const int16_t a[NTRUPLUS_N])
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (a[i] < observed_min)
		{
			observed_min = a[i];
		}
		if (a[i] > observed_max)
		{
			observed_max = a[i];
		}
	}
	observed_samples++;
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

static void scatter_current_row_vectors_to_block(
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

static void scatter_row_vectors_to_rowpack(
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

static void scatter_v2_transpose_blocks_to_rowpack(
	int16_t rowpack[NTRUPLUS_N],
	int16_t row_vectors[GT_ROWS][GT_ROW_N][GT_VECTOR_LANES])
{
	memset(rowpack, 0, NTRUPLUS_N * sizeof(rowpack[0]));

	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int block = 0; block < GT_ROW_N / GT_VECTOR_LANES; block++)
		{
			for (int lane = 0; lane < GT_VECTOR_LANES; lane++)
			{
				const int branch = lane / GT_QUARTIC_LANES;
				const int quartic_lane = lane % GT_QUARTIC_LANES;

				for (int vlane = 0; vlane < GT_VECTOR_LANES; vlane++)
				{
					const int k32 = block * GT_VECTOR_LANES + vlane;

					rowpack[rowpack_index(branch, row, quartic_lane, k32)] =
						row_vectors[row][k32][lane];
				}
			}
		}
	}
}

static int check_scatter_boundary_model(void)
{
	int16_t row_vectors[GT_ROWS][GT_ROW_N][GT_VECTOR_LANES];
	int16_t current_block[NTRUPLUS_N];
	int16_t converted_rowpack[NTRUPLUS_N];
	int16_t direct_rowpack[NTRUPLUS_N];
	int16_t v2_rowpack[NTRUPLUS_N];

	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			for (int lane = 0; lane < GT_VECTOR_LANES; lane++)
			{
				row_vectors[row][k32][lane] =
					(int16_t)(1000 + row * 256 + k32 * 8 + lane);
			}
		}
	}

	scatter_current_row_vectors_to_block(current_block, row_vectors);
	block_to_rowpack(converted_rowpack, current_block);
	scatter_row_vectors_to_rowpack(direct_rowpack, row_vectors);
	scatter_v2_transpose_blocks_to_rowpack(v2_rowpack, row_vectors);

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (converted_rowpack[i] != direct_rowpack[i])
		{
			fprintf(stderr,
			        "row-vector scatter contract mismatch at %d: got=%d want=%d\n",
			        i,
			        converted_rowpack[i],
			        direct_rowpack[i]);
			return 0;
		}

		if (converted_rowpack[i] != v2_rowpack[i])
		{
			fprintf(stderr,
			        "v2 transpose scatter contract mismatch at %d: got=%d want=%d\n",
			        i,
			        v2_rowpack[i],
			        converted_rowpack[i]);
			return 0;
		}
	}

	return 1;
}

static int check_forward_rowpack_direct(unsigned pattern, uint32_t seed)
{
	int16_t natural[NTRUPLUS_N];
	int16_t gt_block[NTRUPLUS_N];
	int16_t want[NTRUPLUS_N];
	int16_t got[NTRUPLUS_N];

	fill_pattern(natural, pattern, seed);
	ntt_gt_rowbitrevlayout(gt_block, natural);
	block_to_rowpack(want, gt_block);
	ntt_gt_rowpack_soa_active(got, natural);
	record_output_range(got);

#if defined(TEST_GT_FORWARD_ROWPACK_V2_ASM) || \
	defined(TEST_GT_FORWARD_ROWPACK_V3_ASM)
	return compare_modq("ASM Forward NTT rowpack output", got, want);
#else
	return compare_modq("direct Forward NTT rowpack output", got, want);
#endif
}

static void print_mapping_samples(void)
{
	for (int row = 0; row < GT_ROWS; row++)
	{
		printf("row=%d k32[0..7] physical_j:", row);
		for (int k32 = 0; k32 < GT_VECTOR_LANES; k32++)
		{
			printf(" %d", physical_j_from_row_k32(row, k32));
		}
		printf("\n");
	}
}

int main(void)
{
	if (!check_mapping_inverse() || !check_scatter_boundary_model())
	{
		return 1;
	}

	for (unsigned pattern = 0; pattern < 5; pattern++)
	{
		if (!check_forward_rowpack_direct(pattern, 0x243f6a88u + pattern))
		{
			return 1;
		}
	}

	for (int t = 0; t < RANDOM_TESTS; t++)
	{
		if (!check_forward_rowpack_direct(4, 0x85a308d3u + (uint32_t)t))
		{
			return 1;
		}
	}

	print_mapping_samples();
	printf("GT Forward NTT rowpack observed output range: samples=%u min=%d max=%d max_abs=%d\n",
	       observed_samples,
	       observed_min,
	       observed_max,
	       observed_min < -observed_max ? -observed_min : observed_max);
	printf("GT Forward NTT rowpack output contract: ok\n");
	return 0;
}
