#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "gt_tmvp_quartic_tmvp_experimental.h"
#include "ntt.h"
#include "params.h"

#define GT_BRANCHES 2
#define GT_BRANCH_N (NTRUPLUS_N / GT_BRANCHES)
#define GT_ROWS 3
#define GT_ROW_N 32
#define GT_QUARTIC_LANES 4
#define VECTOR_CASES 16
#define STAGE4_BOUND 1728

#define TEST_NTRUPLUS_R (-147)
#define TEST_NTRUPLUS_QINV 12929

static int rowpack_index(int branch, int row, int lane, int k32)
{
	return branch * GT_BRANCH_N +
	       row * (GT_QUARTIC_LANES * GT_ROW_N) +
	       lane * GT_ROW_N + k32;
}

static int16_t montgomery_reduce(int32_t a)
{
	int16_t t = (int16_t)a * TEST_NTRUPLUS_QINV;

	t = (a - (int32_t)t * NTRUPLUS_Q) >> 16;
	return t;
}

static int16_t fqmul(int16_t a, int16_t b)
{
	return montgomery_reduce((int32_t)a * b);
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

static int centered_modq(int64_t a)
{
	int r = modq(a);

	if (r > NTRUPLUS_Q / 2)
	{
		r -= NTRUPLUS_Q;
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

static int16_t bounded_stage4_sample(uint32_t *seed)
{
	return (int16_t)((int)(next_u32(seed) % (2 * STAGE4_BOUND + 1)) -
	                 STAGE4_BOUND);
}

static void fill_stage4_case(int16_t v[NTRUPLUS_N], int which, uint32_t seed)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		switch (which)
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
		case 4:
			v[i] = (int16_t)((i % 7) - 3);
			break;
		case 5:
			v[i] = (int16_t)(((i * 19) % (2 * STAGE4_BOUND + 1)) -
			                 STAGE4_BOUND);
			break;
		default:
			v[i] = bounded_stage4_sample(&seed);
			break;
		}
	}

	if (which == 6)
	{
		memset(v, 0, sizeof(int16_t) * NTRUPLUS_N);
		v[rowpack_index(0, 0, 0, 0)] = STAGE4_BOUND;
		v[rowpack_index(0, 0, 1, 1)] = -STAGE4_BOUND;
		v[rowpack_index(1, 2, 3, 31)] = 17;
	}
	else if (which == 7)
	{
		memset(v, 0, sizeof(int16_t) * NTRUPLUS_N);
		v[rowpack_index(0, 2, 1, 30)] = -29;
		v[rowpack_index(1, 0, 2, 1)] = STAGE4_BOUND;
		v[rowpack_index(1, 1, 3, 16)] = -STAGE4_BOUND;
	}
}

static void materialize_stage5_rowpack(int16_t complete[NTRUPLUS_N],
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
					const int even_index = rowpack_index(
						branch, row, lane, k_even);
					const int odd_index = rowpack_index(
						branch, row, lane, k_odd);
					const int16_t t = fqmul(stage4[odd_index], w);

					complete[even_index] = (int16_t)(stage4[even_index] + t);
					complete[odd_index] = (int16_t)(stage4[even_index] - t);
				}
			}
		}
	}
}

static void complete_to_stage1_adapter(int16_t adapter[NTRUPLUS_N],
                                       const int16_t complete_tmvp[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int pair = 0; pair < GT_ROW_N / 2; pair++)
			{
				const int k_even = 2 * pair;
				const int k_odd = k_even + 1;

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					const int even_index = rowpack_index(
						branch, row, lane, k_even);
					const int odd_index = rowpack_index(
						branch, row, lane, k_odd);
					const int16_t ce = complete_tmvp[even_index];
					const int16_t co = complete_tmvp[odd_index];

					adapter[even_index] = (int16_t)(ce + co);
					adapter[odd_index] = (int16_t)(ce - co);
				}
			}
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
			fprintf(stderr, "%s mismatch at %d: got=%d want=%d\n",
			        label, i, got[i], want[i]);
			return 0;
		}
	}

	return 1;
}

static int check_bound(const char *label, const int16_t v[NTRUPLUS_N],
                       int bound)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		const int centered = centered_modq(v[i]);

		if (centered < -bound || centered > bound)
		{
			fprintf(stderr,
			        "%s centered bound mismatch at %d: value=%d centered=%d bound=%d\n",
			        label, i, v[i], centered, bound);
			return 0;
		}
	}

	return 1;
}

static int check_product_case(int t)
{
	int16_t a4[NTRUPLUS_N];
	int16_t b4[NTRUPLUS_N];
	int16_t a_complete[NTRUPLUS_N];
	int16_t b_complete[NTRUPLUS_N];
	int16_t complete_tmvp[NTRUPLUS_N];
	int16_t want_adapter[NTRUPLUS_N];
	int16_t got_adapter[NTRUPLUS_N];
	const uint32_t seed = 0x12345678u + (uint32_t)t * 0x01010101u;
	int status;

	fill_stage4_case(a4, t, seed);
	fill_stage4_case(b4, (t + 5) % VECTOR_CASES, seed ^ 0x9e3779b9u);
	materialize_stage5_rowpack(a_complete, a4);
	materialize_stage5_rowpack(b_complete, b4);

	status = gt_tmvp_quartic_tmvp_experimental_c(
		complete_tmvp, a_complete, b_complete);
	if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "complete C TMVP returned %s\n",
		        gt_tmvp_quartic_tmvp_experimental_status_name(status));
		return 0;
	}
	complete_to_stage1_adapter(want_adapter, complete_tmvp);

	status = gt_tmvp_quartic_tmvp_incomplete_materialized_stage5_adapter_c(
		got_adapter, a4, b4);
	if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "Candidate A product C TMVP returned %s\n",
		        gt_tmvp_quartic_tmvp_experimental_status_name(status));
		return 0;
	}

	return check_bound("product stage4 input a", a4, STAGE4_BOUND) &&
	       check_bound("product stage4 input b", b4, STAGE4_BOUND) &&
	       compare_modq("Candidate A product adapter", got_adapter, want_adapter);
}

static int check_product_add_case(int t)
{
	int16_t a4[NTRUPLUS_N];
	int16_t b4[NTRUPLUS_N];
	int16_t c4[NTRUPLUS_N];
	int16_t a_complete[NTRUPLUS_N];
	int16_t b_complete[NTRUPLUS_N];
	int16_t c_complete[NTRUPLUS_N];
	int16_t complete_tmvp[NTRUPLUS_N];
	int16_t want_adapter[NTRUPLUS_N];
	int16_t got_adapter[NTRUPLUS_N];
	const uint32_t seed = 0x31415926u + (uint32_t)t * 0x001f123bu;
	int status;

	fill_stage4_case(a4, t, seed);
	fill_stage4_case(b4, (t + 7) % VECTOR_CASES, seed ^ 0x7f4a7c15u);
	fill_stage4_case(c4, (t + 11) % VECTOR_CASES, seed ^ 0xa5a5a5a5u);
	materialize_stage5_rowpack(a_complete, a4);
	materialize_stage5_rowpack(b_complete, b4);
	materialize_stage5_rowpack(c_complete, c4);

	status = gt_tmvp_quartic_tmvp_add_experimental_c(
		complete_tmvp, a_complete, b_complete, c_complete);
	if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "complete C TMVP add returned %s\n",
		        gt_tmvp_quartic_tmvp_experimental_status_name(status));
		return 0;
	}
	complete_to_stage1_adapter(want_adapter, complete_tmvp);

	status = gt_tmvp_quartic_tmvp_add_incomplete_materialized_stage5_adapter_c(
		got_adapter, a4, b4, c4);
	if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "Candidate A product-add C TMVP returned %s\n",
		        gt_tmvp_quartic_tmvp_experimental_status_name(status));
		return 0;
	}

	return check_bound("product-add stage4 input a", a4, STAGE4_BOUND) &&
	       check_bound("product-add stage4 input b", b4, STAGE4_BOUND) &&
	       check_bound("product-add stage4 input c", c4, STAGE4_BOUND) &&
	       compare_modq("Candidate A product-add adapter",
	                    got_adapter, want_adapter);
}

static int write_report(int product_cases, int add_cases, int mismatches)
{
	FILE *f = fopen("docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-c-harness-report.yml",
	                "w");

	if (f == 0)
	{
		return 0;
	}

	fprintf(f, "candidate_a_c_harness_status: %s\n",
	        mismatches == 0 ? "incomplete_materialized_stage5_tmvp_c_harness_pass" :
	                          "incomplete_materialized_stage5_tmvp_c_harness_failed");
	fprintf(f, "selected_path: incomplete_stage4_materialized_stage5_quartic_pair_to_invntt_stage2\n");
	fprintf(f, "candidate: fused_stage5_plus_current_quartic_leaves\n");
	fprintf(f, "stage4_input_layout: rowpack_k_even_u_k_odd_v\n");
	fprintf(f, "current_quartic_leaf_reused: true\n");
	fprintf(f, "direct_naive_octic_asm_used: false\n");
	fprintf(f, "product_cases_run: %d\n", product_cases);
	fprintf(f, "product_add_cases_run: %d\n", add_cases);
	fprintf(f, "mismatches: %d\n", mismatches);
	fprintf(f, "product_count_delta_vs_current: 0\n");
	fprintf(f, "stage5_materialized_inside_tmvp_c: true\n");
	fprintf(f, "output_adapter_even_slot: ce_plus_co\n");
	fprintf(f, "output_adapter_odd_slot: ce_minus_co\n");
	fprintf(f, "direct_invntt_stage1_adapter_checked: true\n");
	fprintf(f, "asm_implemented: false\n");
	fprintf(f, "full_pipeline_replaced: false\n");
	fprintf(f, "benchmark_or_cycle_claim_made: false\n");
	fprintf(f, "recommended_next_gate: candidate_a_stage2_to_postmerge_c_or_asm_contract\n");
	fclose(f);
	return 1;
}

int main(void)
{
	int16_t a[NTRUPLUS_N];
	int16_t b[NTRUPLUS_N];
	int16_t r[NTRUPLUS_N];
	int product_cases = 0;
	int add_cases = 0;
	int mismatches = 0;

	if (gt_tmvp_quartic_tmvp_incomplete_materialized_stage5_adapter_c(0, a, b) !=
	    GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT)
	{
		fprintf(stderr, "Candidate A product invalid argument check failed\n");
		return 1;
	}
	if (gt_tmvp_quartic_tmvp_add_incomplete_materialized_stage5_adapter_c(
		    r, a, b, 0) != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT)
	{
		fprintf(stderr, "Candidate A product-add invalid argument check failed\n");
		return 1;
	}

	for (int t = 0; t < VECTOR_CASES; t++)
	{
		product_cases++;
		if (!check_product_case(t))
		{
			mismatches++;
		}

		add_cases++;
		if (!check_product_add_case(t))
		{
			mismatches++;
		}
	}

	if (!write_report(product_cases, add_cases, mismatches))
	{
		fprintf(stderr, "failed to write Candidate A C harness report\n");
		return 1;
	}

	if (mismatches != 0)
	{
		return 1;
	}

	printf("Candidate A incomplete materialized-stage5 TMVP C harness: ok\n");
	printf("product_cases=%d product_add_cases=%d mismatches=%d\n",
	       product_cases, add_cases, mismatches);
	return 0;
}
