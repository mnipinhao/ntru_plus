#include <stdint.h>
#include <stdio.h>
#include "gt_asm.h"

/*
 * Include the C reference directly so this test can compare the standalone
 * ASM kernel against the exact static ntt32_radix2() oracle.
 */
#include "../ntt.c"

#define TEST_VECTORS 96

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

static uint32_t xorshift32(uint32_t *state)
{
	uint32_t x = *state;

	x ^= x << 13;
	x ^= x >> 17;
	x ^= x << 5;
	*state = x;
	return x;
}

static void fill_vec(int16_t in[32], uint32_t seed)
{
	if (seed == 0)
	{
		for (int i = 0; i < 32; i++)
		{
			in[i] = 0;
		}
		return;
	}

	if (seed == 1)
	{
		for (int i = 0; i < 32; i++)
		{
			in[i] = (i & 1) ? -(NTRUPLUS_Q / 2) : NTRUPLUS_Q / 2;
		}
		return;
	}

	if (seed == 2)
	{
		for (int i = 0; i < 32; i++)
		{
			in[i] = (int16_t)((i * 173 + 29) % NTRUPLUS_Q - NTRUPLUS_Q / 2);
		}
		return;
	}

	uint32_t s = 0x9e3779b9U ^ seed;

	for (int i = 0; i < 32; i++)
	{
		const uint32_t x = xorshift32(&s);

		in[i] = (int16_t)((int)(x % (2U * NTRUPLUS_Q)) - NTRUPLUS_Q);
	}
}

int main(void)
{
	int min_mod_matches = 32;
	int min_exact_matches = 32;

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		int16_t in[32];
		int16_t ref[32];
		int16_t got[32];
		int mod_matches = 0;
		int exact_matches = 0;

		fill_vec(in, seed);
		ntt32_radix2(ref, in);
		ntt32_radix2_asm(got, in);

		for (int i = 0; i < 32; i++)
		{
			mod_matches += equal_modq(ref[i], got[i]);
			exact_matches += ref[i] == got[i];
		}

		if (mod_matches < min_mod_matches)
		{
			min_mod_matches = mod_matches;
		}
		if (exact_matches < min_exact_matches)
		{
			min_exact_matches = exact_matches;
		}

		if (mod_matches != 32)
		{
			printf("ntt32_radix2_asm mismatch at seed %u\n", seed);
			for (int i = 0; i < 32; i++)
			{
				if (!equal_modq(ref[i], got[i]))
				{
					printf("  i=%d ref=%d got=%d\n", i, ref[i], got[i]);
				}
			}
			return 1;
		}
	}

	printf("ntt32_radix2_asm: mod %d/32, exact %d/32 minimum coefficient match\n",
	       min_mod_matches,
	       min_exact_matches);
	return 0;
}
