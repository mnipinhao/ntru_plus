/* Benchmark-only KEM namespace using the fixed-fqinv hierarchical backend. */
#define crypto_kem_keypair bench_crypto_kem_keypair_u01v3_candidate
#define crypto_kem_enc bench_crypto_kem_enc_u01v3_candidate
#define crypto_kem_dec bench_crypto_kem_dec_u01v3_candidate
#define poly_baseinv_scaled_r poly_baseinv_scaled_r_fqinv15_fixed_candidate
#define gt_keygen_baseinv_cq_to_cq_scaled_r \
  gt_keygen_baseinv_cq_to_cq_scaled_r_fqinv15_fixed_candidate

#include "ntruplus/kem.c"
