#define _GNU_SOURCE
#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "api.h"
#include "internal.h"
#include "params.h"

#define SAMPLES 20
#define INNER 64

int ntruplus768_enc_derand_qword_impl(uint8_t *, uint8_t *,
	const uint8_t *, const uint8_t *);
int ntruplus768_dec_qword_impl(uint8_t *, const uint8_t *, const uint8_t *);
void gt32_qword_ntt_frontend_avx2(int16_t *, const int16_t *);
void gt32_qword_ntt_m_avx2(int16_t *, const int16_t *);

static uint64_t rng_state = UINT64_C(0x243f6a8885a308d3);
static volatile uint64_t sink;

static uint32_t next_u32(void)
{
	rng_state ^= rng_state << 7;
	rng_state ^= rng_state >> 9;
	return (uint32_t)rng_state;
}

static uint64_t ticks(void)
{
	unsigned aux;
	_mm_lfence();
	uint64_t value = __rdtscp(&aux);
	_mm_lfence();
	return value;
}

static int cmp_u64(const void *left, const void *right)
{
	uint64_t a = *(const uint64_t *)left;
	uint64_t b = *(const uint64_t *)right;
	return (a > b) - (a < b);
}

static int cmp_i64(const void *left, const void *right)
{
	int64_t a = *(const int64_t *)left;
	int64_t b = *(const int64_t *)right;
	return (a > b) - (a < b);
}

static uint64_t median(uint64_t values[SAMPLES])
{
	uint64_t sorted[SAMPLES];
	memcpy(sorted, values, sizeof sorted);
	qsort(sorted, SAMPLES, sizeof sorted[0], cmp_u64);
	return (sorted[SAMPLES / 2 - 1] + sorted[SAMPLES / 2]) / 2;
}

static int64_t median_delta(uint64_t control[SAMPLES],
	uint64_t candidate[SAMPLES], int *wins)
{
	int64_t values[SAMPLES];
	*wins = 0;
	for (int i = 0; i < SAMPLES; i++) {
		values[i] = (int64_t)candidate[i] - (int64_t)control[i];
		*wins += values[i] < 0;
	}
	qsort(values, SAMPLES, sizeof values[0], cmp_i64);
	return (values[SAMPLES / 2 - 1] + values[SAMPLES / 2]) / 2;
}

static void pin_current_cpu(void)
{
	cpu_set_t set;
	int cpu = sched_getcpu();
	CPU_ZERO(&set);
	CPU_SET(cpu, &set);
	if (sched_setaffinity(0, sizeof set, &set) != 0) {
		perror("sched_setaffinity");
		exit(2);
	}
	printf("pinned_cpu=%d\n", cpu);
}

static int correctness(void)
{
	uint8_t pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES];
	uint8_t coins[NTRUPLUS_N / 8];
	uint8_t ct0[CRYPTO_CIPHERTEXTBYTES], ct1[CRYPTO_CIPHERTEXTBYTES];
	uint8_t ss0[CRYPTO_BYTES], ss1[CRYPTO_BYTES];
	uint8_t dec0[CRYPTO_BYTES], dec1[CRYPTO_BYTES];

	if (ntruplus768_keypair_impl(pk, sk) != 0)
		return 1;
	for (int trial = 0; trial < 1000; trial++) {
		for (size_t i = 0; i < sizeof coins; i++)
			coins[i] = (uint8_t)next_u32();
		int e0 = ntruplus768_enc_derand_impl(ct0, ss0, pk, coins);
		int e1 = ntruplus768_enc_derand_qword_impl(ct1, ss1, pk, coins);
		if (e0 != e1 || memcmp(ct0, ct1, sizeof ct0) != 0 ||
		    memcmp(ss0, ss1, sizeof ss0) != 0)
			return 2;
		int d0 = ntruplus768_dec_impl(dec0, ct0, sk);
		int d1 = ntruplus768_dec_qword_impl(dec1, ct0, sk);
		if (d0 != d1 || memcmp(dec0, dec1, sizeof dec0) != 0 ||
		    memcmp(dec0, ss0, sizeof dec0) != 0)
			return 3;
		ct0[(unsigned)trial % sizeof ct0] ^= (uint8_t)(1u << (trial & 7));
		d0 = ntruplus768_dec_impl(dec0, ct0, sk);
		d1 = ntruplus768_dec_qword_impl(dec1, ct0, sk);
		if (d0 != d1 || memcmp(dec0, dec1, sizeof dec0) != 0)
			return 4;
	}
	return 0;
}

static void bench_forward(void)
{
	_Alignas(32) int16_t in[NTRUPLUS_N], tmp[NTRUPLUS_N], out[NTRUPLUS_N];
	uint64_t control[SAMPLES], candidate[SAMPLES];
	for (int i = 0; i < NTRUPLUS_N; i++) in[i] = (int16_t)((next_u32() & 7) - 3);
	for (int sample = 0; sample < SAMPLES; sample++) {
		int candidate_first = sample & 1;
		if (candidate_first) goto candidate_forward;
	control_forward:
		uint64_t start = ticks();
		for (int i = 0; i < INNER; i++) {
			ntruplus768_ntt_frontend_avx2(tmp, in);
			ntruplus768_ntt_m_avx2(out, tmp);
			sink += (uint16_t)out[i & (NTRUPLUS_N - 1)];
		}
		control[sample] = (ticks() - start) / INNER;
		if (candidate_first) continue;
	candidate_forward:
		start = ticks();
		for (int i = 0; i < INNER; i++) {
			gt32_qword_ntt_frontend_avx2(tmp, in);
			gt32_qword_ntt_m_avx2(out, tmp);
			sink += (uint16_t)out[i & (NTRUPLUS_N - 1)];
		}
		candidate[sample] = (ticks() - start) / INNER;
		if (candidate_first) goto control_forward;
	}
	int wins;
	int64_t delta = median_delta(control, candidate, &wins);
	printf("Forward control=%llu candidate=%llu paired_delta=%lld wins=%d/%d TSC\n",
		(unsigned long long)median(control),
		(unsigned long long)median(candidate),
		(long long)delta, wins, SAMPLES);
}

static void bench_kem(void)
{
	uint8_t pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES];
	uint8_t coins[NTRUPLUS_N / 8] = {0};
	uint8_t ct[CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES], out[CRYPTO_BYTES];
	uint64_t enc0[SAMPLES], enc1[SAMPLES], dec0[SAMPLES], dec1[SAMPLES];
	if (ntruplus768_keypair_impl(pk, sk) != 0) exit(3);
	if (ntruplus768_enc_derand_impl(ct, ss, pk, coins) != 0) exit(3);
	for (int sample = 0; sample < SAMPLES; sample++) {
		int candidate_first = sample & 1;
		if (candidate_first) goto candidate_encap;
	control_encap:
		uint64_t start = ticks();
		for (int i = 0; i < INNER; i++) sink += ntruplus768_enc_derand_impl(ct, out, pk, coins);
		enc0[sample] = (ticks() - start) / INNER;
		if (candidate_first) goto candidate_decap;
	candidate_encap:
		start = ticks();
		for (int i = 0; i < INNER; i++) sink += ntruplus768_enc_derand_qword_impl(ct, out, pk, coins);
		enc1[sample] = (ticks() - start) / INNER;
		if (candidate_first) goto control_encap;
	control_decap:
		start = ticks();
		for (int i = 0; i < INNER; i++) sink += ntruplus768_dec_impl(out, ct, sk);
		dec0[sample] = (ticks() - start) / INNER;
		if (candidate_first) continue;
	candidate_decap:
		start = ticks();
		for (int i = 0; i < INNER; i++) sink += ntruplus768_dec_qword_impl(out, ct, sk);
		dec1[sample] = (ticks() - start) / INNER;
		if (candidate_first) goto control_decap;
		continue;
	}
	int enc_wins, dec_wins;
	int64_t enc_delta = median_delta(enc0, enc1, &enc_wins);
	int64_t dec_delta = median_delta(dec0, dec1, &dec_wins);
	printf("Encap   control=%llu candidate=%llu paired_delta=%lld wins=%d/%d TSC\n",
		(unsigned long long)median(enc0), (unsigned long long)median(enc1),
		(long long)enc_delta, enc_wins, SAMPLES);
	printf("Decap   control=%llu candidate=%llu paired_delta=%lld wins=%d/%d TSC\n",
		(unsigned long long)median(dec0), (unsigned long long)median(dec1),
		(long long)dec_delta, dec_wins, SAMPLES);
}

int main(void)
{
	pin_current_cpu();
	int result = correctness();
	if (result != 0) {
		fprintf(stderr, "KEM differential failed: %d\n", result);
		return 1;
	}
	puts("KEM: 1000 valid/malformed differentials PASS");
	bench_forward();
	bench_kem();
	return sink == UINT64_MAX;
}
