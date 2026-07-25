/*
 * Deterministic benchmark-only randombytes implementation.
 *
 * This is not a cryptographic random number generator. It exists only to feed
 * identical byte streams to the two benchmark binaries.
 */
#include <stddef.h>
#include <stdint.h>

static uint32_t bench_random_state = UINT32_C(0x6d2b79f5);

void bench_randombytes_reset(uint32_t seed)
{
    bench_random_state = seed ? seed : UINT32_C(1);
}

void randombytes(uint8_t *out, size_t outlen)
{
    while (outlen-- != 0) {
        bench_random_state =
            bench_random_state * UINT32_C(1664525) + UINT32_C(1013904223);
        *out++ = (uint8_t)(bench_random_state >> 24);
    }
}
