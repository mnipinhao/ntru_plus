#include <stdint.h>
#include <stdio.h>
#include "poly.h"
#include "ntt.h"
#include "gt_asm.h"

#define TEST_VECTORS 8

static int modq(int32_t a)
{
	int r = a % NTRUPLUS_Q;

	if (r < 0)
	{
		r += NTRUPLUS_Q;
	}

	return r;
}

static int equal_modq(int16_t a, int16_t b)
{
	return modq(a - b) == 0;
}

static void fill_poly(poly *a, uint32_t seed)
{
	uint32_t s = seed + 1;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		s = s * 1664525u + 1013904223u;
		a->coeffs[i] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
	}
}

static int coeff_match_count(const poly *a, const poly *b)
{
	int count = 0;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		count += equal_modq(a->coeffs[i], b->coeffs[i]);
	}

	return count;
}

int main(void)
{
	int min_matches = NTRUPLUS_N;

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		poly a;
		poly ref;
		poly got;
		int matches;

		fill_poly(&a, seed);
		ntt_gt_rowbitrevlayout(ref.coeffs, a.coeffs);
		poly_ntt_gt_asm(&got, &a);

		matches = coeff_match_count(&ref, &got);
		if (matches < min_matches)
		{
			min_matches = matches;
		}
	}

	printf("poly_ntt_gt_asm scaffold: %d/%d minimum coefficient match\n",
	       min_matches, NTRUPLUS_N);
	return min_matches == NTRUPLUS_N ? 0 : 1;
}
