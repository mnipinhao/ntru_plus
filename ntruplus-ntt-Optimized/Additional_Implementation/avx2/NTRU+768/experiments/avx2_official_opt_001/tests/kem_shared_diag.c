#define poly_basemul ntruplus768_officialopt_shared_basemul
#include "../src/kem_shared.c"

int officialopt_shared_enc_derand(uint8_t *ct, uint8_t *ss,
                                  const uint8_t *pk, const uint8_t *coins) {
    return crypto_kem_enc_derand(ct, ss, pk, coins);
}
