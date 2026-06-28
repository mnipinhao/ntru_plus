/*
 * Benchmark-only GT KEM wrapper with direct32 poly_basemul_add finalizer.
 *
 * This keeps the GT production KEM path unchanged except for the encap
 * poly_basemul_add call.  The direct32 prototype is intentionally opt-in and
 * is used only by the PMU/correctness gate.
 */
#ifndef GT_USE_DIRECT32_BASEMUL_ADD_EXPERIMENTAL
#error "GT_USE_DIRECT32_BASEMUL_ADD_EXPERIMENTAL must be explicitly enabled"
#endif

#define crypto_kem_keypair bench_crypto_kem_keypair_direct32_basemul_add
#define crypto_kem_enc bench_crypto_kem_enc_direct32_basemul_add
#define crypto_kem_dec bench_crypto_kem_dec_direct32_basemul_add

#define GT_PRODUCTION_USE_SCALED_KEYPAIR 1
#define GT_PRODUCTION_USE_RMINUS1_DECAP 1
#define GT_BASEINV_BATCH_USE_ASM_FINISH 1

#define poly_basemul_add poly_basemul_add_direct32_finalizer_prototype

#include "ntruplus/kem.c"
