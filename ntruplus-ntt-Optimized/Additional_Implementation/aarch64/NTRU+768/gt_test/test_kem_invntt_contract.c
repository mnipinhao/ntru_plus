#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "../api.h"

#ifndef KEM_CONTRACT_TESTS
#define KEM_CONTRACT_TESTS 64
#endif

int crypto_kem_keypair(uint8_t *pk, uint8_t *sk);
int crypto_kem_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int crypto_kem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);

int main(void)
{
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t sk[NTRUPLUS_SECRETKEYBYTES];
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t ss_enc[NTRUPLUS_SSBYTES];
	uint8_t ss_dec[NTRUPLUS_SSBYTES];

	for (int i = 0; i < KEM_CONTRACT_TESTS; i++)
	{
		if (crypto_kem_keypair(pk, sk) != 0)
		{
			printf("crypto_kem_keypair failed at %d\n", i);
			return 1;
		}

		if (crypto_kem_enc(ct, ss_enc, pk) != 0)
		{
			printf("crypto_kem_enc failed at %d\n", i);
			return 1;
		}

		const int dec_fail = crypto_kem_dec(ss_dec, ct, sk);

		if (memcmp(ss_enc, ss_dec, sizeof(ss_enc)) != 0)
		{
			printf("KEM shared-secret mismatch at %d (dec_fail=%d)\n",
			       i, dec_fail);
			return 1;
		}
	}

	printf("KEM inverse-output representative contract ok (%d cases)\n",
	       KEM_CONTRACT_TESTS);
	return 0;
}
