/*
 * SHA3 Keccak backend gate.
 *
 * keccakf1600_v84a.S must be a drop-in replacement for the scalar permutation in
 * keccakf1600.S: same output on every state, and AAPCS64-clean.  The second
 * property is not decoration -- the widely copied version of this routine uses
 * d8-d15 for state without saving them, which silently corrupts any caller that
 * keeps a live value there.
 *
 * Build:  cc -O2 -o test_keccak_v84a test/test_keccak_v84a.c keccakf1600.S keccakf1600_v84a.S
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#if !defined(__ARM_FEATURE_SHA3)
int main(void)
{
    printf("test_keccak_v84a: skipped (target has no FEAT_SHA3)\n");
    return 0;
}
#else

void ntruplus_keccak_f1600_x1_aarch64(uint64_t *state, const uint64_t *rc);
void ntruplus_keccak_f1600_x1_v84a_aarch64(uint64_t *state, const uint64_t *rc);

static const uint64_t round_constants[24] = {
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
    0x0000000080000001ULL, 0x8000000080008008ULL,
};

#define CASES 100003

static uint64_t rng_state = 0x243F6A8885A308D3ULL;

static uint64_t next(void)
{
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 7;
    rng_state ^= rng_state << 17;
    return rng_state;
}

/* Keeps eight doubles live across the call; they land in d8-d15. */
static double abi_probe(void (*permute)(uint64_t *, const uint64_t *),
                        uint64_t *state)
{
    volatile double a = 1.5, b = 2.5, c = 3.5, d = 4.5;
    volatile double e = 5.5, f = 6.5, g = 7.5, h = 8.5;

    permute(state, round_constants);
    return a + b + c + d + e + f + g + h;
}

int main(void)
{
    uint64_t scalar[25], ce[25];
    int mismatches = 0;
    int i, t;

    for (t = 0; t < CASES; t++) {
        for (i = 0; i < 25; i++) {
            uint64_t v;

            if (t == 0) {
                v = 0;
            } else if (t == 1) {
                v = ~0ULL;
            } else if (t == 2) {
                v = (uint64_t)i;
            } else {
                v = next();
            }
            scalar[i] = v;
            ce[i] = v;
        }
        ntruplus_keccak_f1600_x1_aarch64(scalar, round_constants);
        ntruplus_keccak_f1600_x1_v84a_aarch64(ce, round_constants);
        if (memcmp(scalar, ce, sizeof scalar) != 0) {
            if (mismatches < 3) {
                printf("test_keccak_v84a: mismatch at case %d\n", t);
            }
            mismatches++;
        }
    }

    for (i = 0; i < 25; i++) {
        scalar[i] = 0;
    }
    if (abi_probe(ntruplus_keccak_f1600_x1_v84a_aarch64, scalar) != 40.0) {
        printf("test_keccak_v84a: v8.4-A backend clobbers callee-saved d8-d15\n");
        mismatches++;
    }
    for (i = 0; i < 25; i++) {
        scalar[i] = 0;
    }
    if (abi_probe(ntruplus_keccak_f1600_x1_aarch64, scalar) != 40.0) {
        printf("test_keccak_v84a: scalar backend clobbers callee-saved d8-d15\n");
        mismatches++;
    }

    if (mismatches != 0) {
        printf("test_keccak_v84a: FAIL (%d)\n", mismatches);
        return 1;
    }
    printf("test_keccak_v84a: pass (%d states, d8-d15 preserved)\n", CASES);
    return 0;
}
#endif /* __ARM_FEATURE_SHA3 */
