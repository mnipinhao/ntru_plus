#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "fips202.h"
#include "params.h"
#include "perf_counter.h"
#include "symmetric.h"

#ifndef BENCH_MODE_STR
#define BENCH_MODE_STR "hash_f"
#endif
#ifndef NTESTS
#define NTESTS 31
#endif
#ifndef NITERATIONS
#define NITERATIONS 2000
#endif
#ifndef NWARMUP
#define NWARMUP 100
#endif

static uint8_t in_poly[NTRUPLUS_POLYBYTES];
static uint8_t in_h[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
static uint8_t in_seed[NTRUPLUS_SYMBYTES];
static uint8_t out[NTRUPLUS_SSBYTES + NTRUPLUS_N / 4];
static volatile uint64_t sink;

static int compare_u64(const void *a, const void *b)
{
    uint64_t x = *(const uint64_t *)a;
    uint64_t y = *(const uint64_t *)b;
    return (x > y) - (x < y);
}

static void run_target(void)
{
    if (strcmp(BENCH_MODE_STR, "hash_f") == 0)
        hash_f(out, in_poly);
    else if (strcmp(BENCH_MODE_STR, "hash_g") == 0)
        hash_g(out, in_poly);
    else if (strcmp(BENCH_MODE_STR, "hash_h") == 0)
        hash_h(out, in_h);
    else if (strcmp(BENCH_MODE_STR, "shake_coins") == 0)
        shake256(out, NTRUPLUS_N / 4, in_seed, sizeof(in_seed));
    else {
        fprintf(stderr, "unknown mode: %s\n", BENCH_MODE_STR);
        exit(EXIT_FAILURE);
    }
}

int main(void)
{
    uint64_t samples[NTESTS];
    size_t i, j;

    for (i = 0; i < sizeof(in_poly); i++) in_poly[i] = (uint8_t)(3 * i + 1);
    for (i = 0; i < sizeof(in_h); i++) in_h[i] = (uint8_t)(5 * i + 7);
    for (i = 0; i < sizeof(in_seed); i++) in_seed[i] = (uint8_t)(11 * i + 9);
    if (perf_counter_open() != 0) return EXIT_FAILURE;
    for (i = 0; i < NWARMUP; i++) run_target();
    for (i = 0; i < NTESTS; i++) {
        if (perf_counter_start() != 0) return EXIT_FAILURE;
        for (j = 0; j < NITERATIONS; j++) run_target();
        samples[i] = perf_counter_stop() / NITERATIONS;
        sink ^= out[(i * 17) % sizeof(out)];
    }
    qsort(samples, NTESTS, sizeof(samples[0]), compare_u64);
    printf("mode=%s\nmedian=%" PRIu64 "\nsamples=", BENCH_MODE_STR,
           samples[NTESTS / 2]);
    for (i = 0; i < NTESTS; i++)
        printf("%s%" PRIu64, i ? "," : "", samples[i]);
    printf("\nsink=%" PRIu64 "\n", sink);
    perf_counter_close();
    return 0;
}
