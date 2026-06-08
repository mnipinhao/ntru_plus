#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "../api.h"

#ifndef BENCH_ITERS
#define BENCH_ITERS 1000
#endif

#ifndef BENCH_WARMUP
#define BENCH_WARMUP 100
#endif

#ifndef BENCH_BATCH
#define BENCH_BATCH 64
#endif

#ifndef BENCH_LABEL
#define BENCH_LABEL "kem_dec"
#endif

int crypto_kem_keypair(uint8_t *pk, uint8_t *sk);
int crypto_kem_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int crypto_kem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);

static inline uint64_t read_counter(void)
{
	uint64_t t;

	__asm__ volatile(
	    "isb\n\t"
	    "mrs %0, cntvct_el0\n\t"
	    "isb"
	    : "=r"(t)
	    :
	    : "memory");
	return t;
}

static inline uint64_t read_counter_freq(void)
{
	uint64_t t;

	__asm__ volatile("mrs %0, cntfrq_el0" : "=r"(t));
	return t;
}

static uint64_t read_wall_ns(void)
{
	struct timespec ts;

	clock_gettime(CLOCK_MONOTONIC, &ts);
	return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

static int cmp_u64(const void *a, const void *b)
{
	const uint64_t aa = *(const uint64_t *)a;
	const uint64_t bb = *(const uint64_t *)b;

	return (aa > bb) - (aa < bb);
}

int main(void)
{
	static uint64_t samples[BENCH_ITERS];
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t sk[NTRUPLUS_SECRETKEYBYTES];
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t ss_enc[NTRUPLUS_SSBYTES];
	uint8_t ss_dec[NTRUPLUS_SSBYTES];
	uint64_t total = 0;
	uint64_t wall_start;
	uint64_t wall_end;
	volatile uint8_t sink = 0;

	if (crypto_kem_keypair(pk, sk) != 0 ||
	    crypto_kem_enc(ct, ss_enc, pk) != 0)
	{
		printf("bench=%s setup_failed\n", BENCH_LABEL);
		return 1;
	}

	crypto_kem_dec(ss_dec, ct, sk);
	if (memcmp(ss_enc, ss_dec, sizeof(ss_enc)) != 0)
	{
		printf("bench=%s correctness_failed\n", BENCH_LABEL);
		return 1;
	}

	for (int i = 0; i < BENCH_WARMUP; i++)
	{
		crypto_kem_dec(ss_dec, ct, sk);
		sink ^= ss_dec[0];
	}

	wall_start = read_wall_ns();
	for (int i = 0; i < BENCH_ITERS; i++)
	{
		const uint64_t start = read_counter();

		for (int j = 0; j < BENCH_BATCH; j++)
		{
			crypto_kem_dec(ss_dec, ct, sk);
			sink ^= ss_dec[0];
		}

		samples[i] = read_counter() - start;
		total += samples[i];
	}
	wall_end = read_wall_ns();

	qsort(samples, BENCH_ITERS, sizeof(samples[0]), cmp_u64);

	printf("bench=%s iters=%d warmup=%d batch=%d cntfrq=%llu sink=%u\n",
	       BENCH_LABEL,
	       BENCH_ITERS,
	       BENCH_WARMUP,
	       BENCH_BATCH,
	       (unsigned long long)read_counter_freq(),
	       (unsigned)sink);
	printf("kem_dec_ticks/call min=%.3f median=%.3f avg=%.3f p90=%.3f p99=%.3f\n",
	       (double)samples[0] / (double)BENCH_BATCH,
	       (double)samples[BENCH_ITERS / 2] / (double)BENCH_BATCH,
	       ((double)total / (double)BENCH_ITERS) / (double)BENCH_BATCH,
	       (double)samples[(BENCH_ITERS * 90) / 100] / (double)BENCH_BATCH,
	       (double)samples[(BENCH_ITERS * 99) / 100] / (double)BENCH_BATCH);
	printf("kem_dec_wall_ns/call avg=%.2f\n",
	       (double)(wall_end - wall_start) /
	           (double)((uint64_t)BENCH_ITERS * (uint64_t)BENCH_BATCH));

	return 0;
}
