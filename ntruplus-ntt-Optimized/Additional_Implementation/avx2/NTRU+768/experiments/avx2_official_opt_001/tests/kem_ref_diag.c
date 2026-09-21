#include "../src/kem_reference.c"

int officialopt_ref_enc_derand(uint8_t *ct, uint8_t *ss,
                               const uint8_t *pk, const uint8_t *coins) {
    return crypto_kem_enc_derand(ct, ss, pk, coins);
}
