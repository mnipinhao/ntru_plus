#include <stdio.h>
#include <string.h>

#include "api.h"

#define FULL_C_KEM_SMOKE_ITERATIONS 8

int main(void)
{
	unsigned char pk[CRYPTO_PUBLICKEYBYTES];
	unsigned char sk[CRYPTO_SECRETKEYBYTES];
	unsigned char ct[CRYPTO_CIPHERTEXTBYTES];
	unsigned char ss_enc[CRYPTO_BYTES];
	unsigned char ss_dec[CRYPTO_BYTES];

	for (int i = 0; i < FULL_C_KEM_SMOKE_ITERATIONS; i++)
	{
		if (crypto_kem_keypair(pk, sk) != 0)
		{
			printf("full_c_kem_smoke: keypair failed at iteration %d\n", i);
			return 1;
		}

		if (crypto_kem_enc(ct, ss_enc, pk) != 0)
		{
			printf("full_c_kem_smoke: encaps failed at iteration %d\n", i);
			return 1;
		}

		if (crypto_kem_dec(ss_dec, ct, sk) != 0)
		{
			printf("full_c_kem_smoke: decaps failed at iteration %d\n", i);
			return 1;
		}

		if (memcmp(ss_enc, ss_dec, sizeof ss_enc) != 0)
		{
			printf("full_c_kem_smoke: shared-secret mismatch at iteration %d\n",
			       i);
			return 1;
		}
	}

	printf("full_c_kem_smoke: iterations=%d mismatches=0\n",
	       FULL_C_KEM_SMOKE_ITERATIONS);
	return 0;
}
