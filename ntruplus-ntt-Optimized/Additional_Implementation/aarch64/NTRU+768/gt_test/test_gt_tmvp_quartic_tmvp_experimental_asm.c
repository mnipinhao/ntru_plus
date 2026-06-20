#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "gt_tmvp_quartic_tmvp_experimental.h"
#include "params.h"

#if !defined(__aarch64__)
#error "gt_tmvp_quartic_tmvp_experimental_asm test requires AArch64"
#endif

#define GT_BRANCHES 2
#define GT_ROWS 3
#define GT_ROW_N 32
#define VECTOR_CASES 14

static int ref_rowpack_index(int branch, int row, int lane, int k32)
{
	return branch * (NTRUPLUS_N / GT_BRANCHES) +
	       row * (4 * GT_ROW_N) + lane * GT_ROW_N + k32;
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

static int write_report(int vector_tests, int alias_tests, int mismatches)
{
	FILE *f = fopen("docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-asm-wiring-report.yml",
	                "w");

	if (f == 0)
	{
		return 0;
	}

	fprintf(f, "asm_wiring_status: %s\n",
	        mismatches == 0 ? "asm_neon_batch8_pass_needs_review" :
	                          "asm_wiring_failed_needs_review");
	fprintf(f, "selected_path: complete_ntt32_quartic_tmvp\n");
	fprintf(f, "asm_wiring_source_created: true\n");
	fprintf(f, "asm_source_file: asm/gt_tmvp_quartic_tmvp_experimental_asm.S\n");
	fprintf(f, "function_name: gt_tmvp_quartic_tmvp_experimental_asm\n");
	fprintf(f, "add_function_name: gt_tmvp_quartic_tmvp_add_experimental_asm\n");
	fprintf(f, "fast_function_name: gt_tmvp_quartic_tmvp_experimental_asm_fast\n");
	fprintf(f, "fast_add_function_name: gt_tmvp_quartic_tmvp_add_experimental_asm_fast\n");
	fprintf(f, "reference_c_entry: gt_tmvp_quartic_tmvp_experimental_c\n");
	fprintf(f, "reference_c_add_entry: gt_tmvp_quartic_tmvp_add_experimental_c\n");
	fprintf(f, "kernel_boundary: rowpack_to_rowpack_full_array_tmvp\n");
	fprintf(f, "asm_loop_coverage: full_2x3x4_batch8_rowpack_walk\n");
	fprintf(f, "rowpack_index_formula: branch*384 + row*128 + lane*32 + k32\n");
	fprintf(f, "lambda_formula: gt_rowbitrev_lambda[branch][(32*row + 3*k32) mod 96]\n");
	fprintf(f, "lambda_load_strategy: rowpack_ordered_vector_table\n");
	fprintf(f, "lambda_rowpack_table_bytes: 384\n");
	fprintf(f, "lambda_address_generation: streaming_postincrement\n");
	fprintf(f, "rowpack_address_generation: row_base_plus_k_postincrement\n");
	fprintf(f, "fast_entry_checked: true\n");
	fprintf(f, "stack_lambda_gather_used: false\n");
	fprintf(f, "batch_arithmetic: inline_aarch64_neon_batch8_montgomery\n");
	fprintf(f, "external_leaf_helper_calls: false\n");
	fprintf(f, "inline_neon_batch8: true\n");
	fprintf(f, "vector_tests_run: %d\n", vector_tests);
	fprintf(f, "alias_tests_run: %d\n", alias_tests);
	fprintf(f, "quartic_products_run: %d\n",
	        (vector_tests + alias_tests) * GT_BRANCHES * GT_ROWS * GT_ROW_N);
	fprintf(f, "batch8_groups_run: %d\n",
	        (vector_tests + alias_tests) * GT_BRANCHES * GT_ROWS *
	                (GT_ROW_N / 8));
	fprintf(f, "mismatches_needing_review: %d\n", mismatches);
	fprintf(f, "slothy_output_generated: false\n");
	fprintf(f, "benchmark_or_cycle_claim_made: false\n");
	fprintf(f, "correctness_claim_made: false\n");
	fprintf(f, "final_candidate_selected: false\n");
	fprintf(f, "recommended_next_gate: benchmark_after_rowpack_lambda_table_then_schedule_review_gate\n");
	fclose(f);

	return 1;
}

int main(void)
{
	int16_t a[NTRUPLUS_N];
	int16_t b[NTRUPLUS_N];
	int16_t c[NTRUPLUS_N];
	int16_t got[NTRUPLUS_N];
	int16_t want[NTRUPLUS_N];
	int vector_tests = 0;
	int alias_tests = 0;
	int mismatches = 0;

	if (gt_tmvp_quartic_tmvp_experimental_asm(0, a, b) !=
	    GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT)
	{
		fprintf(stderr, "asm invalid argument check failed for mul\n");
		return 1;
	}
	if (gt_tmvp_quartic_tmvp_add_experimental_asm(got, a, b, 0) !=
	    GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_INVALID_ARGUMENT)
	{
		fprintf(stderr, "asm invalid argument check failed for add\n");
		return 1;
	}

	for (int t = 0; t < VECTOR_CASES; t++)
	{
		const uint32_t seed = 0x31415927u + (uint32_t)t * 0x20011u;
		int c_status;
		int asm_status;
		int fast_status;

		fill_case(a, t, seed);
		fill_case(b, (t + 5) % VECTOR_CASES, seed ^ 0xa1b2c3d4u);
		fill_case(c, (t + 9) % VECTOR_CASES, seed ^ 0x9e3779b9u);

		c_status = gt_tmvp_quartic_tmvp_experimental_c(want, a, b);
		asm_status = gt_tmvp_quartic_tmvp_experimental_asm(got, a, b);
		if (c_status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK ||
		    asm_status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
		{
			fprintf(stderr, "mul status mismatch on case %d: c=%s asm=%s\n",
			        t,
			        gt_tmvp_quartic_tmvp_experimental_status_name(c_status),
			        gt_tmvp_quartic_tmvp_experimental_status_name(asm_status));
			return 1;
		}
		if (!compare_exact("asm_mul", got, want))
		{
			mismatches++;
		}
		fast_status = gt_tmvp_quartic_tmvp_experimental_asm_fast(got, a, b);
		if (fast_status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
		{
			fprintf(stderr, "fast mul status mismatch on case %d: fast=%s\n",
			        t,
			        gt_tmvp_quartic_tmvp_experimental_status_name(fast_status));
			return 1;
		}
		if (!compare_exact("asm_fast_mul", got, want))
		{
			mismatches++;
		}
		vector_tests++;

		c_status = gt_tmvp_quartic_tmvp_add_experimental_c(want, a, b, c);
		asm_status = gt_tmvp_quartic_tmvp_add_experimental_asm(got, a, b, c);
		if (c_status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK ||
		    asm_status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
		{
			fprintf(stderr, "add status mismatch on case %d: c=%s asm=%s\n",
			        t,
			        gt_tmvp_quartic_tmvp_experimental_status_name(c_status),
			        gt_tmvp_quartic_tmvp_experimental_status_name(asm_status));
			return 1;
		}
		if (!compare_exact("asm_add", got, want))
		{
			mismatches++;
		}
		fast_status = gt_tmvp_quartic_tmvp_add_experimental_asm_fast(got, a, b, c);
		if (fast_status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
		{
			fprintf(stderr, "fast add status mismatch on case %d: fast=%s\n",
			        t,
			        gt_tmvp_quartic_tmvp_experimental_status_name(fast_status));
			return 1;
		}
		if (!compare_exact("asm_fast_add", got, want))
		{
			mismatches++;
		}
		vector_tests++;
	}

	fill_case(a, 11, 0x13579bdfu);
	fill_case(b, 12, 0x2468ace0u);
	fill_case(c, 13, 0x10203040u);

	(void)gt_tmvp_quartic_tmvp_experimental_c(want, a, b);
	memcpy(got, a, sizeof(got));
	if (gt_tmvp_quartic_tmvp_experimental_asm(got, got, b) !=
	    GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "asm mul alias r==a returned non-OK\n");
		return 1;
	}
	if (!compare_exact("asm_mul_alias_a", got, want))
	{
		mismatches++;
	}
	alias_tests++;

	(void)gt_tmvp_quartic_tmvp_experimental_c(want, a, b);
	memcpy(got, b, sizeof(got));
	if (gt_tmvp_quartic_tmvp_experimental_asm(got, a, got) !=
	    GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "asm mul alias r==b returned non-OK\n");
		return 1;
	}
	if (!compare_exact("asm_mul_alias_b", got, want))
	{
		mismatches++;
	}
	alias_tests++;

	(void)gt_tmvp_quartic_tmvp_add_experimental_c(want, a, b, c);
	memcpy(got, c, sizeof(got));
	if (gt_tmvp_quartic_tmvp_add_experimental_asm(got, a, b, got) !=
	    GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "asm add alias r==c returned non-OK\n");
		return 1;
	}
	if (!compare_exact("asm_add_alias_c", got, want))
	{
		mismatches++;
	}
	alias_tests++;

	if (!write_report(vector_tests, alias_tests, mismatches))
	{
		fprintf(stderr, "could not write ASM wiring report\n");
		return 1;
	}

	printf("Good-Thomas quartic TMVP ASM wiring summary:\n");
	printf("  vector tests: %d\n", vector_tests);
	printf("  alias tests: %d\n", alias_tests);
	printf("  quartic products: %d\n",
	       (vector_tests + alias_tests) * GT_BRANCHES * GT_ROWS * GT_ROW_N);
	printf("  batch8 groups: %d\n",
	       (vector_tests + alias_tests) * GT_BRANCHES * GT_ROWS *
	               (GT_ROW_N / 8));
	printf("  comparison: %s\n",
	       mismatches == 0 ? "asm_neon_batch8_pass_needs_review" :
	                         "asm_wiring_failed_needs_review");
	printf("  mismatches needing review: %d\n", mismatches);
	printf("  lambda load: rowpack_ordered_vector_table\n");
	printf("  lambda address generation: streaming_postincrement\n");
	printf("  fast entry checked: true\n");
	printf("  next gate: benchmark_after_rowpack_lambda_table_then_schedule_review_gate\n");

	return mismatches == 0 ? 0 : 1;
}
