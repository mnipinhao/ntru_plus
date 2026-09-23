/*
 * Diagnostic KEM translation unit for the same-ELF caller-lazy pricing bench:
 * the given kem.c (Official or src/kem_lazy.c) plus an exported wrapper of
 * its static crypto_kem_enc_derand, as NTRU+768 tests/kem_{ref,lazy}_diag.c.
 * Never part of an exported implementation.
 */
#include KEM_SOURCE

int DERAND_NAME(uint8_t *ct, uint8_t *ss, const uint8_t *pk, const uint8_t *coins) {
    return crypto_kem_enc_derand(ct, ss, pk, coins);
}
