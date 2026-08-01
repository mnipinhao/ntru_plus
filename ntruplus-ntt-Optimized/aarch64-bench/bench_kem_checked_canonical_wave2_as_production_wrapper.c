/* Benchmark-only Wave 2 namespace used as side A of a Wave 2/Wave 3 pair. */
#define crypto_kem_keypair bench_crypto_kem_keypair_u01v3_prod
#define crypto_kem_enc bench_crypto_kem_enc_u01v3_prod
#define crypto_kem_dec bench_crypto_kem_dec_u01v3_prod

#include "ntruplus/experiments/checked_canonical_decode/wave2_checked_kem_candidate.c"
