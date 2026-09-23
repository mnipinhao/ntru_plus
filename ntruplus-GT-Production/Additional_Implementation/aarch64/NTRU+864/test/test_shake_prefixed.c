/*
 * shake256_prefixed must equal shake256 over an explicitly built
 * domain || message, for every length that matters.
 *
 * The prefixed entry point exists so no caller has to materialise that
 * concatenation, which is where NTRU+864's hash_f and hash_g each used to spend
 * a 1297-byte stack copy.  It absorbs with the domain byte folded into lane 0
 * and unaligned lane loads thereafter, so the block boundaries do not line up
 * with the caller's buffer -- exactly the part worth testing.
 *
 * Build: cc -O2 -I. -o t test/test_shake_prefixed.c fips202.c keccakf1600.S \
 *            keccakf1600_v84a.S
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include "fips202.h"
#include "params.h"

#define MAXIN  (NTRUPLUS_POLYBYTES + 8)
/* Large enough for every entry of outlens[] below, not just the
 * production transcripts -- the 2-block boundary cases exceed those. */
#define MAXOUT 320

static uint8_t msg[MAXIN];
static uint8_t cat[MAXIN + 1];
static uint8_t want[MAXOUT];
static uint8_t got[MAXOUT];
static uint8_t alias[MAXIN];   /* aliasing case needs room for message and output */

static uint64_t rng = 0x243F6A8885A308D3ULL;

static uint8_t next_byte(void)
{
    rng ^= rng << 13;
    rng ^= rng >> 7;
    rng ^= rng << 17;
    return (uint8_t)(rng >> 24);
}

/* Rate boundaries, the production transcripts, and their neighbours. */
static const size_t inlens[] = {
    0, 1, 7, 8, 9, 127, 134, 135, 136, 137, 271, 272, 273,
    NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES,
    NTRUPLUS_POLYBYTES - 1, NTRUPLUS_POLYBYTES, NTRUPLUS_POLYBYTES + 1,
};
static const size_t outlens[] = {
    1, 8, 31, 32, 33, 135, 136, 137, 191, 192, 271, 272, 273,
    NTRUPLUS_N / 4, NTRUPLUS_SSBYTES + NTRUPLUS_N / 4,
};

int main(void)
{
    size_t a, b, i;
    int fails = 0;
    int domains[3] = {0x00, 0x01, 0x02};
    int d;

    for (i = 0; i < MAXIN; i++) {
        msg[i] = next_byte();
    }

    for (d = 0; d < 3; d++) {
        for (a = 0; a < sizeof inlens / sizeof inlens[0]; a++) {
            for (b = 0; b < sizeof outlens / sizeof outlens[0]; b++) {
                size_t inlen = inlens[a], outlen = outlens[b];

                cat[0] = (uint8_t)domains[d];
                memcpy(cat + 1, msg, inlen);
                shake256(want, outlen, cat, inlen + 1);
                memset(got, 0, outlen);
                shake256_prefixed(got, outlen, (uint8_t)domains[d], msg, inlen);
                if (memcmp(want, got, outlen) != 0) {
                    if (fails < 3) {
                        printf("test_shake_prefixed: mismatch domain %02x "
                               "inlen %zu outlen %zu\n",
                               domains[d], inlen, outlen);
                    }
                    fails++;
                }
            }
        }
    }

    /* Exact input/output aliasing, as hash_f uses it. */
    memcpy(cat + 1, msg, NTRUPLUS_POLYBYTES);
    cat[0] = 0x00;
    shake256(want, 32, cat, NTRUPLUS_POLYBYTES + 1);
    memcpy(alias, msg, NTRUPLUS_POLYBYTES);
    shake256_prefixed(alias, 32, 0x00, alias, NTRUPLUS_POLYBYTES);
    if (memcmp(want, alias, 32) != 0) {
        printf("test_shake_prefixed: aliasing mismatch\n");
        fails++;
    }

    if (fails != 0) {
        printf("test_shake_prefixed: FAIL (%d)\n", fails);
        return 1;
    }
    printf("test_shake_prefixed: pass (%zu cases + aliasing)\n",
           3 * (sizeof inlens / sizeof inlens[0]) *
           (sizeof outlens / sizeof outlens[0]));
    return 0;
}
