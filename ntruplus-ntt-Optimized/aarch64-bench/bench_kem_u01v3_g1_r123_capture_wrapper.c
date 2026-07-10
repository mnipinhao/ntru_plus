/*
 * Preparation-only KEM namespace. Its NTT hook captures the four real
 * encap/decap inputs and then delegates to production poly_ntt.
 */
#define crypto_kem_keypair bench_crypto_kem_keypair_u01v3_capture
#define crypto_kem_enc bench_crypto_kem_enc_u01v3_capture
#define crypto_kem_dec bench_crypto_kem_dec_u01v3_capture
#define poly_ntt bench_u01v3_capture_poly_ntt

#include "ntruplus/kem.c"
