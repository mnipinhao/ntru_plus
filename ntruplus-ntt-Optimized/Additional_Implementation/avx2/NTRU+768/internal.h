#ifndef NTRUPLUS768_AVX2_CLEAN_INTERNAL_H
#define NTRUPLUS768_AVX2_CLEAN_INTERNAL_H

#include <stdint.h>

#include "params.h"

#define NTRUPLUS768_POLY_WORDS NTRUPLUS_N
#define NTRUPLUS768_SERIALIZED_BYTES NTRUPLUS_POLYBYTES

/* Coefficient-order input -> shared GT frontend state. */
void ntruplus768_ntt_frontend_avx2(int16_t out[NTRUPLUS_N],
	const int16_t in[NTRUPLUS_N]);

/* Frontend state -> persistent M or key-generation P representation. */
void ntruplus768_ntt_m_avx2(int16_t out[NTRUPLUS_N],
	const int16_t frontend[NTRUPLUS_N]);
void ntruplus768_ntt_p_avx2(int16_t out[NTRUPLUS_N],
	const int16_t frontend[NTRUPLUS_N]);

void ntruplus768_basemul_scale_m_avx2(int16_t out[NTRUPLUS_N],
	const int16_t a[NTRUPLUS_N], const int16_t b[NTRUPLUS_N]);
void ntruplus768_basemul_general_m_avx2(int16_t out[NTRUPLUS_N],
	const int16_t a[NTRUPLUS_N], const int16_t b[NTRUPLUS_N]);
void ntruplus768_basemul_f0_j1_avx2(int16_t out[NTRUPLUS_N],
	const int16_t f0[NTRUPLUS_N], const int16_t j1[NTRUPLUS_N]);

int ntruplus768_baseinv_j1_avx2(int16_t out[NTRUPLUS_N],
	const int16_t in[NTRUPLUS_N]);
void ntruplus768_invntt_m_avx2(int16_t out[NTRUPLUS_N],
	const int16_t in[NTRUPLUS_N]);
void ntruplus768_invntt_tail_avx2(int16_t out[NTRUPLUS_N],
	const int16_t in[NTRUPLUS_N]);

int ntruplus768_unpack_m_avx2(int16_t out[NTRUPLUS_N],
	const uint8_t in[NTRUPLUS_POLYBYTES]);
int ntruplus768_unpack3_m_avx2(int16_t c[NTRUPLUS_N],
	int16_t f[NTRUPLUS_N], int16_t hinv[NTRUPLUS_N],
	const uint8_t ct[NTRUPLUS_POLYBYTES],
	const uint8_t sk[2 * NTRUPLUS_POLYBYTES]);

void ntruplus768_pack_m_centered_avx2(
	uint8_t out[NTRUPLUS_POLYBYTES], const int16_t in[NTRUPLUS_N]);
void ntruplus768_pack_m_lazy10788_avx2(
	uint8_t out[NTRUPLUS_POLYBYTES], const int16_t in[NTRUPLUS_N]);
void ntruplus768_pack_m_highrange12699_avx2(
	uint8_t out[NTRUPLUS_POLYBYTES], const int16_t in[NTRUPLUS_N]);
void ntruplus768_pack_p_sp1_lazy10788_avx2(
	uint8_t out[NTRUPLUS_POLYBYTES], const int16_t in[NTRUPLUS_N]);

int ntruplus768_equal_m_modq12699_avx2(
	const int16_t recovered[NTRUPLUS_N],
	const int16_t derived[NTRUPLUS_N]);

int ntruplus768_keypair_impl(uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);
int ntruplus768_enc_derand_impl(uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);
int ntruplus768_dec_impl(uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

#endif
