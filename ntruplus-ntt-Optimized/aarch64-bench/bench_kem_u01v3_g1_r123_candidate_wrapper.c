/* Benchmark-only G1R123+S2 KEM namespace for same-binary paired PMU. */
#define crypto_kem_keypair bench_crypto_kem_keypair_u01v3_candidate
#define crypto_kem_enc bench_crypto_kem_enc_u01v3_candidate
#define crypto_kem_dec bench_crypto_kem_dec_u01v3_candidate
#define poly_ntt poly_ntt_u01v3_g1_r123_s2

#include "ntruplus/kem.c"
