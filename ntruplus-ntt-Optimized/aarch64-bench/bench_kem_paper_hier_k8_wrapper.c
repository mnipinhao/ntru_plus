/* Benchmark-only KEM wrapper for the paper-exact recursive hier_k8 core. */
#define crypto_kem_keypair bench_crypto_kem_keypair_paper_hier_k8
#define crypto_kem_enc bench_crypto_kem_enc_paper_hier_k8
#define crypto_kem_dec bench_crypto_kem_dec_paper_hier_k8
#define poly_baseinv_scaled_r poly_baseinv_scaled_r_paper_hier_k8_for_bench

#include "ntruplus/kem.c"
