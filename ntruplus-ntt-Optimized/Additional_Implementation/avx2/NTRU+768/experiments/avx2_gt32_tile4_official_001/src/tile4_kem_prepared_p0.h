#ifndef NTRUPLUS_GT32_TILE4_KEM_PREPARED_P0_H
#define NTRUPLUS_GT32_TILE4_KEM_PREPARED_P0_H

#include <stdint.h>

#include "api.h"
#include "params.h"
#include "tile4.h"
#include "tile4_prepared_fixed_b3.h"

typedef struct __attribute__((aligned(64))) {
	gt32_prepared_fixed_b3_general_e1 h_matrix;
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES];
} gt32_prepared_pk_p0;

typedef struct __attribute__((aligned(64))) {
	int16_t f[GT32_TILE4_POLY_WORDS];
	gt32_prepared_fixed_b3_general_e1 hinv_matrix;
	uint8_t hash_key[NTRUPLUS_SYMBYTES];
} gt32_prepared_sk_p0;

int gt32_prepare_pk_p0(gt32_prepared_pk_p0 *ctx,
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES]);
int gt32_prepare_sk_p0(gt32_prepared_sk_p0 *ctx,
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

int gt32_enc_derand_prepared_p0(
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES],
	const gt32_prepared_pk_p0 *ctx,
	const uint8_t coins[NTRUPLUS_N / 8]);
int gt32_dec_prepared_p0(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const gt32_prepared_sk_p0 *ctx);

#endif
