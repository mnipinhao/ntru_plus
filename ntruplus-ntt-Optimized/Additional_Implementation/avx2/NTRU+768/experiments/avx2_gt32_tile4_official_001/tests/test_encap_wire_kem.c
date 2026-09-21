#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "internal.h"
#include "kat/rng.h"

int ntruplus768_wire_research_enc_derand_impl(uint8_t *, uint8_t *,
    const uint8_t *, const uint8_t *, int);

static int same(const uint8_t *a, const uint8_t *b, size_t n) {
    return memcmp(a, b, n) == 0;
}

int main(void) {
    uint8_t entropy[48];
    uint8_t pk[NTRUPLUS_PUBLICKEYBYTES], sk[NTRUPLUS_SECRETKEYBYTES];
    uint8_t coins[NTRUPLUS_N / 8];
    uint8_t control_ct[NTRUPLUS_CIPHERTEXTBYTES];
    uint8_t wire1_ct[NTRUPLUS_CIPHERTEXTBYTES];
    uint8_t wire2_ct[NTRUPLUS_CIPHERTEXTBYTES];
    uint8_t bad_ct[NTRUPLUS_CIPHERTEXTBYTES];
    uint8_t control_ss[NTRUPLUS_SSBYTES], wire1_ss[NTRUPLUS_SSBYTES];
    uint8_t wire2_ss[NTRUPLUS_SSBYTES], dec_ss[NTRUPLUS_SSBYTES];
    uint8_t bad_ss[NTRUPLUS_SSBYTES], bad_ss_again[NTRUPLUS_SSBYTES];

    for (size_t i = 0; i < sizeof entropy; i++)
        entropy[i] = (uint8_t)(19U + 23U * i);
    randombytes_init(entropy, NULL, 256);
    if (ntruplus768_keypair_impl(pk, sk) != 0) {
        fputs("keypair failed\n", stderr);
        return 1;
    }
    for (unsigned trial = 0; trial < 100; trial++) {
        for (size_t i = 0; i < sizeof coins; i++)
            coins[i] = (uint8_t)(trial * 73U + i * 19U);
        int control = ntruplus768_enc_derand_impl(control_ct, control_ss,
            pk, coins);
        int wire1 = ntruplus768_wire_research_enc_derand_impl(wire1_ct,
            wire1_ss, pk, coins, 0);
        int wire2 = ntruplus768_wire_research_enc_derand_impl(wire2_ct,
            wire2_ss, pk, coins, 1);
        if (control || wire1 != control || wire2 != control ||
            !same(control_ct, wire1_ct, sizeof control_ct) ||
            !same(control_ct, wire2_ct, sizeof control_ct) ||
            !same(control_ss, wire1_ss, sizeof control_ss) ||
            !same(control_ss, wire2_ss, sizeof control_ss)) {
            fprintf(stderr, "encap mismatch at trial %u\n", trial);
            return 1;
        }
        if (ntruplus768_dec_impl(dec_ss, wire1_ct, sk) != 0 ||
            !same(dec_ss, wire1_ss, sizeof dec_ss)) {
            fprintf(stderr, "valid decap mismatch at trial %u\n", trial);
            return 1;
        }
        memcpy(bad_ct, wire2_ct, sizeof bad_ct);
        bad_ct[(trial * 17U) % sizeof bad_ct] ^= (uint8_t)(1U << (trial & 7U));
        int bad = ntruplus768_dec_impl(bad_ss, bad_ct, sk);
        int again = ntruplus768_dec_impl(bad_ss_again, bad_ct, sk);
        const uint8_t cleared[NTRUPLUS_SSBYTES] = {0};
        if (bad != 1 || again != 1 ||
            !same(bad_ss, cleared, sizeof bad_ss) ||
            !same(bad_ss, bad_ss_again, sizeof bad_ss)) {
            fprintf(stderr, "invalid CT behavior unstable at trial %u\n", trial);
            return 1;
        }
    }
    puts("W-Montgomery generated-key KEM differential: pass (100 vectors)");
    return 0;
}
