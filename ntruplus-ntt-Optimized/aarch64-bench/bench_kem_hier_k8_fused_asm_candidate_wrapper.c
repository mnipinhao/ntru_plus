/*
 * Benchmark-only GT KEM wrapper for the fused HIER_K8 prepare ASM candidate.
 * Production dispatch remains unchanged.
 */
#define crypto_kem_keypair bench_crypto_kem_keypair_hier_k8_fused_asm_candidate
#define crypto_kem_enc bench_crypto_kem_enc_hier_k8_fused_asm_candidate
#define crypto_kem_dec bench_crypto_kem_dec_hier_k8_fused_asm_candidate
#define poly_baseinv_scaled_r \
  poly_baseinv_scaled_r_hier_k8_prepare_fused_asm_candidate

#define GT_PRODUCTION_USE_SCALED_KEYPAIR 1
#define GT_PRODUCTION_USE_RMINUS1_DECAP 1
#define GT_BASEINV_BATCH_USE_ASM_FINISH 1
#define GT_EXPERIMENT_USE_HIERK8_FUSED_ASM_CANDIDATE 1

#include "ntruplus/kem.c"
