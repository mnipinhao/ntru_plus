/*
 * Benchmark-only current-production KEM wrapper.
 *
 * This compiles kem.c once with the selected production variant macros from
 * the aarch64-bench Makefile and renamed public symbols so PMU harnesses can
 * compare it against local explicit variants in the same binary.
 */
#define crypto_kem_keypair bench_crypto_kem_keypair_current
#define crypto_kem_enc bench_crypto_kem_enc_current
#define crypto_kem_dec bench_crypto_kem_dec_current

#include "ntruplus/kem.c"
