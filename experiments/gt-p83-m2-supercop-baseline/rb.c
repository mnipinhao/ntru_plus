/* Deterministic xorshift RNG shared by every binary in this comparison.
 * The shipped randombytes reads /dev/urandom, one syscall per call, whose
 * variance swamps the arithmetic being measured.  Both sides use this one, so
 * the comparison is unaffected and the noise floor drops. */
#include "randombytes.h"
static uint64_t s0 = 0x243f6a8885a308d3ULL, s1 = 0x13198a2e03707344ULL;
void randombytes(uint8_t *out, size_t length)
{
    while (length) {
        uint64_t x = s0, y = s1;
        s0 = y; x ^= x << 23; s1 = x ^ y ^ (x >> 17) ^ (y >> 26);
        uint64_t r = s1 + y;
        size_t n = length < 8 ? length : 8;
        for (size_t i = 0; i < n; i++) out[i] = (uint8_t)(r >> (8*i));
        out += n; length -= n;
    }
}
