#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"

#define U01_BLOCK_FIRST_SCRATCH_WORDS NTRUPLUS_N
#define U01_BLOCK_FIRST_ROW_WORDS 256
#define U01_BLOCK_FIRST_Q_WORDS 8
#define U01_BLOCK_FIRST_BLOCK0_QS 8

/*
 * This harness is intentionally partial.  It checks the first U01 block-first
 * gate: post-Stage12 Q0..Q7 for rows0/1/2, which is Stage345 block0 input.
 *
 * Link it only after benchmark-only callable wrappers exist:
 *
 *   void u01_block_first_candidate(int16_t scratch[768],
 *                                  const int16_t input[768]);
 *   void u01_block_first_production_oracle(int16_t scratch[768],
 *                                          const int16_t input[768]);
 */

#if !defined(U01_BLOCK_FIRST_HAVE_IMPL) && !defined(U01_BLOCK_FIRST_USE_VECTORS)
int main(void)
{
	printf("u01_block_first_skip=no_callable_candidate_or_oracle\n");
	return 77;
}
#else
void u01_block_first_candidate(int16_t scratch[U01_BLOCK_FIRST_SCRATCH_WORDS],
			       const int16_t input[NTRUPLUS_N]);

#ifdef U01_BLOCK_FIRST_USE_VECTORS
#include "u01_block_first_vectors.inc"
#else
void u01_block_first_production_oracle(
	int16_t scratch[U01_BLOCK_FIRST_SCRATCH_WORDS],
	const int16_t input[NTRUPLUS_N]);
#endif

#ifndef U01_BLOCK_FIRST_USE_VECTORS
static uint32_t lcg_state = 1;

static uint32_t lcg_next(void)
{
	lcg_state = lcg_state * 1664525u + 1013904223u;
	return lcg_state;
}

static void fill_zero(int16_t input[NTRUPLUS_N])
{
	memset(input, 0, sizeof(int16_t) * NTRUPLUS_N);
}

static void fill_small_positive(int16_t input[NTRUPLUS_N])
{
	for (int i = 0; i < NTRUPLUS_N; i++) {
		input[i] = (int16_t)(i % 9);
	}
}

static void fill_near_q(int16_t input[NTRUPLUS_N])
{
	for (int i = 0; i < NTRUPLUS_N; i++) {
		input[i] = (int16_t)(NTRUPLUS_Q - 1 - (i % 23));
	}
}

static void fill_near_lazy_bound(int16_t input[NTRUPLUS_N])
{
	const int bound = 3 * (NTRUPLUS_Q - 1);

	for (int i = 0; i < NTRUPLUS_N; i++) {
		input[i] = (int16_t)(bound - (i % 47));
	}
}

static void fill_random_bounded(int16_t input[NTRUPLUS_N])
{
	const int bound = 3 * (NTRUPLUS_Q - 1);
	const int span = 2 * bound + 1;

	for (int i = 0; i < NTRUPLUS_N; i++) {
		input[i] = (int16_t)((int)(lcg_next() % (uint32_t)span) - bound);
	}
}

static int compare_block0(const char *name,
			  const int16_t want[U01_BLOCK_FIRST_SCRATCH_WORDS],
			  const int16_t got[U01_BLOCK_FIRST_SCRATCH_WORDS])
{
	int mismatches = 0;

	for (int row = 0; row < 3; row++) {
		const int row_base = row * U01_BLOCK_FIRST_ROW_WORDS;
		for (int q = 0; q < U01_BLOCK_FIRST_BLOCK0_QS; q++) {
			const int q_base = row_base + q * U01_BLOCK_FIRST_Q_WORDS;
			for (int lane = 0; lane < U01_BLOCK_FIRST_Q_WORDS; lane++) {
				const int idx = q_base + lane;
				if (want[idx] != got[idx]) {
					if (mismatches < 16) {
						printf("%s mismatch row=%d q=%d lane=%d "
						       "want=%d got=%d\n",
						       name, row, q, lane, want[idx],
						       got[idx]);
					}
					mismatches++;
				}
			}
		}
	}

	return mismatches;
}

static int compare_case(const char *name, const int16_t input[NTRUPLUS_N])
{
	int16_t want[U01_BLOCK_FIRST_SCRATCH_WORDS]
		__attribute__((aligned(64)));
	int16_t got[U01_BLOCK_FIRST_SCRATCH_WORDS]
		__attribute__((aligned(64)));

	memset(want, 0xa5, sizeof(want));
	memset(got, 0x5a, sizeof(got));
	u01_block_first_production_oracle(want, input);
	u01_block_first_candidate(got, input);
	return compare_block0(name, want, got);
}
#else
static int compare_vector(int vector_id)
{
	int16_t got[U01_BLOCK_FIRST_SCRATCH_WORDS]
		__attribute__((aligned(64)));
	int mismatches = 0;
	int expected_idx = 0;

	memset(got, 0x5a, sizeof(got));
	u01_block_first_candidate(got, u01_block_first_inputs[vector_id]);

	for (int row = 0; row < 3; row++) {
		const int row_base = row * U01_BLOCK_FIRST_ROW_WORDS;
		for (int q = 0; q < U01_BLOCK_FIRST_BLOCK0_QS; q++) {
			const int q_base = row_base + q * U01_BLOCK_FIRST_Q_WORDS;
			for (int lane = 0; lane < U01_BLOCK_FIRST_Q_WORDS; lane++) {
				const int got_idx = q_base + lane;
				const int16_t want =
					u01_block_first_expected[vector_id][expected_idx++];
				if (got[got_idx] != want) {
					if (mismatches < 16) {
						printf("vector%d mismatch row=%d q=%d lane=%d "
						       "want=%d got=%d\n",
						       vector_id, row, q, lane, want,
						       got[got_idx]);
					}
					mismatches++;
				}
			}
		}
	}
	return mismatches;
}
#endif

int main(void)
{
#ifndef U01_BLOCK_FIRST_USE_VECTORS
	int16_t input[NTRUPLUS_N] __attribute__((aligned(64)));
#endif
	int mismatches = 0;

#ifndef U01_BLOCK_FIRST_USE_VECTORS
	fill_zero(input);
	mismatches += compare_case("zero", input);

	fill_small_positive(input);
	mismatches += compare_case("small_positive", input);

	fill_near_q(input);
	mismatches += compare_case("near_q", input);

	fill_near_lazy_bound(input);
	mismatches += compare_case("near_lazy_bound", input);

	for (int t = 0; t < 64; t++) {
		fill_random_bounded(input);
		mismatches += compare_case("random_bounded", input);
	}
#else
	for (int t = 0; t < U01_BLOCK_FIRST_VECTOR_COUNT; t++) {
		mismatches += compare_vector(t);
	}
#endif

	printf("u01_block_first_block0_mismatches=%d\n", mismatches);
	printf("mismatches = %d\n", mismatches);
	return mismatches == 0 ? 0 : 1;
}
#endif
