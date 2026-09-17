/*
 * Differential for the fused SHAKE256 kernels against the generic sponge.
 *
 * The generic path is the oracle: hash_f is shake256(0x00 || msg) truncated to
 * 32 bytes and hash_g is shake256(0x01 || msg) to 288, both over exactly
 * NTRUPLUS_POLYBYTES of message.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "fips202.h"

#define PB 1728
void ntruplus_hash_f_fixed(uint8_t output[32], const uint8_t input[PB]);
void ntruplus_hash_g_fixed(uint8_t output[288], const uint8_t input[PB]);

static uint64_t s = 0x9E3779B97F4A7C15ull;
static uint64_t rnd(void){s^=s<<13;s^=s>>7;s^=s<<17;return s;}

static uint8_t msg[PB], data[1 + PB];
static uint8_t f_ref[32], f_got[32], g_ref[288], g_got[288];

int main(void)
{
    int bad_f = 0, bad_g = 0;
    for (int t = 0; t < 4000; t++) {
        if (t == 0)      memset(msg, 0x00, PB);
        else if (t == 1) memset(msg, 0xFF, PB);
        else for (int i = 0; i < PB; i++) msg[i] = (uint8_t)rnd();

        data[0] = 0x00; memcpy(data + 1, msg, PB);
        shake256(f_ref, 32, data, PB + 1);
        ntruplus_hash_f_fixed(f_got, msg);
        bad_f += memcmp(f_ref, f_got, 32) != 0;

        data[0] = 0x01; memcpy(data + 1, msg, PB);
        shake256(g_ref, 288, data, PB + 1);
        ntruplus_hash_g_fixed(g_got, msg);
        bad_g += memcmp(g_ref, g_got, 288) != 0;
    }
    printf("4000 inputs (all-zero, all-ones, 3998 random)\n");
    printf("  hash_f  32 bytes out: mismatches %d\n", bad_f);
    printf("  hash_g 288 bytes out: mismatches %d\n", bad_g);
    if (bad_g) {
        for (int i = 0; i < 288; i++)
            if (g_ref[i] != g_got[i]) { printf("  first differing byte: %d\n", i); break; }
    }
    return (bad_f || bad_g) != 0;
}
