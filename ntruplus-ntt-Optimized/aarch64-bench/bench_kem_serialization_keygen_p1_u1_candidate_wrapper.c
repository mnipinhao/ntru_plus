/* Benchmark-only keygen-P1 plus U1-unpack KEM namespace. */
#include "ntruplus/poly.h"

void poly_tobytes_gt_canonical_p1(uint8_t r[NTRUPLUS_POLYBYTES],
                                  const poly *a);
void poly_frombytes_gt_canonical_u1(poly *r,
                                    const uint8_t a[NTRUPLUS_POLYBYTES]);

#define crypto_kem_keypair bench_crypto_kem_keypair_u01v3_candidate
#define crypto_kem_enc bench_crypto_kem_enc_u01v3_candidate
#define crypto_kem_dec bench_crypto_kem_dec_u01v3_candidate
#define GT_KEYGEN_POLY_TOBYTES poly_tobytes_gt_canonical_p1
#define poly_frombytes_gt_canonical poly_frombytes_gt_canonical_u1

#include "ntruplus/kem.c"
