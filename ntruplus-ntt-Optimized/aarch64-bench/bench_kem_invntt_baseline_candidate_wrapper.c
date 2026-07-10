/* Benchmark-only historical InvNTT KEM namespace. */
#define crypto_kem_keypair bench_crypto_kem_keypair_u01v3_candidate
#define crypto_kem_enc bench_crypto_kem_enc_u01v3_candidate
#define crypto_kem_dec bench_crypto_kem_dec_u01v3_candidate
#define poly_invntt_from_rminus1 poly_invntt_from_rminus1_baseline

#include "ntruplus/kem.c"
