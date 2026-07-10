/* Benchmark-only KEM namespace for the lazy Stage123+len16 InvNTT. */
#define crypto_kem_keypair bench_crypto_kem_keypair_u01v3_candidate
#define crypto_kem_enc bench_crypto_kem_enc_u01v3_candidate
#define crypto_kem_dec bench_crypto_kem_dec_u01v3_candidate
#define poly_invntt_from_rminus1 poly_invntt_rminus1_lazy_twiddle1_stage123_len16

#include "ntruplus/kem.c"
