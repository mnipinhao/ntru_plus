#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "internal.h"
#include "working_set_057.h"

static uint64_t rng_state = UINT64_C(0x057a91c65e4f237b);

static uint32_t random32(void)
{
	rng_state ^= rng_state << 13;
	rng_state ^= rng_state >> 7;
	rng_state ^= rng_state << 17;
	return (uint32_t)rng_state;
}

static void pack_pair(uint8_t out[3], uint16_t a, uint16_t b)
{
	out[0] = (uint8_t)a;
	out[1] = (uint8_t)((a >> 8) | (b << 4));
	out[2] = (uint8_t)(b >> 4);
}

static int run_profile(unsigned profile, uint8_t *ct, uint8_t *ss,
	const uint8_t *pk, const uint8_t *coins)
{
	if (profile < 2)
		return working_set_057_reserved(profile, ct, ss, pk, coins);
	return working_set_057_compact(ct, ss, pk, coins);
}

int main(void)
{
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t coins[NTRUPLUS_N / 8];
	uint8_t expected_ct[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t expected_ss[NTRUPLUS_SSBYTES];

	for (unsigned trial = 0; trial < 1000; trial++) {
		for (size_t i = 0; i < NTRUPLUS_N / 2; i++)
			pack_pair(pk + 3 * i, (uint16_t)(random32() % 3457),
				(uint16_t)(random32() % 3457));
		for (size_t i = 0; i < sizeof coins; i++)
			coins[i] = (uint8_t)random32();
		if (ntruplus768_enc_derand_impl(expected_ct, expected_ss, pk, coins) != 0)
			return 1;
		for (unsigned profile = 0; profile < WORKING_SET_057_PROFILES; profile++) {
			uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES];
			uint8_t ss[NTRUPLUS_SSBYTES];
			if (run_profile(profile, ct, ss, pk, coins) != 0
				|| memcmp(ct, expected_ct, sizeof ct) != 0
				|| memcmp(ss, expected_ss, sizeof ss) != 0) {
				fprintf(stderr, "valid trial %u profile %u mismatch\n", trial, profile);
				return 2;
			}
		}
	}

	memset(coins, 0xa5, sizeof coins);
	for (unsigned slot = 0; slot < NTRUPLUS_N; slot++) {
		memset(pk, 0, sizeof pk);
		pack_pair(pk + 3 * (slot / 2), (slot & 1) ? 0 : 3457,
			(slot & 1) ? 3457 : 0);
		memset(expected_ct, 0x5a, sizeof expected_ct);
		memset(expected_ss, 0x5a, sizeof expected_ss);
		if (ntruplus768_enc_derand_impl(expected_ct, expected_ss, pk, coins) != 1)
			return 3;
		for (unsigned profile = 0; profile < WORKING_SET_057_PROFILES; profile++) {
			uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES];
			uint8_t ss[NTRUPLUS_SSBYTES];
			memset(ct, 0x5a, sizeof ct);
			memset(ss, 0x5a, sizeof ss);
			if (run_profile(profile, ct, ss, pk, coins) != 1
				|| memcmp(ct, expected_ct, sizeof ct) != 0
				|| memcmp(ss, expected_ss, sizeof ss) != 0) {
				fprintf(stderr, "malformed slot %u profile %u mismatch\n",
					slot, profile);
				return 4;
			}
		}
	}
	puts("1000 valid and 768 malformed-slot differentials passed");
	return 0;
}
