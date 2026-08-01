/*
 * Benchmark-only attribution variant.
 *
 * It preserves checked canonical input rejection and zero failure outputs but
 * disables caller-scratch clearing so the valid-path PMU delta isolates the
 * scalar checked-decode integration cost. It is not a promotion candidate.
 */
#define crypto_kem_keypair bench_crypto_kem_keypair_u01v3_candidate
#define crypto_kem_enc bench_crypto_kem_enc_u01v3_candidate
#define crypto_kem_dec bench_crypto_kem_dec_u01v3_candidate
#define GT_EXPERIMENT_WAVE2_DISABLE_SCRATCH_CLEAR

#include "ntruplus/experiments/checked_canonical_decode/wave2_checked_kem_candidate.c"
