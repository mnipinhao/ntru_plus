/*
 * Benchmark-only current-production KEM wrapper with the decap verify
 * basemul->tobytes C candidate contract gate enabled.
 *
 * This does not replace generic poly_basemul.  It only changes the local decap
 * verify block from:
 *
 *   poly_basemul(&r2, &c, &hinv);
 *   poly_tobytes(buf1, &r2);
 *
 * to the C byte-output candidate helper.
 */
#define crypto_kem_keypair bench_crypto_kem_keypair_decap_verify_contract_c
#define crypto_kem_enc bench_crypto_kem_enc_decap_verify_contract_c
#define crypto_kem_dec bench_crypto_kem_dec_decap_verify_contract_c

#define GT_PRODUCTION_USE_SCALED_KEYPAIR 1
#define GT_PRODUCTION_USE_RMINUS1_DECAP 1
#define GT_BASEINV_BATCH_USE_ASM_FINISH 1
#define GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_C 1

#include "ntruplus/kem.c"
