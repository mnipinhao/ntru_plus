#include <stdint.h>

#include "tile4.h"
#include "../generated/tile4_basemul_constants.h"

#define Q GT32_TILE4_Q
#define R 3310

static int32_t modq(int64_t value)
{
	int64_t reduced = value % Q;
	reduced += (reduced >> 63) & Q;
	return (int32_t)reduced;
}

static int16_t centered(int32_t value)
{
	value = modq(value);
	value -= Q & -(value > Q / 2);
	return (int16_t)value;
}

static int32_t mulq(int32_t left, int32_t right)
{
	return modq((int64_t)left * right);
}

static int32_t inverse_q(int32_t value)
{
	/* q-2 = 3455; exponent and loop shape are public constants. */
	uint32_t exponent = Q - 2U;
	int32_t accumulator = 1;
	int32_t base = modq(value);
	for (unsigned bit = 0; bit < 12; bit++) {
		if (((exponent >> bit) & 1U) != 0U)
			accumulator = mulq(accumulator, base);
		base = mulq(base, base);
	}
	return accumulator;
}

static int32_t lambda_normal(unsigned tile, unsigned vector, unsigned lane)
{
	const int32_t lambda_mont =
		gt32_tile4_lambda_mont[tile][vector][4U * lane];
	/* R^-1 mod q = 2775. */
	return mulq(lambda_mont, 2775);
}

int gt32_tile4_baseinv_j1_aos_ref(gt32_baseinv_j1_aos_e1_t *out,
	const gt32_f0_aos_e0_t *in)
{
	uint32_t failure = 0;

	for (unsigned tile = 0; tile < 6; tile++) {
		for (unsigned vector = 0; vector < 8; vector++) {
			for (unsigned lane = 0; lane < 4; lane++) {
				const unsigned offset = 128U * tile + 16U * vector
					+ 4U * lane;
				const int32_t a0 = modq(in->words[offset + 0]);
				const int32_t a1 = modq(in->words[offset + 1]);
				const int32_t a2 = modq(in->words[offset + 2]);
				const int32_t a3 = modq(in->words[offset + 3]);
				const int32_t lambda = lambda_normal(tile, vector, lane);
				const int32_t t0 = modq(mulq(a0, a0)
					+ mulq(lambda, modq(mulq(a2, a2)
						- 2 * mulq(a1, a3))));
				const int32_t t1 = modq(mulq(a1, a1)
					+ mulq(lambda, mulq(a3, a3))
					- 2 * mulq(a0, a2));
				const int32_t determinant = modq(mulq(t0, t0)
					- mulq(lambda, mulq(t1, t1)));
				const int32_t inverse = inverse_q(determinant);
				const int32_t numerator[4] = {
					modq(mulq(a0, t0) + mulq(lambda, mulq(a2, t1))),
					modq(-mulq(lambda, mulq(a3, t1)) - mulq(a1, t0)),
					modq(mulq(a2, t0) + mulq(a0, t1)),
					modq(-mulq(a1, t1) - mulq(a3, t0)),
				};

				failure |= (uint32_t)(determinant == 0);
				for (unsigned degree = 0; degree < 4; degree++)
					out->words[offset + degree] = centered(
						mulq(mulq(numerator[degree], inverse), R));
			}
		}
	}

	/* Match poly_baseinv: one failed leaf zeroes the complete result. */
	const uint16_t keep = (uint16_t)-(uint16_t)(failure == 0U);
	for (unsigned index = 0; index < GT32_TILE4_POLY_WORDS; index++)
		out->words[index] = (int16_t)((uint16_t)out->words[index] & keep);
	return (int)(failure != 0U);
}
