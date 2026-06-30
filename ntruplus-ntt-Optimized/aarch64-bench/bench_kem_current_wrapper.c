/*
 * Benchmark-only current-production KEM wrapper.
 *
 * This compiles kem.c once with the current gt_production decap contract and
 * renamed public symbols so a PMU harness can compare it against local
 * explicit/fused decap variants in the same binary.
 */
#define crypto_kem_keypair bench_crypto_kem_keypair_current
#define crypto_kem_enc bench_crypto_kem_enc_current
#define crypto_kem_dec bench_crypto_kem_dec_current

#define GT_PRODUCTION_USE_SCALED_KEYPAIR 1
#define GT_PRODUCTION_USE_RMINUS1_DECAP 1
#define GT_BASEINV_BATCH_USE_ASM_FINISH 1

#include "ntruplus/kem.c"
