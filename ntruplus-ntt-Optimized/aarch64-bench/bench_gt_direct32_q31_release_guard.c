/*
 * Link-only release guard binary for the direct32 Q31 encap opt-in.
 *
 * This intentionally does not call the benchmark-only direct micro target.
 * The nm/objdump guard checks this binary so the Q31 assembly symbol is only
 * reachable through the encap tobytes-contract helper.
 */
#include <stdint.h>

int bench_crypto_kem_keypair_current(uint8_t *pk, uint8_t *sk);
int bench_crypto_kem_enc_current(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int bench_crypto_kem_dec_current(uint8_t *ss, const uint8_t *ct,
                                 const uint8_t *sk);

int bench_crypto_kem_keypair_direct32_q31_basemul_add(uint8_t *pk,
                                                      uint8_t *sk);
int bench_crypto_kem_enc_direct32_q31_basemul_add(uint8_t *ct, uint8_t *ss,
                                                  const uint8_t *pk);
int bench_crypto_kem_dec_direct32_q31_basemul_add(uint8_t *ss,
                                                  const uint8_t *ct,
                                                  const uint8_t *sk);

typedef int (*keypair_fn)(uint8_t *pk, uint8_t *sk);
typedef int (*enc_fn)(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
typedef int (*dec_fn)(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);

static keypair_fn keypair_symbols[] = {
    bench_crypto_kem_keypair_current,
    bench_crypto_kem_keypair_direct32_q31_basemul_add,
};

static enc_fn enc_symbols[] = {
    bench_crypto_kem_enc_current,
    bench_crypto_kem_enc_direct32_q31_basemul_add,
};

static dec_fn dec_symbols[] = {
    bench_crypto_kem_dec_current,
    bench_crypto_kem_dec_direct32_q31_basemul_add,
};

int main(void)
{
    return keypair_symbols[0] == 0 || keypair_symbols[1] == 0 ||
           enc_symbols[0] == 0 || enc_symbols[1] == 0 ||
           dec_symbols[0] == 0 || dec_symbols[1] == 0;
}
