#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "encap_b3_addm_032.h"
#include "internal.h"
#include "poly.h"
#include "symmetric.h"

#define LOOPS 3
#define TIMINGS 32
#define OBSERVATIONS (LOOPS * TIMINGS)

typedef int (*encap_fn)(uint8_t *, uint8_t *, const uint8_t *,
	const uint8_t *);

static uint64_t rng_state = UINT64_C(0x032c0de51a6e7b93);
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

static void make_local_inputs(int16_t h[NTRUPLUS_N],
	int16_t r_hat[NTRUPLUS_N], int16_t m_hat[NTRUPLUS_N],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	uint8_t r_bytes[NTRUPLUS_POLYBYTES];
	int16_t coeff[NTRUPLUS_N] __attribute__((aligned(64)));
	int16_t frontend[NTRUPLUS_N] __attribute__((aligned(64)));
	if (ntruplus768_unpack_m_avx2(h, pk) != 0)
		exit(1);
	memcpy(msg, coins, NTRUPLUS_N / 8);
	hash_f(msg + NTRUPLUS_N / 8, pk);
	hash_h(buf, msg);
	poly_cbd1((poly *)(void *)coeff, buf + NTRUPLUS_SYMBYTES);
	ntruplus768_ntt_frontend_avx2(frontend, coeff);
	ntruplus768_ntt_m_avx2(r_hat, frontend);
	ntruplus768_pack_m_lazy10788_avx2(r_bytes, r_hat);
	hash_g(r_bytes, r_bytes);
	poly_sotp_encode((poly *)(void *)coeff, msg, r_bytes);
	ntruplus768_ntt_frontend_avx2(frontend, coeff);
	ntruplus768_ntt_m_avx2(m_hat, frontend);
}

static uint64_t digest(const void *input, size_t bytes)
{
	const uint8_t *data = input;
	uint64_t result = UINT64_C(1469598103934665603);
	for (size_t i = 0; i < bytes; i++) {
		result ^= data[i];
		result *= UINT64_C(1099511628211);
	}
	return result;
}

static void print_observations(const char *name,
	const long long observations[OBSERVATIONS])
{
	printf("%s_cycles", name);
	for (size_t i = 0; i < OBSERVATIONS; i++)
		printf(" %lld", observations[i]);
	putchar('\n');
}

static void measure_local(const char *name, gt32_032_local_fn fn,
	int16_t out[NTRUPLUS_N], const int16_t h[NTRUPLUS_N],
	const int16_t r_hat[NTRUPLUS_N], const int16_t m_hat[NTRUPLUS_N])
{
	uint8_t packed[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
	long long observations[OBSERVATIONS];
	long long stamps[TIMINGS + 1];
	size_t used = 0;
	for (size_t warmup = 0; warmup < 64; warmup++) {
		fn(out, h, r_hat, m_hat);
		ntruplus768_pack_m_highrange12699_avx2(packed, out);
	}
	for (size_t loop = 0; loop < LOOPS; loop++) {
		for (size_t i = 0; i <= TIMINGS; i++) {
			stamps[i] = cpucycles();
			fn(out, h, r_hat, m_hat);
			ntruplus768_pack_m_highrange12699_avx2(packed, out);
		}
		for (size_t i = 0; i < TIMINGS; i++)
			observations[used++] = stamps[i + 1] - stamps[i];
	}
	output_sink ^= digest(packed, sizeof packed);
	print_observations(name, observations);
}

static void measure_full(const char *name, encap_fn fn,
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES], uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
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
	output_sink ^= digest(ct, NTRUPLUS_CIPHERTEXTBYTES)
		^ digest(ss, NTRUPLUS_SSBYTES);
	print_observations(name, observations);
}

int main(int argc, char **argv)
{
	static int16_t h[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t r_hat[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t m_hat[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t out[NTRUPLUS_N] __attribute__((aligned(64)));
	static uint8_t pk[NTRUPLUS_PUBLICKEYBYTES] __attribute__((aligned(64)));
	static uint8_t coins[NTRUPLUS_N / 8] __attribute__((aligned(64)));
	static uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES] __attribute__((aligned(64)));
	static uint8_t ss[NTRUPLUS_SSBYTES] __attribute__((aligned(64)));
	const char *placement = argc > 1 ? argv[1] : "normal";
	const char *order = argc > 2 ? argv[2] : "AB";
	gt32_032_local_fn local_control;
	gt32_032_local_fn local_candidate;
	encap_fn full_control;
	encap_fn full_candidate;

	if (strcmp(placement, "normal") == 0) {
		local_control = gt32_032_local_control_normal;
		local_candidate = gt32_032_local_candidate_normal;
		full_control = gt32_032_encap_control_normal;
		full_candidate = gt32_032_encap_candidate_normal;
	} else if (strcmp(placement, "reversed") == 0) {
		local_control = gt32_032_local_control_reversed;
		local_candidate = gt32_032_local_candidate_reversed;
		full_control = gt32_032_encap_control_reversed;
		full_candidate = gt32_032_encap_candidate_reversed;
	} else {
		return 2;
	}
	if (strcmp(order, "AB") != 0 && strcmp(order, "BA") != 0)
		return 2;
	make_inputs(pk, coins);
	make_local_inputs(h, r_hat, m_hat, pk, coins);
	printf("cpucycles_implementation %s\n", cpucycles_implementation());
	printf("placement %s\n", placement);
	printf("local_control_address %p\n", (void *)(uintptr_t)local_control);
	printf("local_candidate_address %p\n", (void *)(uintptr_t)local_candidate);
	printf("full_control_address %p\n", (void *)(uintptr_t)full_control);
	printf("full_candidate_address %p\n", (void *)(uintptr_t)full_candidate);
	if (strcmp(order, "AB") == 0) {
		measure_local("local_control", local_control, out, h, r_hat, m_hat);
		measure_local("local_candidate", local_candidate, out, h, r_hat, m_hat);
		measure_full("full_control", full_control, ct, ss, pk, coins);
		measure_full("full_candidate", full_candidate, ct, ss, pk, coins);
	} else {
		measure_local("local_candidate", local_candidate, out, h, r_hat, m_hat);
		measure_local("local_control", local_control, out, h, r_hat, m_hat);
		measure_full("full_candidate", full_candidate, ct, ss, pk, coins);
		measure_full("full_control", full_control, ct, ss, pk, coins);
	}
	printf("sink %" PRIu64 "\n", output_sink);
	return 0;
}
