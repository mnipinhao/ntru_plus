#include <stdint.h>

#include "ntt.h"
#include "params.h"
#include "poly.h"

#define GT_DIRECT32_QINV 12929

void poly_basemul_add_direct32_finalizer_prototype(poly *r,
                                                   const poly *a,
                                                   const poly *b,
                                                   const poly *c);

static int16_t montgomery_reduce_ref(int32_t x)
{
	int16_t t;

	t = (int16_t)x * GT_DIRECT32_QINV;
	t = (int16_t)((x - (int32_t)t * NTRUPLUS_Q) >> 16);
	return t;
}

static int16_t centered_modq_i32(int32_t x)
{
	x %= NTRUPLUS_Q;
	if (x > NTRUPLUS_Q / 2)
		x -= NTRUPLUS_Q;
	if (x < -NTRUPLUS_Q / 2)
		x += NTRUPLUS_Q;
	return (int16_t)x;
}

static void basemul_add_direct32_quartic(int16_t r[4],
                                         const int16_t a[4],
                                         const int16_t b[4],
                                         const int16_t c[4],
                                         int16_t lambda)
{
	int16_t w2;
	int16_t w1;
	int16_t w0;
	int32_t p0;
	int32_t p1;
	int32_t p2;
	int32_t p3;

	w2 = montgomery_reduce_ref((int32_t)a[3] * b[3]);
	w1 = montgomery_reduce_ref((int32_t)a[2] * b[3] +
	                           (int32_t)a[3] * b[2]);
	w0 = montgomery_reduce_ref((int32_t)a[1] * b[3] +
	                           (int32_t)a[2] * b[2] +
	                           (int32_t)a[3] * b[1]);

	p0 = (int32_t)w0 * lambda + (int32_t)a[0] * b[0];
	p1 = (int32_t)w1 * lambda +
	     (int32_t)a[0] * b[1] + (int32_t)a[1] * b[0];
	p2 = (int32_t)w2 * lambda +
	     (int32_t)a[0] * b[2] + (int32_t)a[1] * b[1] +
	     (int32_t)a[2] * b[0];
	p3 = (int32_t)a[0] * b[3] + (int32_t)a[1] * b[2] +
	     (int32_t)a[2] * b[1] + (int32_t)a[3] * b[0];

	r[0] = centered_modq_i32(p0 + c[0]);
	r[1] = centered_modq_i32(p1 + c[1]);
	r[2] = centered_modq_i32(p2 + c[2]);
	r[3] = centered_modq_i32(p3 + c[3]);
}

void poly_basemul_add_direct32_finalizer_prototype(poly *r,
                                                   const poly *a,
                                                   const poly *b,
                                                   const poly *c)
{
	for (int branch = 0; branch < 2; branch++) {
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++) {
			const int pos = branch_start + 4 * physical_j;
			const int16_t lambda =
				gt_rowbitrev_lambda[branch][physical_j];

			basemul_add_direct32_quartic(r->coeffs + pos,
			                             a->coeffs + pos,
			                             b->coeffs + pos,
			                             c->coeffs + pos,
			                             lambda);
		}
	}
}
