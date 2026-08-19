#define _GNU_SOURCE

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "encap_lifetime_031.h"
#include "internal.h"

#define LOOPS 3
#define TIMINGS 32
#define OBSERVATIONS (LOOPS * TIMINGS)

typedef int (*encap_fn)(uint8_t *, uint8_t *, const uint8_t *,
	const uint8_t *);

static uint64_t rng_state = UINT64_C(0x031b3e6c85a94d21);
static volatile uint64_t output_sink;

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

static void make_inputs(uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	uint8_t coins[NTRUPLUS_N / 8])
{
	for (size_t i = 0; i < NTRUPLUS_N / 2; i++)
		pack_pair(pk + 3 * i, (uint16_t)(random32() % 3457),
			(uint16_t)(random32() % 3457));
	for (size_t i = 0; i < NTRUPLUS_N / 8; i++)
		coins[i] = (uint8_t)random32();
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

static void measure_variant(const char *name, encap_fn fn,
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	static uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES] __attribute__((aligned(64)));
	static uint8_t ss[NTRUPLUS_SSBYTES] __attribute__((aligned(64)));
	long long observations[OBSERVATIONS];
	long long stamps[TIMINGS + 1];
	size_t used = 0;

	for (size_t warmup = 0; warmup < 32; warmup++) {
		if (fn(ct, ss, pk, coins) != 0) {
			fprintf(stderr, "%s warmup rejected canonical input\n", name);
			exit(1);
		}
	}
	for (size_t loop = 0; loop < LOOPS; loop++) {
		for (size_t i = 0; i <= TIMINGS; i++) {
			stamps[i] = cpucycles();
			if (fn(ct, ss, pk, coins) != 0) {
				fprintf(stderr, "%s rejected canonical input\n", name);
				exit(1);
			}
		}
		for (size_t i = 0; i < TIMINGS; i++)
			observations[used++] = stamps[i + 1] - stamps[i];
	}
	output_sink ^= digest(ct, sizeof ct) ^ digest(ss, sizeof ss);
	printf("%s_cycles", name);
	for (size_t i = 0; i < OBSERVATIONS; i++)
		printf(" %lld", observations[i]);
	putchar('\n');
}

int main(int argc, char **argv)
{
	static uint8_t pk[NTRUPLUS_PUBLICKEYBYTES] __attribute__((aligned(64)));
	static uint8_t coins[NTRUPLUS_N / 8] __attribute__((aligned(64)));
	const char *order = argc == 2 ? argv[1] : "AB";

	if (strcmp(order, "AB") != 0 && strcmp(order, "BA") != 0) {
		fprintf(stderr, "usage: %s [AB|BA]\n", argv[0]);
		return 2;
	}
	make_inputs(pk, coins);
	printf("cpucycles_implementation %s\n", cpucycles_implementation());
	printf("control_address %p\n", (void *)(uintptr_t)ntruplus768_enc_derand_impl);
	printf("candidate_address %p\n", (void *)(uintptr_t)gt32_encap_lifetime_031);
	if (strcmp(order, "AB") == 0) {
		measure_variant("control", ntruplus768_enc_derand_impl, pk, coins);
		measure_variant("candidate", gt32_encap_lifetime_031, pk, coins);
	} else {
		measure_variant("candidate", gt32_encap_lifetime_031, pk, coins);
		measure_variant("control", ntruplus768_enc_derand_impl, pk, coins);
	}
	printf("sink %" PRIu64 "\n", output_sink);
	return 0;
}
