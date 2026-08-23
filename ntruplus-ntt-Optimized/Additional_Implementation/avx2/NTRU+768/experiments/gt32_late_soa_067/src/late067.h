#ifndef GT32_LATE_SOA_067_H
#define GT32_LATE_SOA_067_H

#include <stdint.h>

#include "params.h"

int ntruplus768_dec_control(uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);
int ntruplus768_dec_latesoa(uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

int crypto_kem_dec_control(unsigned char *ss, const unsigned char *ct,
	const unsigned char *sk);
int crypto_kem_dec_latesoa(unsigned char *ss, const unsigned char *ct,
	const unsigned char *sk);

#endif
