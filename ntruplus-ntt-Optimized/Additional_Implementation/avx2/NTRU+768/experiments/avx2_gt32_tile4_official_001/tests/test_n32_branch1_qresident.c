#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "tile4.h"

#define WORDS 128
#define TRIALS 1000

static uint32_t rng_state = UINT32_C(0x7251d94b);

static uint32_t next_u32(void)
{
	rng_state ^= rng_state << 13;
	rng_state ^= rng_state >> 17;
	rng_state ^= rng_state << 5;
	return rng_state;
}

int main(void)
{
	int16_t input[WORDS] __attribute__((aligned(64)));
	int16_t qmem[WORDS] __attribute__((aligned(64)));
	int16_t qreg[WORDS] __attribute__((aligned(64)));

	for (int trial = 0; trial < TRIALS; trial++) {
		for (int index = 0; index < WORDS; index++)
			input[index] = (int16_t)((next_u32() % 14001U) - 7000);
		memset(qmem, 0x5a, sizeof(qmem));
		memset(qreg, 0xa5, sizeof(qreg));
		gt32_n32_branch1_qmem_asm(qmem, input);
		gt32_n32_branch1_qreg_asm(qreg, input);
		if (memcmp(qmem, qreg, sizeof(qmem)) != 0) {
			for (int index = 0; index < WORDS; index++) {
				if (qmem[index] != qreg[index]) {
					fprintf(stderr,
						"trial %d word %d: qmem=%d qreg=%d\n",
						trial, index, qmem[index], qreg[index]);
					break;
				}
			}
			return 1;
		}
	}
	puts("n32 Branch-1 q memory/register: 1000 exact-word trials passed");
	return 0;
}
