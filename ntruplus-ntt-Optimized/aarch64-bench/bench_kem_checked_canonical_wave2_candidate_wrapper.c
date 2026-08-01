/* Benchmark-only Wave 2 checked-canonical KEM namespace. */
#define crypto_kem_keypair bench_crypto_kem_keypair_u01v3_candidate
#define crypto_kem_enc bench_crypto_kem_enc_u01v3_candidate
#define crypto_kem_dec bench_crypto_kem_dec_u01v3_candidate

#include "ntruplus/experiments/checked_canonical_decode/wave2_checked_kem_candidate.c"
