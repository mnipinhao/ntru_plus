#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "tile4.h"

int main(void)
{
	int16_t recovered[GT32_TILE4_POLY_WORDS] __attribute__((aligned(64)));
	int16_t derived[GT32_TILE4_POLY_WORDS] __attribute__((aligned(64)));

	for (int difference = -12699; difference <= 12699; difference++) {
		memset(recovered, 0, sizeof recovered);
		memset(derived, 0, sizeof derived);
		int a = difference;
		if (a > 1911)
			a = 1911;
		if (a < -1911)
			a = -1911;
		const int b = a - difference;
		if (b < -10788 || b > 10788)
			return 1;
		recovered[0] = (int16_t)a;
		derived[0] = (int16_t)b;
		const int expected = difference % GT32_TILE4_Q != 0;
		const int actual = gt32_tile4_soa_equal_modq_12699_asm(recovered,
			derived);
		if (actual != expected) {
			fprintf(stderr, "difference=%d expected=%d actual=%d\n",
				difference, expected, actual);
			return 1;
		}
	}
	puts("gt32-native-rcheck: exhaustive-difference-range-pass");
	return 0;
}
