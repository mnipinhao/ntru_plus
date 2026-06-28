#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "ntt.h"
#include "params.h"

#define GT_DIRECT32_QINV 12929
#define GT_DIRECT32_R (-147)
#define GT_DIRECT32_RSQ 867
#define GT_DIRECT32_CENTER_BOUND ((NTRUPLUS_Q - 1) / 2)

struct range_tracker {
	int64_t min_p;
	int64_t max_p;
	int64_t min_pc;
	int64_t max_pc;
	int64_t max_abs_p;
	int64_t max_abs_pc;
};

struct model_counts {
	int exact_mismatches;
	int packed_mismatches;
	int non_modq_mismatches;
};

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static int16_t centered_modq_i64(int64_t x)
{
	x %= NTRUPLUS_Q;
	if (x > NTRUPLUS_Q / 2)
		x -= NTRUPLUS_Q;
	if (x < -NTRUPLUS_Q / 2)
		x += NTRUPLUS_Q;
	return (int16_t)x;
}

static int16_t montgomery_reduce_ref(int32_t a)
{
	int16_t t;

	t = (int16_t)a * GT_DIRECT32_QINV;
	t = (int16_t)((a - (int32_t)t * NTRUPLUS_Q) >> 16);
	return t;
}

static int same_modq(int16_t a, int16_t b)
{
	int32_t diff = (int32_t)a - b;

	diff %= NTRUPLUS_Q;
	if (diff < 0)
		diff += NTRUPLUS_Q;
	return diff == 0;
}

static uint16_t pack_coeff_contract(int16_t x)
{
	int32_t y = x;

	if (y < 0)
		y += NTRUPLUS_Q;
	return (uint16_t)y;
}

static int16_t candidate_reduce32_centered(int32_t pc)
{
	return centered_modq_i64(pc);
}

static int16_t current_add32_finalizer_from_p(int32_t p, int16_t c)
{
	const int16_t raw = montgomery_reduce_ref(p);
	const int32_t prefinal =
		(int32_t)c * GT_DIRECT32_R + (int32_t)raw * GT_DIRECT32_RSQ;

	return montgomery_reduce_ref(prefinal);
}

static int16_t candidate_direct32_from_p(int32_t p, int16_t c)
{
	return candidate_reduce32_centered(p + (int32_t)c);
}

static void p_model_from_quartic(int32_t p[4],
                                 const int16_t a[4],
                                 const int16_t b[4],
                                 int16_t lambda)
{
	const int16_t w2 =
		montgomery_reduce_ref((int32_t)a[3] * b[3]);
	const int16_t w1 =
		montgomery_reduce_ref((int32_t)a[2] * b[3] +
		                      (int32_t)a[3] * b[2]);
	const int16_t w0 =
		montgomery_reduce_ref((int32_t)a[1] * b[3] +
		                      (int32_t)a[2] * b[2] +
		                      (int32_t)a[3] * b[1]);

	p[0] = (int32_t)w0 * lambda + (int32_t)a[0] * b[0];
	p[1] = (int32_t)w1 * lambda +
	       (int32_t)a[0] * b[1] + (int32_t)a[1] * b[0];
	p[2] = (int32_t)w2 * lambda +
	       (int32_t)a[0] * b[2] + (int32_t)a[1] * b[1] +
	       (int32_t)a[2] * b[0];
	p[3] = (int32_t)a[0] * b[3] + (int32_t)a[1] * b[2] +
	       (int32_t)a[2] * b[1] + (int32_t)a[3] * b[0];
}

static void update_range(struct range_tracker *range, int32_t p, int32_t pc)
{
	if (p < range->min_p)
		range->min_p = p;
	if (p > range->max_p)
		range->max_p = p;
	if (pc < range->min_pc)
		range->min_pc = pc;
	if (pc > range->max_pc)
		range->max_pc = pc;
	if (llabs((long long)p) > range->max_abs_p)
		range->max_abs_p = llabs((long long)p);
	if (llabs((long long)pc) > range->max_abs_pc)
		range->max_abs_pc = llabs((long long)pc);
}

static void init_range(struct range_tracker *range)
{
	range->min_p = INT64_MAX;
	range->max_p = INT64_MIN;
	range->min_pc = INT64_MAX;
	range->max_pc = INT64_MIN;
	range->max_abs_p = 0;
	range->max_abs_pc = 0;
}

static void add_counts(struct model_counts *total,
                       const struct model_counts *delta)
{
	total->exact_mismatches += delta->exact_mismatches;
	total->packed_mismatches += delta->packed_mismatches;
	total->non_modq_mismatches += delta->non_modq_mismatches;
}

static void print_counts(const char *prefix, const struct model_counts *counts)
{
	printf("%s_exact_mismatches=%d\n", prefix, counts->exact_mismatches);
	printf("%s_packed_mismatches=%d\n", prefix, counts->packed_mismatches);
	printf("%s_non_modq_mismatches=%d\n", prefix,
	       counts->non_modq_mismatches);
}

static void check_case(const char *label, const int16_t a[4],
                       const int16_t b[4], const int16_t c[4],
                       int16_t lambda, struct range_tracker *range,
                       struct model_counts *counts, int print_limit)
{
	int32_t p[4];

	p_model_from_quartic(p, a, b, lambda);
	for (int i = 0; i < 4; i++) {
		const int16_t current =
			current_add32_finalizer_from_p(p[i], c[i]);
		const int16_t candidate =
			candidate_direct32_from_p(p[i], c[i]);
		const uint16_t current_packed =
			pack_coeff_contract(current);
		const uint16_t candidate_packed =
			pack_coeff_contract(candidate);
		const int32_t pc = p[i] + (int32_t)c[i];

		update_range(range, p[i], pc);
		if (current != candidate) {
			if (counts->exact_mismatches < print_limit)
				printf("%s exact mismatch coeff=%d P=%d c=%d "
				       "P+c=%d current=%d candidate=%d "
				       "current_packed=%u candidate_packed=%u "
				       "same_modq=%d\n",
				       label, i, p[i], c[i], pc,
				       current, candidate,
				       current_packed, candidate_packed,
				       same_modq(current, candidate));
			counts->exact_mismatches++;
		}
		if (!same_modq(current, candidate)) {
			if (counts->non_modq_mismatches < print_limit)
				printf("%s non-modq mismatch coeff=%d P=%d "
				       "c=%d P+c=%d current=%d candidate=%d\n",
				       label, i, p[i], c[i], pc,
				       current, candidate);
			counts->non_modq_mismatches++;
		}
		if (current_packed != candidate_packed) {
			if (counts->packed_mismatches < print_limit)
				printf("%s packed mismatch coeff=%d P=%d "
				       "c=%d P+c=%d current=%d candidate=%d "
				       "current_packed=%u candidate_packed=%u\n",
				       label, i, p[i], c[i], pc,
				       current, candidate, current_packed,
				       candidate_packed);
			counts->packed_mismatches++;
		}
	}
}

static int16_t random_centered(uint32_t *state)
{
	const uint32_t x = next_u32(state);
	return (int16_t)((int)(x % NTRUPLUS_Q) - GT_DIRECT32_CENTER_BOUND);
}

static struct model_counts run_random_checks(struct range_tracker *range)
{
	uint32_t state = 1;
	struct model_counts counts = { 0, 0, 0 };

	for (int iter = 0; iter < 200000; iter++) {
		int16_t a[4], b[4], c[4];
		int16_t lambda = random_centered(&state);

		for (int i = 0; i < 4; i++) {
			a[i] = random_centered(&state);
			b[i] = random_centered(&state);
			c[i] = random_centered(&state);
		}
		check_case("random_centered", a, b, c, lambda, range,
		           &counts,
		           counts.exact_mismatches == 0 &&
		           counts.packed_mismatches == 0 ? 8 : 0);
	}

	print_counts("direct32_random_centered", &counts);
	return counts;
}

static struct model_counts run_edge_checks(struct range_tracker *range)
{
	static const int16_t vals[] = {
		0, 1, -1,
		GT_DIRECT32_CENTER_BOUND,
		-GT_DIRECT32_CENTER_BOUND,
		(int16_t)(GT_DIRECT32_CENTER_BOUND - 1),
		(int16_t)(-GT_DIRECT32_CENTER_BOUND + 1),
		NTRUPLUS_Q - 1,
		-(NTRUPLUS_Q - 1)
	};
	const int nvals = (int)(sizeof(vals) / sizeof(vals[0]));
	struct model_counts counts = { 0, 0, 0 };

	for (int shift = 0; shift < nvals; shift++) {
		int16_t a[4], b[4], c[4];
		const int16_t lambda = vals[shift];

		for (int i = 0; i < 4; i++) {
			a[i] = vals[(shift + i) % nvals];
			b[i] = vals[(shift + 2 * i + 1) % nvals];
			c[i] = vals[(shift + 3 * i + 2) % nvals];
		}
		check_case("edge", a, b, c, lambda, range, &counts,
		           counts.exact_mismatches == 0 &&
		           counts.packed_mismatches == 0 ? 8 : 0);
	}

	print_counts("direct32_edge", &counts);
	return counts;
}

static struct model_counts run_ambiguity_check(void)
{
	struct model_counts counts = { 0, 0, 0 };

	for (int pc = -2 * NTRUPLUS_Q; pc <= 2 * NTRUPLUS_Q; pc++) {
		int have = 0;
		int16_t first = 0;
		uint16_t first_packed = 0;

		for (int c = -GT_DIRECT32_CENTER_BOUND;
		     c <= GT_DIRECT32_CENTER_BOUND; c += 17) {
			const int p = pc - c;
			const int16_t out =
				current_add32_finalizer_from_p(p, (int16_t)c);
			const uint16_t out_packed = pack_coeff_contract(out);

			if (!have) {
				first = out;
				first_packed = out_packed;
				have = 1;
			} else if (out != first) {
				if (counts.exact_mismatches < 8)
					printf("direct32_exact_ambiguous_pc=%d "
					       "first=%d other=%d c=%d p=%d\n",
					       pc, first, out, c, p);
				counts.exact_mismatches++;
				if (out_packed != first_packed) {
					if (counts.packed_mismatches < 8)
						printf("direct32_packed_ambiguous_pc=%d "
						       "first=%u other=%u c=%d p=%d\n",
						       pc, first_packed, out_packed,
						       c, p);
					counts.packed_mismatches++;
					break;
				}
			}
		}
	}

	print_counts("direct32_ambiguous_pc", &counts);
	return counts;
}

static struct model_counts run_existing_lambda_checks(struct range_tracker *range)
{
	uint32_t state = 123;
	struct model_counts counts = { 0, 0, 0 };

	for (int branch = 0; branch < 2; branch++) {
		for (int physical_j = 0; physical_j < 96; physical_j++) {
			for (int iter = 0; iter < 64; iter++) {
				int16_t a[4], b[4], c[4];
				const int16_t lambda =
					gt_rowbitrev_lambda[branch][physical_j];

				for (int i = 0; i < 4; i++) {
					a[i] = random_centered(&state);
					b[i] = random_centered(&state);
					c[i] = random_centered(&state);
				}
				check_case("gt_lambda_random", a, b, c,
				           lambda, range, &counts,
				           counts.exact_mismatches == 0 &&
				           counts.packed_mismatches == 0 ? 8 : 0);
			}
		}
	}

	print_counts("direct32_gt_lambda_random", &counts);
	return counts;
}

static void print_range(const struct range_tracker *range)
{
	printf("direct32_observed_P_min=%lld\n", (long long)range->min_p);
	printf("direct32_observed_P_max=%lld\n", (long long)range->max_p);
	printf("direct32_observed_abs_P_max=%lld\n",
	       (long long)range->max_abs_p);
	printf("direct32_observed_P_plus_c_min=%lld\n",
	       (long long)range->min_pc);
	printf("direct32_observed_P_plus_c_max=%lld\n",
	       (long long)range->max_pc);
	printf("direct32_observed_abs_P_plus_c_max=%lld\n",
	       (long long)range->max_abs_pc);
	printf("direct32_int32_margin_P_plus_c=%lld\n",
	       (long long)INT_MAX - (long long)range->max_abs_pc);
}

static void print_symbolic_range_bound(void)
{
	const int64_t b = GT_DIRECT32_CENTER_BOUND;
	const int64_t w_bound = NTRUPLUS_Q - 1;
	const int64_t lambda_bound = GT_DIRECT32_CENTER_BOUND;
	const int64_t p0_bound = w_bound * lambda_bound + b * b;
	const int64_t p1_bound = w_bound * lambda_bound + 2 * b * b;
	const int64_t p2_bound = w_bound * lambda_bound + 3 * b * b;
	const int64_t p3_bound = 4 * b * b;
	int64_t p_bound = p0_bound;

	if (p1_bound > p_bound)
		p_bound = p1_bound;
	if (p2_bound > p_bound)
		p_bound = p2_bound;
	if (p3_bound > p_bound)
		p_bound = p3_bound;

	printf("direct32_symbolic_w_bound=%lld\n", (long long)w_bound);
	printf("direct32_symbolic_P0_bound=%lld\n", (long long)p0_bound);
	printf("direct32_symbolic_P1_bound=%lld\n", (long long)p1_bound);
	printf("direct32_symbolic_P2_bound=%lld\n", (long long)p2_bound);
	printf("direct32_symbolic_P3_bound=%lld\n", (long long)p3_bound);
	printf("direct32_symbolic_P_plus_c_bound=%lld\n",
	       (long long)(p_bound + b));
	printf("direct32_symbolic_int32_safe=%d\n",
	       p_bound + b <= INT_MAX);
}

int main(void)
{
	struct range_tracker range;
	struct model_counts total = { 0, 0, 0 };
	struct model_counts counts;
	struct model_counts ambiguous;

	init_range(&range);
	print_symbolic_range_bound();

	counts = run_random_checks(&range);
	add_counts(&total, &counts);
	counts = run_existing_lambda_checks(&range);
	add_counts(&total, &counts);
	counts = run_edge_checks(&range);
	add_counts(&total, &counts);
	ambiguous = run_ambiguity_check();
	print_range(&range);

	print_counts("direct32_total", &total);
	print_counts("direct32_total_ambiguous_pc", &ambiguous);
	if (total.packed_mismatches != 0 ||
	    total.non_modq_mismatches != 0 ||
	    ambiguous.packed_mismatches != 0) {
		printf("gt_basemul_add_direct32_model: not_byte_equivalent\n");
		return 1;
	}

	printf("gt_basemul_add_direct32_model: byte_equivalent\n");
	return 0;
}
