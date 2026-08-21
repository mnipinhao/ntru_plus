#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "geometry_056.h"

#define ITERATIONS 20000

static volatile uint64_t sink;

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
		return 1;
	profile = (unsigned)strtoul(argv[1], NULL, 0);
	if (profile >= GEOMETRY_056_PROFILES)
		return 2;
	for (size_t i = 0; i < NTRUPLUS_N / 2; i++)
		pack_pair(pk + 3 * i, (uint16_t)((37 * i + 11) % 3457),
			(uint16_t)((91 * i + 7) % 3457));
	for (size_t i = 0; i < sizeof coins; i++)
		coins[i] = (uint8_t)(53 * i + 19);
	for (unsigned i = 0; i < 32; i++)
		if (geometry_056_encap(profile, ct, ss, pk, coins) != 0)
			return 3;
	for (unsigned i = 0; i < ITERATIONS; i++)
		if (geometry_056_encap(profile, ct, ss, pk, coins) != 0)
			return 4;
	sink ^= ct[profile * 101] ^ ss[profile * 7];
	printf("%llu\n", (unsigned long long)sink);
	return 0;
}
