/* Deterministic RNG, resettable.
 *
 * Key generation rejects and retries -- `do { randombytes(coins); r = gen(...) }
 * while (r)` -- so its cost depends entirely on how many draws the stream
 * happens to need.  Measured on one stream the spread between the cheapest and
 * dearest single key generation is 11x.  If the timed batches of two builds
 * start at different points in the stream they are not measuring the same work,
 * and where they start depends on how many warm-up iterations each managed,
 * which depends on speed.  Reseeding before every batch removes that entirely:
 * every build generates the identical sequence of keys.
 */
#include "randombytes.h"
static uint64_t s0, s1;
void rb_seed(void){ s0 = 0x243f6a8885a308d3ULL; s1 = 0x13198a2e03707344ULL; }
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
