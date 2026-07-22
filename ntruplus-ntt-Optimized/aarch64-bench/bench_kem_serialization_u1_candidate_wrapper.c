/* Benchmark-only U1 unpack KEM namespace for same-binary PMU. */
#define crypto_kem_keypair bench_crypto_kem_keypair_u01v3_candidate
#define crypto_kem_enc bench_crypto_kem_enc_u01v3_candidate
#define crypto_kem_dec bench_crypto_kem_dec_u01v3_candidate
#define poly_frombytes_gt_canonical poly_frombytes_gt_canonical_u1

#include "ntruplus/kem.c"
