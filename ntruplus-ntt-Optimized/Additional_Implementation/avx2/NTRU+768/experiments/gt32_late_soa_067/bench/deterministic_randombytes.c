#include <stddef.h>
#include <stdint.h>

#include "randombytes.h"

void randombytes(uint8_t *out, size_t outlen)
{
	static uint64_t state = UINT64_C(0x0679e3779b97f4a7);
	while (outlen-- != 0) {
		state ^= state << 7;
		state ^= state >> 9;
		*out++ = (uint8_t)state;
	}
}
