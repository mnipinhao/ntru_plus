/* Benchmark-only KEM wrapper for the two-block fused HIER_K8 prepare ASM. */
#define crypto_kem_keypair \
  bench_crypto_kem_keypair_hier_k8_prepare2_fused_asm_candidate
#define crypto_kem_enc bench_crypto_kem_enc_hier_k8_prepare2_fused_asm_candidate
#define crypto_kem_dec bench_crypto_kem_dec_hier_k8_prepare2_fused_asm_candidate
#define poly_baseinv_scaled_r \
  poly_baseinv_scaled_r_hier_k8_prepare2_fused_asm_candidate

#define GT_PRODUCTION_USE_SCALED_KEYPAIR 1
#define GT_PRODUCTION_USE_RMINUS1_DECAP 1
#define GT_BASEINV_BATCH_USE_ASM_FINISH 1
#define GT_EXPERIMENT_USE_HIERK8_PREPARE2_FUSED_ASM_CANDIDATE 1

#include "ntruplus/kem.c"
