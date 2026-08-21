#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "cpucycles.h"
#include "params.h"

#define SAMPLES 31
#define ROUNDS 32

typedef int (*unpack_fn)(int16_t *, const uint8_t *);
typedef void (*basemul_fn)(int16_t *, const int16_t *, const int16_t *);
typedef struct { unpack_fn unpack; basemul_fn basemul; } profile;
int gt042_encap_common(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *,
	unpack_fn, basemul_fn);
int ntruplus768_unpack_m_avx2(int16_t *, const uint8_t *);
int gt042d_ntruplus768_unpack_m_avx2(int16_t *, const uint8_t *);
void ntruplus768_basemul_general_m_avx2(int16_t *, const int16_t *, const int16_t *);
void gt042b_ntruplus768_basemul_general_m_avx2(int16_t *, const int16_t *, const int16_t *);

static uint8_t pk[NTRUPLUS_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t coins[NTRUPLUS_N / 8] __attribute__((aligned(64)));
static volatile uint64_t sink;

static void pack_pair(uint8_t out[3], uint16_t a, uint16_t b)
{
	out[0] = (uint8_t)a;
	out[1] = (uint8_t)((a >> 8) | (b << 4));
	out[2] = (uint8_t)(b >> 4);
}

static int cmp_u64(const void *x, const void *y)
{
	const uint64_t a = *(const uint64_t *)x, b = *(const uint64_t *)y;
	return (a > b) - (a < b);
}

static int invoke(const profile *p, uint8_t *ct, uint8_t *ss)
{
	return gt042_encap_common(ct, ss, pk, coins, p->unpack, p->basemul);
}

static uint64_t measure(const profile *p)
{
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES] __attribute__((aligned(64)));
	uint8_t ss[NTRUPLUS_SSBYTES] __attribute__((aligned(64)));
	uint64_t samples[SAMPLES];
	for (unsigned i = 0; i < 32; i++)
		if (invoke(p, ct, ss) != 0) exit(10);
	for (unsigned i = 0; i < SAMPLES; i++) {
		const long long begin = cpucycles();
		if (invoke(p, ct, ss) != 0) exit(11);
		samples[i] = (uint64_t)(cpucycles() - begin);
	}
	qsort(samples, SAMPLES, sizeof samples[0], cmp_u64);
	sink += ct[0] + ss[0];
	return samples[SAMPLES / 2];
}

int main(void)
{
	static const char *names[4] = {"A", "D", "B", "DB"};
	static const profile profiles[4] = {
		{ntruplus768_unpack_m_avx2, ntruplus768_basemul_general_m_avx2},
		{gt042d_ntruplus768_unpack_m_avx2, ntruplus768_basemul_general_m_avx2},
		{ntruplus768_unpack_m_avx2, gt042b_ntruplus768_basemul_general_m_avx2},
		{gt042d_ntruplus768_unpack_m_avx2, gt042b_ntruplus768_basemul_general_m_avx2}
	};
	uint8_t ref_ct[NTRUPLUS_CIPHERTEXTBYTES], ref_ss[NTRUPLUS_SSBYTES];
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES], ss[NTRUPLUS_SSBYTES];
	for (unsigned i = 0; i < NTRUPLUS_N / 2; i++)
		pack_pair(pk + 3 * i, (uint16_t)((i * 73U + 11U) % 3457U),
			(uint16_t)((i * 193U + 7U) % 3457U));
	for (unsigned i = 0; i < sizeof coins; i++) coins[i] = (uint8_t)(i * 151U + 29U);
	if (invoke(&profiles[0], ref_ct, ref_ss) != 0) return 2;
	for (unsigned p = 1; p < 4; p++) {
		if (invoke(&profiles[p], ct, ss) != 0) return 3;
		for (unsigned i = 0; i < sizeof ct; i++) if (ct[i] != ref_ct[i]) return 4;
		for (unsigned i = 0; i < sizeof ss; i++) if (ss[i] != ref_ss[i]) return 5;
	}
	printf("cpucycles_implementation %s\n", cpucycles_implementation());
	printf("address_caller %p\n", (void *)(uintptr_t)gt042_encap_common);
	for (unsigned i = 0; i < 4; i++) {
		printf("address_%s_unpack %p\n", names[i],
			(void *)(uintptr_t)profiles[i].unpack);
		printf("address_%s_basemul %p\n", names[i],
			(void *)(uintptr_t)profiles[i].basemul);
	}
	for (unsigned round = 0; round < ROUNDS; round++) {
		uint64_t values[4];
		for (unsigned step = 0; step < 4; step++) {
			const unsigned profile = (round + step) & 3U;
			values[profile] = measure(&profiles[profile]);
		}
		printf("round %u A %" PRIu64 " D %" PRIu64 " B %" PRIu64
		       " DB %" PRIu64 "\n", round, values[0], values[1],
		       values[2], values[3]);
	}
	printf("sink %" PRIu64 "\n", sink);
	return 0;
}
