#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "fips202.h"

void capture_fused_frame(uint8_t *, const uint8_t *, const uint64_t *, uint64_t *);
static const uint64_t rc[24] = {
    0x0000000000000001ULL, 0x0000000000008082ULL,
    0x800000000000808aULL, 0x8000000080008000ULL,
    0x000000000000808bULL, 0x0000000080000001ULL,
    0x8000000080008081ULL, 0x8000000000008009ULL,
    0x000000000000008aULL, 0x0000000000000088ULL,
    0x0000000080008009ULL, 0x000000008000000aULL,
    0x000000008000808bULL, 0x800000000000008bULL,
    0x8000000000008089ULL, 0x8000000000008003ULL,
    0x8000000000008002ULL, 0x8000000000000080ULL,
    0x000000000000800aULL, 0x800000008000000aULL,
    0x8000000080008081ULL, 0x8000000000008080ULL,
    0x0000000080000001ULL, 0x8000000080008008ULL
};
int test_fused_frame(void)
{
    uint8_t msg[1152], joined[1153], expected[192], actual[192];
    uint64_t capture[36];
    for (unsigned seed = 0; seed < 256; ++seed) {
        for (unsigned i = 0; i < sizeof msg; ++i)
            msg[i] = (uint8_t)(i * 17 + seed * 71);
        joined[0] = 1; memcpy(joined + 1, msg, sizeof msg);
        shake256(expected, sizeof expected, joined, sizeof joined);
        memset(capture, 0xa5, sizeof capture);
        capture_fused_frame(actual, msg, rc, capture);
        if (memcmp(expected, actual, sizeof actual)) return 1;
        for (unsigned i = 0; i < 36; ++i) {
            if (capture[i]) {
                fprintf(stderr, "fused cleanup word %u: %llx\n",
                        i, (unsigned long long)capture[i]);
                return 1;
            }
        }
    }
    return 0;
}
