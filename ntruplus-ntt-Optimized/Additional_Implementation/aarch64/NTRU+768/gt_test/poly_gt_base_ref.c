#include <stdint.h>
#include <string.h>

#include "ntt.h"
#include "poly.h"

/*
 * GT row-bitrev reference base operations.
 *
 * Layout contract:
 *   coeff[branch*384 + 4*physical_j + lane]
 *
 * For each branch b and physical block j, the quartic product ring is
 *   Z_q[X] / (X^4 - lambda_b[j])
 * with lambda read from gt_rowbitrev_lambda[b][j] in physical row-bitrev
 * block order.  The lambda values are Montgomery-form constants consumed by
 * ntt.c's scalar basemul/baseinv helpers.
 *
 * This file intentionally provides scalar C reference symbols matching the
 * KEM ABI.  It is not an optimized assembly replacement for asm/stock/base.s.
 */
void poly_basemul_gt_ref(poly *r, const poly *a, const poly *b);
void poly_basemul_add_gt_ref(poly *r, const poly *a, const poly *b,
                             const poly *c);
int poly_baseinv_gt_ref(poly *r, const poly *a);

void poly_basemul_gt_ref(poly *r, const poly *a, const poly *b)
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int pos = branch_start + 4 * physical_j;

			basemul(r->coeffs + pos, a->coeffs + pos, b->coeffs + pos,
			        gt_rowbitrev_lambda[branch][physical_j]);
		}
	}
}

void poly_basemul_add_gt_ref(poly *r, const poly *a, const poly *b,
                             const poly *c)
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int pos = branch_start + 4 * physical_j;

			basemul_add(r->coeffs + pos,
			            a->coeffs + pos,
			            b->coeffs + pos,
			            c->coeffs + pos,
			            gt_rowbitrev_lambda[branch][physical_j]);
		}
	}
}

int poly_baseinv_gt_ref(poly *r, const poly *a)
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int pos = branch_start + 4 * physical_j;

			if (baseinv(r->coeffs + pos, a->coeffs + pos,
			            gt_rowbitrev_lambda[branch][physical_j]))
			{
				memset(r->coeffs, 0, sizeof(r->coeffs));
				return 1;
			}
		}
	}

	return 0;
}

#if !defined(GT_BASE_REF_NO_ABI_WRAPPERS) && \
	!defined(GT_BASE_REF_ONLY_BASEINV_ABI)
void poly_basemul(poly *r, const poly *a, const poly *b)
{
	poly_basemul_gt_ref(r, a, b);
}

void poly_basemul_add(poly *r, const poly *a, const poly *b, const poly *c)
{
	poly_basemul_add_gt_ref(r, a, b, c);
}
#endif

#ifndef GT_BASE_REF_NO_ABI_WRAPPERS
int poly_baseinv(poly *r, const poly *a)
{
	return poly_baseinv_gt_ref(r, a);
}
#endif
