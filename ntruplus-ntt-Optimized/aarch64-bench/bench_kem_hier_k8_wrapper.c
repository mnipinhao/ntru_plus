/*
 * Benchmark-only GT KEM wrapper for the explicit hier_k8 scaled-baseinv path.
 *
 * GT production now enables hier_k8 through gt_production_variants.mk. This
 * wrapper still compiles kem.c with the keypair baseinv call rebound to the
 * explicit candidate symbol, so production and explicit-hier keypairs can
 * coexist in one binary for byte-differential sanity checks.
 */
#define crypto_kem_keypair bench_crypto_kem_keypair_hier_k8
#define crypto_kem_enc bench_crypto_kem_enc_hier_k8
#define crypto_kem_dec bench_crypto_kem_dec_hier_k8
#define poly_baseinv_scaled_r poly_baseinv_scaled_r_hier_k8_candidate

#define GT_PRODUCTION_USE_SCALED_KEYPAIR 1
#define GT_PRODUCTION_USE_RMINUS1_DECAP 1
#define GT_BASEINV_BATCH_USE_ASM_FINISH 1

#include "ntruplus/kem.c"
