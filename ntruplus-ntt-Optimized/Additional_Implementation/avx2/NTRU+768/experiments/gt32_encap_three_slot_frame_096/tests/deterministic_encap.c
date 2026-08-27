#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "internal.h"

static uint64_t state = UINT64_C(0x096a3c4f17b2d851);

static uint32_t rnd(void)
{
	state ^= state << 13;
	state ^= state >> 7;
	state ^= state << 17;
	return (uint32_t)state;
}

static void pair(uint8_t out[3], uint16_t a, uint16_t b)
{
	out[0] = (uint8_t)a;
	out[1] = (uint8_t)((a >> 8) | (b << 4));
	out[2] = (uint8_t)(b >> 4);
}

static void pkgen(uint8_t *pk)
{
	for (size_t i = 0; i < NTRUPLUS_N / 2; i++)
		pair(pk + 3 * i, (uint16_t)(rnd() % 3457),
			(uint16_t)(rnd() % 3457));
}

static void corrupt_slot(uint8_t *pk, size_t index)
{
	size_t p = index / 2;
	uint16_t a = (uint16_t)(pk[3 * p] |
		((uint16_t)(pk[3 * p + 1] & 15) << 8));
	uint16_t b = (uint16_t)((pk[3 * p + 1] >> 4) |
		((uint16_t)pk[3 * p + 2] << 4));
	if (index & 1)
		b = 3457;
	else
		a = 3457;
	pair(pk + 3 * p, a, b);
}

static uint64_t mix(uint64_t hash, const uint8_t *data, size_t length)
{
	for (size_t i = 0; i < length; i++) {
		hash ^= data[i];
		hash *= UINT64_C(1099511628211);
	}
	return hash;
}

int main(void)
{
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES], pk_copy[sizeof pk];
	uint8_t coins[NTRUPLUS_N / 8], coins_copy[sizeof coins];
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES], ss[NTRUPLUS_SSBYTES];
	uint64_t hash = UINT64_C(1469598103934665603);

	for (size_t test = 0; test < 1000; test++) {
		pkgen(pk);
		for (size_t i = 0; i < sizeof coins; i++)
			coins[i] = (uint8_t)rnd();
		memcpy(pk_copy, pk, sizeof pk);
		memcpy(coins_copy, coins, sizeof coins);
		if (ntruplus768_enc_derand_impl(ct, ss, pk, coins) != 0 ||
		    memcmp(pk, pk_copy, sizeof pk) != 0 ||
		    memcmp(coins, coins_copy, sizeof coins) != 0)
			return 1;
		hash = mix(hash, ct, sizeof ct);
		hash = mix(hash, ss, sizeof ss);
	}
	memset(coins, 0xa5, sizeof coins);
	for (size_t index = 0; index < NTRUPLUS_N; index++) {
		memset(pk, 0, sizeof pk);
		corrupt_slot(pk, index);
		memcpy(pk_copy, pk, sizeof pk);
		memcpy(coins_copy, coins, sizeof coins);
		memset(ct, 0x5a, sizeof ct);
		memset(ss, 0x5a, sizeof ss);
		if (ntruplus768_enc_derand_impl(ct, ss, pk, coins) != 1 ||
		    memcmp(pk, pk_copy, sizeof pk) != 0 ||
		    memcmp(coins, coins_copy, sizeof coins) != 0)
			return 1;
		for (size_t i = 0; i < sizeof ct; i++)
			if (ct[i] != 0)
				return 1;
		for (size_t i = 0; i < sizeof ss; i++)
			if (ss[i] != 0)
				return 1;
	}
	printf("PASS digest=%016llx 1000 exact-corpus + 768 noncanonical + immutable-inputs\n",
		(unsigned long long)hash);
	return 0;
}
