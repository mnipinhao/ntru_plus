#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "ntt.h"
#include "poly.h"

#define RANDOM_TESTS 32

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static void fill_zero(poly *a)
{
	memset(a->coeffs, 0, sizeof(a->coeffs));
}

static void fill_pattern(poly *a, int pattern, uint32_t seed)
{
	static const int lazy_vals[] = {
		0, 1, -1,
		NTRUPLUS_Q - 1, -(NTRUPLUS_Q - 1),
		2 * (NTRUPLUS_Q - 1), -2 * (NTRUPLUS_Q - 1),
		3 * (NTRUPLUS_Q - 1), -3 * (NTRUPLUS_Q - 1),
		4 * (NTRUPLUS_Q - 1), -4 * (NTRUPLUS_Q - 1)
	};

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		switch (pattern)
		{
		case 0:
			a->coeffs[i] = 0;
			break;
		case 1:
			a->coeffs[i] = 1;
			break;
		case 2:
			a->coeffs[i] = (i & 1) ? -1 : 1;
			break;
		case 3:
			a->coeffs[i] = (i & 1) ? -(NTRUPLUS_Q / 2) : (NTRUPLUS_Q / 2);
			break;
		case 4:
			a->coeffs[i] =
			    (int16_t)lazy_vals[i % (int)(sizeof(lazy_vals) / sizeof(lazy_vals[0]))];
			break;
		default:
			a->coeffs[i] =
			    (int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
			break;
		}
	}
}

static void fill_impulse(poly *a, int pos, int16_t value)
{
	fill_zero(a);
	a->coeffs[pos] = value;
}

static int crepmod3_sensitive_equal(int16_t a, int16_t b)
{
	/*
	 * poly_crepmod3 consumes the signed representative.  Since q = 3457 == 1
	 * mod 3, changing a representative by q changes this observation by 1.
	 */
	return (int16_t)(a - b) == 0;
}

static int representative_mismatch_count(const poly *got, const poly *want)
{
	int mismatches = 0;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!crepmod3_sensitive_equal(got->coeffs[i], want->coeffs[i]))
		{
			mismatches++;
		}
	}

	return mismatches;
}

static int check_case(const char *label, const poly *time_input)
{
	poly freq;
	poly got;
	poly want;

	poly_ntt(&freq, time_input);
	poly_invntt(&got, &freq);
	invntt_gt_rowbitrevlayout_exact(want.coeffs, freq.coeffs);

	if (representative_mismatch_count(&got, &want) != 0)
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			if (!crepmod3_sensitive_equal(got.coeffs[i], want.coeffs[i]))
			{
				fprintf(stderr,
				        "%s representative mismatch at %d: got=%d want=%d "
				        "delta_mod3=%d\n",
				        label, i, got.coeffs[i], want.coeffs[i],
				        (int)((got.coeffs[i] - want.coeffs[i]) % 3));
				return 0;
			}
		}
	}

	return 1;
}

static int check_out_of_contract_edge_hazard(void)
{
	poly a;
	poly freq;
	poly got;
	poly want;
	int mismatches;

	fill_pattern(&a, 3, 0);
	poly_ntt(&freq, &a);
	poly_invntt(&got, &freq);
	invntt_gt_rowbitrevlayout_exact(want.coeffs, freq.coeffs);
	mismatches = representative_mismatch_count(&got, &want);

	if (mismatches == 0)
	{
		fprintf(stderr,
		        "out-of-contract centered-edge stress did not expose a "
		        "representative-sensitive difference\n");
		return 0;
	}

	printf("out-of-contract centered-edge stress observed %d representative hazards\n",
	       mismatches);
	return 1;
}

int main(void)
{
	poly a;
	char label[96];

	for (int pattern = 0; pattern < 3; pattern++)
	{
		fill_pattern(&a, pattern, 0x12345678u + (uint32_t)pattern);
		snprintf(label, sizeof(label), "pattern %d", pattern);
		if (!check_case(label, &a))
		{
			return 1;
		}
	}

	for (int pos = 0; pos < NTRUPLUS_N; pos++)
	{
		fill_impulse(&a, pos, (int16_t)(1 + (pos % 7)));
		snprintf(label, sizeof(label), "impulse %d", pos);
		if (!check_case(label, &a))
		{
			return 1;
		}
	}

	for (int t = 0; t < RANDOM_TESTS; t++)
	{
		uint32_t seed = 0x9e3779b9u + (uint32_t)t;

		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a.coeffs[i] = (int16_t)((int)(next_u32(&seed) % 3) - 1);
		}

		snprintf(label, sizeof(label), "random %d", t);
		if (!check_case(label, &a))
		{
			return 1;
		}
	}

	if (!check_out_of_contract_edge_hazard())
	{
		return 1;
	}

	printf("inverse NTT representative-sensitive tests ok\n");
	return 0;
}
