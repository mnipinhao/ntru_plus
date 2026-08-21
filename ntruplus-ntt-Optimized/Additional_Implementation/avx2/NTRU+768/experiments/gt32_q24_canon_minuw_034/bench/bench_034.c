#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "params.h"

#define LOOPS 3
#define TIMINGS 32
#define OBSERVATIONS (LOOPS * TIMINGS)

typedef void (*pack_fn)(uint8_t *, const int16_t *);

void ntruplus768_pack_m_lazy10788_avx2(uint8_t *, const int16_t *);
void gt034_ntruplus768_pack_m_lazy10788_avx2(uint8_t *, const int16_t *);

static volatile uint64_t sink;

static uint64_t digest(const uint8_t *data, size_t bytes)
{
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

static void measure(const char *name, pack_fn fn, size_t calls,
	const int16_t *a, const int16_t *b)
{
	uint8_t out_a[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
	uint8_t out_b[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
	long long observations[OBSERVATIONS];
	long long stamps[TIMINGS + 1];
	size_t used = 0;
	for (size_t warmup = 0; warmup < 128; warmup++) {
		fn(out_a, a);
		if (calls == 2)
			fn(out_b, b);
	}
	for (size_t loop = 0; loop < LOOPS; loop++) {
		for (size_t i = 0; i <= TIMINGS; i++) {
			stamps[i] = cpucycles();
			fn(out_a, a);
			if (calls == 2)
				fn(out_b, b);
		}
		for (size_t i = 0; i < TIMINGS; i++)
			observations[used++] = stamps[i + 1] - stamps[i];
	}
	sink ^= digest(out_a, sizeof out_a);
	if (calls == 2)
		sink ^= digest(out_b, sizeof out_b);
	print_observations(name, observations);
}

int main(int argc, char **argv)
{
	static int16_t a[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t b[NTRUPLUS_N] __attribute__((aligned(64)));
	const char *order = argc > 1 ? argv[1] : "AB";
	for (size_t i = 0; i < NTRUPLUS_N; i++) {
		a[i] = (int16_t)((i * 7919u + 1237u) % 21577u - 10788);
		b[i] = (int16_t)((i * 3571u + 9181u) % 25399u - 12699);
	}
	if (strcmp(order, "AB") != 0 && strcmp(order, "BA") != 0)
		return 2;
	printf("cpucycles_implementation %s\n", cpucycles_implementation());
	printf("control_address %p\n", (void *)(uintptr_t)ntruplus768_pack_m_lazy10788_avx2);
	printf("candidate_address %p\n", (void *)(uintptr_t)gt034_ntruplus768_pack_m_lazy10788_avx2);
	if (strcmp(order, "AB") == 0) {
		measure("single_control", ntruplus768_pack_m_lazy10788_avx2, 1, a, b);
		measure("single_candidate", gt034_ntruplus768_pack_m_lazy10788_avx2, 1, a, b);
		measure("double_control", ntruplus768_pack_m_lazy10788_avx2, 2, a, b);
		measure("double_candidate", gt034_ntruplus768_pack_m_lazy10788_avx2, 2, a, b);
	} else {
		measure("single_candidate", gt034_ntruplus768_pack_m_lazy10788_avx2, 1, a, b);
		measure("single_control", ntruplus768_pack_m_lazy10788_avx2, 1, a, b);
		measure("double_candidate", gt034_ntruplus768_pack_m_lazy10788_avx2, 2, a, b);
		measure("double_control", ntruplus768_pack_m_lazy10788_avx2, 2, a, b);
	}
	printf("sink %" PRIu64 "\n", sink);
	return 0;
}

