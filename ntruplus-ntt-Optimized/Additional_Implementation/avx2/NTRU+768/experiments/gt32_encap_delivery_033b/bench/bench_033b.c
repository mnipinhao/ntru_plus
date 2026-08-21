#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "cpucycles.h"
#include "params.h"

#define LOOPS 3
#define TIMINGS 32
#define OBSERVATIONS (LOOPS * TIMINGS)
#define PMU_CALLS 10000

int gt033b_encap(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);

static volatile uint64_t sink;

static void pack_pair(uint8_t out[3], uint16_t a, uint16_t b)
{
	out[0] = (uint8_t)a;
	out[1] = (uint8_t)((a >> 8) | (b << 4));
	out[2] = (uint8_t)(b >> 4);
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

int main(int argc, char **argv)
{
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t coins[NTRUPLUS_N / 8];
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES] __attribute__((aligned(64)));
	uint8_t ss[NTRUPLUS_SSBYTES] __attribute__((aligned(64)));
	for (size_t i = 0; i < NTRUPLUS_N / 2; i++)
		pack_pair(pk + 3 * i, (uint16_t)((i * 73 + 11) % 3457),
			(uint16_t)((i * 193 + 7) % 3457));
	for (size_t i = 0; i < sizeof coins; i++)
		coins[i] = (uint8_t)(i * 151 + 29);

	if (argc == 2 && argv[1][0] == 'P') {
		for (size_t i = 0; i < PMU_CALLS; i++)
			if (gt033b_encap(ct, ss, pk, coins) != 0)
				return 1;
		sink ^= digest(ct, sizeof ct) ^ digest(ss, sizeof ss);
		printf("pmu_calls %d\nsink %" PRIu64 "\n", PMU_CALLS, sink);
		return 0;
	}

	long long observations[OBSERVATIONS];
	long long stamps[TIMINGS + 1];
	size_t used = 0;
	for (size_t warmup = 0; warmup < 64; warmup++)
		if (gt033b_encap(ct, ss, pk, coins) != 0)
			return 1;
	for (size_t loop = 0; loop < LOOPS; loop++) {
		for (size_t i = 0; i <= TIMINGS; i++) {
			stamps[i] = cpucycles();
			if (gt033b_encap(ct, ss, pk, coins) != 0)
				return 1;
		}
		for (size_t i = 0; i < TIMINGS; i++)
			observations[used++] = stamps[i + 1] - stamps[i];
	}
	sink ^= digest(ct, sizeof ct) ^ digest(ss, sizeof ss);
	printf("cpucycles_implementation %s\n", cpucycles_implementation());
	printf("caller_address %p\n", (void *)(uintptr_t)gt033b_encap);
	printf("cycles");
	for (size_t i = 0; i < OBSERVATIONS; i++)
		printf(" %lld", observations[i]);
	printf("\nsink %" PRIu64 "\n", sink);
	return 0;
}

