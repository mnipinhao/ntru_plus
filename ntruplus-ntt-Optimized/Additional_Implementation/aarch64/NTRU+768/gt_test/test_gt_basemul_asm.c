#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"

#define RANDOM_TESTS 32

void poly_basemul_gt_ref(poly *r, const poly *a, const poly *b);
void poly_basemul_add_gt_ref(poly *r, const poly *a, const poly *b,
                             const poly *c);

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

static void fill_random(poly *a, uint32_t seed)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		a->coeffs[i] =
			(int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) -
			          NTRUPLUS_Q);
	}
}

static void fill_edge(poly *a, int pattern)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		switch ((i + pattern) & 7)
		{
		case 0:
			a->coeffs[i] = 0;
			break;
		case 1:
			a->coeffs[i] = 1;
			break;
		case 2:
			a->coeffs[i] = -1;
			break;
		case 3:
			a->coeffs[i] = NTRUPLUS_Q - 1;
			break;
		case 4:
			a->coeffs[i] = -(NTRUPLUS_Q - 1);
			break;
		case 5:
			a->coeffs[i] = NTRUPLUS_Q / 2;
			break;
		case 6:
			a->coeffs[i] = -NTRUPLUS_Q / 2;
			break;
		default:
			a->coeffs[i] = (int16_t)(NTRUPLUS_Q + 127);
			break;
		}
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

static int compare_exact(const char *label, const poly *got, const poly *want)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (got->coeffs[i] != want->coeffs[i])
		{
			printf("%s exact mismatch at %d: got=%d want=%d mod_equal=%d\n",
			       label,
			       i,
			       got->coeffs[i],
			       want->coeffs[i],
			       equal_modq(got->coeffs[i], want->coeffs[i]));
			return 0;
		}
	}

	return 1;
}

static int compare_modq(const char *label, const poly *got, const poly *want)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!equal_modq(got->coeffs[i], want->coeffs[i]))
		{
			printf("%s mod-q mismatch at %d: got=%d want=%d\n",
			       label, i, got->coeffs[i], want->coeffs[i]);
			return 0;
		}
	}

	return 1;
}

static int check_impulse_exact(void)
{
	for (int branch = 0; branch < 2; branch++)
	{
		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			char label[80];
			poly a = {0};
			poly b = {0};
			poly got;
			poly want;
			const int pos = branch * (NTRUPLUS_N / 2) + 4 * physical_j;

			a.coeffs[pos + 1] = 1;
			b.coeffs[pos + 3] = 1;

			poly_basemul(&got, &a, &b);
			poly_basemul_gt_ref(&want, &a, &b);

			snprintf(label, sizeof(label),
			         "GT basemul impulse branch=%d physical_j=%d",
			         branch, physical_j);
			if (!compare_exact(label, &got, &want))
			{
				return 0;
			}
		}
	}

	printf("GT ASM basemul physical-order impulse exact checks ok\n");
	return 1;
}

static int check_random_modq(void)
{
	for (uint32_t seed = 0; seed < RANDOM_TESTS; seed++)
	{
		char label[64];
		poly a;
		poly b;
		poly got;
		poly want;

		fill_random(&a, 0x6a09e667u + seed);
		fill_random(&b, 0xbb67ae85u + seed);

		poly_basemul(&got, &a, &b);
		poly_basemul_gt_ref(&want, &a, &b);

		snprintf(label, sizeof(label), "GT basemul random seed=%u", seed);
		if (!compare_modq(label, &got, &want))
		{
			return 0;
		}
	}

	printf("GT ASM basemul random mod-q checks ok\n");
	return 1;
}

static int check_edge_modq(void)
{
	for (int pattern = 0; pattern < 8; pattern++)
	{
		char label[64];
		poly a;
		poly b;
		poly got;
		poly want;

		fill_edge(&a, pattern);
		fill_edge(&b, pattern + 3);

		poly_basemul(&got, &a, &b);
		poly_basemul_gt_ref(&want, &a, &b);

		snprintf(label, sizeof(label), "GT basemul edge pattern=%d", pattern);
		if (!compare_modq(label, &got, &want))
		{
			return 0;
		}
	}

	printf("GT ASM basemul edge mod-q checks ok\n");
	return 1;
}

static int check_ntt_product_roundtrip(void)
{
	for (uint32_t seed = 0; seed < RANDOM_TESTS; seed++)
	{
		char label[80];
		poly a;
		poly b;
		poly want;
		poly ntt_a;
		poly ntt_b;
		poly ntt_c;
		poly got;

		fill_random(&a, 0x3c6ef372u + seed);
		fill_random(&b, 0xa54ff53au + seed);

		schoolbook_mul_reference(&want, &a, &b);
		poly_ntt(&ntt_a, &a);
		poly_ntt(&ntt_b, &b);
		poly_basemul(&ntt_c, &ntt_a, &ntt_b);
		poly_invntt(&got, &ntt_c);

		snprintf(label, sizeof(label), "GT ASM basemul product seed=%u", seed);
		if (!compare_modq(label, &got, &want))
		{
			return 0;
		}
	}

	printf("GT ASM basemul NTT product roundtrip checks ok\n");
	return 1;
}

static int check_basemul_add_modq(void)
{
	for (uint32_t seed = 0; seed < RANDOM_TESTS; seed++)
	{
		char label[80];
		poly a;
		poly b;
		poly c;
		poly got;
		poly want;

		fill_random(&a, 0x510e527fu + seed);
		fill_random(&b, 0x9b05688cu + seed);
		fill_random(&c, 0x1f83d9abu + seed);

		poly_basemul_add(&got, &a, &b, &c);
		poly_basemul_add_gt_ref(&want, &a, &b, &c);

		snprintf(label, sizeof(label), "GT basemul_add random seed=%u", seed);
		if (!compare_modq(label, &got, &want))
		{
			return 0;
		}
	}

	printf("GT ASM basemul_add random mod-q checks ok\n");
	return 1;
}

static int check_ntt_product_add_roundtrip(void)
{
	for (uint32_t seed = 0; seed < RANDOM_TESTS; seed++)
	{
		char label[80];
		poly a;
		poly b;
		poly c;
		poly want;
		poly ntt_a;
		poly ntt_b;
		poly ntt_c;
		poly ntt_out;
		poly got;

		fill_random(&a, 0x5be0cd19u + seed);
		fill_random(&b, 0x137e2179u + seed);
		fill_random(&c, 0x9966cc41u + seed);

		schoolbook_mul_reference(&want, &a, &b);
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			want.coeffs[i] = (int16_t)centered_modq(
			    (int64_t)want.coeffs[i] + c.coeffs[i]);
		}

		poly_ntt(&ntt_a, &a);
		poly_ntt(&ntt_b, &b);
		poly_ntt(&ntt_c, &c);
		poly_basemul_add(&ntt_out, &ntt_a, &ntt_b, &ntt_c);
		poly_invntt(&got, &ntt_out);

		snprintf(label, sizeof(label), "GT ASM basemul_add product seed=%u", seed);
		if (!compare_modq(label, &got, &want))
		{
			return 0;
		}
	}

	printf("GT ASM basemul_add NTT product roundtrip checks ok\n");
	return 1;
}

int main(void)
{
	int ok = 1;

	ok &= check_impulse_exact();
	ok &= check_random_modq();
	ok &= check_edge_modq();
	ok &= check_ntt_product_roundtrip();
	ok &= check_basemul_add_modq();
	ok &= check_ntt_product_add_roundtrip();

	return ok ? 0 : 1;
}
