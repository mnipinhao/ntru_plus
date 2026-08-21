#define _GNU_SOURCE
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "working_set_057.h"

#define LOOPS 3
#define TIMINGS 32
#define OBSERVATIONS (LOOPS * TIMINGS)

static volatile uint64_t output_sink;

static void pack_pair(uint8_t out[3], uint16_t a, uint16_t b)
{
	out[0] = (uint8_t)a;
	out[1] = (uint8_t)((a >> 8) | (b << 4));
	out[2] = (uint8_t)(b >> 4);
}

static void make_inputs(uint8_t *pk, uint8_t *coins)
{
	for (size_t i = 0; i < NTRUPLUS_N / 2; i++)
		pack_pair(pk + 3 * i, (uint16_t)((37 * i + 11) % 3457),
			(uint16_t)((91 * i + 7) % 3457));
	for (size_t i = 0; i < NTRUPLUS_N / 8; i++)
		coins[i] = (uint8_t)(53 * i + 19);
}

static int encap(unsigned profile, uint8_t *ct, uint8_t *ss,
	const uint8_t *pk, const uint8_t *coins)
{
	if (profile < 2)
		return working_set_057_reserved(profile, ct, ss, pk, coins);
	return working_set_057_compact(ct, ss, pk, coins);
}

static void measure(unsigned profile, const uint8_t *pk, const uint8_t *coins)
{
	static uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES] __attribute__((aligned(64)));
	static uint8_t ss[NTRUPLUS_SSBYTES] __attribute__((aligned(64)));
	long long values[OBSERVATIONS], stamps[TIMINGS + 1];
	size_t used = 0;

	for (unsigned i = 0; i < 32; i++)
		if (encap(profile, ct, ss, pk, coins) != 0)
			exit(2);
	for (unsigned loop = 0; loop < LOOPS; loop++) {
		for (unsigned i = 0; i <= TIMINGS; i++) {
			stamps[i] = cpucycles();
			if (encap(profile, ct, ss, pk, coins) != 0)
				exit(3);
		}
		for (unsigned i = 0; i < TIMINGS; i++)
			values[used++] = stamps[i + 1] - stamps[i];
	}
	printf("p%u_cycles", profile);
	for (unsigned i = 0; i < OBSERVATIONS; i++)
		printf(" %lld", values[i]);
	putchar('\n');
	output_sink ^= ct[0] ^ ss[0];
}

int main(int argc, char **argv)
{
	static uint8_t pk[NTRUPLUS_PUBLICKEYBYTES] __attribute__((aligned(64)));
	static uint8_t coins[NTRUPLUS_N / 8] __attribute__((aligned(64)));
	const char *order = argc == 2 ? argv[1] : "012";

	if (strlen(order) != WORKING_SET_057_PROFILES)
		return 4;
	make_inputs(pk, coins);
	printf("cpucycles_implementation %s\n", cpucycles_implementation());
	printf("reserved_function %p\n",
		(void *)(uintptr_t)working_set_057_reserved);
	printf("compact_function %p\n", (void *)(uintptr_t)working_set_057_compact);
	for (unsigned i = 0; i < WORKING_SET_057_PROFILES; i++) {
		unsigned profile = (unsigned)(order[i] - '0');
		if (profile >= WORKING_SET_057_PROFILES)
			return 5;
		measure(profile, pk, coins);
	}
	printf("sink %" PRIu64 "\n", output_sink);
	return 0;
}
