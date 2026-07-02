/*
 * Benchmark-only GT KEM wrapper for the hier_k8 scaled-baseinv candidate.
 *
 * The production poly_baseinv_scaled_r() symbol is left unchanged.  This
 * wrapper compiles kem.c with the keypair baseinv call rebound to the explicit
 * candidate symbol so current and candidate keypairs can coexist in one binary.
 */
#define crypto_kem_keypair bench_crypto_kem_keypair_hier_k8
#define crypto_kem_enc bench_crypto_kem_enc_hier_k8
#define crypto_kem_dec bench_crypto_kem_dec_hier_k8
#define poly_baseinv_scaled_r poly_baseinv_scaled_r_hier_k8_candidate

#define GT_PRODUCTION_USE_SCALED_KEYPAIR 1
#define GT_PRODUCTION_USE_RMINUS1_DECAP 1
#define GT_BASEINV_BATCH_USE_ASM_FINISH 1

#include "ntruplus/kem.c"
