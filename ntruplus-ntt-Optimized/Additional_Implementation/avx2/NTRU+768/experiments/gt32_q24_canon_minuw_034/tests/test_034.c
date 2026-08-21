#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"

void ntruplus768_pack_m_highrange12699_avx2(uint8_t *, const int16_t *);
void gt034_ntruplus768_pack_m_highrange12699_avx2(uint8_t *, const int16_t *);

static uint16_t unpack_slot(const uint8_t *input, size_t slot)
{
	size_t pair = slot / 2;
	if ((slot & 1) == 0)
		return (uint16_t)(input[3 * pair]
			| ((uint16_t)(input[3 * pair + 1] & 15) << 8));
	return (uint16_t)((input[3 * pair + 1] >> 4)
		| ((uint16_t)input[3 * pair + 2] << 4));
}

static uint64_t rng_state = UINT64_C(0x034c0de4d1f29a7b);

static uint16_t random16(void)
{
	rng_state ^= rng_state << 13;
	rng_state ^= rng_state >> 7;
	rng_state ^= rng_state << 17;
	return (uint16_t)rng_state;
}

int main(void)
{
	static int16_t input[NTRUPLUS_N] __attribute__((aligned(64)));
	static uint8_t control[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
	static uint8_t candidate[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));

	/* Exhaust the entire signed-int16 scalar domain through every wire slot. */
	for (int value = -32768; value <= 32767; value++) {
		int expected = value % 3457;
		if (expected < 0)
			expected += 3457;
		for (size_t lane = 0; lane < NTRUPLUS_N; lane++)
			input[lane] = (int16_t)value;
		ntruplus768_pack_m_highrange12699_avx2(control, input);
		gt034_ntruplus768_pack_m_highrange12699_avx2(candidate, input);
		if (memcmp(control, candidate, sizeof control) != 0) {
			fprintf(stderr, "control/candidate mismatch x=%d\n", value);
			return 1;
		}
		for (size_t slot = 0; slot < NTRUPLUS_N; slot++) {
			uint16_t actual = unpack_slot(candidate, slot);
			if (actual != (uint16_t)expected) {
				fprintf(stderr, "x=%d slot=%zu got=%u expected=%d\n",
					value, slot, actual, expected);
				return 1;
			}
		}
	}

	/* Heterogeneous vectors catch lane/permutation mistakes hidden above. */
	for (size_t trial = 0; trial < 10000; trial++) {
		for (size_t lane = 0; lane < NTRUPLUS_N; lane++)
			input[lane] = (int16_t)random16();
		ntruplus768_pack_m_highrange12699_avx2(control, input);
		gt034_ntruplus768_pack_m_highrange12699_avx2(candidate, input);
		if (memcmp(control, candidate, sizeof control) != 0) {
			fprintf(stderr, "heterogeneous mismatch trial=%zu\n", trial);
			return 1;
		}
	}

	puts("034: 65536 scalar values x 768 slots + 10000 heterogeneous trials PASS");
	return 0;
}

