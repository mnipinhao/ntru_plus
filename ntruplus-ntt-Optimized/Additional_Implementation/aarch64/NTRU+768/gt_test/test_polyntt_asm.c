#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "ntt.h"
#include "poly.h"

#define RANDOM_TESTS 8

#ifndef POLYNTT_ASM_ALLOW_LAZY
#define POLYNTT_ASM_ALLOW_LAZY 0
#endif

/*
 * Link this harness with exactly one poly_ntt() implementation, normally
 * asm/my_ntt.s.  The golden output comes from the C Good-Thomas reference in
 * ntt.c, so this test does not depend on production poly.c or asm/ntt.s.
 *
 * Default policy is strict exact matching to catch permutation and reduction
 * shape errors early.  For an intentionally lazy-reduced ASM kernel, build
 * with -DPOLYNTT_ASM_ALLOW_LAZY=1 to accept mod-q equality.
 */

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

	if (strcmp(name, "ramp") == 0)
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a->coeffs[i] = (int16_t)((i % NTRUPLUS_Q) - NTRUPLUS_Q / 2);
		}
		return;
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		seed = seed * 1664525u + 1013904223u;
		a->coeffs[i] = (int16_t)((int)(seed % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
	}
}

static void fill_impulse(poly *a, int pos, int16_t value)
{
	fill_zero(a);
	a->coeffs[pos] = value;
}

static void reference_poly_ntt(poly *r, const poly *a)
{
	ntt_gt_rowbitrevlayout(r->coeffs, a->coeffs);
}

static int compare_poly(const char *label, const poly *asm_out, const poly *ref)
{
	int exact_matches = 0;
	int mod_matches = 0;
	int printed = 0;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		const int exact = asm_out->coeffs[i] == ref->coeffs[i];
		const int mod = equal_modq(asm_out->coeffs[i], ref->coeffs[i]);

		exact_matches += exact;
		mod_matches += mod;

		if (!mod && printed < 8)
		{
			printf("  mismatch %-24s i=%3d asm=%7d ref=%7d diff_mod_q=%4d\n",
			       label,
			       i,
			       asm_out->coeffs[i],
			       ref->coeffs[i],
			       modq((int)asm_out->coeffs[i] - (int)ref->coeffs[i]));
			printed++;
		}
	}

	printf("%-28s exact %3d/768, mod-q %3d/768\n",
	       label, exact_matches, mod_matches);

#if POLYNTT_ASM_ALLOW_LAZY
	return mod_matches == NTRUPLUS_N;
#else
	return exact_matches == NTRUPLUS_N;
#endif
}

static int compare_to_reference_case(const char *label, const poly *input)
{
	poly ref;
	poly asm_out;

	reference_poly_ntt(&ref, input);
	poly_ntt(&asm_out, input);

	return compare_poly(label, &asm_out, &ref);
}

static int check_reference_differential(void)
{
	static const char *patterns[] = {
		"zero",
		"one",
		"alternating_pm1",
		"centered_edges",
		"ramp"
	};
	static const int impulse_positions[] = {
		0, 1, 2, 3, 4, 31, 32, 33,
		127, 128, 255, 256, 383, 384, 511, 512, 767
	};
	poly input;
	char label[64];
	int ok = 1;

	for (unsigned i = 0; i < sizeof(patterns) / sizeof(patterns[0]); i++)
	{
		fill_pattern(&input, patterns[i], 0);
		ok &= compare_to_reference_case(patterns[i], &input);
	}

	for (unsigned i = 0; i < sizeof(impulse_positions) / sizeof(impulse_positions[0]); i++)
	{
		fill_impulse(&input, impulse_positions[i], 1);
		snprintf(label, sizeof(label), "impulse_%03d", impulse_positions[i]);
		ok &= compare_to_reference_case(label, &input);
	}

	for (uint32_t seed = 0; seed < RANDOM_TESTS; seed++)
	{
		fill_pattern(&input, "random", 0x9e3779b9u ^ seed);
		snprintf(label, sizeof(label), "random_%u", seed);
		ok &= compare_to_reference_case(label, &input);
	}

	return ok;
}

static int check_roundtrip(void)
{
	poly input;
	poly freq;
	poly round;
	int min_matches = NTRUPLUS_N;

	for (uint32_t seed = 0; seed < RANDOM_TESTS; seed++)
	{
		int matches = 0;

		fill_pattern(&input, "random", 0x243f6a88u ^ seed);
		poly_ntt(&freq, &input);
		invntt_gt_rowbitrevlayout(round.coeffs, freq.coeffs);

		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			matches += equal_modq(round.coeffs[i], input.coeffs[i]);
		}

		if (matches < min_matches)
		{
			min_matches = matches;
		}
	}

	printf("%-28s mod-q %3d/768\n", "roundtrip", min_matches);
	return min_matches == NTRUPLUS_N;
}

static void rowbitrev_basemul_reference(poly *r, const poly *a, const poly *b)
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int pos = branch_start + 4*physical_j;

			basemul(r->coeffs + pos,
			        a->coeffs + pos,
			        b->coeffs + pos,
			        gt_rowbitrev_lambda[branch][physical_j]);
		}
	}
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

	/* NTRU+768 ring: X^768 = X^384 - 1. */
	for (int i = 2*NTRUPLUS_N - 2; i >= NTRUPLUS_N; i--)
	{
		const int64_t c = tmp[i];

		tmp[i - NTRUPLUS_N / 2] += c;
		tmp[i - NTRUPLUS_N] -= c;
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		r->coeffs[i] = (int16_t)modq(tmp[i]);
	}
}

static int check_multiplication(void)
{
	poly a;
	poly b;
	poly A;
	poly B;
	poly C;
	poly product;
	poly schoolbook;
	int min_matches = NTRUPLUS_N;

	for (uint32_t seed = 0; seed < RANDOM_TESTS; seed++)
	{
		int matches = 0;

		fill_pattern(&a, "random", 0xa4093822u ^ seed);
		fill_pattern(&b, "random", 0x299f31d0u ^ seed);
		schoolbook_mul_reference(&schoolbook, &a, &b);

		poly_ntt(&A, &a);
		poly_ntt(&B, &b);
		rowbitrev_basemul_reference(&C, &A, &B);
		invntt_gt_rowbitrevlayout(product.coeffs, C.coeffs);

		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			matches += equal_modq(product.coeffs[i], schoolbook.coeffs[i]);
		}

		if (matches < min_matches)
		{
			min_matches = matches;
		}
	}

	printf("%-28s mod-q %3d/768\n", "multiplication", min_matches);
	return min_matches == NTRUPLUS_N;
}

int main(void)
{
	int ok = 1;

	printf("polyntt ASM test policy: %s\n",
	       POLYNTT_ASM_ALLOW_LAZY ? "mod-q equality accepts lazy reduction"
	                              : "strict exact output equality");

	ok &= check_reference_differential();
	ok &= check_roundtrip();
	ok &= check_multiplication();

	return ok ? 0 : 1;
}
