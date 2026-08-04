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
#include "prototype_keypair_adapter.h"

int gt_crypto_kem_keypair(unsigned char *pk, unsigned char *sk);
int gt_crypto_kem_enc(unsigned char *ct, unsigned char *ss,
                      const unsigned char *pk);
int gt_crypto_kem_dec(unsigned char *ss, const unsigned char *ct,
                      const unsigned char *sk);

enum { BACKENDS = 4, DEFAULT_SAMPLES = 24, MAX_SAMPLES = 60 };

typedef struct {
    const char *name;
    int (*keypair)(unsigned char *, unsigned char *);
    int (*enc)(unsigned char *, unsigned char *, const unsigned char *);
    int (*dec)(unsigned char *, const unsigned char *, const unsigned char *);
} kem_backend;

typedef struct {
    double keypair;
    double encap;
    double decap;
    double total;
} sample_result;

static volatile uint64_t checksum_sink;

static uint64_t ticks(void)
{
    unsigned aux;
    _mm_lfence();
    const uint64_t value = __rdtscp(&aux);
    _mm_lfence();
    return value;
}

static void reset_rng(unsigned domain, unsigned sample)
{
    unsigned char entropy[48];
    for (size_t i = 0; i < sizeof entropy; ++i)
        entropy[i] = (unsigned char)(i + 43U * domain + 109U * sample);
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
    if ((count & 1U) != 0)
        return copy[count / 2];
    return (copy[count / 2 - 1] + copy[count / 2]) / 2.0;
}

static double mad(const double *values, unsigned count, double center)
{
    double deviations[MAX_SAMPLES];
    for (unsigned i = 0; i < count; ++i)
        deviations[i] = fabs(values[i] - center);
    return median(deviations, count);
}

static void absorb(const unsigned char *data, size_t length)
{
    uint64_t value = checksum_sink;
    for (size_t i = 0; i < length; i += 97)
        value = value * UINT64_C(1315423911) + data[i];
    checksum_sink = value;
}

static sample_result measure(const kem_backend *backend, uint64_t iterations,
                             unsigned sample, const unsigned char *pk,
                             const unsigned char *sk, const unsigned char *ct)
{
    unsigned char out_pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char out_sk[CRYPTO_SECRETKEYBYTES];
    unsigned char out_ct[CRYPTO_CIPHERTEXTBYTES];
    unsigned char out_ss[CRYPTO_BYTES];
    sample_result result;

    reset_rng(11, sample);
    uint64_t begin = ticks();
    for (uint64_t i = 0; i < iterations; ++i)
        (void)backend->keypair(out_pk, out_sk);
    uint64_t end = ticks();
    result.keypair = (double)(end - begin) / (double)iterations;
    absorb(out_pk, sizeof out_pk);
    absorb(out_sk, sizeof out_sk);

    reset_rng(13, sample);
    begin = ticks();
    for (uint64_t i = 0; i < iterations; ++i)
        (void)backend->enc(out_ct, out_ss, pk);
    end = ticks();
    result.encap = (double)(end - begin) / (double)iterations;
    absorb(out_ct, sizeof out_ct);
    absorb(out_ss, sizeof out_ss);

    begin = ticks();
    for (uint64_t i = 0; i < iterations; ++i)
        (void)backend->dec(out_ss, ct, sk);
    end = ticks();
    result.decap = (double)(end - begin) / (double)iterations;
    absorb(out_ss, sizeof out_ss);
    result.total = result.keypair + result.encap + result.decap;
    return result;
}

static void summarize(const sample_result values[MAX_SAMPLES], unsigned count,
                      sample_result *center, sample_result *dispersion)
{
    double field[MAX_SAMPLES];
#define FIELD(member) do { \
        for (unsigned i = 0; i < count; ++i) field[i] = values[i].member; \
        center->member = median(field, count); \
        dispersion->member = mad(field, count, center->member); \
    } while (0)
    FIELD(keypair);
    FIELD(encap);
    FIELD(decap);
    FIELD(total);
#undef FIELD
}

static double delta_percent(double candidate, double official)
{
    return 100.0 * (candidate - official) / official;
}

int main(int argc, char **argv)
{
    uint64_t iterations = 100;
    unsigned samples = DEFAULT_SAMPLES;
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--iterations") == 0 && i + 1 < argc)
            iterations = strtoull(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--samples") == 0 && i + 1 < argc)
            samples = (unsigned)strtoul(argv[++i], NULL, 10);
        else {
            fprintf(stderr, "usage: %s [--iterations N] [--samples N]\n",
                    argv[0]);
            return 2;
        }
    }
    if (iterations == 0 || samples == 0 || samples > MAX_SAMPLES) {
        fprintf(stderr, "invalid benchmark dimensions\n");
        return 2;
    }
    if (pin_cpu1() != 0) {
        fprintf(stderr, "sched_setaffinity(cpu=1): %s\n", strerror(errno));
        return 2;
    }

    const kem_backend backends[BACKENDS] = {
        { "official", crypto_kem_keypair, crypto_kem_enc, crypto_kem_dec },
        { "round3_canonical_gt", gt_crypto_kem_keypair,
          gt_crypto_kem_enc, gt_crypto_kem_dec },
        { "prototype_keypair_hardened_hybrid", prototype_crypto_kem_keypair,
          crypto_kem_enc, crypto_kem_dec },
        { "prototype_keypair_no_clear_hybrid",
          prototype_crypto_kem_keypair_no_clear,
          crypto_kem_enc, crypto_kem_dec }
    };
    static const unsigned orders[4][BACKENDS] = {
        { 0, 1, 2, 3 }, { 3, 2, 1, 0 }, { 1, 3, 0, 2 }, { 2, 0, 3, 1 }
    };
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    unsigned char ct[CRYPTO_CIPHERTEXTBYTES];
    unsigned char ss[CRYPTO_BYTES];
    reset_rng(17, 0);
    if (crypto_kem_keypair(pk, sk) != 0)
        return 1;
    reset_rng(19, 0);
    if (crypto_kem_enc(ct, ss, pk) != 0)
        return 1;

    for (unsigned warmup = 0; warmup < 2; ++warmup)
        for (unsigned position = 0; position < BACKENDS; ++position)
            (void)measure(&backends[orders[warmup][position]], iterations,
                          warmup, pk, sk, ct);

    sample_result values[BACKENDS][MAX_SAMPLES];
    for (unsigned sample = 0; sample < samples; ++sample)
        for (unsigned position = 0; position < BACKENDS; ++position) {
            const unsigned index = orders[sample % 4][position];
            values[index][sample] = measure(&backends[index], iterations,
                                             sample + 2, pk, sk, ct);
        }

    sample_result centers[BACKENDS];
    sample_result dispersions[BACKENDS];
    sample_result delta_centers[BACKENDS];
    sample_result delta_dispersions[BACKENDS];
    for (unsigned i = 0; i < BACKENDS; ++i)
        summarize(values[i], samples, &centers[i], &dispersions[i]);
    for (unsigned i = 0; i < BACKENDS; ++i) {
        sample_result differences[MAX_SAMPLES];
        for (unsigned sample = 0; sample < samples; ++sample) {
            differences[sample].keypair = values[i][sample].keypair
                - values[0][sample].keypair;
            differences[sample].encap = values[i][sample].encap
                - values[0][sample].encap;
            differences[sample].decap = values[i][sample].decap
                - values[0][sample].decap;
            differences[sample].total = values[i][sample].total
                - values[0][sample].total;
        }
        summarize(differences, samples, &delta_centers[i],
                  &delta_dispersions[i]);
    }

    printf("{\n");
    printf("  \"schema_version\": 1,\n");
    printf("  \"scope\": \"prototype-native-keypair-only; hybrid encap/decap are Official\",\n");
    printf("  \"cpu\": 1,\n");
    printf("  \"iterations_per_operation_per_sample\": %" PRIu64 ",\n",
           iterations);
    printf("  \"warmups\": 2,\n");
    printf("  \"paired_samples\": %u,\n", samples);
    printf("  \"backends\": {\n");
    for (unsigned i = 0; i < BACKENDS; ++i) {
        printf("    \"%s\": {\"keypair\": {\"median_cycles\": %.3f, "
               "\"mad_cycles\": %.3f}, \"encap\": {\"median_cycles\": %.3f, "
               "\"mad_cycles\": %.3f}, \"decap\": {\"median_cycles\": %.3f, "
               "\"mad_cycles\": %.3f}, \"total\": {\"median_cycles\": %.3f, "
               "\"mad_cycles\": %.3f}, \"paired_delta_cycles_vs_official\": "
               "{\"median\": %.3f, \"mad\": %.3f}, "
               "\"delta_percent_vs_official\": %.3f}%s\n",
               backends[i].name, centers[i].keypair, dispersions[i].keypair,
               centers[i].encap, dispersions[i].encap, centers[i].decap,
               dispersions[i].decap, centers[i].total, dispersions[i].total,
               delta_centers[i].total, delta_dispersions[i].total,
               delta_percent(centers[i].total, centers[0].total),
               i + 1 == BACKENDS ? "" : ",");
    }
    printf("  },\n");
    printf("  \"checksum\": \"%016" PRIx64 "\"\n", checksum_sink);
    printf("}\n");
    return 0;
}
