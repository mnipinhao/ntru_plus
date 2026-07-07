/*
 * Link-only guard binary for the no-Q31 GT production variant.
 *
 * The release script checks this binary to ensure the direct32 Q31 helper is
 * absent when the fallback/no-Q31 production variant is selected.
 */
#include <stdint.h>

int bench_crypto_kem_keypair_current(uint8_t *pk, uint8_t *sk);
int bench_crypto_kem_enc_current(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int bench_crypto_kem_dec_current(uint8_t *ss, const uint8_t *ct,
                                 const uint8_t *sk);

typedef int (*keypair_fn)(uint8_t *pk, uint8_t *sk);
typedef int (*enc_fn)(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
typedef int (*dec_fn)(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);

static keypair_fn keypair_symbols[] = {
    bench_crypto_kem_keypair_current,
};

static enc_fn enc_symbols[] = {
    bench_crypto_kem_enc_current,
};

static dec_fn dec_symbols[] = {
    bench_crypto_kem_dec_current,
};

int main(void)
{
    return keypair_symbols[0] == 0 || enc_symbols[0] == 0 ||
           dec_symbols[0] == 0;
}
