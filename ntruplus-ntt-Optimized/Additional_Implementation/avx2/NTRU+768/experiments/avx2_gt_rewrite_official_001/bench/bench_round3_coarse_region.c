#define _GNU_SOURCE
#include <errno.h>
#include <immintrin.h>
#include <inttypes.h>
#include <math.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "api.h"
#include "kat/rng.h"

enum { MAX_SAMPLES = 64 };

int gt_crypto_kem_keypair(unsigned char *, unsigned char *);
int gt_crypto_kem_enc(unsigned char *, unsigned char *, const unsigned char *);
int gt_crypto_kem_dec(unsigned char *, const unsigned char *,
                      const unsigned char *);

static volatile uint64_t checksum_sink;

static uint64_t region_start(void)
{
    _mm_lfence();
    return __rdtsc();
}

static uint64_t region_stop(void)
{
    unsigned aux;
    const uint64_t value = __rdtscp(&aux);
    _mm_lfence();
    return value;
}

static void reset_rng(void)
{
    unsigned char entropy[48];
    for (size_t i = 0; i < sizeof entropy; ++i)
        entropy[i] = (unsigned char)(19U + 31U * i);
    randombytes_init(entropy, NULL, 256);
}

static int pin_cpu1(void)
{
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(1, &set);
    return sched_setaffinity(0, sizeof set, &set);
}

static int compare_double(const void *left, const void *right)
{
    const double a = *(const double *)left;
    const double b = *(const double *)right;
    return (a > b) - (a < b);
}

static double median(const double *values, unsigned count)
{
    double copy[MAX_SAMPLES];
    memcpy(copy, values, count * sizeof *copy);
    qsort(copy, count, sizeof *copy, compare_double);
    return (count & 1U) != 0 ? copy[count / 2]
        : (copy[count / 2 - 1] + copy[count / 2]) / 2.0;
}

static double mad(const double *values, unsigned count, double center)
{
    double deviations[MAX_SAMPLES];
    for (unsigned i = 0; i < count; ++i)
        deviations[i] = fabs(values[i] - center);
    return median(deviations, count);
}

static double measure(int (*dec)(unsigned char *, const unsigned char *,
                                 const unsigned char *),
                      uint64_t iterations, const unsigned char *ct,
                      const unsigned char *sk)
{
    unsigned char ss[CRYPTO_BYTES];
    const uint64_t begin = region_start();
    for (uint64_t i = 0; i < iterations; ++i)
        (void)dec(ss, ct, sk);
    const uint64_t end = region_stop();
    for (size_t i = 0; i < sizeof ss; ++i)
        checksum_sink = checksum_sink * UINT64_C(1315423911) + ss[i];
    return (double)(end - begin) / (double)iterations;
}

int main(int argc, char **argv)
{
    uint64_t iterations = 100;
    unsigned samples = 20;
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--iterations") == 0 && i + 1 < argc)
            iterations = strtoull(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--samples") == 0 && i + 1 < argc)
            samples = (unsigned)strtoul(argv[++i], NULL, 10);
        else return 2;
    }
    if (iterations == 0 || samples == 0 || samples > MAX_SAMPLES) return 2;
    if (pin_cpu1() != 0) {
        fprintf(stderr, "sched_setaffinity(cpu=1): %s\n", strerror(errno));
        return 2;
    }
    const char *scope = getenv("PROFILE_SCOPE");
    if (scope == NULL || strcmp(scope, "shared_differential") != 0) return 2;

    unsigned char pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES];
    unsigned char ct[CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES];
    reset_rng();
    if (crypto_kem_keypair(pk, sk) != 0 || crypto_kem_enc(ct, ss, pk) != 0)
        return 1;
    for (unsigned i = 0; i < 2; ++i) {
        (void)measure(crypto_kem_dec, iterations, ct, sk);
        (void)measure(gt_crypto_kem_dec, iterations, ct, sk);
    }
    double official[MAX_SAMPLES], gt[MAX_SAMPLES];
    for (unsigned i = 0; i < samples; ++i) {
        if ((i & 1U) == 0) {
            official[i] = measure(crypto_kem_dec, iterations, ct, sk);
            gt[i] = measure(gt_crypto_kem_dec, iterations, ct, sk);
        } else {
            gt[i] = measure(gt_crypto_kem_dec, iterations, ct, sk);
            official[i] = measure(crypto_kem_dec, iterations, ct, sk);
        }
    }
    const double om = median(official, samples), gm = median(gt, samples);
    printf("{\n  \"schema_version\": 1,\n");
    printf("  \"profile_scope\": \"shared_differential\",\n");
    printf("  \"region\": \"decap-complete-non-nested\",\n");
    printf("  \"timer\": \"lfence;rdtsc ... rdtscp;lfence\",\n");
    printf("  \"cpu\": 1, \"iterations\": %" PRIu64
           ", \"warmups\": 2, \"samples\": %u,\n", iterations, samples);
    printf("  \"official\": {\"median_cycles\": %.3f, \"mad_cycles\": %.3f},\n",
           om, mad(official, samples, om));
    printf("  \"gt\": {\"median_cycles\": %.3f, \"mad_cycles\": %.3f},\n",
           gm, mad(gt, samples, gm));
    printf("  \"differential_cycles\": %.3f,\n", gm - om);
    printf("  \"checksum\": \"%016" PRIx64 "\"\n}\n", checksum_sink);
    return 0;
}
