#include <limits.h>
#include <stdint.h>
#include <stdio.h>

#include "ntt.h"
#include "params.h"
#include "poly.h"

#define GT_ADD32_QINV 12929
#define GT_ADD32_R -147
#define GT_ADD32_RSQ 867
#define GT_ADD32_CENTER_BOUND ((NTRUPLUS_Q - 1) / 2)

/*
 * This file is a contract test for the proposed basemul_add32 direction.
 *
 * There are two different "lazy" meanings that must not be mixed:
 *
 * 1. Strict raw quartic dot product:
 *      out = c + a*b in Z_q[X]/(X^4 - lambda)
 *    This can be written as direct int64 dot products, and is checked below
 *    against scalar basemul_add().  It is not a safe int32 plan for the
 *    current GT layout because wrapped terms are multiplied by lambda.
 *
 * 2. R^-1 product accumulator:
 *      raw_i = current basemul inner result before the final R^2 correction
 *      out = Mont(c*R + (raw_0 + raw_1 + ...)*R^2)
 *    This still uses the existing internal Montgomery reductions needed by
 *    X^4-lambda, but delays product finalization/add reduction.  This is the
 *    acc32 route that is range-safe for KEM-sized accumulation counts.
 */

static int16_t centered_modq_i64(int64_t x)
{
	x %= NTRUPLUS_Q;
	if (x > NTRUPLUS_Q / 2)
		x -= NTRUPLUS_Q;
	if (x < -NTRUPLUS_Q / 2)
		x += NTRUPLUS_Q;
	return (int16_t)x;
}

static int16_t centered_modq_u32(uint32_t x)
{
	int16_t r = (int16_t)(x % NTRUPLUS_Q);

	if (r > NTRUPLUS_Q / 2)
		r -= NTRUPLUS_Q;
	return r;
}

static int same_modq(int16_t a, int16_t b)
{
	int32_t diff = (int32_t)a - b;

	diff %= NTRUPLUS_Q;
	if (diff < 0)
		diff += NTRUPLUS_Q;
	return diff == 0;
}

static int compare_poly_modq(const char *label, const poly *want,
                             const poly *got)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!same_modq(want->coeffs[i], got->coeffs[i]))
		{
			printf("%s mismatch at %d: want=%d got=%d\n",
			       label, i, want->coeffs[i], got->coeffs[i]);
			return 1;
		}
	}

	return 0;
}

static int16_t montgomery_reduce_ref(int32_t a)
{
	int16_t t;

	t = (int16_t)a * GT_ADD32_QINV;
	t = (int16_t)((a - (int32_t)t * NTRUPLUS_Q) >> 16);
	return t;
}

static int16_t lambda_from_montgomery(int16_t zeta_mont)
{
	return montgomery_reduce_ref(zeta_mont);
}

static void fill_poly(poly *a, uint32_t seed)
{
	uint32_t x = seed ? seed : 1;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		x = x * 1664525u + 1013904223u;
		a->coeffs[i] = centered_modq_u32(x);
	}
}

static void fill_boundaries(poly *a, int variant)
{
	static const int16_t vals[] = {
		0, 1, -1, GT_ADD32_CENTER_BOUND, -GT_ADD32_CENTER_BOUND,
		NTRUPLUS_Q - 1, -(NTRUPLUS_Q - 1)
	};
	const int nvals = (int)(sizeof(vals) / sizeof(vals[0]));

	for (int i = 0; i < NTRUPLUS_N; i++)
		a->coeffs[i] = vals[(i + variant) % nvals];
}

static void basemul_raw_rminus1_ref(int16_t r[4], const int16_t a[4],
                                    const int16_t b[4], int16_t zeta)
{
	r[0] = montgomery_reduce_ref((int32_t)a[1] * b[3] +
	                             (int32_t)a[2] * b[2] +
	                             (int32_t)a[3] * b[1]);
	r[1] = montgomery_reduce_ref((int32_t)a[2] * b[3] +
	                             (int32_t)a[3] * b[2]);
	r[2] = montgomery_reduce_ref((int32_t)a[3] * b[3]);

	r[0] = montgomery_reduce_ref((int32_t)r[0] * zeta +
	                             (int32_t)a[0] * b[0]);
	r[1] = montgomery_reduce_ref((int32_t)r[1] * zeta +
	                             (int32_t)a[0] * b[1] +
	                             (int32_t)a[1] * b[0]);
	r[2] = montgomery_reduce_ref((int32_t)r[2] * zeta +
	                             (int32_t)a[0] * b[2] +
	                             (int32_t)a[1] * b[1] +
	                             (int32_t)a[2] * b[0]);
	r[3] = montgomery_reduce_ref((int32_t)a[0] * b[3] +
	                             (int32_t)a[1] * b[2] +
	                             (int32_t)a[2] * b[1] +
	                             (int32_t)a[3] * b[0]);
}

static void basemul_add_direct_i64_ref(int16_t r[4], const int16_t a[4],
                                       const int16_t b[4],
                                       const int16_t c[4],
                                       int16_t zeta_mont)
{
	const int16_t lambda = lambda_from_montgomery(zeta_mont);
	int64_t acc[4];

	acc[0] = (int64_t)a[0] * b[0] +
	         (int64_t)lambda *
	         ((int64_t)a[1] * b[3] +
	          (int64_t)a[2] * b[2] +
	          (int64_t)a[3] * b[1]) +
	         c[0];
	acc[1] = (int64_t)a[0] * b[1] +
	         (int64_t)a[1] * b[0] +
	         (int64_t)lambda *
	         ((int64_t)a[2] * b[3] +
	          (int64_t)a[3] * b[2]) +
	         c[1];
	acc[2] = (int64_t)a[0] * b[2] +
	         (int64_t)a[1] * b[1] +
	         (int64_t)a[2] * b[0] +
	         (int64_t)lambda * ((int64_t)a[3] * b[3]) +
	         c[2];
	acc[3] = (int64_t)a[0] * b[3] +
	         (int64_t)a[1] * b[2] +
	         (int64_t)a[2] * b[1] +
	         (int64_t)a[3] * b[0] +
	         c[3];

	for (int i = 0; i < 4; i++)
		r[i] = centered_modq_i64(acc[i]);
}

static void basemul_add32_rminus1_finalize_ref(int16_t r[4],
                                               const int32_t acc_raw[4],
                                               const int16_t c[4])
{
	for (int i = 0; i < 4; i++)
	{
		const int32_t prefinal =
			(int32_t)c[i] * GT_ADD32_R + acc_raw[i] * GT_ADD32_RSQ;
		r[i] = montgomery_reduce_ref(prefinal);
	}
}

static void poly_basemul_add_direct_i64_ref(poly *r, const poly *a,
                                            const poly *b, const poly *c)
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int pos = branch_start + 4 * physical_j;

			basemul_add_direct_i64_ref(r->coeffs + pos,
			                           a->coeffs + pos,
			                           b->coeffs + pos,
			                           c->coeffs + pos,
			                           gt_rowbitrev_lambda[branch][physical_j]);
		}
	}
}

static void poly_basemul_add32_rminus1_k1_ref(poly *r, const poly *a,
                                              const poly *b, const poly *c)
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int pos = branch_start + 4 * physical_j;
			int16_t raw[4];
			int32_t acc[4];

			basemul_raw_rminus1_ref(raw, a->coeffs + pos,
			                        b->coeffs + pos,
			                        gt_rowbitrev_lambda[branch][physical_j]);
			for (int i = 0; i < 4; i++)
				acc[i] = raw[i];
			basemul_add32_rminus1_finalize_ref(r->coeffs + pos,
			                                   acc, c->coeffs + pos);
		}
	}
}

static void poly_basemul_add32_rminus1_k2_ref(poly *r,
                                              const poly *a0, const poly *b0,
                                              const poly *a1, const poly *b1,
                                              const poly *c)
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int pos = branch_start + 4 * physical_j;
			int16_t raw0[4], raw1[4];
			int32_t acc[4];

			basemul_raw_rminus1_ref(raw0, a0->coeffs + pos,
			                        b0->coeffs + pos,
			                        gt_rowbitrev_lambda[branch][physical_j]);
			basemul_raw_rminus1_ref(raw1, a1->coeffs + pos,
			                        b1->coeffs + pos,
			                        gt_rowbitrev_lambda[branch][physical_j]);
			for (int i = 0; i < 4; i++)
				acc[i] = (int32_t)raw0[i] + raw1[i];
			basemul_add32_rminus1_finalize_ref(r->coeffs + pos,
			                                   acc, c->coeffs + pos);
		}
	}
}

static int run_equivalence_checks(void)
{
	poly a0, b0, a1, b1, c;
	poly want, got, tmp;

	fill_poly(&a0, 11);
	fill_poly(&b0, 22);
	fill_poly(&a1, 33);
	fill_poly(&b1, 44);
	fill_poly(&c, 55);

	poly_basemul_add_direct_i64_ref(&got, &a0, &b0, &c);
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int pos = branch_start + 4 * physical_j;

			basemul_add(want.coeffs + pos,
			            a0.coeffs + pos,
			            b0.coeffs + pos,
			            c.coeffs + pos,
			            gt_rowbitrev_lambda[branch][physical_j]);
		}
	}
	if (compare_poly_modq("direct_i64_k1", &want, &got))
		return 1;

	poly_basemul_add32_rminus1_k1_ref(&got, &a0, &b0, &c);
	if (compare_poly_modq("rminus1_add32_k1", &want, &got))
		return 1;

	poly_basemul_add32_rminus1_k1_ref(&tmp, &a0, &b0, &c);
	poly_basemul_add32_rminus1_k1_ref(&want, &a1, &b1, &tmp);
	poly_basemul_add32_rminus1_k2_ref(&got, &a0, &b0, &a1, &b1, &c);
	if (compare_poly_modq("rminus1_add32_k2", &want, &got))
		return 1;

	fill_boundaries(&a0, 0);
	fill_boundaries(&b0, 1);
	fill_boundaries(&a1, 2);
	fill_boundaries(&b1, 3);
	fill_boundaries(&c, 4);
	poly_basemul_add32_rminus1_k1_ref(&tmp, &a0, &b0, &c);
	poly_basemul_add32_rminus1_k1_ref(&want, &a1, &b1, &tmp);
	poly_basemul_add32_rminus1_k2_ref(&got, &a0, &b0, &a1, &b1, &c);
	if (compare_poly_modq("rminus1_add32_k2_boundary", &want, &got))
		return 1;

	return 0;
}

static int run_range_contract(void)
{
	const int64_t bq = GT_ADD32_CENTER_BOUND;
	const int64_t b_rowlazy = 27648;
	const int64_t blambda = GT_ADD32_CENTER_BOUND;
	const int64_t raw_normal_q =
		bq * bq + 3 * blambda * bq * bq + bq;
	const int64_t raw_normal_rowlazy =
		b_rowlazy * b_rowlazy +
		3 * blambda * b_rowlazy * b_rowlazy + bq;
	const int64_t first_dot_rowlazy =
		3 * b_rowlazy * b_rowlazy;
	const int64_t rminus1_raw_bound = NTRUPLUS_Q - 1;
	const int64_t rminus1_prefinal_k1 =
		bq * (-GT_ADD32_R) + rminus1_raw_bound * GT_ADD32_RSQ;
	const int64_t rminus1_prefinal_k2 =
		bq * (-GT_ADD32_R) + 2 * rminus1_raw_bound * GT_ADD32_RSQ;
	const int64_t rminus1_max_k =
		((int64_t)INT_MAX - bq * (-GT_ADD32_R)) /
		(rminus1_raw_bound * GT_ADD32_RSQ);

	printf("range_direct_q_centered_bound: %lld\n",
	       (long long)raw_normal_q);
	printf("range_direct_rowlazy_bound: %lld\n",
	       (long long)raw_normal_rowlazy);
	printf("range_first_dot_rowlazy_bound: %lld\n",
	       (long long)first_dot_rowlazy);
	printf("range_rminus1_prefinal_k1_bound: %lld\n",
	       (long long)rminus1_prefinal_k1);
	printf("range_rminus1_prefinal_k2_bound: %lld\n",
	       (long long)rminus1_prefinal_k2);
	printf("range_rminus1_max_products_int32_prefinal: %lld\n",
	       (long long)rminus1_max_k);

	if (raw_normal_q <= INT_MAX)
	{
		printf("unexpected: direct lambda raw q-sized path fits int32\n");
		return 1;
	}
	if (first_dot_rowlazy <= INT_MAX)
	{
		printf("unexpected: rowlazy first dot still fits int32\n");
		return 1;
	}
	if (rminus1_prefinal_k2 > INT_MAX || rminus1_max_k < 2)
	{
		printf("unexpected: R^-1 add32 K=2 prefinal exceeds int32\n");
		return 1;
	}

	return 0;
}

int main(void)
{
	if (run_equivalence_checks())
		return 1;
	if (run_range_contract())
		return 1;

	printf("gt_basemul_add32_ref_correctness: ok\n");
	printf("gt_basemul_add32_ref_contract: direct_raw_dot_needs_int64_or_extra_reduction\n");
	printf("gt_basemul_add32_ref_contract: rminus1_acc32_finalize_is_int32_safe_for_kem\n");
	return 0;
}
