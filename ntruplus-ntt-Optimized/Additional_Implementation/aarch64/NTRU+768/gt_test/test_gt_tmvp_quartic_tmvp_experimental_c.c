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
#define VECTOR_CASES 14

static int ref_rowpack_index(int branch, int row, int lane, int k32)
{
	return branch * GT_BRANCH_N +
	       row * (GT_QUARTIC_LANES * GT_ROW_N) +
	       lane * GT_ROW_N + k32;
}

static int ref_physical_j(int row, int k32)
{
	return (GT_ROW_N * row + GT_ROWS * k32) % (GT_ROWS * GT_ROW_N);
}

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static int16_t bounded_sample(uint32_t *seed)
{
	return (int16_t)((int)(next_u32(seed) % (2 * NTRUPLUS_Q)) -
	                 NTRUPLUS_Q);
}

static int16_t ref_montgomery_reduce(int32_t a)
{
	int16_t t = (int16_t)a * 12929;

	t = (a - (int32_t)t * NTRUPLUS_Q) >> 16;
	return t;
}

static int16_t ref_fqmul(int16_t a, int16_t b)
{
	return ref_montgomery_reduce((int32_t)a * b);
}

static void fill_case(int16_t v[NTRUPLUS_N], int which, uint32_t seed)
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
			v[i] = (i & 1) ? -(NTRUPLUS_Q / 2) : (NTRUPLUS_Q / 2);
			break;
		case 4:
			v[i] = (int16_t)((i % 5) - 2);
			break;
		case 5:
			v[i] = (int16_t)(((i * 17) % NTRUPLUS_Q) -
			                 (NTRUPLUS_Q / 2));
			break;
		case 6:
			v[i] = (int16_t)((i % 3 == 0) ? (NTRUPLUS_Q - 1) :
			                 (i % 3 == 1) ? -(NTRUPLUS_Q - 1) : 0);
			break;
		default:
			v[i] = bounded_sample(&seed);
			break;
		}
	}

	if (which == 7)
	{
		memset(v, 0, sizeof(int16_t) * NTRUPLUS_N);
		v[ref_rowpack_index(0, 0, 0, 0)] = 1;
		v[ref_rowpack_index(0, 0, 3, 0)] = -1;
		v[ref_rowpack_index(1, 2, 2, 31)] = NTRUPLUS_Q / 2;
	}
	else if (which == 8)
	{
		memset(v, 0, sizeof(int16_t) * NTRUPLUS_N);
		v[ref_rowpack_index(0, 2, 1, 31)] = -3;
		v[ref_rowpack_index(1, 0, 2, 0)] = 5;
		v[ref_rowpack_index(1, 1, 3, 17)] = -7;
	}
}

static void materialize_complete_stage5(int16_t complete[NTRUPLUS_N],
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
				const int16_t w =
					gt_ntt32_ct_twiddle(5, (unsigned)k_even);

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					const int even_index =
						ref_rowpack_index(branch, row, lane, k_even);
					const int odd_index =
						ref_rowpack_index(branch, row, lane, k_odd);
					const int16_t weighted =
						ref_fqmul(stage4[odd_index], w);

					complete[even_index] =
						(int16_t)(stage4[even_index] + weighted);
					complete[odd_index] =
						(int16_t)(stage4[even_index] - weighted);
				}
			}
		}
	}
}

static int check_index_maps(void)
{
	int seen[GT_ROWS * GT_ROW_N] = { 0 };

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				for (int k32 = 0; k32 < GT_ROW_N; k32++)
				{
					const int got = gt_tmvp_quartic_tmvp_rowpack_index(
						branch, row, lane, k32);
					const int want = ref_rowpack_index(branch, row, lane, k32);

					if (got != want)
					{
						fprintf(stderr,
						        "rowpack index mismatch: branch=%d row=%d lane=%d k32=%d got=%d want=%d\n",
						        branch, row, lane, k32, got, want);
						return 0;
					}
				}
			}
		}
	}

	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			const int got = gt_tmvp_quartic_tmvp_physical_j(row, k32);
			const int want = ref_physical_j(row, k32);

			if (got != want)
			{
				fprintf(stderr,
				        "physical_j mismatch: row=%d k32=%d got=%d want=%d\n",
				        row, k32, got, want);
				return 0;
			}
			seen[got]++;
		}
	}

	for (int i = 0; i < GT_ROWS * GT_ROW_N; i++)
	{
		if (seen[i] != 1)
		{
			fprintf(stderr, "physical_j coverage mismatch at %d: seen=%d\n",
			        i, seen[i]);
			return 0;
		}
	}

	return 1;
}

static void reference_mul(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N],
                          const int16_t b[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_ROW_N; k32++)
			{
				int16_t aa[GT_QUARTIC_LANES];
				int16_t bb[GT_QUARTIC_LANES];
				int16_t rr[GT_QUARTIC_LANES];
				const int physical_j = ref_physical_j(row, k32);

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					const int index = ref_rowpack_index(branch, row, lane, k32);
					aa[lane] = a[index];
					bb[lane] = b[index];
				}

				basemul(rr, aa, bb, gt_rowbitrev_lambda[branch][physical_j]);

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					const int index = ref_rowpack_index(branch, row, lane, k32);
					r[index] = rr[lane];
				}
			}
		}
	}
}

static void reference_add(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N],
                          const int16_t b[NTRUPLUS_N],
                          const int16_t c[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_ROW_N; k32++)
			{
				int16_t aa[GT_QUARTIC_LANES];
				int16_t bb[GT_QUARTIC_LANES];
				int16_t cc[GT_QUARTIC_LANES];
				int16_t rr[GT_QUARTIC_LANES];
				const int physical_j = ref_physical_j(row, k32);

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					const int index = ref_rowpack_index(branch, row, lane, k32);
					aa[lane] = a[index];
					bb[lane] = b[index];
					cc[lane] = c[index];
				}

				basemul_add(rr, aa, bb, cc,
				            gt_rowbitrev_lambda[branch][physical_j]);

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					const int index = ref_rowpack_index(branch, row, lane, k32);
					r[index] = rr[lane];
				}
			}
		}
	}
}

static int compare_exact(const char *label, const int16_t got[NTRUPLUS_N],
                         const int16_t want[NTRUPLUS_N])
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (got[i] != want[i])
		{
			fprintf(stderr, "%s mismatch at %d: got=%d want=%d\n",
			        label, i, got[i], want[i]);
			return 0;
		}
	}

	return 1;
}

static int write_report(int vector_tests, int alias_tests,
                        int complete_stage5_tests, int mismatches)
{
	FILE *f;

	f = fopen("docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-production-c-experimental-interface.yml",
	          "w");
	if (f == 0)
	{
		return 0;
	}
	fprintf(f, "production_c_experimental_status: production_c_entry_created_needs_review\n");
	fprintf(f, "function_name: gt_tmvp_quartic_tmvp_experimental_c\n");
	fprintf(f, "add_function_name: gt_tmvp_quartic_tmvp_add_experimental_c\n");
	fprintf(f, "selected_path: complete_ntt32_quartic_tmvp\n");
	fprintf(f, "rowpack_index_formula: branch*384 + row*128 + lane*32 + k32\n");
	fprintf(f, "lambda_table_formula: gt_rowbitrev_lambda[branch][(32*row + 3*k32) mod 96]\n");
	fprintf(f, "lambda_representation: production_montgomery_form\n");
	fprintf(f, "reduction_convention: mirrors_production_basemul_bounded_output\n");
	fprintf(f, "opt_in_macro: GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C\n");
	fprintf(f, "macro_scope: make_test_target_only\n");
	fprintf(f, "default_sources_modified: false\n");
	fprintf(f, "production_default_path_replaced: false\n");
	fclose(f);

	f = fopen("docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-production-c-experimental-report.yml",
	          "w");
	if (f == 0)
	{
		return 0;
	}
	fprintf(f, "selected_path: complete_ntt32_quartic_tmvp\n");
	fprintf(f, "production_c_experimental_path_created: true\n");
	fprintf(f, "opt_in_macro: GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C\n");
	fprintf(f, "default_sources_modified: false\n");
	fprintf(f, "production_default_path_replaced: false\n");
	fprintf(f, "ntt_or_poly_api_modified: false\n");
	fprintf(f, "asm_generated: false\n");
	fprintf(f, "slothy_output_generated: false\n");
	fprintf(f, "benchmark_or_cycle_claim_made: false\n");
	fprintf(f, "correctness_claim_made: false\n");
	fprintf(f, "final_candidate_selected: false\n");
	fprintf(f, "vector_tests_run: %d\n", vector_tests);
	fprintf(f, "alias_tests_run: %d\n", alias_tests);
	fprintf(f, "complete_stage5_adapter_tests_run: %d\n",
	        complete_stage5_tests);
	fprintf(f, "leaf_calls_run: %d\n",
	        (vector_tests + alias_tests) * GT_BRANCHES * GT_ROWS * GT_ROW_N);
	fprintf(f, "comparison_status: %s\n",
	        mismatches == 0 ? "production_c_experimental_pass_needs_review" :
	                          "production_c_experimental_failed_needs_review");
	fprintf(f, "mismatches_needing_review: %d\n", mismatches);
	fprintf(f, "references_used:\n");
	fprintf(f, "- production_basemul\n");
	fprintf(f, "- production_basemul_add\n");
	fprintf(f, "- gt_rowbitrev_lambda\n");
	fprintf(f, "recommended_next_gate: opt_in_poly_wrapper_gate\n");
	fclose(f);

	return 1;
}

int main(void)
{
	int16_t a[NTRUPLUS_N];
	int16_t b[NTRUPLUS_N];
	int16_t c[NTRUPLUS_N];
	int16_t a_complete[NTRUPLUS_N];
	int16_t b_complete[NTRUPLUS_N];
	int16_t c_complete[NTRUPLUS_N];
	int16_t got[NTRUPLUS_N];
	int16_t want[NTRUPLUS_N];
	int vector_tests = 0;
	int alias_tests = 0;
	int complete_stage5_tests = 0;
	int mismatches = 0;

	if (!check_index_maps())
	{
		return 1;
	}

	if (gt_tmvp_quartic_tmvp_experimental_c(0, a, b) !=
	    GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT)
	{
		fprintf(stderr, "invalid argument check failed for mul\n");
		return 1;
	}
	if (gt_tmvp_quartic_tmvp_add_experimental_c(got, a, b, 0) !=
	    GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT)
	{
		fprintf(stderr, "invalid argument check failed for add\n");
		return 1;
	}
	if (gt_tmvp_quartic_tmvp_incomplete_complete_stage5_adapter_c(
		    0, a, b) != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT)
	{
		fprintf(stderr, "invalid argument check failed for complete-stage5 mul\n");
		return 1;
	}
	if (gt_tmvp_quartic_tmvp_add_incomplete_complete_stage5_adapter_c(
		    got, a, b, 0) !=
	    GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT)
	{
		fprintf(stderr, "invalid argument check failed for complete-stage5 add\n");
		return 1;
	}

	for (int t = 0; t < VECTOR_CASES; t++)
	{
		const uint32_t seed = 0x9e3779b9u + (uint32_t)t * 0x10001u;
		int status;

		fill_case(a, t, seed);
		fill_case(b, (t + 3) % VECTOR_CASES, seed ^ 0xa5a5a5a5u);
		fill_case(c, (t + 7) % VECTOR_CASES, seed ^ 0x5a5a5a5au);

		reference_mul(want, a, b);
		status = gt_tmvp_quartic_tmvp_experimental_c(got, a, b);
		if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
		{
			fprintf(stderr, "mul returned %s on vector case %d\n",
			        gt_tmvp_quartic_tmvp_experimental_status_name(status), t);
			return 1;
		}
		if (!compare_exact("mul", got, want))
		{
			mismatches++;
		}
		vector_tests++;

		reference_add(want, a, b, c);
		status = gt_tmvp_quartic_tmvp_add_experimental_c(got, a, b, c);
		if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
		{
			fprintf(stderr, "add returned %s on vector case %d\n",
			        gt_tmvp_quartic_tmvp_experimental_status_name(status), t);
			return 1;
		}
		if (!compare_exact("add", got, want))
		{
			mismatches++;
		}
		vector_tests++;

		materialize_complete_stage5(a_complete, a);
		materialize_complete_stage5(b_complete, b);
		materialize_complete_stage5(c_complete, c);

		status = gt_tmvp_quartic_tmvp_incomplete_materialized_stage5_adapter_c(
			want, a, b);
		if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
		{
			fprintf(stderr, "materialized-stage5 mul returned %s on vector case %d\n",
			        gt_tmvp_quartic_tmvp_experimental_status_name(status), t);
			return 1;
		}
		status = gt_tmvp_quartic_tmvp_incomplete_complete_stage5_adapter_c(
			got, a_complete, b_complete);
		if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
		{
			fprintf(stderr, "complete-stage5 mul returned %s on vector case %d\n",
			        gt_tmvp_quartic_tmvp_experimental_status_name(status), t);
			return 1;
		}
		if (!compare_exact("complete_stage5_mul", got, want))
		{
			mismatches++;
		}
		complete_stage5_tests++;

		status =
			gt_tmvp_quartic_tmvp_add_incomplete_materialized_stage5_adapter_c(
				want, a, b, c);
		if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
		{
			fprintf(stderr, "materialized-stage5 add returned %s on vector case %d\n",
			        gt_tmvp_quartic_tmvp_experimental_status_name(status), t);
			return 1;
		}
		status =
			gt_tmvp_quartic_tmvp_add_incomplete_complete_stage5_adapter_c(
				got, a_complete, b_complete, c_complete);
		if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
		{
			fprintf(stderr, "complete-stage5 add returned %s on vector case %d\n",
			        gt_tmvp_quartic_tmvp_experimental_status_name(status), t);
			return 1;
		}
		if (!compare_exact("complete_stage5_add", got, want))
		{
			mismatches++;
		}
		complete_stage5_tests++;
	}

	fill_case(a, 11, 0x13579bdfu);
	fill_case(b, 12, 0x2468ace0u);
	fill_case(c, 13, 0x10203040u);

	reference_mul(want, a, b);
	memcpy(got, a, sizeof(got));
	if (gt_tmvp_quartic_tmvp_experimental_c(got, got, b) !=
	    GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "mul alias r==a returned non-OK\n");
		return 1;
	}
	if (!compare_exact("mul_alias_a", got, want))
	{
		mismatches++;
	}
	alias_tests++;

	reference_mul(want, a, b);
	memcpy(got, b, sizeof(got));
	if (gt_tmvp_quartic_tmvp_experimental_c(got, a, got) !=
	    GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "mul alias r==b returned non-OK\n");
		return 1;
	}
	if (!compare_exact("mul_alias_b", got, want))
	{
		mismatches++;
	}
	alias_tests++;

	reference_add(want, a, b, c);
	memcpy(got, c, sizeof(got));
	if (gt_tmvp_quartic_tmvp_add_experimental_c(got, a, b, got) !=
	    GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "add alias r==c returned non-OK\n");
		return 1;
	}
	if (!compare_exact("add_alias_c", got, want))
	{
		mismatches++;
	}
	alias_tests++;

	if (!write_report(vector_tests, alias_tests, complete_stage5_tests,
	                  mismatches))
	{
		fprintf(stderr, "could not write production C experimental report\n");
		return 1;
	}

	printf("Good-Thomas quartic TMVP production C experimental path summary:\n");
	printf("  vector tests: %d\n", vector_tests);
	printf("  alias tests: %d\n", alias_tests);
	printf("  Complete-stage5 adapter tests: %d\n", complete_stage5_tests);
	printf("  leaf calls: %d\n",
	       (vector_tests + alias_tests) * GT_BRANCHES * GT_ROWS * GT_ROW_N);
	printf("  comparison: %s\n",
	       mismatches == 0 ? "production_c_experimental_pass_needs_review" :
	                         "production_c_experimental_failed_needs_review");
	printf("  mismatches needing review: %d\n", mismatches);
	printf("  next gate: opt_in_poly_wrapper_gate\n");

	return mismatches == 0 ? 0 : 1;
}
