#include <stdint.h>
#include <stdio.h>

#include "params.h"
#include "poly.h"
#include "../test/counter.h"

#ifndef BENCH_SAMPLES
#define BENCH_SAMPLES 257
#endif

#ifndef BENCH_BATCH
#define BENCH_BATCH 64
#endif

static poly inputs[BENCH_BATCH];
static poly output;
static uint64_t samples[BENCH_SAMPLES];

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static void init_inputs(void)
{
	uint32_t seed = 0x6a09e667u;

	for (int b = 0; b < BENCH_BATCH; b++)
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			inputs[b].coeffs[i] =
				(int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) -
				          NTRUPLUS_Q);
		}
	}
}

static void sort_samples(void)
{
	for (int i = 1; i < BENCH_SAMPLES; i++)
	{
		const uint64_t x = samples[i];
		int j = i - 1;

		while (j >= 0 && samples[j] > x)
		{
			samples[j + 1] = samples[j];
			j--;
		}
		samples[j + 1] = x;
	}
}

int main(void)
{
	uint64_t checksum = 0;
	unsigned long long total = 0;

	init_inputs();
	setup_counter();

	for (int warmup = 0; warmup < 64; warmup++)
	{
		poly_ntt(&output, &inputs[warmup % BENCH_BATCH]);
		checksum += (uint16_t)output.coeffs[warmup % NTRUPLUS_N];
	}

	for (int s = 0; s < BENCH_SAMPLES; s++)
	{
		const uint64_t start = counter();
		for (int b = 0; b < BENCH_BATCH; b++)
		{
			poly_ntt(&output, &inputs[(s + b) % BENCH_BATCH]);
		}
		const uint64_t end = counter();
		const uint64_t elapsed = end - start;
		const uint64_t corrected =
			elapsed > countergap ? elapsed - countergap : elapsed;
		samples[s] = corrected / BENCH_BATCH;
		total += samples[s];
		checksum += (uint16_t)output.coeffs[s % NTRUPLUS_N];
	}

	sort_samples();
	printf("rowpack_poly_ntt_cntvct_ticks/call median=%llu avg=%.3f min=%llu max=%llu samples=%d batch=%d checksum=%llu\n",
	       (unsigned long long)samples[BENCH_SAMPLES / 2],
	       (double)total / (double)BENCH_SAMPLES,
	       (unsigned long long)samples[0],
	       (unsigned long long)samples[BENCH_SAMPLES - 1],
	       BENCH_SAMPLES,
	       BENCH_BATCH,
	       (unsigned long long)checksum);
	return 0;
}
