#include <stdint.h>
#include <stdlib.h>

#include "working_set_057.h"

#define ITERATIONS 20000

static volatile uint8_t sink;

static void pack_pair(uint8_t out[3], uint16_t a, uint16_t b)
{
	out[0] = (uint8_t)a;
	out[1] = (uint8_t)((a >> 8) | (b << 4));
	out[2] = (uint8_t)(b >> 4);
}

int main(int argc, char **argv)
{
	static uint8_t pk[NTRUPLUS_PUBLICKEYBYTES] __attribute__((aligned(64)));
	static uint8_t coins[NTRUPLUS_N / 8] __attribute__((aligned(64)));
	static uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES] __attribute__((aligned(64)));
	static uint8_t ss[NTRUPLUS_SSBYTES] __attribute__((aligned(64)));
	unsigned profile;

	if (argc != 2)
		return 2;
	profile = (unsigned)strtoul(argv[1], NULL, 10);
	if (profile >= WORKING_SET_057_PROFILES)
		return 3;
	for (size_t i = 0; i < NTRUPLUS_N / 2; i++)
		pack_pair(pk + 3 * i, (uint16_t)((37 * i + 11) % 3457),
			(uint16_t)((91 * i + 7) % 3457));
	for (size_t i = 0; i < sizeof coins; i++)
		coins[i] = (uint8_t)(53 * i + 19);
	for (unsigned i = 0; i < ITERATIONS; i++) {
		int rc = profile < 2
			? working_set_057_reserved(profile, ct, ss, pk, coins)
			: working_set_057_compact(ct, ss, pk, coins);
		if (rc != 0)
			return 4;
		sink ^= ct[i % sizeof ct] ^ ss[i % sizeof ss];
	}
	return sink == 0xff;
}
