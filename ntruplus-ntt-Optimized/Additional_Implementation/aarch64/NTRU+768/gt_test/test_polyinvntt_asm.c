#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "ntt.h"
#include "poly.h"

#define RANDOM_TESTS 32

static int modq(int64_t a)
{
	int r = (int)(a % NTRUPLUS_Q);

	if (r < 0)
	{
		r += NTRUPLUS_Q;
	}

	return r;
}

static int equal_modq(int16_t a, int16_t b)
{
	return modq((int)a - (int)b) == 0;
}

static int scaled_equal_modq(const poly *got, const poly *want, int scale)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!equal_modq(got->coeffs[i], (int16_t)modq((int64_t)scale * want->coeffs[i])))
		{
			return 0;
		}
	}

	return 1;
}

static int compare_poly(const char *label, const poly *got, const poly *want)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!equal_modq(got->coeffs[i], want->coeffs[i]))
		{
			fprintf(stderr,
			        "%s mismatch at %d: got %d want %d (mod %d vs %d)\n",
			        label, i, got->coeffs[i], want->coeffs[i],
			        modq(got->coeffs[i]), modq(want->coeffs[i]));

			if (scaled_equal_modq(got, want, 96))
			{
				fprintf(stderr, "%s has residual scale factor 96\n", label);
			}
			else if (scaled_equal_modq(got, want, 192))
			{
				fprintf(stderr, "%s has residual scale factor 192\n", label);
			}

			return 0;
		}

#ifdef INVNTT_EXPECT_CENTERED_OUTPUT
		if (got->coeffs[i] < -(NTRUPLUS_Q / 2) ||
		    got->coeffs[i] > (NTRUPLUS_Q / 2))
		{
			fprintf(stderr,
			        "%s non-centered output at %d: got %d\n",
			        label, i, got->coeffs[i]);
			return 0;
		}
#endif
	}

	return 1;
}

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static void fill_zero(poly *a)
{
	memset(a->coeffs, 0, sizeof(a->coeffs));
}

static void fill_pattern(poly *a, const char *name, uint32_t seed)
{
	if (strcmp(name, "zero") == 0)
	{
		fill_zero(a);
		return;
	}

	if (strcmp(name, "one") == 0)
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a->coeffs[i] = 1;
		}
		return;
	}

	if (strcmp(name, "alternating_pm1") == 0)
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a->coeffs[i] = (i & 1) ? -1 : 1;
		}
		return;
	}

	if (strcmp(name, "centered_edges") == 0)
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a->coeffs[i] = (i & 1) ? -(NTRUPLUS_Q / 2) : (NTRUPLUS_Q / 2);
		}
		return;
	}

	if (strcmp(name, "lazy_edges") == 0)
	{
		static const int vals[] = {
			0, 1, -1,
			NTRUPLUS_Q - 1, -(NTRUPLUS_Q - 1),
			2 * (NTRUPLUS_Q - 1), -2 * (NTRUPLUS_Q - 1),
			3 * (NTRUPLUS_Q - 1), -3 * (NTRUPLUS_Q - 1),
			4 * (NTRUPLUS_Q - 1), -4 * (NTRUPLUS_Q - 1)
		};

		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a->coeffs[i] = (int16_t)vals[i % (int)(sizeof(vals) / sizeof(vals[0]))];
		}
		return;
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		a->coeffs[i] = (int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
	}
}

static void fill_impulse(poly *a, int pos, int16_t value)
{
	fill_zero(a);
	a->coeffs[pos] = value;
}

static void reference_inv(poly *r, const poly *a)
{
	invntt_gt_rowbitrevlayout_exact(r->coeffs, a->coeffs);
}

static int check_direct_inverse_compare(void)
{
	static const char *patterns[] = {
		"zero", "one", "alternating_pm1", "centered_edges", "lazy_edges", "random"
	};
	poly freq;
	poly got;
	poly want;

	for (unsigned i = 0; i < sizeof(patterns) / sizeof(patterns[0]); i++)
	{
		char label[96];

		fill_pattern(&freq, patterns[i], 0x12345678u + i);
		poly_invntt(&got, &freq);
		reference_inv(&want, &freq);

		snprintf(label, sizeof(label), "direct inverse %s", patterns[i]);
		if (!compare_poly(label, &got, &want))
		{
			return 0;
		}
	}

	for (int t = 0; t < RANDOM_TESTS; t++)
	{
		char label[96];

		fill_pattern(&freq, "random", 0x9e3779b9u + (uint32_t)t);
		poly_invntt(&got, &freq);
		reference_inv(&want, &freq);

		snprintf(label, sizeof(label), "direct inverse random %d", t);
		if (!compare_poly(label, &got, &want))
		{
			return 0;
		}
	}

	printf("C inverse vs ASM inverse direct-domain tests ok\n");
	return 1;
}

static int check_roundtrip_patterns(void)
{
	static const char *patterns[] = {
		"zero", "one", "alternating_pm1", "centered_edges", "lazy_edges", "random"
	};
	poly a;
	poly freq;
	poly got;

	for (unsigned i = 0; i < sizeof(patterns) / sizeof(patterns[0]); i++)
	{
		char label[96];

		fill_pattern(&a, patterns[i], 0xa5a5a5a5u + i);
		poly_ntt(&freq, &a);
		poly_invntt(&got, &freq);

		snprintf(label, sizeof(label), "roundtrip %s", patterns[i]);
		if (!compare_poly(label, &got, &a))
		{
			return 0;
		}
	}

	for (int t = 0; t < RANDOM_TESTS; t++)
	{
		char label[96];

		fill_pattern(&a, "random", 0x31415926u + (uint32_t)t);
		poly_ntt(&freq, &a);
		poly_invntt(&got, &freq);

		snprintf(label, sizeof(label), "roundtrip random %d", t);
		if (!compare_poly(label, &got, &a))
		{
			return 0;
		}
	}

	printf("poly_invntt(poly_ntt(a)) pattern/random tests ok\n");
	return 1;
}

static int check_impulses(void)
{
	poly a;
	poly freq;
	poly got;

	for (int pos = 0; pos < NTRUPLUS_N; pos++)
	{
		char label[96];
		int16_t value = (int16_t)(1 + (pos % 7));

		fill_impulse(&a, pos, value);
		poly_ntt(&freq, &a);
		poly_invntt(&got, &freq);

		snprintf(label, sizeof(label), "impulse %d", pos);
		if (!compare_poly(label, &got, &a))
		{
			return 0;
		}
	}

	printf("all-position impulse roundtrip tests ok\n");
	return 1;
}

static void schoolbook_mul_reference(poly *r, const poly *a, const poly *b)
{
	int64_t tmp[2*NTRUPLUS_N - 1];

	for (int i = 0; i < 2*NTRUPLUS_N - 1; i++)
	{
		tmp[i] = 0;
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		for (int j = 0; j < NTRUPLUS_N; j++)
		{
			tmp[i + j] += (int64_t)a->coeffs[i] * b->coeffs[j];
		}
	}

	/* NTRU+768 works modulo X^768 - X^384 + 1, so X^768 = X^384 - 1. */
	for (int i = 2*NTRUPLUS_N - 2; i >= NTRUPLUS_N; i--)
	{
		const int64_t c = tmp[i];

		tmp[i - NTRUPLUS_N/2] += c;
		tmp[i - NTRUPLUS_N] -= c;
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		r->coeffs[i] = (int16_t)modq(tmp[i]);
	}
}

static void rowbitrev_basemul_reference(poly *r, const poly *a, const poly *b)
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int pos = branch_start + 4*physical_j;

			basemul(r->coeffs + pos, a->coeffs + pos, b->coeffs + pos,
			        gt_rowbitrev_lambda[branch][physical_j]);
		}
	}
}

static int check_multiplication_roundtrip(void)
{
	poly a;
	poly b;
	poly schoolbook;
	poly ntt_a;
	poly ntt_b;
	poly ntt_c;
	poly got;

	for (int t = 0; t < 8; t++)
	{
		char label[96];

		fill_pattern(&a, "random", 0x10203040u + (uint32_t)t);
		fill_pattern(&b, "random", 0x90807060u + (uint32_t)t);

		schoolbook_mul_reference(&schoolbook, &a, &b);
		poly_ntt(&ntt_a, &a);
		poly_ntt(&ntt_b, &b);
		rowbitrev_basemul_reference(&ntt_c, &ntt_a, &ntt_b);
		poly_invntt(&got, &ntt_c);

		snprintf(label, sizeof(label), "multiplication roundtrip %d", t);
		if (!compare_poly(label, &got, &schoolbook))
		{
			return 0;
		}
	}

	printf("ntt/basemul/invntt multiplication tests ok\n");
	return 1;
}

int main(void)
{
	if (!check_direct_inverse_compare())
	{
		return 1;
	}

	if (!check_roundtrip_patterns())
	{
		return 1;
	}

	if (!check_impulses())
	{
		return 1;
	}

	if (!check_multiplication_roundtrip())
	{
		return 1;
	}

	return 0;
}
