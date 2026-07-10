/* Benchmark-only production KEM namespace for same-binary paired PMU. */
#define crypto_kem_keypair bench_crypto_kem_keypair_u01v3_prod
#define crypto_kem_enc bench_crypto_kem_enc_u01v3_prod
#define crypto_kem_dec bench_crypto_kem_dec_u01v3_prod

#include "ntruplus/kem.c"
