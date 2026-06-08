#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "ntt.h"
#include "poly.h"

#define RANDOM_TESTS 16

#ifdef TEST_GT_BASE_USE_ABI
#define poly_basemul_gt_ref poly_basemul
#define poly_basemul_add_gt_ref poly_basemul_add
#define poly_baseinv_gt_ref poly_baseinv
#else
void poly_basemul_gt_ref(poly *r, const poly *a, const poly *b);
void poly_basemul_add_gt_ref(poly *r, const poly *a, const poly *b,
                             const poly *c);
int poly_baseinv_gt_ref(poly *r, const poly *a);
#endif

#define NTRUPLUS_QINV 12929

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

static int16_t s16(uint16_t a)
{
	return (int16_t)a;
}

static int16_t montgomery_reduce(int32_t a)
{
	int16_t t;

	t = s16((uint16_t)a * NTRUPLUS_QINV);
	t = s16((a - (int32_t)t * NTRUPLUS_Q) >> 16);
	return t;
}

static int normal_from_mont(int16_t a)
{
	return modq(montgomery_reduce(a));
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

static void fill_random(poly *a, uint32_t seed)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		a->coeffs[i] =
			(int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) -
			          NTRUPLUS_Q);
	}
}

static void schoolbook_mul_reference(poly *r, const poly *a, const poly *b)
{
	int64_t tmp[2 * NTRUPLUS_N - 1];

	memset(tmp, 0, sizeof(tmp));

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		for (int j = 0; j < NTRUPLUS_N; j++)
		{
			tmp[i + j] += (int64_t)a->coeffs[i] * b->coeffs[j];
		}
	}

	/* NTRU+768 works modulo X^768 - X^384 + 1, so X^768 = X^384 - 1. */
	for (int i = 2 * NTRUPLUS_N - 2; i >= NTRUPLUS_N; i--)
	{
		const int64_t c = tmp[i];

		tmp[i - NTRUPLUS_N / 2] += c;
		tmp[i - NTRUPLUS_N] -= c;
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		r->coeffs[i] = (int16_t)centered_modq(tmp[i]);
	}
}

static int compare_poly(const char *label, const poly *got, const poly *want)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!equal_modq(got->coeffs[i], want->coeffs[i]))
		{
			printf("%s mismatch at %d: got=%d want=%d\n",
			       label, i, got->coeffs[i], want->coeffs[i]);
			return 0;
		}
	}

	return 1;
}

static void quartic_mul_plain(int16_t out[4], const int16_t a[4],
                              const int16_t b[4], int lambda)
{
	const int64_t c0 = (int64_t)a[0] * b[0] +
	                   (int64_t)lambda *
	                       ((int64_t)a[1] * b[3] +
	                        (int64_t)a[2] * b[2] +
	                        (int64_t)a[3] * b[1]);
	const int64_t c1 = (int64_t)a[0] * b[1] +
	                   (int64_t)a[1] * b[0] +
	                   (int64_t)lambda *
	                       ((int64_t)a[2] * b[3] +
	                        (int64_t)a[3] * b[2]);
	const int64_t c2 = (int64_t)a[0] * b[2] +
	                   (int64_t)a[1] * b[1] +
	                   (int64_t)a[2] * b[0] +
	                   (int64_t)lambda * a[3] * b[3];
	const int64_t c3 = (int64_t)a[0] * b[3] +
	                   (int64_t)a[1] * b[2] +
	                   (int64_t)a[2] * b[1] +
	                   (int64_t)a[3] * b[0];

	out[0] = (int16_t)centered_modq(c0);
	out[1] = (int16_t)centered_modq(c1);
	out[2] = (int16_t)centered_modq(c2);
	out[3] = (int16_t)centered_modq(c3);
}

static int check_quartic_product_reference(void)
{
	for (int branch = 0; branch < 2; branch++)
	{
		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			poly a = {0};
			poly b = {0};
			poly got = {0};
			int16_t want[4];
			const int pos = branch * (NTRUPLUS_N / 2) + 4 * physical_j;
			uint32_t seed = 0x9e3779b9u + 257u * branch + 17u * physical_j;

			for (int lane = 0; lane < 4; lane++)
			{
				a.coeffs[pos + lane] =
					(int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) -
					          NTRUPLUS_Q);
				b.coeffs[pos + lane] =
					(int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) -
					          NTRUPLUS_Q);
			}

			poly_basemul_gt_ref(&got, &a, &b);
			quartic_mul_plain(want, a.coeffs + pos, b.coeffs + pos,
			                  normal_from_mont(gt_rowbitrev_lambda[branch][physical_j]));

			for (int lane = 0; lane < 4; lane++)
			{
				if (!equal_modq(got.coeffs[pos + lane], want[lane]))
				{
					printf("quartic ref mismatch branch=%d physical_j=%d lane=%d\n",
					       branch, physical_j, lane);
					return 0;
				}
			}
		}
	}

	printf("GT quartic product reference checks ok\n");
	return 1;
}

static int check_lambda_impulses(void)
{
	for (int branch = 0; branch < 2; branch++)
	{
		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			poly a = {0};
			poly b = {0};
			poly got = {0};
			const int pos = branch * (NTRUPLUS_N / 2) + 4 * physical_j;
			const int lambda =
				normal_from_mont(gt_rowbitrev_lambda[branch][physical_j]);

			a.coeffs[pos + 1] = 1;
			b.coeffs[pos + 3] = 1;
			poly_basemul_gt_ref(&got, &a, &b);

			if (!equal_modq(got.coeffs[pos], (int16_t)lambda))
			{
				printf("lambda impulse mismatch branch=%d physical_j=%d "
				       "got=%d want=%d\n",
				       branch, physical_j, got.coeffs[pos], lambda);
				return 0;
			}
		}
	}

	printf("GT lambda physical-order impulse checks ok\n");
	return 1;
}

static int check_basemul_add(void)
{
	for (uint32_t seed = 0; seed < RANDOM_TESTS; seed++)
	{
		poly a;
		poly b;
		poly c;
		poly prod;
		poly add;

		fill_random(&a, 0x11111111u + seed);
		fill_random(&b, 0x22222222u + seed);
		fill_random(&c, 0x33333333u + seed);

		poly_basemul_gt_ref(&prod, &a, &b);
		poly_basemul_add_gt_ref(&add, &a, &b, &c);

		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			if (!equal_modq(add.coeffs[i], prod.coeffs[i] + c.coeffs[i]))
			{
				printf("GT basemul_add mismatch seed=%u i=%d\n", seed, i);
				return 0;
			}
		}
	}

	printf("GT basemul_add reference checks ok\n");
	return 1;
}

static int check_ntt_product_roundtrip(void)
{
	for (uint32_t seed = 0; seed < RANDOM_TESTS; seed++)
	{
		char label[64];
		poly a;
		poly b;
		poly want;
		poly ntt_a;
		poly ntt_b;
		poly ntt_c;
		poly got;

		fill_random(&a, 0x44444444u + seed);
		fill_random(&b, 0x55555555u + seed);

		schoolbook_mul_reference(&want, &a, &b);
		ntt_gt_rowbitrevlayout(ntt_a.coeffs, a.coeffs);
		ntt_gt_rowbitrevlayout(ntt_b.coeffs, b.coeffs);
		poly_basemul_gt_ref(&ntt_c, &ntt_a, &ntt_b);
		invntt_gt_rowbitrevlayout(got.coeffs, ntt_c.coeffs);

		snprintf(label, sizeof(label), "GT product roundtrip seed=%u", seed);
		if (!compare_poly(label, &got, &want))
		{
			return 0;
		}
	}

	printf("GT NTT/basemul/invNTT product checks ok\n");
	return 1;
}

static int check_baseinv(void)
{
	poly a = {0};
	poly inv;
	poly prod;

	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int pos = branch_start + 4 * physical_j;

			a.coeffs[pos] = 1;
		}
	}

	if (poly_baseinv_gt_ref(&inv, &a))
	{
		printf("GT baseinv reference unexpectedly failed\n");
		return 0;
	}

	poly_basemul_gt_ref(&prod, &a, &inv);

	if (!compare_poly("GT baseinv identity", &prod, &a))
	{
		return 0;
	}

	printf("GT baseinv reference identity check ok\n");
	return 1;
}

int main(void)
{
	int ok = 1;

	ok &= check_lambda_impulses();
	ok &= check_quartic_product_reference();
	ok &= check_basemul_add();
	ok &= check_ntt_product_roundtrip();
	ok &= check_baseinv();

	return ok ? 0 : 1;
}
