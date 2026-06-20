#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "gt_tmvp_quartic_tmvp_experimental.h"
#include "params.h"

#define NTRUPLUS_NTT_REFERENCE_TEST
#include "../ntt.c"

#define GT_BRANCHES 2
#define GT_BRANCH_N (NTRUPLUS_N / GT_BRANCHES)
#define GT_ROWS 3
#define GT_ROW_N 32
#define GT_QUARTIC_LANES 4
#define VECTOR_CASES 16
#define STAGE4_BOUND 1728

#ifdef CANDIDATE_A_STAGE2_TO5_ASM
#define REPORT_PATH                                                           \
	"docs/gt_tmvp_decomposition_experiment/"                              \
	"decomposition-quartic-tmvp-incomplete-candidate-a-stage2-to5-asm-report.yml"
#else
#define REPORT_PATH                                                           \
	"docs/gt_tmvp_decomposition_experiment/"                              \
	"decomposition-quartic-tmvp-incomplete-candidate-a-stage2-postmerge-c-report.yml"
#endif

#ifdef CANDIDATE_A_STAGE2_TO5_ASM
void ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end(
	int16_t *row_plane, const int16_t *consts);
extern const int16_t
	ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end_consts[];
#endif

struct mismatch_counts
{
	int adapter;
	int rowkernel;
	int postmerge;
	int asm_rowkernel;
	int asm_postmerge;
};

struct range_stats
{
	int adapter_max_abs;
	int full_rows_max_abs;
	int candidate_rows_max_abs;
	int postmerge_max_abs;
	int asm_rows_max_abs;
	int asm_postmerge_max_abs;
};

static const int16_t row_stage123_mul[5] = {
	1, 708, 1521, 708, -1716,
};

static const int16_t row_stage123_pre[5] = {
	9, 6711, 14417, 6711, -16266,
};

static const int16_t row_stage45_mul[8][3] = {
	{ 1, 1, 708 },
	{ -39, -436, -1015 },
	{ 1521, -39, 44 },
	{ -550, -281, 1558 },
	{ 708, 1521, -1716 },
	{ 44, 588, 1464 },
	{ -1716, -550, 1241 },
	{ 1241, 1267, 1673 },
};

static const int16_t row_stage45_pre[8][3] = {
	{ 9, 9, 6711 },
	{ -370, -4133, -9621 },
	{ 14417, -370, 417 },
	{ -5213, -2664, 14768 },
	{ 6711, 14417, -16266 },
	{ 417, 5573, 13877 },
	{ -16266, -5213, 11763 },
	{ 11763, 12010, 15858 },
};

static int rowpack_index(int branch, int row, int lane, int k32)
{
	return branch * GT_BRANCH_N +
	       row * (GT_QUARTIC_LANES * GT_ROW_N) +
	       lane * GT_ROW_N + k32;
}

static int harness_modq(int64_t a)
{
	int r = (int)(a % NTRUPLUS_Q);

	if (r < 0)
	{
		r += NTRUPLUS_Q;
	}
	return r;
}

static int harness_equal_modq(int16_t a, int16_t b)
{
	return harness_modq((int)a - (int)b) == 0;
}

static int harness_abs_i(int x)
{
	return x < 0 ? -x : x;
}

static void update_max_abs(int *max_abs, const int16_t a[NTRUPLUS_N])
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		const int abs_v = harness_abs_i(a[i]);

		if (abs_v > *max_abs)
		{
			*max_abs = abs_v;
		}
	}
}

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static int16_t bounded_stage4_sample(uint32_t *seed)
{
	return (int16_t)((int)(next_u32(seed) % (2 * STAGE4_BOUND + 1)) -
	                 STAGE4_BOUND);
}

static void fill_stage4_case(int16_t v[NTRUPLUS_N], int which, uint32_t seed)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		switch (which & 7)
		{
		case 0:
			v[i] = 0;
			break;
		case 1:
			v[i] = 1;
			break;
		case 2:
			v[i] = (i & 1) ? -1 : 1;
			break;
		case 3:
			v[i] = (i & 1) ? -STAGE4_BOUND : STAGE4_BOUND;
			break;
		default:
			v[i] = bounded_stage4_sample(&seed);
			break;
		}
	}
}

static int16_t row_wrap16(int32_t x)
{
	return (int16_t)(uint16_t)x;
}

static int64_t row_arshift(int64_t x, unsigned shift)
{
	if (x >= 0)
	{
		return x >> shift;
	}
	return -(((-x) + ((INT64_C(1) << shift) - 1)) >> shift);
}

static int16_t row_sat16(int64_t x)
{
	if (x > 32767)
	{
		return 32767;
	}
	if (x < -32768)
	{
		return -32768;
	}
	return (int16_t)x;
}

static int16_t row_sqrdmulh_s16(int16_t a, int16_t b)
{
	const int64_t doubled = INT64_C(2) * a * b;
	const int64_t rounded = row_arshift(doubled + (INT64_C(1) << 15), 16);

	return row_sat16(rounded);
}

static int16_t row_fqmul_pre(int16_t a, int16_t mul, int16_t pre)
{
	const int16_t qhat = row_sqrdmulh_s16(a, pre);
	int16_t prod = row_wrap16((int32_t)a * mul);

	prod = row_wrap16((int32_t)prod - (int32_t)qhat * NTRUPLUS_Q);
	return prod;
}

static void row_butterfly(int16_t a[GT_ROW_N], int lo, int hi,
                          int16_t mul, int16_t pre)
{
	const int16_t old_lo = a[lo];
	const int16_t prod = row_fqmul_pre(a[hi], mul, pre);

	a[lo] = row_wrap16((int32_t)a[lo] + prod);
	a[hi] = row_wrap16((int32_t)old_lo - prod);
}

static void invntt32_row_stage1_only_no_entry(
	int16_t out[GT_ROW_N],
	const int16_t in[GT_ROW_N])
{
	memcpy(out, in, GT_ROW_N * sizeof(out[0]));

	for (int base = 0; base < GT_ROW_N; base += 8)
	{
		row_butterfly(out, base + 0, base + 1,
		              row_stage123_mul[0], row_stage123_pre[0]);
		row_butterfly(out, base + 2, base + 3,
		              row_stage123_mul[0], row_stage123_pre[0]);
		row_butterfly(out, base + 4, base + 5,
		              row_stage123_mul[0], row_stage123_pre[0]);
		row_butterfly(out, base + 6, base + 7,
		              row_stage123_mul[0], row_stage123_pre[0]);
	}
}

static void invntt32_row_stage2_to5_no_entry_no_end(
	int16_t out[GT_ROW_N],
	const int16_t in[GT_ROW_N])
{
	memcpy(out, in, GT_ROW_N * sizeof(out[0]));

	for (int base = 0; base < GT_ROW_N; base += 8)
	{
		row_butterfly(out, base + 0, base + 2,
		              row_stage123_mul[0], row_stage123_pre[0]);
		row_butterfly(out, base + 1, base + 3,
		              row_stage123_mul[1], row_stage123_pre[1]);
		row_butterfly(out, base + 4, base + 6,
		              row_stage123_mul[0], row_stage123_pre[0]);
		row_butterfly(out, base + 5, base + 7,
		              row_stage123_mul[1], row_stage123_pre[1]);

		row_butterfly(out, base + 0, base + 4,
		              row_stage123_mul[0], row_stage123_pre[0]);
		row_butterfly(out, base + 1, base + 5,
		              row_stage123_mul[2], row_stage123_pre[2]);
		row_butterfly(out, base + 2, base + 6,
		              row_stage123_mul[3], row_stage123_pre[3]);
		row_butterfly(out, base + 3, base + 7,
		              row_stage123_mul[4], row_stage123_pre[4]);
	}

	for (int j = 0; j < 8; j++)
	{
		row_butterfly(out, j, j + 8,
		              row_stage45_mul[j][0], row_stage45_pre[j][0]);
		row_butterfly(out, j + 16, j + 24,
		              row_stage45_mul[j][0], row_stage45_pre[j][0]);
		row_butterfly(out, j, j + 16,
		              row_stage45_mul[j][1], row_stage45_pre[j][1]);
		row_butterfly(out, j + 8, j + 24,
		              row_stage45_mul[j][2], row_stage45_pre[j][2]);
	}
}

static void invntt32_row_stage1_to5_no_entry_no_end(
	int16_t out[GT_ROW_N],
	const int16_t in[GT_ROW_N])
{
	int16_t stage1[GT_ROW_N];

	invntt32_row_stage1_only_no_entry(stage1, in);
	invntt32_row_stage2_to5_no_entry_no_end(out, stage1);
}

static void apply_rowkernel_stage1_only(
	int16_t r[NTRUPLUS_N],
	const int16_t a[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				const int pos = rowpack_index(branch, row, lane, 0);

				invntt32_row_stage1_only_no_entry(&r[pos], &a[pos]);
			}
		}
	}
}

static void apply_rowkernel_stage1_to5(
	int16_t r[NTRUPLUS_N],
	const int16_t a[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				const int pos = rowpack_index(branch, row, lane, 0);

				invntt32_row_stage1_to5_no_entry_no_end(&r[pos], &a[pos]);
			}
		}
	}
}

static void apply_rowkernel_stage2_to5(
	int16_t r[NTRUPLUS_N],
	const int16_t a[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				const int pos = rowpack_index(branch, row, lane, 0);

				invntt32_row_stage2_to5_no_entry_no_end(&r[pos], &a[pos]);
			}
		}
	}
}

#ifdef CANDIDATE_A_STAGE2_TO5_ASM
static void apply_rowkernel_stage2_to5_asm(
	int16_t r[NTRUPLUS_N],
	const int16_t a[NTRUPLUS_N])
{
	memcpy(r, a, NTRUPLUS_N * sizeof(r[0]));

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				const int pos = rowpack_index(branch, row, lane, 0);

				ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end(
					&r[pos],
					ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end_consts);
			}
		}
	}
}
#endif

static void materialize_complete_stage5(
	int16_t out[NTRUPLUS_N],
	const int16_t stage4[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int pair = 0; pair < GT_ROW_N / 2; pair++)
			{
				const int k_even = 2 * pair;
				const int k_odd = k_even + 1;
				const int16_t w = gt_ntt32_ct_twiddle(5, (unsigned)k_even);

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					const int even_index =
						rowpack_index(branch, row, lane, k_even);
					const int odd_index =
						rowpack_index(branch, row, lane, k_odd);
					const int16_t weighted =
						fqmul(stage4[odd_index], w);

					out[even_index] =
						(int16_t)(stage4[even_index] + weighted);
					out[odd_index] =
						(int16_t)(stage4[even_index] - weighted);
				}
			}
		}
	}
}

static void invntt_rowpack_branch_combine(
	int16_t r[NTRUPLUS_N],
	const int16_t branches[NTRUPLUS_N])
{
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

static void invntt_rowpack_postmerge_from_rows(
	int16_t r[NTRUPLUS_N],
	const int16_t work[NTRUPLUS_N])
{
	int16_t branches[NTRUPLUS_N];

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		const int branch_start = branch * GT_BRANCH_N;
		const int16_t *untwist =
			branch == 0 ? untwist_branch0 : untwist_branch1;

		for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
		{
			int16_t mat[GT_ROWS][GT_ROW_N];

			for (int row = 0; row < GT_ROWS; row++)
			{
				for (int k32 = 0; k32 < GT_ROW_N; k32++)
				{
					mat[row][k32] =
						work[rowpack_index(branch, row, lane, k32)];
				}
			}

			for (int k32 = 0; k32 < GT_ROW_N; k32++)
			{
				dft3_inverse(&mat[0][k32], &mat[1][k32], &mat[2][k32]);
			}

			for (int n3 = 0; n3 < GT_ROWS; n3++)
			{
				for (int n32 = 0; n32 < GT_ROW_N; n32++)
				{
					const int n =
						(64 * n3 + 33 * n32) % (GT_ROWS * GT_ROW_N);

					branches[branch_start + GT_QUARTIC_LANES * n + lane] =
						fqmul(mat[n3][n32], untwist[n]);
				}
			}
		}
	}

	invntt_rowpack_branch_combine(r, branches);
}

static int compare_modq_count(const char *label,
                              const int16_t got[NTRUPLUS_N],
                              const int16_t want[NTRUPLUS_N])
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!harness_equal_modq(got[i], want[i]))
		{
			fprintf(stderr,
			        "%s mismatch at %d: got %d want %d\n",
			        label, i, got[i], want[i]);
			return 0;
		}
	}
	return 1;
}

static int check_one_case(int which, int is_add,
                          struct mismatch_counts *mismatches,
                          struct range_stats *ranges)
{
	int16_t a_stage4[NTRUPLUS_N];
	int16_t b_stage4[NTRUPLUS_N];
	int16_t c_stage4[NTRUPLUS_N];
	int16_t a_complete[NTRUPLUS_N];
	int16_t b_complete[NTRUPLUS_N];
	int16_t c_complete[NTRUPLUS_N];
	int16_t full_tmvp[NTRUPLUS_N];
	int16_t candidate_adapter[NTRUPLUS_N];
	int16_t full_stage1[NTRUPLUS_N];
	int16_t full_rows[NTRUPLUS_N];
	int16_t candidate_rows[NTRUPLUS_N];
	int16_t full_out[NTRUPLUS_N];
	int16_t candidate_out[NTRUPLUS_N];
#ifdef CANDIDATE_A_STAGE2_TO5_ASM
	int16_t candidate_rows_asm[NTRUPLUS_N];
	int16_t candidate_out_asm[NTRUPLUS_N];
#endif
	int status;
	int ok = 1;

	fill_stage4_case(a_stage4, which, 0x243f6a88u + (uint32_t)which);
	fill_stage4_case(b_stage4, which + 3, 0x85a308d3u + (uint32_t)which);
	fill_stage4_case(c_stage4, which + 5, 0x13198a2eu + (uint32_t)which);

	materialize_complete_stage5(a_complete, a_stage4);
	materialize_complete_stage5(b_complete, b_stage4);
	materialize_complete_stage5(c_complete, c_stage4);

	if (is_add)
	{
		status = gt_tmvp_quartic_tmvp_add_experimental_c(
			full_tmvp, a_complete, b_complete, c_complete);
	}
	else
	{
		status = gt_tmvp_quartic_tmvp_experimental_c(
			full_tmvp, a_complete, b_complete);
	}
	if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "complete TMVP returned %s\n",
		        gt_tmvp_quartic_tmvp_experimental_status_name(status));
		return 0;
	}

	if (is_add)
	{
		status =
			gt_tmvp_quartic_tmvp_add_incomplete_materialized_stage5_adapter_c(
				candidate_adapter, a_stage4, b_stage4, c_stage4);
	}
	else
	{
		status =
			gt_tmvp_quartic_tmvp_incomplete_materialized_stage5_adapter_c(
				candidate_adapter, a_stage4, b_stage4);
	}
	if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "Candidate A TMVP returned %s\n",
		        gt_tmvp_quartic_tmvp_experimental_status_name(status));
		return 0;
	}

	apply_rowkernel_stage1_only(full_stage1, full_tmvp);
	apply_rowkernel_stage1_to5(full_rows, full_tmvp);
	apply_rowkernel_stage2_to5(candidate_rows, candidate_adapter);
	invntt_rowpack_postmerge_from_rows(full_out, full_rows);
	invntt_rowpack_postmerge_from_rows(candidate_out, candidate_rows);
#ifdef CANDIDATE_A_STAGE2_TO5_ASM
	apply_rowkernel_stage2_to5_asm(candidate_rows_asm, candidate_adapter);
	invntt_rowpack_postmerge_from_rows(candidate_out_asm, candidate_rows_asm);
#endif

	update_max_abs(&ranges->adapter_max_abs, candidate_adapter);
	update_max_abs(&ranges->full_rows_max_abs, full_rows);
	update_max_abs(&ranges->candidate_rows_max_abs, candidate_rows);
	update_max_abs(&ranges->postmerge_max_abs, candidate_out);
#ifdef CANDIDATE_A_STAGE2_TO5_ASM
	update_max_abs(&ranges->asm_rows_max_abs, candidate_rows_asm);
	update_max_abs(&ranges->asm_postmerge_max_abs, candidate_out_asm);
#endif

	if (!compare_modq_count(is_add ? "add adapter state" : "product adapter state",
	                        candidate_adapter, full_stage1))
	{
		mismatches->adapter++;
		ok = 0;
	}
	if (!compare_modq_count(is_add ? "add rowkernel stage2-to5" :
	                                 "product rowkernel stage2-to5",
	                        candidate_rows, full_rows))
	{
		mismatches->rowkernel++;
		ok = 0;
	}
	if (!compare_modq_count(is_add ? "add postmerge" : "product postmerge",
	                        candidate_out, full_out))
	{
		mismatches->postmerge++;
		ok = 0;
	}
#ifdef CANDIDATE_A_STAGE2_TO5_ASM
	if (!compare_modq_count(is_add ? "add asm rowkernel stage2-to5" :
	                                 "product asm rowkernel stage2-to5",
	                        candidate_rows_asm, candidate_rows))
	{
		mismatches->asm_rowkernel++;
		ok = 0;
	}
	if (!compare_modq_count(is_add ? "add asm postmerge" :
	                                 "product asm postmerge",
	                        candidate_out_asm, candidate_out))
	{
		mismatches->asm_postmerge++;
		ok = 0;
	}
#endif

	return ok;
}

static int write_report(int product_cases, int add_cases,
                        const struct mismatch_counts *mismatches,
                        const struct range_stats *ranges)
{
	const int total_mismatches =
		mismatches->adapter + mismatches->rowkernel +
		mismatches->postmerge + mismatches->asm_rowkernel +
		mismatches->asm_postmerge;
	FILE *f = fopen(REPORT_PATH, "w");

	if (!f)
	{
		perror("open Candidate A stage2/postmerge report");
		return 0;
	}

#ifdef CANDIDATE_A_STAGE2_TO5_ASM
	fprintf(f, "candidate_a_stage2_to5_asm_contract_status: %s\n",
	        total_mismatches == 0 ? "pass" : "fail");
#else
	fprintf(f, "candidate_a_stage2_postmerge_c_status: %s\n",
	        total_mismatches == 0 ? "pass" : "fail");
#endif
	fprintf(f, "selected_path: incomplete_stage4_candidate_a_tmvp_to_invntt_stage2_to_postmerge\n");
	fprintf(f, "tmvp_boundary: materialized_stage5_current_quartic_leaf\n");
	fprintf(f, "candidate_input_state: invntt_rowkernel_after_stage1_adapter\n");
	fprintf(f, "rowkernel_stage1_skipped: true\n");
	fprintf(f, "full_rowkernel_reference: scalar_no_entry_no_end_stage1_to5\n");
#ifdef CANDIDATE_A_STAGE2_TO5_ASM
	fprintf(f, "candidate_rowkernel: slothy_opt_no_entry_no_end_stage2_to5\n");
	fprintf(f, "candidate_rowkernel_asm_source: docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end.opt.S\n");
	fprintf(f, "candidate_rowkernel_asm_symbol: ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end\n");
	fprintf(f, "candidate_rowkernel_asm_const_symbol: ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end_consts\n");
	fprintf(f, "asm_compared_against: scalar_no_entry_no_end_stage2_to5_then_postmerge\n");
#else
	fprintf(f, "candidate_rowkernel: scalar_no_entry_no_end_stage2_to5\n");
#endif
	fprintf(f, "postmerge_reference: scalar_rowpack_postmerge_from_rows\n");
	fprintf(f, "adapter_even_slot: ce_plus_co\n");
	fprintf(f, "adapter_odd_slot: ce_minus_co\n");
	fprintf(f, "product_cases_run: %d\n", product_cases);
	fprintf(f, "product_add_cases_run: %d\n", add_cases);
	fprintf(f, "adapter_mismatches: %d\n", mismatches->adapter);
	fprintf(f, "rowkernel_mismatches: %d\n", mismatches->rowkernel);
	fprintf(f, "postmerge_mismatches: %d\n", mismatches->postmerge);
	fprintf(f, "asm_rowkernel_mismatches: %d\n", mismatches->asm_rowkernel);
	fprintf(f, "asm_postmerge_mismatches: %d\n", mismatches->asm_postmerge);
	fprintf(f, "total_mismatches: %d\n", total_mismatches);
	fprintf(f, "adapter_max_abs_observed: %d\n", ranges->adapter_max_abs);
	fprintf(f, "full_rows_max_abs_observed: %d\n", ranges->full_rows_max_abs);
	fprintf(f, "candidate_rows_max_abs_observed: %d\n",
	        ranges->candidate_rows_max_abs);
	fprintf(f, "postmerge_output_max_abs_observed: %d\n",
	        ranges->postmerge_max_abs);
#ifdef CANDIDATE_A_STAGE2_TO5_ASM
	fprintf(f, "asm_rows_max_abs_observed: %d\n",
	        ranges->asm_rows_max_abs);
	fprintf(f, "asm_postmerge_output_max_abs_observed: %d\n",
	        ranges->asm_postmerge_max_abs);
	fprintf(f, "asm_implemented: true\n");
	fprintf(f, "slothy_generated_opt_asm_used: true\n");
#else
	fprintf(f, "asm_implemented: false\n");
#endif
	fprintf(f, "full_pipeline_replaced: false\n");
	fprintf(f, "benchmark_or_cycle_claim_made: false\n");
#ifdef CANDIDATE_A_STAGE2_TO5_ASM
	fprintf(f, "recommended_next_gate: candidate_a_stage2_to5_rowkernel_asm_benchmark_or_fullpath_probe\n");
#else
	fprintf(f, "recommended_next_gate: candidate_a_stage2_to5_rowkernel_asm_contract\n");
#endif
	fclose(f);
	return 1;
}

int main(void)
{
	struct mismatch_counts mismatches = { 0 };
	struct range_stats ranges = { 0 };
	int product_cases = 0;
	int add_cases = 0;

	for (int t = 0; t < VECTOR_CASES; t++)
	{
		product_cases++;
		(void)check_one_case(t, 0, &mismatches, &ranges);

		add_cases++;
		(void)check_one_case(t, 1, &mismatches, &ranges);
	}

	if (!write_report(product_cases, add_cases, &mismatches, &ranges))
	{
		return 1;
	}

#ifdef CANDIDATE_A_STAGE2_TO5_ASM
	printf("Candidate A stage2-to5 ASM contract: %s\n",
	       (mismatches.adapter == 0 && mismatches.rowkernel == 0 &&
	        mismatches.postmerge == 0 && mismatches.asm_rowkernel == 0 &&
	        mismatches.asm_postmerge == 0) ? "ok" : "failed");
	printf("product_cases=%d product_add_cases=%d adapter_mismatches=%d rowkernel_mismatches=%d postmerge_mismatches=%d asm_rowkernel_mismatches=%d asm_postmerge_mismatches=%d\n",
	       product_cases, add_cases, mismatches.adapter,
	       mismatches.rowkernel, mismatches.postmerge,
	       mismatches.asm_rowkernel, mismatches.asm_postmerge);

	return (mismatches.adapter == 0 && mismatches.rowkernel == 0 &&
	        mismatches.postmerge == 0 && mismatches.asm_rowkernel == 0 &&
	        mismatches.asm_postmerge == 0) ? 0 : 1;
#else
	printf("Candidate A stage2-to-postmerge C contract: %s\n",
	       (mismatches.adapter == 0 && mismatches.rowkernel == 0 &&
	        mismatches.postmerge == 0) ? "ok" : "failed");
	printf("product_cases=%d product_add_cases=%d adapter_mismatches=%d rowkernel_mismatches=%d postmerge_mismatches=%d\n",
	       product_cases, add_cases, mismatches.adapter,
	       mismatches.rowkernel, mismatches.postmerge);

	return (mismatches.adapter == 0 && mismatches.rowkernel == 0 &&
	        mismatches.postmerge == 0) ? 0 : 1;
#endif
}
