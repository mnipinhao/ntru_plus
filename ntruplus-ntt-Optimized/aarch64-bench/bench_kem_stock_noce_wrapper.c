/*
 * Benchmark-only stock NO_CE KEM wrapper.
 *
 * This compiles kem.c without GT production macros and renames public symbols
 * so the non-hash substage PMU harness can prepare stock-valid KEM inputs.
 */
#define crypto_kem_keypair bench_crypto_kem_keypair_stock
#define crypto_kem_enc bench_crypto_kem_enc_stock
#define crypto_kem_dec bench_crypto_kem_dec_stock

#include "ntruplus/kem.c"
