#ifndef NTRUPLUS_GT_KEYGEN_NATIVE_H
#define NTRUPLUS_GT_KEYGEN_NATIVE_H

#include <stdint.h>

#include "params.h"
#include "poly.h"

void gt_poly_ntt_lazy(poly *out, const poly *in);
int gt_poly_baseinv_l3(poly *out, const poly *in);
void gt_poly_basemul_native(poly *out, const poly *a, const poly *b);

int ntruplus_gt_keypair_derand(
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	uint8_t sk[NTRUPLUS_SECRETKEYBYTES],
	const uint8_t f_coins[NTRUPLUS_SYMBYTES],
	const uint8_t g_coins[NTRUPLUS_SYMBYTES]);

int crypto_kem_keypair_gt(unsigned char *pk, unsigned char *sk);

#endif
