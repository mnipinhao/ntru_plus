#include <stddef.h>
#include <stdint.h>

#include "tile4_prepared_fixed_b3.h"
#include "tile4_prepared_fixed_b3_lambda.h"

#define Q 3457
#define HALF_Q 1728
#define RMODQ (-147)

static int16_t center_modq(int32_t value)
{
	int32_t reduced = value % Q;
	uint32_t over;

	reduced += (reduced >> 31) & Q;
	over = (uint32_t)(HALF_Q - reduced) >> 31;
	reduced -= (int32_t)(over * Q);
	return (int16_t)reduced;
}

static int16_t scale_e1(int16_t value)
{
	return center_modq((int32_t)value * RMODQ);
}

static void pack_pair(int16_t dst[16], const int16_t x[16],
	const int16_t y[16], int high)
{
	const int base0 = high ? 4 : 0;
	const int base1 = high ? 12 : 8;

	for (int i = 0; i < 4; ++i) {
		dst[2 * i] = x[base0 + i];
		dst[2 * i + 1] = y[base0 + i];
		dst[8 + 2 * i] = x[base1 + i];
		dst[8 + 2 * i + 1] = y[base1 + i];
	}
}

void gt32_prepare_fixed_b3_general_e1(
	gt32_prepared_fixed_b3_general_e1 *matrix,
	const int16_t fixed[GT32_TILE4_POLY_WORDS])
{
	for (int block = 0; block < 12; ++block) {
		int16_t a[4][16];
		int16_t la[4][16];
		int16_t rows[4][4][16];
		int16_t *out = matrix->row_packets + block * 4 * 4 * 16;

		for (int degree = 0; degree < 4; ++degree) {
			for (int lane = 0; lane < 16; ++lane) {
				const int16_t av = center_modq(
					fixed[block * 64 + degree * 16 + lane]);
				const int16_t lambda =
					gt32_tile4_prepared_fixed_b3_lambda[block * 16 + lane];
				a[degree][lane] = scale_e1(av);
				/* The generated lambda stream is already lambda*R (e=1). */
				la[degree][lane] = center_modq((int32_t)lambda * av);
			}
		}

		for (int lane = 0; lane < 16; ++lane) {
			rows[0][0][lane] = a[0][lane];
			rows[0][1][lane] = la[3][lane];
			rows[0][2][lane] = la[2][lane];
			rows[0][3][lane] = la[1][lane];
			rows[1][0][lane] = a[1][lane];
			rows[1][1][lane] = a[0][lane];
			rows[1][2][lane] = la[3][lane];
			rows[1][3][lane] = la[2][lane];
			rows[2][0][lane] = a[2][lane];
			rows[2][1][lane] = a[1][lane];
			rows[2][2][lane] = a[0][lane];
			rows[2][3][lane] = la[3][lane];
			rows[3][0][lane] = a[3][lane];
			rows[3][1][lane] = a[2][lane];
			rows[3][2][lane] = a[1][lane];
			rows[3][3][lane] = a[0][lane];
		}

		for (int degree = 0; degree < 4; ++degree) {
			pack_pair(out + degree * 64 + 0,
				rows[degree][0], rows[degree][1], 0);
			pack_pair(out + degree * 64 + 16,
				rows[degree][2], rows[degree][3], 0);
			pack_pair(out + degree * 64 + 32,
				rows[degree][0], rows[degree][1], 1);
			pack_pair(out + degree * 64 + 48,
				rows[degree][2], rows[degree][3], 1);
		}
	}
}
