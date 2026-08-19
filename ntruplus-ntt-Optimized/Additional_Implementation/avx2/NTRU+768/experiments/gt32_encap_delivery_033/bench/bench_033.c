#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "encap_delivery_033.h"
#include "encap_lifetime_031.h"
#include "internal.h"

#define LOOPS 3
#define TIMINGS 32
#define OBSERVATIONS (LOOPS * TIMINGS)
#define PMU_CALLS 10000

typedef int (*encap_fn)(uint8_t *, uint8_t *, const uint8_t *,
	const uint8_t *);

static uint64_t rng_state = UINT64_C(0x033de11a6eadd2c1);
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

static void exact_check(const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	uint8_t ct[3][NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t ss[3][NTRUPLUS_SSBYTES];
	encap_fn functions[3] = {
		ntruplus768_enc_derand_impl,
		gt32_encap_lifetime_031,
		gt32_encap_delivery_033,
	};
	for (size_t i = 0; i < 3; i++)
		if (functions[i](ct[i], ss[i], pk, coins) != 0)
			exit(1);
	for (size_t i = 1; i < 3; i++)
		if (memcmp(ct[0], ct[i], sizeof ct[0]) != 0
			|| memcmp(ss[0], ss[i], sizeof ss[0]) != 0) {
			fprintf(stderr, "A/B/C exact check failed\n");
			exit(1);
		}
}

static void measure(const char *name, encap_fn fn,
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	static uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES] __attribute__((aligned(64)));
	static uint8_t ss[NTRUPLUS_SSBYTES] __attribute__((aligned(64)));
	long long observations[OBSERVATIONS];
	long long stamps[TIMINGS + 1];
	size_t used = 0;
	for (size_t warmup = 0; warmup < 32; warmup++)
		if (fn(ct, ss, pk, coins) != 0)
			exit(1);
	for (size_t loop = 0; loop < LOOPS; loop++) {
		for (size_t i = 0; i <= TIMINGS; i++) {
			stamps[i] = cpucycles();
			if (fn(ct, ss, pk, coins) != 0)
				exit(1);
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
	const char *order = argc == 2 ? argv[1] : "ABC";
	encap_fn functions[3] = {
		ntruplus768_enc_derand_impl,
		gt32_encap_lifetime_031,
		gt32_encap_delivery_033,
	};
	const char *names[3] = {"A", "B", "C"};
	int sequence[3];
	if (strcmp(order, "CHECK") == 0) {
		make_inputs(pk, coins);
		exact_check(pk, coins);
		return 0;
#ifdef GT033_PMU_MODE
	} else if (strcmp(order, "PMU_B") == 0
		|| strcmp(order, "PMU_C") == 0) {
		uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES];
		uint8_t ss[NTRUPLUS_SSBYTES];
		int index = order[4] == 'B' ? 1 : 2;
		make_inputs(pk, coins);
		exact_check(pk, coins);
		for (size_t i = 0; i < PMU_CALLS; i++)
			if (functions[index](ct, ss, pk, coins) != 0)
				return 1;
		output_sink ^= digest(ct, sizeof ct) ^ digest(ss, sizeof ss);
		printf("pmu_calls %d\nsink %" PRIu64 "\n", PMU_CALLS,
			output_sink);
		return 0;
#endif
	} else if (strcmp(order, "ABC") == 0) {
		sequence[0] = 0; sequence[1] = 1; sequence[2] = 2;
	} else if (strcmp(order, "BCA") == 0) {
		sequence[0] = 1; sequence[1] = 2; sequence[2] = 0;
	} else if (strcmp(order, "CAB") == 0) {
		sequence[0] = 2; sequence[1] = 0; sequence[2] = 1;
	} else {
		return 2;
	}
	make_inputs(pk, coins);
	exact_check(pk, coins);
	printf("cpucycles_implementation %s\n", cpucycles_implementation());
	printf("A_address %p\n", (void *)(uintptr_t)functions[0]);
	printf("B_address %p\n", (void *)(uintptr_t)functions[1]);
	printf("C_address %p\n", (void *)(uintptr_t)functions[2]);
	printf("B3_address %p\n", (void *)(uintptr_t)gt32_033_b3_addm);
	for (size_t i = 0; i < 3; i++) {
		int index = sequence[i];
		measure(names[index], functions[index], pk, coins);
	}
	printf("sink %" PRIu64 "\n", output_sink);
	return 0;
}
