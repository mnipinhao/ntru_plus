#include "late067.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "api.h"

static int compare_case(unsigned trial, const uint8_t *ct, const uint8_t *sk,
	int expect_valid, const uint8_t *expected)
{
	uint8_t control[NTRUPLUS_SSBYTES];
	uint8_t candidate[NTRUPLUS_SSBYTES];
	const int control_status = crypto_kem_dec_control(control, ct, sk);
	const int candidate_status = crypto_kem_dec_latesoa(candidate, ct, sk);
	if (control_status != candidate_status
		|| memcmp(control, candidate, sizeof control) != 0) {
		fprintf(stderr, "Decap differential failed at trial %u\n", trial);
		return 1;
	}
	if (expect_valid != 0 && (control_status != 0
		|| memcmp(control, expected, sizeof control) != 0)) {
		fprintf(stderr, "valid Decap failed at trial %u\n", trial);
		return 1;
	}
	return 0;
}

int main(void)
{
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t sk[NTRUPLUS_SECRETKEYBYTES];
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t mutated[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t expected[NTRUPLUS_SSBYTES];
	unsigned valid = 0;
	unsigned invalid = 0;

	for (unsigned key = 0; key < 8; ++key) {
		if (crypto_kem_keypair(pk, sk) != 0)
			return 1;
		for (unsigned trial = 0; trial < 32; ++trial) {
			if (crypto_kem_enc(ct, expected, pk) != 0
				|| compare_case(valid, ct, sk, 1, expected) != 0)
				return 1;
			++valid;
			if (trial < 8) {
				memcpy(mutated, ct, sizeof mutated);
				mutated[(37U * trial + 11U * key) % sizeof mutated]
					^= (uint8_t)(1U << ((trial + key) & 7U));
				if (compare_case(invalid, mutated, sk, 0, NULL) != 0)
					return 1;
				++invalid;
			}
		}
	}

	static const uint8_t fills[] = {0x00, 0xff, 0x55, 0xaa, 0x80};
	for (unsigned i = 0; i < sizeof fills; ++i) {
		memset(mutated, fills[i], sizeof mutated);
		if (compare_case(invalid, mutated, sk, 0, NULL) != 0)
			return 1;
		++invalid;
	}

	printf("Late-SoA 067 production correctness passed: valid=%u invalid=%u "
	       "status=exact ss=byte-exact\n", valid, invalid);
	return 0;
}
