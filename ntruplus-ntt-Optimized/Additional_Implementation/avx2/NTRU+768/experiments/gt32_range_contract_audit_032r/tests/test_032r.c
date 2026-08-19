#include <stdint.h>
#include <stdio.h>

#include "params.h"

void ntruplus768_pack_m_highrange12699_avx2(uint8_t *, const int16_t *);

static uint16_t unpack_slot(const uint8_t *input, size_t slot)
{
	size_t pair = slot / 2;
	if ((slot & 1) == 0)
		return (uint16_t)(input[3 * pair]
			| ((uint16_t)(input[3 * pair + 1] & 15) << 8));
	return (uint16_t)((input[3 * pair + 1] >> 4)
		| ((uint16_t)input[3 * pair + 2] << 4));
}

int main(void)
{
	static int16_t input[NTRUPLUS_N] __attribute__((aligned(64)));
	static uint8_t output[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
	const int bound = 20296;
	for (int value = -bound; value <= bound; value++) {
		int expected = value % 3457;
		if (expected < 0)
			expected += 3457;
		for (size_t lane = 0; lane < NTRUPLUS_N; lane++)
			input[lane] = (int16_t)value;
		ntruplus768_pack_m_highrange12699_avx2(output, input);
		for (size_t slot = 0; slot < NTRUPLUS_N; slot++) {
			uint16_t actual = unpack_slot(output, slot);
			if (actual != (uint16_t)expected) {
				fprintf(stderr, "packet mismatch x=%d slot=%zu got=%u expected=%d\n",
					value, slot, actual, expected);
				return 1;
			}
		}
	}
	printf("032R: 40593 scalar values x 768 serialized slots PASS\n");
	return 0;
}
