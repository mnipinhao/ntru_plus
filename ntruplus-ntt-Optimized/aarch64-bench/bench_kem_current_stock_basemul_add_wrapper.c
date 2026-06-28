/*
 * Benchmark-only GT KEM wrapper with a cross-backend poly_basemul_add gate.
 *
 * GT_USE_STOCK_BASEMUL_ADD_EXPERIMENTAL is intentionally opt-in and should
 * only be used by the PMU/correctness gate.  It replaces the encap
 * poly_basemul_add call in kem.c with a renamed stock NO_CE implementation
 * while keeping the rest of the GT production path unchanged.
 */
#ifndef GT_USE_STOCK_BASEMUL_ADD_EXPERIMENTAL
#error "GT_USE_STOCK_BASEMUL_ADD_EXPERIMENTAL must be explicitly enabled"
#endif

#define crypto_kem_keypair bench_crypto_kem_keypair_stock_basemul_add
#define crypto_kem_enc bench_crypto_kem_enc_stock_basemul_add
#define crypto_kem_dec bench_crypto_kem_dec_stock_basemul_add

#define GT_PRODUCTION_USE_SCALED_KEYPAIR 1
#define GT_PRODUCTION_USE_RMINUS1_DECAP 1
#define GT_BASEINV_BATCH_USE_ASM_FINISH 1

#define poly_basemul_add poly_basemul_add_stock_noce_experimental

#include "ntruplus/kem.c"
