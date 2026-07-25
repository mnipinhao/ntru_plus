/* Benchmark-only KEM namespace for the InvNTT Stage45 row-helper candidate. */
#define crypto_kem_keypair bench_crypto_kem_keypair_u01v3_candidate
#define crypto_kem_enc bench_crypto_kem_enc_u01v3_candidate
#define crypto_kem_dec bench_crypto_kem_dec_u01v3_candidate
#define poly_invntt poly_invntt_rminus1_stage45_row_helper

#include "ntruplus/kem.c"
