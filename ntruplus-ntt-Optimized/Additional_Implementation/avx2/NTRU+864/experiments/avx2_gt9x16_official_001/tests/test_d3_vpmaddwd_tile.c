#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "d3_vpmaddwd_tile.h"

#define Q 3457
#define QINV 12929
#define GUARD 16

static uint32_t rng_state = 0xd3a50864u;

static uint32_t next_u32(void)
{
    uint32_t x = rng_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    rng_state = x;
    return x;
}

static int16_t mont(int16_t a, int16_t b)
{
    int32_t s = (int32_t)a * b;
    int16_t t = (int16_t)((uint16_t)s * (uint16_t)QINV);
    return (int16_t)(((int64_t)s - (int64_t)t * Q) / 65536);
}

static int canonical(int16_t x)
{
    int r = x % Q;
    return r < 0 ? r + Q : r;
}

static void reference(int16_t out[48], const int16_t a[48],
                      const int16_t b[48], const int16_t zeta[16])
{
    for (int q = 0; q < 16; ++q) {
        int16_t av[3], bv[3];
        for (int j = 0; j < 3; ++j) {
            av[j] = a[3 * q + j];
            bv[j] = b[3 * q + j];
        }
        int16_t d0 = mont(av[0], bv[0]);
        int16_t d1 = mont(av[1], bv[1]);
        int16_t d2 = mont(av[2], bv[2]);
        int16_t s0 = (int16_t)(mont(av[1], bv[2]) + mont(av[2], bv[1]));
        int16_t s1 = (int16_t)(mont(av[0], bv[1]) + mont(av[1], bv[0]));
        int16_t s2 = (int16_t)(mont(av[0], bv[2]) + mont(av[2], bv[0]));
        out[q] = (int16_t)(d0 + mont(s0, zeta[q]));
        out[16 + q] = (int16_t)(s1 + mont(d2, zeta[q]));
        out[32 + q] = (int16_t)(s2 + d1);
    }
}

static int guards_ok(const int16_t *buffer, int words)
{
    for (int i = 0; i < GUARD; ++i)
        if (buffer[i] != (int16_t)0x5a5a ||
            buffer[GUARD + words + i] != (int16_t)0x5a5a)
            return 0;
    return 1;
}

int main(void)
{
    _Alignas(32) int16_t a_guard[48 + 2 * GUARD];
    _Alignas(32) int16_t b_guard[48 + 2 * GUARD];
    _Alignas(32) int16_t out0_guard[48 + 2 * GUARD];
    _Alignas(32) int16_t out1_guard[48 + 2 * GUARD];
    _Alignas(32) int16_t scratch_guard[96 + 2 * GUARD];
    _Alignas(32) int16_t zeta_pair[32];
    _Alignas(32) int16_t a_copy[48], b_copy[48], expected[48];
    int16_t *a = a_guard + GUARD;
    int16_t *b = b_guard + GUARD;
    int16_t *out0 = out0_guard + GUARD;
    int16_t *out1 = out1_guard + GUARD;
    int16_t *scratch = scratch_guard + GUARD;

    for (int test = 0; test < 10003; ++test) {
        for (size_t i = 0; i < sizeof a_guard / sizeof a_guard[0]; ++i)
            a_guard[i] = (int16_t)0x5a5a;
        for (size_t i = 0; i < sizeof b_guard / sizeof b_guard[0]; ++i)
            b_guard[i] = (int16_t)0x5a5a;
        for (size_t i = 0; i < sizeof out0_guard / sizeof out0_guard[0]; ++i)
            out0_guard[i] = (int16_t)0x5a5a;
        for (size_t i = 0; i < sizeof out1_guard / sizeof out1_guard[0]; ++i)
            out1_guard[i] = (int16_t)0x5a5a;
        for (size_t i = 0; i < sizeof scratch_guard / sizeof scratch_guard[0]; ++i)
            scratch_guard[i] = (int16_t)0x5a5a;
        for (int i = 0; i < 48; ++i) {
            a[i] = (int16_t)(next_u32() % Q);
            b[i] = (int16_t)next_u32();
        }
        if (test == 0)
            for (int i = 0; i < 48; ++i) {
                a[i] = (i & 1) ? Q - 1 : 0;
                b[i] = (i & 2) ? INT16_MAX : INT16_MIN;
            }
        if (test == 1)
            memset(a, 0, 48 * sizeof *a);
        if (test == 2)
            memset(b, 0, 48 * sizeof *b);
        for (int q = 0; q < 16; ++q) {
            int16_t z = (int16_t)((int)(next_u32() % Q) - (Q - 1) / 2);
            zeta_pair[q] = (int16_t)((uint16_t)z * (uint16_t)QINV);
            zeta_pair[16 + q] = z;
        }
        memcpy(a_copy, a, sizeof a_copy);
        memcpy(b_copy, b, sizeof b_copy);
        reference(expected, a, b, zeta_pair + 16);
        ntruplus864_exp001_d3_tile_baseline(out0, a, b, zeta_pair, scratch);
        ntruplus864_exp001_d3_tile_vpmaddwd(out1, a, b, zeta_pair, scratch);
        for (int i = 0; i < 48; ++i) {
            if (canonical(out0[i]) != canonical(expected[i]) ||
                canonical(out1[i]) != canonical(expected[i])) {
                fprintf(stderr, "D3 mismatch test=%d word=%d ref=%d baseline=%d candidate=%d\n",
                        test, i, expected[i], out0[i], out1[i]);
                return 1;
            }
        }
        if (memcmp(a, a_copy, sizeof a_copy) || memcmp(b, b_copy, sizeof b_copy))
            return 2;
        if (!guards_ok(a_guard, 48) || !guards_ok(b_guard, 48) ||
            !guards_ok(out0_guard, 48) || !guards_ok(out1_guard, 48) ||
            !guards_ok(scratch_guard, 96))
            return 3;
    }
    puts("D3 ASM0: 10003 tile differential cases; canonical equality, immutability, alignment, and canaries passed");
    return 0;
}
