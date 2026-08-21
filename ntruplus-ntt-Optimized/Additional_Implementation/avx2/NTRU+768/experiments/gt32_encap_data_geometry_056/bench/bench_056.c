#define _GNU_SOURCE
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "geometry_056.h"

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

static void make_inputs(uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	uint8_t coins[NTRUPLUS_N / 8])
{
	for (size_t i = 0; i < NTRUPLUS_N / 2; i++)
		pack_pair(pk + 3 * i, (uint16_t)((37 * i + 11) % 3457),
			(uint16_t)((91 * i + 7) % 3457));
	for (size_t i = 0; i < NTRUPLUS_N / 8; i++)
		coins[i] = (uint8_t)(53 * i + 19);
}

static uint64_t digest(const uint8_t *data, size_t bytes)
{
	uint64_t result = UINT64_C(1469598103934665603);
	for (size_t i = 0; i < bytes; i++) {
		result ^= data[i];
		result *= UINT64_C(1099511628211);
	}
	return result;
}

static void measure_profile(unsigned profile,
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	static const char *region_names[] = { "cbd", "rprod", "b3" };
	static uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES] __attribute__((aligned(64)));
	static uint8_t ss[NTRUPLUS_SSBYTES] __attribute__((aligned(64)));
	long long values[OBSERVATIONS];
	long long stamps[TIMINGS + 1];
	size_t used;

	for (unsigned warmup = 0; warmup < 16; warmup++)
		if (geometry_056_encap(profile, ct, ss, pk, coins) != 0)
			exit(2);
	for (unsigned region = 0; region < GEOMETRY_056_REGIONS; region++) {
		used = 0;
		for (unsigned loop = 0; loop < LOOPS; loop++)
			for (unsigned i = 0; i < TIMINGS; i++) {
				long long value = geometry_056_measure_region(profile,
					region, pk, coins);
				if (value < 0)
					exit(3);
				values[used++] = value;
			}
		printf("p%u_%s_cycles", profile, region_names[region]);
		for (unsigned i = 0; i < OBSERVATIONS; i++)
			printf(" %lld", values[i]);
		putchar('\n');
	}
	used = 0;
	for (unsigned loop = 0; loop < LOOPS; loop++) {
		for (unsigned i = 0; i <= TIMINGS; i++) {
			stamps[i] = cpucycles();
			if (geometry_056_encap(profile, ct, ss, pk, coins) != 0)
				exit(4);
		}
		for (unsigned i = 0; i < TIMINGS; i++)
			values[used++] = stamps[i + 1] - stamps[i];
	}
	printf("p%u_full_cycles", profile);
	for (unsigned i = 0; i < OBSERVATIONS; i++)
		printf(" %lld", values[i]);
	putchar('\n');
	output_sink ^= digest(ct, sizeof ct) ^ digest(ss, sizeof ss);
}

int main(int argc, char **argv)
{
	static uint8_t pk[NTRUPLUS_PUBLICKEYBYTES] __attribute__((aligned(64)));
	static uint8_t coins[NTRUPLUS_N / 8] __attribute__((aligned(64)));
	static uint8_t expected_ct[NTRUPLUS_CIPHERTEXTBYTES];
	static uint8_t expected_ss[NTRUPLUS_SSBYTES];
	const char *order = argc == 2 ? argv[1] : "012";

	if (strlen(order) != GEOMETRY_056_PROFILES)
		return 5;
	make_inputs(pk, coins);
	if (geometry_056_encap(GEOMETRY_056_CURRENT, expected_ct, expected_ss,
		pk, coins) != 0)
		return 6;
	for (unsigned profile = 1; profile < GEOMETRY_056_PROFILES; profile++) {
		uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES];
		uint8_t ss[NTRUPLUS_SSBYTES];
		if (geometry_056_encap(profile, ct, ss, pk, coins) != 0
			|| memcmp(ct, expected_ct, sizeof ct) != 0
			|| memcmp(ss, expected_ss, sizeof ss) != 0)
			return 7;
	}
	printf("cpucycles_implementation %s\n", cpucycles_implementation());
	printf("geometry_function %p\n", (void *)(uintptr_t)geometry_056_encap);
	for (unsigned i = 0; i < GEOMETRY_056_PROFILES; i++) {
		unsigned profile = (unsigned)(order[i] - '0');
		if (profile >= GEOMETRY_056_PROFILES)
			return 8;
		measure_profile(profile, pk, coins);
	}
	printf("sink %" PRIu64 "\n", output_sink);
	return 0;
}
