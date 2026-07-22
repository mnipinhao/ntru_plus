/* Benchmark-only P1 pack KEM namespace for same-binary PMU. */
#define crypto_kem_keypair bench_crypto_kem_keypair_u01v3_candidate
#define crypto_kem_enc bench_crypto_kem_enc_u01v3_candidate
#define crypto_kem_dec bench_crypto_kem_dec_u01v3_candidate
#define poly_tobytes_gt_canonical poly_tobytes_gt_canonical_p1

#include "ntruplus/kem.c"
