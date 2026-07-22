/* Benchmark-only Q31 pair-pipeline KEM namespace for same-binary PMU. */
#define crypto_kem_keypair bench_crypto_kem_keypair_u01v3_candidate
#define crypto_kem_enc bench_crypto_kem_enc_u01v3_candidate
#define crypto_kem_dec bench_crypto_kem_dec_u01v3_candidate
#define poly_basemul_add_encap_direct32_q31_tobytes_contract \
  poly_basemul_add_encap_direct32_q31_pair_slothy

#include "ntruplus/kem.c"
