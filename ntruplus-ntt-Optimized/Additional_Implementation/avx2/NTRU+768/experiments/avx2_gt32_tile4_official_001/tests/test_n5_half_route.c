#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define WORDS 768

void gt32_tile4_n5_to_n32_half_asm(int16_t *, const int16_t *);

static int physical_k3(int slot, int qword)
{
	if (slot == 0)
		return 0;
	if (slot == 1)
		return qword < 2 ? 1 : 2;
	return qword < 2 ? 2 : 1;
}

static void reference(int16_t out[WORDS], const int16_t in[WORDS])
{
	for (int branch = 0; branch < 2; branch++)
		for (int group = 0; group < 8; group++)
			for (int slot = 0; slot < 3; slot++) {
				const int dst = (branch * 8 + group) * 3 + slot;
				for (int qword = 0; qword < 4; qword++) {
					const int k3 = physical_k3(slot, qword);
					const int src = (k3 * 2 + branch) * 8 + group;
					for (int degree = 0; degree < 4; degree++)
						out[16 * dst + 4 * qword + degree] =
							in[16 * src + 4 * qword + degree];
				}
			}
}

int main(void)
{
	_Alignas(32) int16_t input[WORDS], expected[WORDS], actual[WORDS];
	for (int trial = 0; trial < 1000; trial++) {
		for (int i = 0; i < WORDS; i++)
			input[i] = (int16_t)(trial * 17 + i);
		reference(expected, input);
		gt32_tile4_n5_to_n32_half_asm(actual, input);
		if (memcmp(expected, actual, sizeof(actual)) != 0) {
			fprintf(stderr, "N5 half route mismatch trial=%d\n", trial);
			return 1;
		}
	}
	puts("N5 terminal -> N32 half-native route: pass");
	return 0;
}
