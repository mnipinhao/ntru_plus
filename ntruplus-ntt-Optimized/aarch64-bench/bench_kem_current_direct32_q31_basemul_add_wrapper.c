/*
 * Benchmark-only GT KEM wrapper with the production-like encap-only direct32
 * Q31 tobytes-contract gate.
 *
 * This keeps the GT production KEM path unchanged except for enabling the
 * explicit encap gate in kem.c.  It does not macro-replace generic
 * poly_basemul_add and is used only by the PMU/correctness gate.
 */
#define crypto_kem_keypair bench_crypto_kem_keypair_direct32_q31_basemul_add
#define crypto_kem_enc bench_crypto_kem_enc_direct32_q31_basemul_add
#define crypto_kem_dec bench_crypto_kem_dec_direct32_q31_basemul_add

#define GT_PRODUCTION_USE_SCALED_KEYPAIR 1
#define GT_PRODUCTION_USE_RMINUS1_DECAP 1
#define GT_BASEINV_BATCH_USE_ASM_FINISH 1
#define GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP 1

#include "ntruplus/kem.c"
